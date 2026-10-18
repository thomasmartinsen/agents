#!/usr/bin/env python3
"""Generate Codex custom agents from GitHub Copilot custom agent profiles.

Reads .github/agents/*.agent.md and writes one TOML file per agent to
.codex/agents/. Use --install to also copy them to ~/.codex/agents/, and
--check to fail when the generated files are out of date.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11
    tomllib = None

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = REPO_ROOT / ".github" / "agents"
TARGET_DIR = REPO_ROOT / ".codex" / "agents"
PERSONAL_DIR = Path.home() / ".codex" / "agents"

TOOL_NOTES = {
    "edit": "You may edit files, but only when the user asks; otherwise return drafts in chat.",
    "no-edit": "Do not create, edit, or delete files. Return your output in chat.",
    "web": "You may use web search to research and verify current information.",
    "no-web": "Do not browse or search the web. Work from supplied material and say what you cannot verify.",
}


def parse_profile(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.DOTALL)
    if not match:
        raise ValueError(f"{path}: missing YAML frontmatter")
    front, body = match.groups()
    meta = {}
    for line in front.splitlines():
        key, sep, value = line.partition(":")
        if sep:
            meta[key.strip()] = value.strip()
    for field in ("name", "description"):
        if not meta.get(field):
            raise ValueError(f"{path}: missing '{field}' in frontmatter")
    tools = [t.strip() for t in meta.get("tools", "").strip("[]").split(",") if t.strip()]
    return {"name": meta["name"], "description": meta["description"], "tools": tools, "body": body.strip()}


def codex_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def toml_string(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def toml_multiline(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"""', '""\\"')
    return f'"""\n{escaped}\n"""'


def developer_instructions(profile: dict) -> str:
    tools = profile["tools"]
    notes = [
        TOOL_NOTES["edit" if "edit" in tools else "no-edit"],
        TOOL_NOTES["web" if "web" in tools else "no-web"],
        "Do not execute generated code or run commands beyond reading and searching files.",
    ]
    return (
        f"{profile['body']}\n\n## Tool boundaries\n\n" + "\n".join(f"- {note}" for note in notes)
    )


def render(profile: dict, source: Path) -> str:
    instructions = developer_instructions(profile)
    rel = source.relative_to(REPO_ROOT).as_posix()
    return (
        f"# Generated from {rel} by scripts/sync_codex_agents.py. Do not edit directly.\n"
        f"name = {toml_string(codex_name(profile['name']))}\n"
        f"description = {toml_string(profile['description'])}\n"
        f"developer_instructions = {toml_multiline(instructions)}\n"
    )


def build() -> dict[str, str]:
    outputs = {}
    for source in sorted(SOURCE_DIR.glob("*.agent.md")):
        profile = parse_profile(source)
        content = render(profile, source)
        if tomllib:
            parsed = tomllib.loads(content)
            if parsed["name"] != codex_name(profile["name"]) or not parsed["developer_instructions"].strip():
                raise ValueError(f"{source}: generated TOML did not round-trip")
        outputs[source.name[: -len(".agent.md")] + ".toml"] = content
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if .codex/agents is out of date")
    parser.add_argument("--install", action="store_true", help="also copy agents to ~/.codex/agents")
    args = parser.parse_args()

    outputs = build()
    existing = {p.name for p in TARGET_DIR.glob("*.toml")} if TARGET_DIR.exists() else set()

    if args.check:
        stale = sorted(
            name for name, content in outputs.items()
            if not (TARGET_DIR / name).exists() or (TARGET_DIR / name).read_text(encoding="utf-8") != content
        ) + sorted(existing - outputs.keys())
        if stale:
            print("Out of date: " + ", ".join(stale) + ". Run scripts/sync_codex_agents.py.")
            return 1
        print(f"{len(outputs)} Codex agents up to date.")
        return 0

    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    for name in existing - outputs.keys():
        (TARGET_DIR / name).unlink()
    for name, content in outputs.items():
        (TARGET_DIR / name).write_text(content, encoding="utf-8")
    print(f"Wrote {len(outputs)} agents to {TARGET_DIR.relative_to(REPO_ROOT)}")

    if args.install:
        PERSONAL_DIR.mkdir(parents=True, exist_ok=True)
        for name in outputs:
            shutil.copyfile(TARGET_DIR / name, PERSONAL_DIR / name)
        print(f"Installed {len(outputs)} agents to {PERSONAL_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
