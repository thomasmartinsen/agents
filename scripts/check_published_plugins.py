#!/usr/bin/env python3
"""Verify generated plugin packages and both marketplace catalogs are published on main.

Requires GitHub CLI authentication with read access to thomasmartinsen/agents
and thomasmartinsen/marketplace. Reads Git trees only; never publishes changes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys

from sync_plugins import REPO_ROOT, build, codex_catalog, json_text

AGENTS_REPOSITORY = "thomasmartinsen/agents"
MARKETPLACE_REPOSITORY = "thomasmartinsen/marketplace"


def git_blob_sha(content: str) -> str:
    data = content.encode("utf-8")
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def published_files(repository: str) -> dict[str, str]:
    result = subprocess.run(
        ["gh", "api", f"repos/{repository}/git/trees/main?recursive=1"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
        check=False,
    )
    if result.returncode:
        raise ValueError(f"Cannot read {repository}@main: {result.stderr.strip()}")
    response = json.loads(result.stdout)
    if response.get("truncated") is not False or not isinstance(response.get("tree"), list):
        raise ValueError(f"{repository}@main: GitHub returned an incomplete Git tree")
    return {
        entry["path"]: entry["sha"]
        for entry in response["tree"]
        if entry.get("type") == "blob" and entry.get("mode") == "100644"
    }


def check_files(expected: dict[str, str], published: dict[str, str]) -> list[str]:
    failures = []
    for path, content in sorted(expected.items()):
        if path not in published:
            failures.append(f"Missing regular file: {path}")
        elif published[path] != git_blob_sha(content):
            failures.append(f"Published content differs: {path}")
    return failures


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()
    outputs, catalog = build()
    expected = {
        AGENTS_REPOSITORY: {
            path.relative_to(REPO_ROOT).as_posix(): content
            for path, content in outputs.items()
        },
        MARKETPLACE_REPOSITORY: {
            ".github/plugin/marketplace.json": json_text(catalog),
            ".agents/plugins/marketplace.json": json_text(codex_catalog(catalog)),
        },
    }
    failed = False
    for repository, files in expected.items():
        try:
            failures = check_files(files, published_files(repository))
        except (OSError, subprocess.SubprocessError, ValueError) as error:
            print(f"{repository}: {error}", file=sys.stderr)
            failed = True
            continue
        if failures:
            print(f"{repository}@main:", file=sys.stderr)
            for failure in failures:
                print(f"  {failure}", file=sys.stderr)
            failed = True
        else:
            print(f"{repository}@main: all {len(files)} generated files match.")
    if failed:
        print(
            "Publication check failed. Publish the matching packages and export both "
            "marketplace catalogs; this check does not modify either repository.",
            file=sys.stderr,
        )
        return 1
    print(f"All {len(catalog['plugins'])} plugins and both client catalogs are published correctly.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
