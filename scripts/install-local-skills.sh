#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_DIR="$ROOT/skills"
TARGETS=("$HOME/.claude/skills" "$HOME/.codex/skills" "$HOME/.agents/skills")

for target in "${TARGETS[@]}"; do
  mkdir -p "$target"
done

for skill in "$SKILLS_DIR"/*/; do
  name="$(basename "$skill")"
  for target in "${TARGETS[@]}"; do
    ln -sfn "$skill" "$target/$name"
    echo "linked $name -> $target/$name"
  done
done
