#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Collect Toolsmith agent-log scans locally and over SSH, then write a Markdown report."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import re
import subprocess
import sys
from typing import Any


def run(cmd: list[str], timeout: int = 180) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, check=False)


def strip_noise(text: str) -> str:
    text = text.replace("\x1bc", "")
    text = re.sub(r"stty: stdin isn't a terminal\s*", "", text)
    return text.strip()


def parse_json_output(text: str) -> dict[str, Any]:
    text = strip_noise(text)
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
      raise ValueError("no JSON object found in command output")
    return json.loads(text[start:end + 1])


def collect(host: str | None, days: float, max_examples: int) -> tuple[str, dict[str, Any] | None, str | None]:
    if host:
        cmd = ["ssh", host, "toolsmith", "scan-agent-logs", "--json", "--days", str(days), "--max-examples", str(max_examples)]
        label = host
    else:
        cmd = ["toolsmith", "scan-agent-logs", "--json", "--days", str(days), "--max-examples", str(max_examples)]
        label = "local"
    proc = run(cmd)
    combined = f"{proc.stdout}\n{proc.stderr}"
    if proc.returncode != 0:
        return label, None, strip_noise(combined)
    try:
        return label, parse_json_output(combined), None
    except Exception as exc:  # noqa: BLE001 - report parser failures usefully
        return label, None, f"{exc}: {strip_noise(combined)[:1000]}"


def counts(entries: list[dict[str, Any]], limit: int = 8) -> str:
    if not entries:
        return "none"
    visible = entries[:limit]
    suffix = f", +{len(entries) - limit} more" if len(entries) > limit else ""
    return ", ".join(f"{item.get('key')}={item.get('count')}" for item in visible) + suffix


def section(label: str, scan: dict[str, Any] | None, error: str | None) -> str:
    if error or scan is None:
        return f"## {label}\n\nERROR: {error or 'scan failed'}\n"
    lost = scan.get("lostOpportunities", {})
    toolsmith = scan.get("toolsmith", {})
    sessions = scan.get("sessions", {})
    lines = [
        f"## {label}",
        "",
        f"Host: {scan.get('host', label)}",
        f"Sessions: Claude {sessions.get('claude', 0)}, Codex {sessions.get('codex', 0)}",
        f"Toolsmith calls: {toolsmith.get('toolCalls', 0)} across {toolsmith.get('sessions', 0)} session(s)",
        f"Toolsmith tools: {counts(toolsmith.get('byTool', []))}",
        f"Hard lost opportunities: {lost.get('total', 0)}",
        f"Apply-patch candidates: {lost.get('editCandidates', 0)}",
        f"By kind: {counts(lost.get('byKind', []), 12)}",
        f"Themes: {counts(scan.get('interactionSignals', {}).get('themes', []), 10)}",
        f"Frustration/surety: {counts(scan.get('interactionSignals', {}).get('frustrationSignals', []), 10)}",
        "",
    ]
    examples = lost.get("examples") or []
    if examples:
        lines.extend(["### Examples", ""])
        for ex in examples[:6]:
            lines.append(f"- {ex.get('agent')} {ex.get('kind')}: `{ex.get('file', 'unknown')}` -> {ex.get('use')}")
        lines.append("")
    return "\n".join(lines)


def total(scan: dict[str, Any] | None, path: tuple[str, ...], default: int = 0) -> int:
    value: Any = scan
    for key in path:
        if not isinstance(value, dict):
            return default
        value = value.get(key)
    return value if isinstance(value, int) else default


def third_order(results: list[tuple[str, dict[str, Any] | None, str | None]]) -> str:
    lines = [
        "## Third-order synthesis",
        "",
        "Use this section to avoid stopping at the obvious fix.",
        "",
    ]
    for label, scan, error in results:
        if error or scan is None:
            continue
        calls = total(scan, ("toolsmith", "toolCalls"))
        lost = total(scan, ("lostOpportunities", "total"))
        candidates = total(scan, ("lostOpportunities", "editCandidates"))
        sessions = total(scan, ("sessions", "claude")) + total(scan, ("sessions", "codex"))
        ratio = lost / max(calls, 1)
        lines.append(f"### {label}")
        lines.append("")
        lines.append(f"- First-order: {lost} hard misses, {candidates} patch candidates, {calls} Toolsmith calls across {sessions} session(s).")
        if calls == 0 and sessions:
            lines.append("- Second-order: registration or instructions may exist, but the workflow is not becoming salient during real work.")
            lines.append("- Third-order path: add an activation nudge or wrapper that appears at the moment of large-file friction, not another static reminder.")
        elif ratio > 3:
            lines.append("- Second-order: agents sometimes know the better tool, but native habits still win under speed pressure.")
            lines.append("- Third-order path: convert repeated misses into named skills/scripts that make the better route shorter than the old route.")
        else:
            lines.append("- Second-order: adoption is visible; now optimize for precision, usefulness, and fewer false-positive nudges.")
            lines.append("- Third-order path: use silence/anomaly detection so absence of lost opportunities is verified, not assumed.")
        lines.append("")
    lines.extend([
        "Candidate new mental paths:",
        "",
        "- **Shadow workflow collector**: capture where the human bridges a gap after agent looping.",
        "- **Silence detector**: flag missing telemetry before calling a workflow healthy.",
        "- **Exit-door drill**: every release-like workflow proves rollback before celebration.",
        "- **Jank weather report**: summarize temporal UI friction, not just screenshots.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days", type=float, default=7)
    parser.add_argument("--max-examples", type=int, default=12)
    parser.add_argument("--remote", action="append", default=[])
    parser.add_argument("--project", default="toolsmith")
    parser.add_argument("--notes-dir", default=None)
    parser.add_argument("--obsidian-dir", default=None)
    args = parser.parse_args()

    home = pathlib.Path.home()
    notes_dir = pathlib.Path(args.notes_dir or home / "dev" / "agent-notes" / args.project / "agent-log-forensics")
    notes_dir.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y-%m-%d-%H%M")

    results = [collect(None, args.days, args.max_examples)]
    for remote in args.remote:
        results.append(collect(remote, args.days, args.max_examples))

    report = [
        f"# Agent log forensics — {stamp}",
        "",
        f"Window: {args.days} day(s)",
        f"Hosts: {', '.join(label for label, _, _ in results)}",
        "",
    ]
    for label, scan, error in results:
        report.append(section(label, scan, error))

    report.append(third_order(results))
    report.append("## Follow-up\n\n- Re-run after more heavy development.\n- Convert repeated hard misses into skills, scripts, or Toolsmith adoption snippets.\n")
    text = "\n".join(report)
    out = notes_dir / f"agent-log-forensics-{stamp}.md"
    out.write_text(text, encoding="utf-8")
    print(out)

    if args.obsidian_dir:
        obsidian = pathlib.Path(args.obsidian_dir)
        obsidian.mkdir(parents=True, exist_ok=True)
        obsidian_out = obsidian / out.name
        obsidian_out.write_text(text, encoding="utf-8")
        print(obsidian_out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
