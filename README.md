# Claude/Codex Skills

Personal skills for Claude Code and Codex.

## Skills

| Skill | Description |
|-------|-------------|
| [pre-mortem](skills/pre-mortem/) | Multi-agent project pre-mortem (Gary Klein technique) |
| [profile-me](skills/profile-me/) | Build AI profile from digital footprint |
| [getting-second-opinions](skills/getting-second-opinions/) | Validate decisions with gpt-5.4-codex via Copilot CLI |
| [handle-pr](skills/handle-pr/) | Auto-handle PR review comments, reply, watch for new ones |
| [chezmoi-drift](skills/chezmoi-drift/) | Audit chezmoi drift, unmanaged dotfiles, and broken shared-skill installs |
| [okta-sso-debugger](skills/okta-sso-debugger/) | Okta CIAM SSO debugging for Leap tenants |
| [trust-audit](skills/trust-audit/) | Audit trust risks across permissions, privacy, billing, file mutation, and silent failure |
| [support-inbox-simulation](skills/support-inbox-simulation/) | Simulate support emails, reviews, refunds, and founder-tax before launch |
| [first-run-red-team](skills/first-run-red-team/) | Red-team onboarding, permissions, activation, and first-run abandonment risk |

## Setup

These skills use a shared `SKILL.md` format that works in both tools.

- **Claude Code:** install into `~/.claude/skills/`
- **Codex:** install into `~/.codex/skills/`
- **Local Carl harness:** also expose shared skills in `~/.agents/skills/`

Symlink individual skills:
```bash
ln -s ~/dev/me/claude-skills/skills/pre-mortem ~/.claude/skills/pre-mortem
ln -s ~/dev/me/claude-skills/skills/pre-mortem ~/.codex/skills/pre-mortem
```

Or symlink all for Claude + Codex:
```bash
mkdir -p ~/.claude/skills ~/.codex/skills
for skill in ~/dev/me/claude-skills/skills/*/; do
  ln -sf "$skill" ~/.claude/skills/$(basename "$skill")
  ln -sf "$skill" ~/.codex/skills/$(basename "$skill")
done
```

If you want the local harness to see them too:
```bash
mkdir -p ~/.agents/skills
for skill in ~/dev/me/claude-skills/skills/*/; do
  ln -sf "$skill" ~/.agents/skills/$(basename "$skill")
done
```

Or use the helper script for Claude + Codex + the local harness:
```bash
~/dev/me/claude-skills/scripts/install-local-skills.sh
```
