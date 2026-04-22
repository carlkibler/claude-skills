---
name: agent-skills-claude
description: "Shared skill collection conventions for Claude Code and Codex. Source of truth for structure, scripts, and distribution."
---

# CLAUDE.md

Shared skill collection for Claude Code and Codex.

## Conventions

### Scripts Must Be Standalone

All Python scripts in skills MUST be self-contained and runnable without cloning any other repo.

**Use PEP 723 inline script metadata** so `uv run` handles deps automatically:
```python
# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx>=0.27", "click>=8.0"]
# ///
```

Also include a `try/except ImportError` fallback for plain `python` usage:
```python
try:
    import click
    import httpx
except ImportError:
    sys.exit("Missing dependencies. Run: pip install httpx click")
```

Invoke scripts with `uv run scripts/my_script.py` — deps install into a temp venv automatically.

### Skill Structure

```
skills/my-skill/
├── SKILL.md              # Required — YAML frontmatter + instructions
├── scripts/              # Standalone Python with PEP 723 headers
├── references/           # Docs loaded into context as needed
└── assets/               # Files used in output (templates, etc.)
```

**SKILL.md frontmatter** — `name` and `description` are required:
```yaml
---
name: my-skill
description: Specific description of what it does and when to use it.
---
```

### Distribution via Plugin Marketplace

This repo supports both Claude Code and Codex distribution patterns.

**Claude Code marketplace**

```
/plugin marketplace add carlkibler/agent-skills
/plugin install <skill-name>@carl-tools
```

Register Claude marketplace entries in `.claude-plugin/marketplace.json`.

**Codex local discovery and marketplace**

- Repo-local skills live in `skills/` and are exposed to Codex through `.agents/skills/` symlinks.
- Repo-local Codex plugin listings live in `.agents/plugins/marketplace.json`.
- Each installable Codex plugin lives at `plugins/<name>/.codex-plugin/plugin.json` and points at the shared skill source.
- Optional Codex app metadata lives in `skills/<name>/agents/openai.yaml`.
- Run `python3 scripts/sync_codex_packaging.py` after adding, renaming, or re-categorizing skills so the Codex symlinks, marketplace entries, manifests, and metadata stay in sync.
- Treat `.agents/skills/*`, `.agents/plugins/marketplace.json`, `plugins/*/.codex-plugin/plugin.json`, `skills/*/agents/openai.yaml`, and `skills/*/assets/icon.svg` as generated artifacts owned by the sync script.

Skills follow the [Agent Skills open standard](https://agentskills.io) and work across Claude Code and Codex. Use `${CLAUDE_SKILL_DIR}` in scripts to reference bundled files at runtime instead of hardcoded paths.

### Naming

- Skill directories: lowercase kebab-case (`okta-sso-debugger`)
- Python scripts: snake_case (`okta_api.py`)

### Creating New Skills

Use the `/skill-creator` skill or copy an existing skill as a starting point.

After creating, register in `.claude-plugin/marketplace.json`.

## Security

Never include credentials, API keys, or secrets in skills. Tokens go in `.env` files (gitignored) or environment variables.

## Directory Structure

```
.claude-plugin/
  ├── marketplace.json            # Claude marketplace catalog
  └── plugin.json                 # Claude repo manifest
.agents/
  ├── skills/                     # Codex repo-local skill discovery symlinks
  └── plugins/marketplace.json    # Codex local marketplace catalog
plugins/
  └── <skill-name>/
      └── .codex-plugin/plugin.json # Codex plugin manifest
scripts/
  └── sync_codex_packaging.py      # Regenerates Codex packaging artifacts
skills/
  ├── pre-mortem/                 # Multi-agent pre-mortem analysis
  ├── profile-me/                 # Build AI profile from digital footprint
  ├── second-opinions/            # Copilot/Codex validation from another model
  ├── handle-pr/                  # Auto-handle PR review comments
  ├── chezmoi-drift/              # Dotfiles drift + shared-skill install audit
  ├── trust-audit/                # Product trust surface audit
  ├── support-inbox-simulation/   # Pre-launch support email simulation
  ├── first-run-red-team/         # First-run experience red-teaming
  ├── wifi-qr/                    # WiFi QR code generator
  └── empathy-audit/              # Four-lens empathy review (user, machine, developer, support)
```
