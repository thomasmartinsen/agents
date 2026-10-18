#!/usr/bin/env python3
"""Package Copilot agents as plugins and optionally export their marketplace catalog."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from sync_codex_agents import REPO_ROOT, SOURCE_DIR, parse_profile

PLUGIN_DIR = REPO_ROOT / "plugins"
VERSION = "1.0.0"
REPOSITORY = "https://github.com/thomasmartinsen/agents"
MARKETPLACE_NAME = "thomasmartinsen"


def json_text(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def build() -> tuple[dict[Path, str], dict]:
    sources = sorted(SOURCE_DIR.glob("*.agent.md"))
    if not sources:
        raise ValueError(f"No agent profiles found in {SOURCE_DIR}")

    outputs = {}
    entries = []
    for source in sources:
        name = source.name.removesuffix(".agent.md")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
            raise ValueError(f"{source}: plugin filename must use kebab-case")
        profile = parse_profile(source)
        manifest = {
            "name": name,
            "description": profile["description"],
            "version": VERSION,
            "author": {"name": "Thomas Martinsen"},
            "repository": REPOSITORY,
            "agents": "agents/",
        }
        outputs[PLUGIN_DIR / name / "plugin.json"] = json_text(manifest)
        outputs[PLUGIN_DIR / name / "agents" / source.name] = source.read_text(encoding="utf-8")
        entries.append({
            "name": name,
            "description": manifest["description"],
            "version": manifest["version"],
            "source": {
                "source": "github",
                "repo": "thomasmartinsen/agents",
                "ref": "main",
                "path": f"plugins/{name}",
            },
        })

    catalog = {
        "name": MARKETPLACE_NAME,
        "owner": {"name": "Thomas Martinsen"},
        "metadata": {
            "description": "Thomas Martinsen's content and advisory agent plugins.",
            "version": VERSION,
        },
        "plugins": entries,
    }
    return outputs, catalog


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if generated files are out of date")
    parser.add_argument(
        "--marketplace-output",
        type=Path,
        help="also export the catalog for thomasmartinsen/marketplace (replaces the target file)",
    )
    args = parser.parse_args()

    outputs, catalog = build()
    existing = set(PLUGIN_DIR.glob("*/plugin.json")) | set(PLUGIN_DIR.glob("*/agents/*.agent.md"))
    if args.marketplace_output:
        target = args.marketplace_output.resolve()
        if target in outputs or target == Path(__file__).resolve():
            parser.error("--marketplace-output must not overwrite plugin files or this script")
        outputs[target] = json_text(catalog)

    stale = [
        path for path, content in outputs.items()
        if not path.is_file() or path.read_text(encoding="utf-8") != content
    ]
    obsolete = sorted(existing - outputs.keys())
    if args.check:
        if stale or obsolete:
            print("Out of date:\n" + "\n".join(str(path) for path in sorted(stale + obsolete)))
            print("Run scripts/sync_plugins.py with the same output options.")
            return 1
        print(f"{len(catalog['plugins'])} plugins up to date.")
        return 0

    for path in obsolete:
        path.unlink()
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
    print(f"Wrote {len(catalog['plugins'])} plugins to {PLUGIN_DIR}")
    if args.marketplace_output:
        print(f"Exported marketplace catalog to {args.marketplace_output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
