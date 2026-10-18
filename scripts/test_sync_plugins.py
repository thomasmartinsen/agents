"""Regression tests for generated plugins and the external marketplace catalog."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import sync_plugins


class PluginTests(unittest.TestCase):
    def test_every_profile_is_packaged_unchanged(self):
        outputs, catalog = sync_plugins.build()
        sources = sorted(sync_plugins.SOURCE_DIR.glob("*.agent.md"))
        self.assertEqual(len(catalog["plugins"]), len(sources))
        self.assertEqual(len(outputs), len(sources) * 2)
        self.assertEqual(len({entry["name"] for entry in catalog["plugins"]}), len(sources))
        for source, entry in zip(sources, catalog["plugins"]):
            root = sync_plugins.PLUGIN_DIR / entry["name"]
            manifest = json.loads(outputs[root / "plugin.json"])
            self.assertEqual(manifest["name"], entry["name"])
            self.assertEqual(manifest["version"], entry["version"])
            self.assertEqual(manifest["description"], entry["description"])
            self.assertEqual(
                outputs[root / manifest["agents"] / source.name],
                source.read_text(encoding="utf-8"),
            )
            self.assertEqual(entry["source"], {
                "source": "github",
                "repo": "thomasmartinsen/agents",
                "ref": "main",
                "path": f"plugins/{entry['name']}",
            })

    def test_empty_source_directory_is_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(sync_plugins, "SOURCE_DIR", Path(directory)):
                with self.assertRaisesRegex(ValueError, "No agent profiles"):
                    sync_plugins.build()

    def test_invalid_plugin_name_is_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "Invalid Name.agent.md"
            source.write_text("---\nname: Test\ndescription: Test\n---\nBody\n", encoding="utf-8")
            with patch.object(sync_plugins, "SOURCE_DIR", Path(directory)):
                with self.assertRaisesRegex(ValueError, "kebab-case"):
                    sync_plugins.build()

    def test_generation_and_check_detect_drift_and_obsolete_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            catalog = root / "marketplace.json"
            args = ["sync_plugins.py", "--marketplace-output", str(catalog)]
            with patch.object(sync_plugins, "PLUGIN_DIR", root / "plugins"):
                with patch("sys.argv", args):
                    self.assertEqual(sync_plugins.main(), 0)
                with patch("sys.argv", args + ["--check"]):
                    self.assertEqual(sync_plugins.main(), 0)
                    manifest = next((root / "plugins").glob("*/plugin.json"))
                    manifest.write_text("{}\n", encoding="utf-8")
                    self.assertEqual(sync_plugins.main(), 1)
                obsolete = root / "plugins" / "removed" / "plugin.json"
                obsolete.parent.mkdir()
                obsolete.write_text("{}\n", encoding="utf-8")
                with patch("sys.argv", args):
                    self.assertEqual(sync_plugins.main(), 0)
                self.assertFalse(obsolete.exists())
                with patch("sys.argv", args + ["--check"]):
                    self.assertEqual(sync_plugins.main(), 0)
                    catalog.write_text("{}\n", encoding="utf-8")
                    self.assertEqual(sync_plugins.main(), 1)


if __name__ == "__main__":
    unittest.main()
