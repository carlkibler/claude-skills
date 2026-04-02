# Claude Code Skills

Personal skills for [Claude Code](https://claude.ai/claude-code).

## Skills

| Skill | Description |
|-------|-------------|
| [pre-mortem](skills/pre-mortem/) | Multi-agent project pre-mortem (Gary Klein technique) |
| [profile-me](skills/profile-me/) | Build AI profile from digital footprint |
| [getting-second-opinions](skills/getting-second-opinions/) | Validate decisions with gpt-5.4-codex via Copilot CLI |
| [okta-sso-debugger](skills/okta-sso-debugger/) | Okta CIAM SSO debugging for Leap tenants |

## Setup

Symlink individual skills:
```bash
ln -s ~/dev/me/claude-skills/skills/pre-mortem ~/.claude/skills/pre-mortem
```

Or symlink all:
```bash
for skill in ~/dev/me/claude-skills/skills/*/; do
  ln -sf "$skill" ~/.claude/skills/$(basename "$skill")
done
```
