# CLAUDE.md

Personal Claude Code skills collection by Carl Kibler.

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
skills/
  ├── pre-mortem/                # Multi-agent pre-mortem analysis
  ├── profile-me/                # Build AI profile from digital footprint
  ├── getting-second-opinions/   # Copilot CLI validation with gpt-5.4-codex
  └── okta-sso-debugger/         # Okta CIAM SSO debugging for Leap tenants
```
