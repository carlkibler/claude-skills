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

SKILL_CONFIG = {
    "chezmoi-drift": {
        "display_name": "Chezmoi Drift",
        "brand_color": "#2563EB",
        "default_prompt": "Audit this machine or dotfiles setup for chezmoi drift and broken shared skill installs. Report first; don't mutate anything unless I explicitly ask.",
        "local_only": True,
        "group": "Utilities",
        "usage": "/chezmoi-drift:run",
        "summary": "Audit chezmoi dotfiles for drift and broken skill installs",
    },
    "first-run-red-team": {
        "display_name": "First-Run Red Team",
        "brand_color": "#DC2626",
        "default_prompt": "Red-team the first-run experience for this product. Find where a new user gets confused, abandons setup, or thinks the app is broken.",
        "local_only": False,
        "group": "Better Products",
        "usage": "/first-run-red-team:run",
        "summary": "Red-team onboarding and first-run experience for abandonment traps",
    },
    "handle-pr": {
        "display_name": "Handle PR",
        "brand_color": "#7C3AED",
        "default_prompt": "Handle the PR review comments end-to-end: evaluate each thread, implement the worthwhile changes, run checks, and prepare replies.",
        "local_only": True,
        "group": "Dev Workflow",
        "usage": "/handle-pr:run",
        "summary": "Autonomously address PR review comments end-to-end",
    },
    "parallel-isolated-app-testing": {
        "display_name": "Parallel Isolated App Testing",
        "brand_color": "#0F766E",
        "default_prompt": "Design a safe parallel isolated testing plan for this app, including collision surfaces, lane boundaries, and launcher contracts.",
        "local_only": False,
        "group": "Dev Workflow",
        "usage": "/parallel-isolated-app-testing:run",
        "summary": "Design parallel isolated test lanes for apps with shared local state",
    },
    "pre-mortem": {
        "display_name": "Pre-Mortem",
        "brand_color": "#B45309",
        "default_prompt": "Run a sharp pre-mortem on this project or launch. Surface specific failure modes, then rank them and propose mitigations.",
        "local_only": False,
        "group": "Better Products",
        "usage": "/pre-mortem:run",
        "summary": "Multi-agent project pre-mortem — ranked risks with mitigations",
    },
    "profile-me": {
        "display_name": "Profile Me",
        "brand_color": "#1D4ED8",
        "default_prompt": "Build an evidence-based AI profile of me from the local artifacts available in this environment, and clearly label inferences vs. observations.",
        "local_only": True,
        "group": "Utilities",
        "usage": "/profile-me:run",
        "summary": "Build a portable AI profile from your digital footprint",
    },
    "second-opinions": {
        "display_name": "Second Opinions",
        "brand_color": "#4F46E5",
        "default_prompt": "Get a second opinion on this implementation or design decision and summarize the strongest agreement, disagreement, and actionable feedback.",
        "local_only": False,
        "group": "Dev Workflow",
        "usage": "/second-opinions:run",
        "summary": "Get a second opinion from a different AI on complex changes",
    },
    "support-inbox-simulation": {
        "display_name": "Support Inbox Simulation",
        "brand_color": "#DB2777",
        "default_prompt": "Simulate the support emails, bug reports, reviews, and refund requests this launch or feature change is likely to generate.",
        "local_only": False,
        "group": "Better Products",
        "usage": "/support-inbox-simulation:run",
        "summary": "Simulate the support emails and refunds a launch will generate",
    },
    "trust-audit": {
        "display_name": "Trust Audit",
        "brand_color": "#059669",
        "default_prompt": "Audit this product or feature for trust risks: permissions, privacy, billing, surprise mutations, and anything that feels creepy or unsafe.",
        "local_only": False,
        "group": "Better Products",
        "usage": "/trust-audit:run",
        "summary": "Audit a product's trust surface: permissions, privacy, billing, and silent failures",
    },
    "wifi-qr": {
        "display_name": "WiFi QR",
        "brand_color": "#0891B2",
        "default_prompt": "Generate a WiFi QR code PNG from an SSID and password, and save it to a path I specify.",
        "local_only": False,
        "group": "Utilities",
        "usage": "/wifi-qr:run",
        "summary": "Generate a WiFi QR code PNG",
    },
    "empathy-audit": {
        "display_name": "Empathy Audit",
        "brand_color": "#7C3AED",
        "default_prompt": "Run an empathy audit on this code or feature through user, machine, developer, and support lenses.",
        "local_only": False,
        "group": "Better Products",
        "usage": "/empathy-audit:run",
        "summary": "Four-lens empathy review: user, machine, developer, support",
    },
}

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
        config = SKILL_CONFIG.get(skill_name, {})
        display_name = config.get("display_name", skill_name.replace("-", " ").title())
        description = plugin_meta.get("description") or frontmatter.get("description", display_name)
        version = plugin_meta.get("version", "1.0.0")
        category = plugin_meta.get("category", "productivity").title()
        brand_color = config.get("brand_color", "#10A37F")
        default_prompt = config.get("default_prompt", f"Use the {display_name} skill for this task.")
        local_only = bool(config.get("local_only", False))
        group = config.get("group", "Utilities")
        usage = config.get("usage", f"/{skill_name}:run")
        summary = config.get("summary", description)

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
        (plugin_root / ".codex-plugin" / "plugin.json").write_text(json.dumps(manifest, indent=2) + "\n")

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

    (AGENT_PLUGINS_DIR / "marketplace.json").write_text(json.dumps(codex_marketplace, indent=2) + "\n")
    update_readme(readme_rows)


if __name__ == "__main__":
    main()
