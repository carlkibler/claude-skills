# RALPH review: `bin/agent` helper

Date: 2026-05-14
Issue: `agent-skills-dzc`

## Scope / frontier

Focused review of `bin/agent`, the OpenRouter helper used by agents for multi-model second opinions. This sweep followed the flexible-input improvement that added `--file`, `@file`, stdin composition, `--dry-run`, and explicit model options.

## Reviewer artifacts

Raw artifacts are under `~/dev/agent-notes/agent-skills/`:

- `ralph-agent-helper-prompt-2026-05-14.md`
- `ralph-agent-smart-foreground-2026-05-14.md`
- `ralph-agent-flash-foreground-2026-05-14.md`
- `ralph-agent-grok-foreground-2026-05-14.md`

Some background reviewer calls produced empty files, which became its own helper-hardening signal: empty model responses should be reported as failures, not silently accepted.

## Accepted fixes

| Finding | Classification | Fix |
|---|---|---|
| Long or stuck OpenRouter calls can hang agent workflows without a visible bound. | Should-fix | Added `--timeout N` and `AGENT_TIMEOUT` support, defaulting to 180s, plus `curl --connect-timeout 10 --max-time "$REQUEST_TIMEOUT"`. |
| Invalid `--temperature`, `--timeout`, or `--max-tokens` values fail later with Python/API noise. | Should-fix | Added upfront validation and clear usage errors. |
| `--stdin` with empty redirected stdin behaved like success, despite being a require-stdin option. | Should-fix | `--stdin` now errors when stdin is empty; auto-stdin still appends only when content exists. |
| Empty provider content can create zero-byte review artifacts and look like a successful call. | Should-fix | Empty OpenRouter message content now exits non-zero with an explicit error. |

## Rejected / already covered findings

| Reviewer item | Decision |
|---|---|
| Temp files leak on exit | Rejected: `mktemp -d` already has `trap 'rm -rf "$tmpdir"' EXIT`. |
| JSON injection via prompt content | Rejected: payload is built by Python `json.dumps`, not shell interpolation. |
| API key leaked by verbose mode | Rejected: verbose only prints model and prompt stats, not curl command or headers. |
| `@file` path traversal | Rejected: this is a local developer tool whose purpose is reading requested local files. Restricting to CWD would break legitimate use. |
| Need `jq` | Rejected: script intentionally uses Python, which is already required by the environment and avoids adding jq dependency. |
| File/`@file` duplication should be disallowed | Rejected: repeated context inputs are intentional and composable. |

## Tests run

Manual shell checks:

- `bash -n bin/agent`
- `--dry-run` with repeated files and piped stdin
- `--dry-run @file grok ...`
- `--dry-run --no-stdin ... < file`
- missing file failure
- empty `--stdin` failure
- invalid `--temperature` / `--timeout` / `--max-tokens` failures
- installed wrapper check through `~/.claude/bin/agent`

Live OpenRouter smoke:

- `bin/agent flash --max-tokens 20 --timeout 30 --file /tmp/agent-ralph/one.txt 'Reply OK only if you can read file.'` → `OK`

## Operating learning

A helper used by agents should be permissive about input shapes but strict about result ambiguity. Accept many doors into the prompt; make every bad door creak loudly.

## Next frontier

Add a small automated test harness for `bin/agent --dry-run` parsing behavior so future model-map edits cannot accidentally break the flexible input contract.
