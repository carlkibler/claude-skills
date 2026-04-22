---
name: agent-skills-agents
description: "Compatibility shim pointing to CLAUDE.md. Source of truth for multi-agent skill conventions."
---

# AGENTS.md

> **Source of truth: [CLAUDE.md](./CLAUDE.md)**
> This file is a thin compatibility shim. All conventions, structure, and requirements live in CLAUDE.md. Read that first.

## What This Repo Is

A shared skill collection designed to work across multiple AI coding agents — Claude Code, Codex, Copilot, Gemini CLI, and any agent that follows the [Agent Skills open standard](https://agentskills.io). Skills are agent-agnostic by design.

## Multi-Agent Support Is Required

Every skill and script must work across agents, not just Claude:

- **Skill instructions** must be written in plain language, not Claude-specific syntax
- **Scripts** must be standalone (PEP 723 headers, `try/except ImportError` fallbacks) — no agent-specific tooling required to run them
- **Distribution** uses both Claude Code marketplace (`.claude-plugin/`) and Codex plugin packaging (`.agents/`, `plugins/`) — both must stay in sync
- Run `python3 scripts/sync_codex_packaging.py` after any skill changes to keep Codex packaging current

## Tool Name Mapping

Skills use Claude Code tool names in their instructions. Other agents should consult their platform's mapping:
- Codex: `references/codex-tools.md`
- Copilot CLI: `references/copilot-tools.md`
- Gemini CLI: tool mapping is loaded automatically via GEMINI.md

## Creating or Modifying Skills

See CLAUDE.md for full conventions. Short version:

1. Skill lives in `skills/<name>/SKILL.md` with YAML frontmatter (`name`, `description` required)
2. Scripts go in `skills/<name>/scripts/` — standalone, PEP 723, works without any agent
3. Register in `.claude-plugin/marketplace.json` for Claude, then run the sync script for Codex
4. Use `${CLAUDE_SKILL_DIR}` (or the agent-equivalent env var) to reference bundled files at runtime
