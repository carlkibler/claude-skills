#!/usr/bin/env python3
"""
Analyze Claude Code conversation history for Speaker profile generation.

Reads ~/.claude/history.jsonl and produces statistics about:
- Project frequency (what they work on most)
- Message length distribution (communication style)
- Vocabulary patterns (technical depth, formality)
- Emotional markers (caps, punctuation patterns)
- Activity timeline (when they work)

Usage:
    python3 collect_history_stats.py [--history-file PATH] [--output-dir PATH] [--sample-size N]

Output:
    stats.json          — Quantitative analysis
    samples.txt         — Representative message samples for qualitative analysis
"""

import argparse
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Analyze Claude Code conversation history")
    parser.add_argument(
        "--history-file",
        default=os.path.expanduser("~/.claude/history.jsonl"),
        help="Path to history.jsonl (default: ~/.claude/history.jsonl)",
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory for output files (default: current directory)",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=80,
        help="Number of representative messages to sample (default: 80)",
    )
    return parser.parse_args()


def load_history(path):
    """Load and parse history.jsonl."""
    entries = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries


def extract_messages(entries):
    """Extract user messages from history entries."""
    messages = []
    for entry in entries:
        display = entry.get("display", "")
        if isinstance(display, str) and display.strip():
            messages.append(
                {
                    "text": display.strip(),
                    "project": entry.get("project", ""),
                    "timestamp": entry.get("timestamp"),
                }
            )
    return messages


def analyze_project_frequency(messages):
    """Count messages per project."""
    projects = Counter()
    for msg in messages:
        project = msg.get("project", "")
        if project:
            short_name = project.rstrip("/").split("/")[-1] if "/" in project else project
            projects[short_name] += 1
    return dict(projects.most_common(30))


def analyze_message_lengths(messages):
    """Analyze message length distribution."""
    lengths = [len(m["text"]) for m in messages]
    if not lengths:
        return {}

    lengths.sort()
    n = len(lengths)
    return {
        "count": n,
        "mean": round(sum(lengths) / n, 1),
        "median": lengths[n // 2],
        "p10": lengths[n // 10],
        "p90": lengths[int(n * 0.9)],
        "min": lengths[0],
        "max": lengths[-1],
        "under_20_chars_pct": round(100 * sum(1 for l in lengths if l < 20) / n, 1),
        "under_50_chars_pct": round(100 * sum(1 for l in lengths if l < 50) / n, 1),
        "over_200_chars_pct": round(100 * sum(1 for l in lengths if l > 200) / n, 1),
        "over_500_chars_pct": round(100 * sum(1 for l in lengths if l > 500) / n, 1),
    }


def analyze_emotional_markers(messages):
    """Detect emotional expression patterns."""
    texts = [m["text"] for m in messages if len(m["text"]) > 10]
    n = len(texts)
    if n == 0:
        return {}

    all_caps_words = 0
    exclamation_msgs = 0
    question_msgs = 0
    ellipsis_msgs = 0
    emoji_msgs = 0

    for text in texts:
        words = text.split()
        all_caps_words += sum(
            1 for w in words if len(w) > 2 and w.isupper() and w.isalpha()
        )
        if "!" in text:
            exclamation_msgs += 1
        if "?" in text:
            question_msgs += 1
        if "..." in text:
            ellipsis_msgs += 1
        if re.search(r"[\U0001F600-\U0001F9FF]", text):
            emoji_msgs += 1

    return {
        "total_messages_analyzed": n,
        "all_caps_words_total": all_caps_words,
        "msgs_with_exclamation_pct": round(100 * exclamation_msgs / n, 1),
        "msgs_with_question_pct": round(100 * question_msgs / n, 1),
        "msgs_with_ellipsis_pct": round(100 * ellipsis_msgs / n, 1),
        "msgs_with_emoji_pct": round(100 * emoji_msgs / n, 1),
    }


def analyze_typo_density(messages):
    """Estimate typo frequency from common patterns."""
    common_typos = [
        (r"\bnad\b", "and"),
        (r"\badn\b", "and"),
        (r"\bteh\b", "the"),
        (r"\bsitll\b", "still"),
        (r"\bthat that\b", "that"),
        (r"\bwoudl\b", "would"),
        (r"\bshoudl\b", "should"),
        (r"\bcoudl\b", "could"),
        (r"\brecieve\b", "receive"),
        (r"\boccured\b", "occurred"),
        (r"\bseperately\b", "separately"),
    ]

    texts = [m["text"] for m in messages]
    typo_count = 0
    word_count = 0

    for text in texts:
        words = text.split()
        word_count += len(words)
        for pattern, _ in common_typos:
            typo_count += len(re.findall(pattern, text, re.IGNORECASE))

    return {
        "detected_typo_instances": typo_count,
        "total_words": word_count,
        "typo_rate_per_1000_words": round(1000 * typo_count / max(word_count, 1), 2),
        "note": "Only detects common transposition patterns; actual rate likely higher",
    }


def analyze_delegation_style(messages):
    """Categorize delegation patterns."""
    texts = [m["text"] for m in messages if len(m["text"]) > 10]
    n = len(texts)
    if n == 0:
        return {}

    imperative = 0  # starts with verb
    questioning = 0  # asks a question
    contextual = 0  # provides background before asking
    terse = 0  # under 30 chars

    imperative_verbs = {
        "fix",
        "add",
        "remove",
        "update",
        "create",
        "delete",
        "move",
        "change",
        "make",
        "run",
        "deploy",
        "check",
        "verify",
        "commit",
        "push",
        "merge",
        "revert",
        "start",
        "stop",
        "build",
        "test",
        "read",
        "write",
        "show",
        "list",
        "find",
        "search",
        "install",
        "configure",
        "set",
        "get",
        "put",
        "send",
        "open",
        "close",
        "do",
        "try",
        "use",
        "dispatch",
        "continue",
        "resume",
        "implement",
        "refactor",
        "rename",
        "split",
        "combine",
    }

    for text in texts:
        first_word = text.split()[0].lower().rstrip(".,!?:;")
        if first_word in imperative_verbs:
            imperative += 1
        if "?" in text:
            questioning += 1
        if len(text) > 200 and ("because" in text.lower() or "context" in text.lower()):
            contextual += 1
        if len(text) < 30:
            terse += 1

    return {
        "imperative_pct": round(100 * imperative / n, 1),
        "questioning_pct": round(100 * questioning / n, 1),
        "contextual_pct": round(100 * contextual / n, 1),
        "terse_pct": round(100 * terse / n, 1),
    }


def sample_messages(messages, sample_size):
    """Sample representative messages across the full history."""
    suitable = [m for m in messages if 20 < len(m["text"]) < 500]
    if not suitable:
        return []

    if len(suitable) <= sample_size:
        return [m["text"] for m in suitable]

    step = len(suitable) // sample_size
    return [suitable[i]["text"] for i in range(0, len(suitable), step)][:sample_size]


def analyze_activity_timeline(messages):
    """Analyze when the user is active."""
    if not any(m.get("timestamp") for m in messages):
        return {"note": "No timestamps found in history"}

    hours = Counter()
    weekdays = Counter()
    day_names = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    for msg in messages:
        ts = msg.get("timestamp")
        if not ts:
            continue
        try:
            if ts > 1e12:
                ts = ts / 1000
            dt = datetime.fromtimestamp(ts)
            hours[dt.hour] += 1
            weekdays[day_names[dt.weekday()]] += 1
        except (ValueError, OSError):
            continue

    peak_hours = sorted(hours.items(), key=lambda x: -x[1])[:5]
    return {
        "peak_hours": {str(h): c for h, c in peak_hours},
        "weekday_distribution": {d: weekdays.get(d, 0) for d in day_names},
    }


def main():
    args = parse_args()
    history_path = Path(args.history_file)

    if not history_path.exists():
        print(f"Error: History file not found at {history_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Reading {history_path}...")
    entries = load_history(history_path)
    print(f"  Found {len(entries)} history entries")

    messages = extract_messages(entries)
    print(f"  Extracted {len(messages)} user messages")

    print("Analyzing...")
    stats = {
        "source": str(history_path),
        "total_entries": len(entries),
        "total_messages": len(messages),
        "project_frequency": analyze_project_frequency(messages),
        "message_lengths": analyze_message_lengths(messages),
        "emotional_markers": analyze_emotional_markers(messages),
        "typo_patterns": analyze_typo_density(messages),
        "delegation_style": analyze_delegation_style(messages),
        "activity_timeline": analyze_activity_timeline(messages),
    }

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    stats_path = output_dir / "stats.json"
    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2)
    print(f"  Wrote {stats_path}")

    samples = sample_messages(messages, args.sample_size)
    samples_path = output_dir / "samples.txt"
    with open(samples_path, "w") as f:
        for s in samples:
            f.write(s + "\n---\n")
    print(f"  Wrote {samples_path} ({len(samples)} samples)")

    # Print summary
    print("\n=== Quick Summary ===")
    print(f"Messages: {len(messages)}")
    print(f"Projects: {len(stats['project_frequency'])}")
    ml = stats["message_lengths"]
    if ml:
        print(f"Message length: median {ml['median']} chars, "
              f"{ml['under_50_chars_pct']}% under 50 chars, "
              f"{ml['over_200_chars_pct']}% over 200 chars")
    ds = stats["delegation_style"]
    if ds:
        print(f"Style: {ds['imperative_pct']}% imperative, "
              f"{ds['questioning_pct']}% questioning, "
              f"{ds['terse_pct']}% terse (<30 chars)")
    print(f"\nTop 5 projects:")
    for proj, count in list(stats["project_frequency"].items())[:5]:
        print(f"  {count:5d}  {proj}")


if __name__ == "__main__":
    main()
