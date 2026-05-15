#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run a clean Django smoke-alarm scan with djangoSecurityHunter when available."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

EXCLUDE_NAMES = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    ".tox",
    ".eggs",
    ".mypy_cache",
    ".pytest_cache",
    "htmlcov",
    "coverage",
    ".worktrees",
    "worktrees",
    "__pycache__",
}

EXCLUDE_PREFIXES = (".env",)


def ignore_names(_dir: str, names: list[str]) -> set[str]:
    ignored = set()
    for name in names:
        if name in EXCLUDE_NAMES or any(name == p or name.startswith(p + ".") for p in EXCLUDE_PREFIXES):
            ignored.add(name)
    return ignored


def parse_env(values: list[str]) -> dict[str, str]:
    env: dict[str, str] = {}
    for item in values:
        if "=" not in item:
            raise SystemExit(f"--env must be KEY=VALUE, got: {item}")
        key, value = item.split("=", 1)
        if not key:
            raise SystemExit(f"--env key cannot be empty: {item}")
        env[key] = value
    return env


def resolve_project_path(project: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    project_relative = project / path
    if project_relative.exists():
        return project_relative.absolute()
    return path.absolute()


def scanner_command(args: argparse.Namespace, project: Path) -> list[str]:
    if args.project_python:
        return [str(resolve_project_path(project, args.project_python)), "-m", "django_security_hunter.cli"]
    return [args.scanner]


def summarize(report_path: Path) -> None:
    data = json.loads(report_path.read_text())
    findings = data.get("findings", [])
    metadata = data.get("metadata", {})
    print(f"settings_loaded={metadata.get('django_settings_loaded')} skip={metadata.get('django_settings_skip_reason')}")
    print(f"findings={len(findings)}")
    print("severity=", dict(Counter(f.get("severity") for f in findings)))
    print("rules=", Counter(f.get("rule_id") for f in findings).most_common(20))
    print("top_paths=")
    for path, count in Counter(f.get("path") or "<settings>" for f in findings).most_common(12):
        print(f"  {count:>3} {path}")
    print("sample=")
    for finding in findings[:20]:
        msg = " ".join(str(finding.get("message", "")).split())[:180]
        print(
            f"  {finding.get('severity')} {finding.get('rule_id')} "
            f"{finding.get('path')}:{finding.get('line')} {finding.get('title')} -- {msg}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default=".", help="Django project root")
    parser.add_argument("--settings", help="Django settings module")
    parser.add_argument("--project-python", help="Project venv Python to run the scanner module")
    parser.add_argument("--scanner", default="django_security_hunter", help="Scanner command when --project-python is omitted")
    parser.add_argument("--scanner-source", help="Local djangoSecurityHunter/src path to prepend to PYTHONPATH")
    parser.add_argument("--output-dir", default="./reports/django-smoke-alarm", help="Directory for JSON report")
    parser.add_argument("--env", action="append", default=[], help="Scan-only KEY=VALUE environment override")
    parser.add_argument("--threshold", default="WARN", help="Scanner severity threshold")
    parser.add_argument("--keep-copy", action="store_true", help="Do not delete the clean temp copy")
    args = parser.parse_args()

    project = Path(args.project).resolve()
    if not project.exists():
        raise SystemExit(f"Project not found: {project}")

    out_dir = Path(args.output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / f"{project.name}-django-smoke-alarm.json"

    temp_parent = Path(tempfile.mkdtemp(prefix="django-smoke-alarm-"))
    clean_project = temp_parent / project.name
    print(f"clean_copy={clean_project}")
    shutil.copytree(project, clean_project, ignore=ignore_names, symlinks=False)

    env = os.environ.copy()
    env.update(parse_env(args.env))
    py_path_parts = [str(clean_project)]
    if args.scanner_source:
        py_path_parts.insert(0, str(resolve_project_path(project, args.scanner_source)))
    if env.get("PYTHONPATH"):
        py_path_parts.append(env["PYTHONPATH"])
    env["PYTHONPATH"] = os.pathsep.join(py_path_parts)

    cmd = scanner_command(args, project) + [
        "scan",
        "--project",
        str(clean_project),
        "--format",
        "json",
        "--output",
        str(report_path),
        "--threshold",
        args.threshold,
    ]
    if args.settings:
        cmd += ["--settings", args.settings, "--allow-project-code"]

    print("command=", " ".join(cmd))
    proc = subprocess.run(cmd, cwd=clean_project, env=env, text=True)
    print(f"scanner_exit={proc.returncode}")

    if report_path.exists():
        summarize(report_path)
        print(f"report={report_path}")
    else:
        print("report=missing", file=sys.stderr)

    if args.keep_copy:
        print(f"kept_copy={clean_project}")
    else:
        shutil.rmtree(temp_parent, ignore_errors=True)

    return 0 if proc.returncode in {0, 2} else proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
