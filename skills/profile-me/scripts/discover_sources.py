#!/usr/bin/env python3
"""
Discover available data sources for Speaker profile generation.

Scans the user's environment for Claude Code artifacts, project files,
shell configuration, and other sources of profile data.

Usage:
    python3 discover_sources.py [--home PATH]

Output:
    Prints a structured report of available data sources and their sizes.
"""

import argparse
import os
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Discover Speaker data sources")
    parser.add_argument(
        "--home",
        default=os.path.expanduser("~"),
        help="Home directory to scan (default: ~)",
    )
    return parser.parse_args()


def file_info(path):
    """Return (exists, size_bytes, line_count_or_none)."""
    p = Path(path)
    if not p.exists():
        return False, 0, None
    size = p.stat().st_size
    if p.suffix in (".jsonl", ".json", ".md", ".txt", ".sh", ".py", ".toml", ".yaml", ".yml"):
        try:
            with open(p) as f:
                lines = sum(1 for _ in f)
            return True, size, lines
        except Exception:
            return True, size, None
    return True, size, None


def human_size(n):
    """Format bytes as human-readable."""
    for unit in ("B", "KB", "MB", "GB"):
        if abs(n) < 1024:
            return f"{n:.1f} {unit}" if unit != "B" else f"{n} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def find_claude_md_files(home):
    """Find all CLAUDE.md files in dev directories."""
    results = []
    dev_dirs = [Path(home) / "dev", Path(home) / "dev" / "me"]
    for dev_dir in dev_dirs:
        if not dev_dir.exists():
            continue
        for child in sorted(dev_dir.iterdir()):
            if child.is_dir():
                claude_md = child / "CLAUDE.md"
                if claude_md.exists():
                    exists, size, lines = file_info(claude_md)
                    results.append((str(claude_md), size, lines))
    return results


def find_memory_files(projects_dir):
    """Find all memory files in Claude projects."""
    results = []
    if not projects_dir.exists():
        return results
    for project in sorted(projects_dir.iterdir()):
        if not project.is_dir():
            continue
        memory_dir = project / "memory"
        if memory_dir.exists():
            for f in sorted(memory_dir.iterdir()):
                if f.is_file():
                    exists, size, lines = file_info(f)
                    results.append((str(f), size, lines))
    return results


def find_project_dirs(home):
    """Find project directories with READMEs."""
    results = []
    dev_dirs = [Path(home) / "dev", Path(home) / "dev" / "me"]
    for dev_dir in dev_dirs:
        if not dev_dir.exists():
            continue
        for child in sorted(dev_dir.iterdir()):
            if child.is_dir() and not child.name.startswith("."):
                readme = None
                for name in ("README.md", "README", "README.txt", "README.rst"):
                    if (child / name).exists():
                        readme = child / name
                        break
                results.append((str(child), child.name, readme is not None))
    return results


def main():
    args = parse_args()
    home = Path(args.home)
    claude_dir = home / ".claude"

    print("=" * 70)
    print("SPEAKER — Data Source Discovery Report")
    print("=" * 70)

    # Section 1: Claude Code Environment
    print("\n## Claude Code Environment")
    print()

    claude_files = [
        (claude_dir / "CLAUDE.md", "Global instructions"),
        (claude_dir / "settings.json", "Settings"),
        (claude_dir / "settings.local.json", "Local settings"),
        (claude_dir / "history.jsonl", "Conversation history"),
    ]

    for path, desc in claude_files:
        exists, size, lines = file_info(path)
        if exists:
            line_info = f" ({lines:,} lines)" if lines else ""
            print(f"  [FOUND] {path.name}: {human_size(size)}{line_info} — {desc}")
        else:
            print(f"  [    ] {path.name} — {desc}")

    # Agents
    agents_dir = claude_dir / "agents"
    if agents_dir.exists():
        agents = list(agents_dir.glob("*.md"))
        print(f"  [FOUND] agents/: {len(agents)} agent definitions")
    else:
        print("  [    ] agents/ — not found")

    # Skills
    skills_dir = claude_dir / "skills"
    if skills_dir.exists():
        skills = [d for d in skills_dir.iterdir() if d.is_dir()]
        print(f"  [FOUND] skills/: {len(skills)} installed skills")
    else:
        print("  [    ] skills/ — not found")

    # Bin
    bin_dir = claude_dir / "bin"
    if bin_dir.exists():
        scripts = [f for f in bin_dir.iterdir() if f.is_file()]
        print(f"  [FOUND] bin/: {len(scripts)} custom scripts")
    else:
        print("  [    ] bin/ — not found")

    # Section 2: Memory Files
    print("\n## Memory Files")
    print()
    projects_dir = claude_dir / "projects"
    memories = find_memory_files(projects_dir)
    if memories:
        total_size = sum(s for _, s, _ in memories)
        print(f"  Found {len(memories)} memory files ({human_size(total_size)} total)")
        for path, size, lines in memories:
            short_path = path.replace(str(projects_dir) + "/", "")
            print(f"    {short_path} ({human_size(size)})")
    else:
        print("  No memory files found")

    # Section 3: Project CLAUDE.md Files
    print("\n## Project CLAUDE.md Files")
    print()
    claude_mds = find_claude_md_files(home)
    if claude_mds:
        print(f"  Found {len(claude_mds)} project CLAUDE.md files")
        for path, size, lines in claude_mds:
            short = path.replace(str(home) + "/", "~/")
            line_info = f" ({lines} lines)" if lines else ""
            print(f"    {short}{line_info}")
    else:
        print("  No project CLAUDE.md files found")

    # Section 4: Shell Configuration
    print("\n## Shell & System Configuration")
    print()
    shell_files = [
        (home / ".bashrc", "Bash config"),
        (home / ".bash_profile", "Bash login"),
        (home / ".zshrc", "Zsh config"),
        (home / ".zprofile", "Zsh login"),
        (home / ".profile", "POSIX profile"),
        (home / ".gitconfig", "Git config"),
        (home / ".ssh" / "config", "SSH config"),
        (home / ".aws" / "config", "AWS config"),
    ]

    for path, desc in shell_files:
        exists, size, lines = file_info(path)
        if exists:
            line_info = f" ({lines} lines)" if lines else ""
            print(f"  [FOUND] {path.name}: {human_size(size)}{line_info} — {desc}")
        else:
            print(f"  [    ] {path.name} — {desc}")

    # Section 5: Project Directories
    print("\n## Project Directories")
    print()
    projects = find_project_dirs(home)
    work_projects = [p for p in projects if "/me/" not in p[0]]
    personal_projects = [p for p in projects if "/me/" in p[0]]

    if work_projects:
        print(f"  Work ({len(work_projects)} repos):")
        for path, name, has_readme in work_projects:
            readme_tag = " [README]" if has_readme else ""
            print(f"    {name}{readme_tag}")

    if personal_projects:
        print(f"\n  Personal ({len(personal_projects)} repos):")
        for path, name, has_readme in personal_projects:
            readme_tag = " [README]" if has_readme else ""
            print(f"    {name}{readme_tag}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    total_sources = 0
    if (claude_dir / "history.jsonl").exists():
        total_sources += 1
        _, hsize, hlines = file_info(claude_dir / "history.jsonl")
        print(f"  Conversation history: {hlines:,} entries ({human_size(hsize)})")
    print(f"  Memory files: {len(memories)}")
    print(f"  CLAUDE.md files: {len(claude_mds) + (1 if (claude_dir / 'CLAUDE.md').exists() else 0)}")
    print(f"  Project directories: {len(projects)}")
    print(f"  Shell/system configs: {sum(1 for p, _ in shell_files if p.exists())}")
    print()
    print("Run collect_history_stats.py next for conversation analysis.")


if __name__ == "__main__":
    main()
