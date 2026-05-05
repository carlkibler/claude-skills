#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Run a command locally and on SSH hosts, then compare exit status and output."""

from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
from dataclasses import asdict, dataclass


@dataclass
class Result:
    label: str
    command: str
    returncode: int
    stdout: str
    stderr: str
    probe: dict[str, str] | None = None


def strip_noise(text: str) -> str:
    text = text.replace("\x1bc", "")
    text = re.sub(r"stty: stdin isn't a terminal\s*", "", text)
    return text.strip()


def run(label: str, cmd: list[str], timeout: int) -> Result:
    proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, check=False)
    return Result(label=label, command=" ".join(shlex.quote(part) for part in cmd), returncode=proc.returncode, stdout=strip_noise(proc.stdout), stderr=strip_noise(proc.stderr))


def probe_command() -> str:
    return "printf 'host=%s\\n' \"$(hostname)\"; printf 'date=%s\\n' \"$(date -u '+%Y-%m-%dT%H:%M:%SZ')\"; printf 'shell=%s\\n' \"$SHELL\"; printf 'path=%s\\n' \"$PATH\"; printf 'cwd=%s\\n' \"$PWD\"; printf 'uptime=%s\\n' \"$(uptime 2>/dev/null || true)\"; printf 'disk=%s\\n' \"$(df -h . 2>/dev/null | tail -1 || true)\""


def parse_probe(text: str) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in strip_noise(text).splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            data[key] = value
    return data


def collect_probe(label: str, host: str | None, timeout: int) -> dict[str, str]:
    cmd = ["bash", "-lc", probe_command()] if host is None else ["ssh", host, "bash", "-lc", probe_command()]
    proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, check=False)
    data = parse_probe(proc.stdout)
    if proc.returncode != 0 and proc.stderr:
        data["probe_stderr"] = strip_noise(proc.stderr)
    data.setdefault("label", label)
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", action="append", default=[], help="SSH host to compare. Repeatable.")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--probe-env", action="store_true", help="Include host/date/shell/PATH/cwd/disk/uptime probes for drift analysis.")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command after --")
    args = parser.parse_args()

    command = args.command
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        parser.error("provide a command after --")

    results = [run("local", command, args.timeout)]
    if args.probe_env:
        results[0].probe = collect_probe("local", None, args.timeout)
    quoted = " ".join(shlex.quote(part) for part in command)
    for host in args.host:
        result = run(host, ["ssh", host, "bash", "-lc", quoted], args.timeout)
        if args.probe_env:
            result.probe = collect_probe(host, host, args.timeout)
        results.append(result)

    ok = all(result.returncode == 0 for result in results)
    if args.json:
        print(json.dumps({"ok": ok, "results": [asdict(result) for result in results]}, indent=2))
    else:
        for result in results:
            print(f"## {result.label} — exit {result.returncode}")
            print(f"$ {result.command}")
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print("stderr:")
                print(result.stderr)
            if result.probe:
                print("probe:")
                for key, value in result.probe.items():
                    print(f"  {key}: {value}")
            print()
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
