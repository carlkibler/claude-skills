#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

import json
import os
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO / "skills"
AGENT_SKILLS_DIR = REPO / ".agents" / "skills"
AGENT_PLUGINS_DIR = REPO / ".agents" / "plugins"
PLUGINS_DIR = REPO / "plugins"
CLAUDE_MARKETPLACE = REPO / ".claude-plugin" / "marketplace.json"
README = REPO / "README.md"

GROUP_ORDER = ["Better Products", "Dev Workflow", "Utilities"]


def parse_skill_frontmatter(text: str) -> dict[str, str]:
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


def load_claude_marketplace() -> dict:
    return json.loads(CLAUDE_MARKETPLACE.read_text())


def ensure_symlink(path: Path, target: Path) -> None:
    if path.is_symlink():
        if os.readlink(path) == str(target):
            return
        path.unlink()
    elif path.exists():
        raise RuntimeError(f"Refusing to replace non-symlink path: {path}")
    path.symlink_to(target)


def skill_icon_svg(display_name: str, color: str) -> str:
    letters = "".join(word[0] for word in re.findall(r"[A-Za-z0-9]+", display_name)[:2]).upper() or "S"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128" fill="none">
  <rect width="128" height="128" rx="28" fill="{color}"/>
  <circle cx="96" cy="32" r="10" fill="white" fill-opacity="0.18"/>
  <path d="M30 92C46 68 66 54 94 44" stroke="white" stroke-opacity="0.18" stroke-width="8" stroke-linecap="round"/>
  <text x="64" y="75" text-anchor="middle" font-size="38" font-family="Inter, ui-sans-serif, system-ui, sans-serif" font-weight="700" fill="white">{letters}</text>
</svg>
'''


def build_openai_yaml(display_name: str, short_description: str, default_prompt: str, brand_color: str, local_only: bool) -> str:
    scope_note = " Best in local Codex CLI/app sessions on your own machine." if local_only else " Safe for repo-local and cloud/repo-checkout workflows."
    short_description = (short_description + scope_note).replace('"', "'")
    default_prompt = default_prompt.replace('"', "'")
    return (
        "interface:\n"
        f"  display_name: \"{display_name}\"\n"
        f"  short_description: \"{short_description}\"\n"
        f"  icon_small: \"./assets/icon.svg\"\n"
        f"  icon_large: \"./assets/icon.svg\"\n"
        f"  brand_color: \"{brand_color}\"\n"
        f"  default_prompt: \"{default_prompt}\"\n"
        "policy:\n"
        f"  allow_implicit_invocation: {'false' if local_only else 'true'}\n"
    )


def replace_section(text: str, heading: str, body: str) -> str:
    pattern = rf"## {re.escape(heading)}\n\n.*?(?=\n## |\Z)"
    replacement = f"## {heading}\n\n{body.rstrip()}\n"
    new_text, count = re.subn(pattern, replacement, text, flags=re.S)
    if count != 1:
        raise RuntimeError(f"Could not uniquely replace README section: {heading}")
    return new_text


def build_skills_section(rows: dict[str, list[dict[str, str]]]) -> str:
    parts = []
    intros = {
        "Better Products": "Find failure modes, trust problems, and support burden before your users do.",
        "Dev Workflow": "Tools for the day-to-day of writing and reviewing code.",
        "Utilities": "",
    }
    for group in GROUP_ORDER:
        parts.append(f"### {group}\n")
        intro = intros[group]
        if intro:
            parts.append(f"{intro}\n")
        parts.append("| Skill | |")
        parts.append("|-------|---|")
        for row in rows[group]:
            install = f"`/plugin install {row['name']}@carl-tools`"
            parts.append(f"| **{row['name']}** | {row['summary']}<br><sub>{install}</sub> |")
        parts.append("")
    return "\n".join(parts).rstrip() + "\n"


def update_readme(rows: dict[str, list[dict[str, str]]]) -> None:
    text = README.read_text()
    skills_body = build_skills_section(rows)
    text = replace_section(text, "Skills", skills_body)
    README.write_text(text)


def main() -> None:
    AGENT_SKILLS_DIR.mkdir(parents=True, exist_ok=True)
    AGENT_PLUGINS_DIR.mkdir(parents=True, exist_ok=True)
    PLUGINS_DIR.mkdir(parents=True, exist_ok=True)

    marketplace = load_claude_marketplace()
    claude_plugins = {plugin["name"]: plugin for plugin in marketplace["plugins"]}

    codex_marketplace = {
        "name": "carl-tools",
        "interface": {"displayName": "Carl Tools"},
        "plugins": [],
    }
    readme_rows = {group: [] for group in GROUP_ORDER}

    for skill_path in sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir()):
        skill_name = skill_path.name
        skill_text = (skill_path / "SKILL.md").read_text()
        frontmatter = parse_skill_frontmatter(skill_text)
        plugin_meta = claude_plugins.get(skill_name, {})
        config_fields = {
            "display_name": frontmatter.get("display_name", skill_name.replace("-", " ").title()),
            "brand_color": frontmatter.get("brand_color", "#10A37F"),
            "default_prompt": frontmatter.get("default_prompt", f"Use the {skill_name} skill."),
            "local_only": frontmatter.get("local_only", "false").lower() == "true",
            "group": frontmatter.get("group", "Utilities"),
            "usage": frontmatter.get("usage", f"/{skill_name}:run"),
            "summary": frontmatter.get("summary", frontmatter.get("description", skill_name)),
        }
        display_name = config_fields["display_name"]
        description = plugin_meta.get("description") or frontmatter.get("description", display_name)
        version = plugin_meta.get("version", "1.0.0")
        category = plugin_meta.get("category", "productivity").title()
        brand_color = config_fields["brand_color"]
        default_prompt = config_fields["default_prompt"]
        local_only = config_fields["local_only"]
        group = config_fields["group"]
        usage = config_fields["usage"]
        summary = config_fields["summary"]

        ensure_symlink(AGENT_SKILLS_DIR / skill_name, Path("..") / ".." / "skills" / skill_name)

        plugin_root = PLUGINS_DIR / skill_name
        (plugin_root / ".codex-plugin").mkdir(parents=True, exist_ok=True)
        (plugin_root / "skills").mkdir(parents=True, exist_ok=True)
        ensure_symlink(plugin_root / "skills" / skill_name, Path("..") / ".." / ".." / "skills" / skill_name)

        manifest = {
            "name": skill_name,
            "version": version,
            "description": description,
            "author": {"name": "carlkibler"},
            "homepage": "https://github.com/carlkibler/agent-skills",
            "repository": "https://github.com/carlkibler/agent-skills",
            "license": "MIT",
            "skills": "./skills/",
            "interface": {
                "displayName": display_name,
                "shortDescription": description,
                "longDescription": description + (" Works best on a local machine with user-specific files and tools available." if local_only else " Works well in repo-local and Codex cloud workflows that operate on a checked-out repository."),
                "developerName": "carlkibler",
                "category": category,
                "websiteURL": "https://github.com/carlkibler/agent-skills",
                "defaultPrompt": [default_prompt],
                "brandColor": brand_color,
                "composerIcon": "./skills/" + skill_name + "/assets/icon.svg",
                "logo": "./skills/" + skill_name + "/assets/icon.svg",
            },
        }
        (plugin_root / ".codex-plugin" / "plugin.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")

        assets_dir = skill_path / "assets"
        assets_dir.mkdir(parents=True, exist_ok=True)
        (assets_dir / "icon.svg").write_text(skill_icon_svg(display_name, brand_color))

        agents_dir = skill_path / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        (agents_dir / "openai.yaml").write_text(
            build_openai_yaml(display_name, description, default_prompt, brand_color, local_only)
        )

        codex_marketplace["plugins"].append(
            {
                "name": skill_name,
                "source": {"source": "local", "path": f"./plugins/{skill_name}"},
                "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                "category": category,
            }
        )
        readme_rows[group].append({"name": skill_name, "usage": usage, "summary": summary})

    (AGENT_PLUGINS_DIR / "marketplace.json").write_text(json.dumps(codex_marketplace, indent=2, ensure_ascii=False) + "\n")
    update_readme(readme_rows)


if __name__ == "__main__":
    main()
