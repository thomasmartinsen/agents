"""Offline regression tests for cross-repository publication checks."""

import contextlib
import io
import json
import subprocess
import unittest
from unittest.mock import patch

import check_published_plugins as publication
from sync_plugins import REPO_ROOT, build, codex_catalog, json_text


class PublicationTests(unittest.TestCase):
    def test_git_blob_sha_uses_git_header_and_utf8_byte_length(self):
        self.assertEqual(publication.git_blob_sha(""), "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391")
        self.assertEqual(publication.git_blob_sha("hello\n"), "ce013625030ba8dba906f756967f9e9ca394464a")
        self.assertNotEqual(publication.git_blob_sha("hello\n"), publication.git_blob_sha("hello\r\n"))
        self.assertEqual(publication.git_blob_sha("caf\u00e9"), "1c2e52cfe7542a64cdea57e5fec2fc1739846c03")

    def test_reports_missing_and_changed_files(self):
        self.assertEqual(
            publication.check_files(
                {"missing.json": "{}", "changed.json": "{}", "correct.json": "{}"},
                {
                    "changed.json": publication.git_blob_sha("old"),
                    "correct.json": publication.git_blob_sha("{}"),
                },
            ),
            [
                "Published content differs: changed.json",
                "Missing regular file: missing.json",
            ],
        )

    def test_fetches_main_and_excludes_symlinks(self):
        response = {
            "truncated": False,
            "tree": [
                {"path": "plugin.json", "sha": "file", "mode": "100644", "type": "blob"},
                {"path": "linked.json", "sha": "link", "mode": "120000", "type": "blob"},
            ],
        }
        completed = subprocess.CompletedProcess([], 0, stdout=json.dumps(response))
        with patch.object(publication.subprocess, "run", return_value=completed) as run:
            self.assertEqual(publication.published_files("owner/repo"), {"plugin.json": "file"})
            self.assertEqual(
                run.call_args.args[0], ["gh", "api", "repos/owner/repo/git/trees/main?recursive=1"],
            )

    def test_api_failure_and_truncated_trees_are_errors(self):
        for result, message in (
            (subprocess.CompletedProcess([], 1, stderr="authentication required"), "authentication required"),
            (subprocess.CompletedProcess([], 0, stdout='{"truncated": true, "tree": []}'), "incomplete Git tree"),
            (subprocess.CompletedProcess([], 0, stdout='{}'), "incomplete Git tree"),
        ):
            with self.subTest(message=message):
                with patch.object(publication.subprocess, "run", return_value=result):
                    with self.assertRaisesRegex(ValueError, message):
                        publication.published_files("owner/repo")

    def test_checks_both_client_catalogs_and_every_generated_package_file(self):
        outputs, catalog = build()
        agents = {
            path.relative_to(REPO_ROOT).as_posix(): publication.git_blob_sha(content)
            for path, content in outputs.items()
        }
        marketplace = {
            ".github/plugin/marketplace.json": publication.git_blob_sha(json_text(catalog)),
            ".agents/plugins/marketplace.json": publication.git_blob_sha(json_text(codex_catalog(catalog))),
        }
        with patch("sys.argv", ["check_published_plugins.py"]):
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                with patch.object(publication, "published_files", side_effect=[agents, marketplace]) as fetch:
                    self.assertEqual(publication.main(), 0)
                    self.assertEqual(fetch.call_count, 2)
                for path in marketplace:
                    with self.subTest(missing=path):
                        incomplete = {key: value for key, value in marketplace.items() if key != path}
                        with patch.object(publication, "published_files", side_effect=[agents, incomplete]):
                            self.assertEqual(publication.main(), 1)
                missing_skill = {key: value for key, value in agents.items() if not key.endswith("SKILL.md")}
                with patch.object(publication, "published_files", side_effect=[missing_skill, marketplace]):
                    self.assertEqual(publication.main(), 1)
                with patch.object(publication, "published_files", side_effect=FileNotFoundError("gh not found")):
                    self.assertEqual(publication.main(), 1)


if __name__ == "__main__":
    unittest.main()
