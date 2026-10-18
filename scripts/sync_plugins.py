#!/usr/bin/env python3
"""Package agents for Copilot and Codex and optionally export their marketplace catalogs."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from sync_codex_agents import REPO_ROOT, SOURCE_DIR, developer_instructions, parse_profile

PLUGIN_DIR = REPO_ROOT / "plugins"
VERSION = "1.0.1"
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
        outputs[PLUGIN_DIR / name / ".codex-plugin" / "plugin.json"] = json_text({
            "name": name,
            "description": profile["description"],
            "version": VERSION,
            "author": manifest["author"],
            "repository": REPOSITORY,
            "skills": "./codex-skills/",
            "interface": {"displayName": profile["name"]},
        })
        outputs[PLUGIN_DIR / name / "codex-skills" / name / "SKILL.md"] = (
            f"---\nname: {name}\n"
            f"description: {json.dumps(profile['description'], ensure_ascii=False)}\n---\n\n"
            f"{developer_instructions(profile)}\n"
        )
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


def codex_catalog(catalog: dict) -> dict:
    return {
        "name": MARKETPLACE_NAME,
        "interface": {"displayName": "Thomas Martinsen"},
        "plugins": [
            {
                "name": entry["name"],
                "description": entry["description"],
                "version": entry["version"],
                "source": {
                    "source": "git-subdir",
                    "url": f"{REPOSITORY}.git",
                    "ref": "main",
                    "path": f"./{entry['source']['path']}",
                },
                "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                "category": "Productivity",
            }
            for entry in catalog["plugins"]
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if generated files are out of date")
    parser.add_argument(
        "--marketplace-output",
        type=Path,
        help="also export the catalog for thomasmartinsen/marketplace (replaces the target file)",
    )
    parser.add_argument(
        "--codex-marketplace-output",
        type=Path,
        help="also export the Codex .agents/plugins/marketplace.json (replaces the target file)",
    )
    args = parser.parse_args()

    outputs, catalog = build()
    existing = (
        set(PLUGIN_DIR.glob("*/plugin.json"))
        | set(PLUGIN_DIR.glob("*/agents/*.agent.md"))
        | set(PLUGIN_DIR.glob("*/.codex-plugin/plugin.json"))
        | set(PLUGIN_DIR.glob("*/codex-skills/*/SKILL.md"))
    )
    for target, data in (
        (args.marketplace_output, catalog),
        (args.codex_marketplace_output, codex_catalog(catalog)),
    ):
        if target:
            target = target.resolve()
            if target in outputs or target == Path(__file__).resolve():
                parser.error("Marketplace outputs must be distinct and must not overwrite plugin files or this script")
            outputs[target] = json_text(data)

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
    for target in (args.marketplace_output, args.codex_marketplace_output):
        if target:
            print(f"Exported marketplace catalog to {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
