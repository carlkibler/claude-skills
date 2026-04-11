---
name: run
description: Audit chezmoi-managed dotfiles for drift, unmanaged files worth tracking, and broken shared-skill installs. Use when checking whether home-directory config has diverged from chezmoi, cleaning up dotfiles, or debugging Claude/Codex skill symlinks.
---

# Chezmoi Drift

Use this skill as a dotfiles weekly checkup. Report first; mutate later.

## Quick Start

```bash
src_dir=$(chezmoi source-path)
chezmoi status 2>&1
chezmoi unmanaged 2>&1 | grep -Ev '\.DS_Store|__pycache__|/Library/|/Caches/' | head -60
```

If `chezmoi status` is empty, managed files are in sync.

## Workflow

### 1. Check managed-file drift

Run:

```bash
chezmoi status 2>&1
```

Interpret status codes:
- `M` = modified in target
- `A` = present in source but not applied
- `R` = present in target but removed from source

Report exact paths and codes. Do not paraphrase away the useful bits.

### 2. Find unmanaged files worth tracking

Run:

```bash
chezmoi unmanaged 2>&1 | grep -Ev '\.DS_Store|__pycache__|/Library/|/Caches/' | head -60
```

Flag only files that look intentional and reusable, especially in:
- `~/`
- `~/.local/bin/`
- `~/.config/`
- `~/.claude/`
- `~/.codex/`

Skip app noise, caches, session files, logs, and secrets.

### 3. Check script and config coverage

Run:

```bash
src_dir=$(chezmoi source-path)
comm -23 \
  <(ls ~/.local/bin | sort) \
  <(ls "$src_dir/dot_local/bin" | sed 's/^executable_//' | sort)

comm -23 \
  <(ls ~/.config | sort) \
  <(ls "$src_dir/dot_config" | sort)
```

Report new scripts or config directories that look worth managing.

### 4. Check shared skill install health

If a local agent-skills repo exists (e.g. `~/dev/me/agent-skills/skills`), prefer symlinks from the live skill directories back to that repo rather than copying.

Inspect:

```bash
for host in ~/.claude/skills ~/.codex/skills ~/.agents/skills; do
  [ -d "$host" ] || continue
  echo "== $host =="
  ls -ld "$host"/chezmoi-drift 2>/dev/null || true
  readlink "$host"/chezmoi-drift 2>/dev/null || true
done
```

Call out:
- missing installs
- copied directories where a symlink should exist
- stale links (broken or pointing to a moved/deleted source)

### 5. Report

Use this format:

```text
DRIFT REPORT
============
Managed files with drift: ...
Unmanaged files worth tracking: ...
Scripts not in chezmoi: ...
Config dirs not in chezmoi: ...
Shared skill install issues: ...
```

Then propose exact commands for anything worth fixing.

## Action Rules

- Do **not** run `chezmoi add`, `chezmoi re-add`, `chezmoi apply`, `rm`, or git commands unless the user explicitly asks.
- Prefer `chezmoi source-path` over hard-coding the source repo path.
- Never add secrets or token-bearing files without converting them to a safe template first.
- For shared skills, prefer `ln -sfn <repo>/skills/<skill> <target>` over copying directories around.
