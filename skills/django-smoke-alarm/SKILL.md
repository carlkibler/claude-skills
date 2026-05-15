---
name: django-smoke-alarm
description: Run and triage Django/DRF security smoke checks for settings hardening, throttling, safe HTML, ORM race/idempotency patterns, and model integrity; especially useful before shipping or when evaluating djangoSecurityHunter-style findings.
display_name: "Django Smoke Alarm"
brand_color: "#DC2626"
local_only: true
group: "Dev Workflow"
usage: "/django-smoke-alarm:run"
summary: "Triage Django security smoke checks into real risks, hygiene, and false positives"
default_prompt: "Run a Django smoke-alarm pass on this project. Use a clean scan, exclude worktrees/vendor/generated folders, and classify findings as REAL, HYGIENE, or FALSE POSITIVE with file-line evidence."
---

# Django Smoke Alarm

Use this when a Django or DRF project needs a fast security/reliability sweep, especially after a tool such as `djangoSecurityHunter`, Bandit, Semgrep, or a custom grep pass reports many findings.

Third-order stance: the goal is not “make the scanner green.” The goal is to find the few boring Django foot-guns that become production incidents, while teaching the project a repeatable preflight. Smoke alarms should be loud, cheap, and easy to silence only with evidence.

## When to Use

- The project is Django/DRF and you need obvious security or reliability issues.
- A scanner reports many findings and you need a grounded triage.
- Before launch, deploy, CI hardening, or exposing new auth/API/upload/HTML surfaces.
- When adding or reviewing settings, DRF auth, OAuth/API keys, XML/Markdown/HTML rendering, import jobs, or admin previews.

## Core Rule

Always classify scanner output before fixing:

- **REAL** — plausible exploit/data-loss/abuse path or broken production posture.
- **HYGIENE** — low-risk but worth making safer/clearer, often to reduce future mistakes.
- **FALSE POSITIVE** — scanner pattern is misleading; document why with code evidence.

Do not create a giant undifferentiated fix list. The dragon is usually three lizards in a trench coat.

---

<process>

## Phase 1: Prepare a Clean Scan

Never judge raw scanner counts from a working repo if it contains worktrees or generated/vendor folders.

Exclude at minimum:

```text
.git .hg .svn .venv venv node_modules dist build .tox .eggs
.mypy_cache .pytest_cache htmlcov coverage
.worktrees .claude/worktrees
.env .env.*
```

If using `djangoSecurityHunter`, prefer a clean temp copy and scan-only env values:

```bash
python3 skills/django-smoke-alarm/scripts/django_smoke_alarm.py \
  --project . \
  --settings myproject.settings \
  --project-python .venv/bin/python \
  --scanner-source /tmp/djangoSecurityHunter/src \
  --env SECRET_KEY=dummy-scan-only-not-production-40-plus-chars \
  --env DEBUG=False \
  --env ALLOWED_HOSTS=localhost,127.0.0.1 \
  --env DATABASE_URL=sqlite:////tmp/django-smoke.sqlite3
```

If the scanner cannot import settings, keep static findings but explicitly say which settings-backed checks were skipped.

## Phase 2: Read the Rule Buckets, Not Just Counts

Group findings by risk surface:

1. **Production settings** — `DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS`, HTTPS redirect, HSTS, secure cookies, CSRF trusted origins, CORS.
2. **DRF/API abuse** — default authentication, permissions, throttles, pagination, auth-like routes, upload limits.
3. **Unsafe HTML** — `mark_safe`, `|safe`, XML/Markdown renderers, admin previews, template tags, rich text blocks.
4. **Persistence races** — `exists/get + create`, multi-save workflows, `save()` in loops, arithmetic updates without `F()`, missing uniqueness/idempotency.
5. **Model integrity** — natural-key slugs, nullable unique-ish fields, risky cascade deletes, missing constraints.
6. **Secrets/logging** — token-looking defaults, exception logs near OAuth/API keys, local `.env*` accidentally tracked.
7. **Dependencies and external scanners** — pip-audit, Bandit, Semgrep, only after the clean project scan is understood.

## Phase 3: Sample Before Fixing

For each noisy rule, inspect representative code before deciding.

### Unsafe HTML triage

Classify as **REAL** if untrusted or external content is inserted into safe HTML without escaping:

- XML or Markdown source from outside the team
- user profile/team/org/bill/client fields
- uploaded file metadata
- admin preview fields backed by user content

Classify as **HYGIENE** if the string is constant or all interpolated variables are escaped, but the code would be safer with `format_html()` / `format_html_join()`.

Classify as **FALSE POSITIVE** only when the full data path is safe and future edits are unlikely to reintroduce unsafe interpolation.

### Transaction/race triage

Do not blindly wrap long-running workflows in `transaction.atomic()`. Multi-save progress markers around external API calls, Celery jobs, or imports may be intentional.

Prefer:

- DB uniqueness constraints for idempotency.
- `get_or_create()` / `update_or_create()` where appropriate.
- `select_for_update()` for concurrent mutation of existing rows.
- `F()` expressions for arithmetic updates.
- Small atomic sections around related DB writes, not around network calls or long LLM/image work.

## Phase 4: Produce a Triage Table

Report a compact table:

| Finding | Classification | Evidence | Recommended move |
|---|---|---|---|
| Missing HSTS | REAL | `settings.py` has no `SECURE_HSTS_SECONDS` under `DEBUG=False` | Add production security block or env-controlled settings |
| Admin `mark_safe` preview | HYGIENE | URL is escaped, constant HTML otherwise | Convert to `format_html` |
| AI pipeline multiple saves | FALSE POSITIVE/HYGIENE | Saves status before/after long external calls | Do not wrap whole function; maybe add comment/tests |

Then list only the **top 3-7 REAL fixes**. Put hygiene work behind those.

## Phase 5: Turn Findings into Project Policy

If the same issue could recur, add a project-local guardrail:

- `settings.py` production security block and test.
- DRF throttle defaults and per-route throttles for auth/OAuth/API-key endpoints.
- HTML renderer helper that escapes text by default and marks only known tags safe.
- Code-review note: “no `mark_safe` with interpolation; use `format_html`.”
- Import/idempotency tests with duplicate input and repeated runs.
- CI smoke-alarm job that runs on a clean copy and stores JSON/SARIF artifacts.

</process>

<tooling>

`scripts/django_smoke_alarm.py` creates a clean temp copy, runs `djangoSecurityHunter` if available, writes JSON, and prints a grouped summary. It is intentionally a wrapper, not the source of truth: the agent still must read code and classify findings.

Useful flags:

- `--project` — Django repo root.
- `--settings` — Django settings module.
- `--project-python` — project venv Python, recommended for settings import.
- `--scanner-source` — local `djangoSecurityHunter/src` checkout to add to `PYTHONPATH`.
- `--env KEY=VALUE` — scan-only env overrides.
- `--output-dir` — report destination.

</tooling>

<interlocks>

- Use `trust-audit` for user-facing permission, privacy, billing, and unsafe-feeling AI/data flows found during the scan.
- Use `kindness-check` after fixes to catch developer/support burden from noisy scanner-driven changes.
- Use `release-operator` if this creates a CI/release gate.
- Use `decision-log` if choosing to accept a scanner false positive or defer a real risk.

</interlocks>
