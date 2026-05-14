#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build a bounded RALPH review prompt for a repo."""

from __future__ import annotations

import argparse
import datetime as dt
import subprocess
from pathlib import Path

DEFAULT_GLOBS = [
    "apps/**/*.py",
    "src/**/*.py",
    "lib/**/*.py",
    "**/views.py",
    "**/tasks.py",
    "**/services/*.py",
    "**/api*.py",
]
KEY_PATTERNS = (
    "^(class|def|async def) |^    def |except |raise |logger\\.|capture_exception|sentry|requests\\.|httpx\\.|send_mail|shared_task|@shared_task|cache\\.|timeout|transaction\\.|json\\.loads|subprocess|token|secret|webhook|password"
)


def run(cmd: list[str], cwd: Path) -> str:
    try:
        return subprocess.check_output(cmd, cwd=cwd, text=True, stderr=subprocess.DEVNULL)
    except Exception:
        return ""


def candidate_files(root: Path, limit: int) -> list[Path]:
    files: dict[Path, int] = {}
    for pattern in DEFAULT_GLOBS:
        for path in root.glob(pattern):
            if path.is_file() and ".venv" not in path.parts and "migrations" not in path.parts:
                try:
                    lines = sum(1 for _ in path.open(errors="ignore"))
                except OSError:
                    continue
                files[path] = lines
    ranked = sorted(files.items(), key=lambda item: item[1], reverse=True)
    return [path for path, _lines in ranked[:limit]]


def excerpt(path: Path, max_lines: int) -> str:
    lines = path.read_text(errors="ignore").splitlines()
    if len(lines) <= max_lines:
        return "\n".join(lines)
    head = max_lines // 2
    tail = max_lines - head
    return "\n".join(lines[:head] + ["\n# ... snip ...\n"] + lines[-tail:])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--focus", default="next under-reviewed code surface")
    parser.add_argument("--out-dir", default="")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--excerpt-lines", type=int, default=120)
    args = parser.parse_args()

    root = Path.cwd()
    repo_name = root.name
    out_dir = Path(args.out_dir or Path.home() / "dev" / "agent-notes" / repo_name)
    out_dir.mkdir(parents=True, exist_ok=True)
    date = dt.date.today().isoformat()
    prompt_path = out_dir / f"ralph-prompt-{date}.md"

    recent = run(["git", "log", "--oneline", "-8"], root)
    status = run(["git", "status", "--short"], root)
    review_docs = sorted(root.glob("docs/reviews/*.md"))[-8:]
    files = candidate_files(root, args.limit)

    parts: list[str] = []
    parts.append("# RALPH codebase hardening review packet\n")
    parts.append(f"Repo: `{repo_name}`")
    parts.append(f"Focus: {args.focus}")
    parts.append("\nReview goals: correctness, security/auth, observability/Sentry, clarity/refactoring, user-safe errors, no secrets/PII leakage.")
    parts.append("Return Must-fix / Should-fix / Nice-to-have / Reject. Include file/function, reason, suggested fix, severity. Prefer small actionable fixes.\n")
    parts.append("## Current git status\n```\n" + (status or "clean\n") + "```\n")
    parts.append("## Recent commits\n```\n" + recent + "```\n")
    if review_docs:
        parts.append("## Recent review docs to avoid repeating\n" + "\n".join(f"- {p}" for p in review_docs) + "\n")

    parts.append("## Candidate file/function/error map\n")
    for path in files:
        rel = path.relative_to(root)
        parts.append(f"### {rel}")
        rg = run(["rg", "-n", KEY_PATTERNS, str(rel)], root)
        parts.append("```\n" + "\n".join(rg.splitlines()[:120]) + "\n```\n")

    parts.append("## Bounded excerpts\n")
    for path in files[:6]:
        rel = path.relative_to(root)
        parts.append(f"### {rel}\n```python\n{excerpt(path, args.excerpt_lines)}\n```\n")

    prompt_path.write_text("\n".join(parts))
    print(prompt_path)
    print(f"chars={prompt_path.stat().st_size}")


if __name__ == "__main__":
    main()
