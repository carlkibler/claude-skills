# agent-skills

Claude Code skills for multi-agent workflows, PR automation, product analysis, and more.

## Install

Add this repo as a Claude Code marketplace:

```
/plugin marketplace add carlkibler/agent-skills
```

Then install individual skills:

```
/plugin install pre-mortem@agent-skills
/plugin install handle-pr@agent-skills
/plugin install trust-audit@agent-skills
```

Or browse and install from the UI: run `/plugin` → **Discover** tab.

After installing, run `/reload-plugins` to activate.

## Usage

Skills are namespaced by plugin name. Invoke directly or let Claude trigger them automatically:

```
/pre-mortem:run
/handle-pr:run
/trust-audit:run
```

Or just ask naturally — Claude will invoke the right skill based on context.

## Skills

| Plugin name | Skill | Description |
|-------------|-------|-------------|
| `pre-mortem` | `/pre-mortem:run` | Multi-agent project pre-mortem (Gary Klein technique) |
| `profile-me` | `/profile-me:run` | Build AI profile from digital footprint |
| `getting-second-opinions` | `/getting-second-opinions:run` | Validate decisions with gpt-5.4-codex via Copilot CLI |
| `handle-pr` | `/handle-pr:run` | Auto-handle PR review comments end-to-end |
| `chezmoi-drift` | `/chezmoi-drift:run` | Audit chezmoi dotfiles drift and broken skill installs |
| `trust-audit` | `/trust-audit:run` | Audit trust risks: permissions, privacy, billing, silent failures |
| `support-inbox-simulation` | `/support-inbox-simulation:run` | Simulate support emails and founder-tax before launch |
| `first-run-red-team` | `/first-run-red-team:run` | Red-team onboarding, permissions, and first-run abandonment |
| `wifi-qr` | `/wifi-qr:run` | Generate a WiFi QR code PNG |

## Managing plugins

```
# Disable without uninstalling
/plugin disable handle-pr@agent-skills

# Re-enable
/plugin enable handle-pr@agent-skills

# Uninstall
/plugin uninstall handle-pr@agent-skills

# Update marketplace listings
/plugin marketplace update agent-skills
```

## Scope

Install at user scope (default, available across all projects) or project scope:

```
# Project scope — adds to .claude/settings.json, shared with team
claude plugin install pre-mortem@agent-skills --scope project
```

## Pre-configure for a team

Add to your project's `.claude/settings.json` to prompt teammates to install on first run:

```json
{
  "extraKnownMarketplaces": {
    "agent-skills": {
      "source": {
        "source": "github",
        "repo": "carlkibler/agent-skills"
      }
    }
  }
}
```

## Local development

Test locally without installing from GitHub:

```bash
claude --plugin-dir ./skills/pre-mortem
```
