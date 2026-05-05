#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Validate that skills, marketplace entries, symlinks, and generated artifacts
are all consistent. Exits 0 if clean, 1 if any issues found.

Usage:
    python3 scripts/lint_skills.py
    uv run scripts/lint_skills.py
"""

import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO / "skills"
AGENT_SKILLS_DIR = REPO / ".agents" / "skills"
PLUGINS_DIR = REPO / "plugins"
CLAUDE_MARKETPLACE = REPO / ".claude-plugin" / "marketplace.json"

MAX_DESCRIPTION_LEN = 160

issues: list[str] = []
warnings: list[str] = []


def err(msg: str) -> None:
    issues.append(f"  ERROR  {msg}")


def warn(msg: str) -> None:
    warnings.append(f"  WARN   {msg}")


def parse_frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        return {}
    meta: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip('"')
    return meta


def yaml_scalar_is_quoted(value: str) -> bool:
    value = value.strip()
    return len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}


def check_simple_yaml_scalars(label: str, yaml_text: str) -> None:
    """Catch common frontmatter breakage without adding a PyYAML dependency."""
    for line_no, line in enumerate(yaml_text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        _key, value = stripped.split(":", 1)
        value = value.strip()
        if value and not yaml_scalar_is_quoted(value) and ": " in value:
            err(f"{label}:{line_no}: unquoted YAML value contains ': '; wrap it in quotes")


def check_skill(skill_path: Path, claude_names: set[str]) -> None:
    name = skill_path.name
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        err(f"{name}: missing SKILL.md")
        return

    skill_text = skill_md.read_text()
    frontmatter = re.match(r"^---\n(.*?)\n---\n", skill_text, re.S)
    if frontmatter:
        check_simple_yaml_scalars(f"{name}/SKILL.md", frontmatter.group(1))
    fm = parse_frontmatter(skill_text)

    if not fm.get("name"):
        err(f"{name}/SKILL.md: missing 'name' in frontmatter")
    elif fm["name"] != name:
        err(f"{name}/SKILL.md: name '{fm['name']}' doesn't match folder name")

    desc = fm.get("description", "")
    if not desc:
        err(f"{name}/SKILL.md: missing 'description' in frontmatter")
    elif len(desc) > MAX_DESCRIPTION_LEN:
        warn(f"{name}/SKILL.md: description is {len(desc)} chars (limit {MAX_DESCRIPTION_LEN})")

    if not fm.get("display_name"):
        warn(f"{name}/SKILL.md: missing 'display_name' in frontmatter")
    if not fm.get("brand_color"):
        warn(f"{name}/SKILL.md: missing 'brand_color' in frontmatter")
    valid_groups = {"Better Products", "Dev Workflow", "Utilities"}
    group = fm.get("group", "")
    if not group:
        warn(f"{name}/SKILL.md: missing 'group' in frontmatter")
    elif group not in valid_groups:
        warn(f"{name}/SKILL.md: 'group' is '{group}', expected one of {sorted(valid_groups)}")

    symlink = AGENT_SKILLS_DIR / name
    if not symlink.exists():
        err(f"{name}: missing .agents/skills/{name} symlink")
    elif not symlink.is_symlink():
        err(f"{name}: .agents/skills/{name} is not a symlink")
    else:
        target = Path(os.readlink(symlink))
        resolved = (symlink.parent / target).resolve()
        if resolved != skill_path.resolve():
            err(f"{name}: .agents/skills/{name} points to wrong target: {target}")

    plugin_dir = PLUGINS_DIR / name
    if not plugin_dir.exists():
        err(f"{name}: missing plugins/{name}/")
    else:
        manifest_path = plugin_dir / ".codex-plugin" / "plugin.json"
        if not manifest_path.exists():
            err(f"{name}: missing plugins/{name}/.codex-plugin/plugin.json")
        else:
            try:
                manifest = json.loads(manifest_path.read_text())
                if manifest.get("name") != name:
                    err(f"{name}: plugin.json 'name' is '{manifest.get('name')}', expected '{name}'")
                pdesc = manifest.get("description", "")
                if len(pdesc) > MAX_DESCRIPTION_LEN:
                    warn(f"{name}: plugin.json description is {len(pdesc)} chars (limit {MAX_DESCRIPTION_LEN})")
                sdesc = manifest.get("interface", {}).get("shortDescription", "")
                if len(sdesc) > MAX_DESCRIPTION_LEN + 80:
                    warn(f"{name}: plugin.json shortDescription is {len(sdesc)} chars")
            except json.JSONDecodeError as e:
                err(f"{name}: plugin.json is invalid JSON: {e}")

        skill_link = plugin_dir / "skills" / name
        if not skill_link.exists():
            err(f"{name}: missing plugins/{name}/skills/{name} symlink")
        stale = [p for p in (plugin_dir / "skills").iterdir() if p.name != name]
        for s in stale:
            err(f"{name}: stale symlink in plugins/{name}/skills/: {s.name}")

    if name not in claude_names:
        warn(f"{name}: not listed in .claude-plugin/marketplace.json")

    openai_yaml = skill_path / "agents" / "openai.yaml"
    if not openai_yaml.exists():
        warn(f"{name}: missing skills/{name}/agents/openai.yaml (run sync_codex_packaging.py)")
    else:
        check_simple_yaml_scalars(f"{name}/agents/openai.yaml", openai_yaml.read_text())

    icon = skill_path / "assets" / "icon.svg"
    if not icon.exists():
        warn(f"{name}: missing skills/{name}/assets/icon.svg (run sync_codex_packaging.py)")


def check_marketplace_orphans(skill_names: set[str], claude_names: set[str]) -> None:
    for name in claude_names - skill_names:
        err(f".claude-plugin/marketplace.json: entry '{name}' has no skills/{name}/ folder")


def check_agent_symlink_orphans(skill_names: set[str]) -> None:
    for symlink in AGENT_SKILLS_DIR.iterdir():
        if symlink.name not in skill_names:
            err(f".agents/skills/{symlink.name}: symlink has no matching skills/ folder")


def check_plugin_orphans(skill_names: set[str]) -> None:
    if not PLUGINS_DIR.exists():
        return
    for plugin_dir in PLUGINS_DIR.iterdir():
        if plugin_dir.name not in skill_names:
            err(f"plugins/{plugin_dir.name}/: no matching skills/ folder")


def main() -> None:
    if not SKILLS_DIR.exists():
        print("ERROR: skills/ directory not found", file=sys.stderr)
        sys.exit(1)

    claude_data = json.loads(CLAUDE_MARKETPLACE.read_text())
    claude_names = {p["name"] for p in claude_data.get("plugins", [])}

    skill_dirs = sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir())
    skill_names = {p.name for p in skill_dirs}

    print(f"Checking {len(skill_dirs)} skills...\n")

    for skill_path in skill_dirs:
        check_skill(skill_path, claude_names)

    check_marketplace_orphans(skill_names, claude_names)
    check_agent_symlink_orphans(skill_names)
    check_plugin_orphans(skill_names)

    for w in warnings:
        print(w)
    for e in issues:
        print(e)

    if not issues and not warnings:
        print("All skills are clean.")
    elif not issues:
        print(f"\n{len(warnings)} warning(s), 0 errors.")
    else:
        print(f"\n{len(warnings)} warning(s), {len(issues)} error(s).")
        sys.exit(1)


if __name__ == "__main__":
    main()
