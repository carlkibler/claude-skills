---
name: ralph-loop
description: "Run repeatable multi-LLM codebase hardening sweeps: map under-reviewed surfaces, get tough reviewers, patch fixes, document learnings, and loop."
display_name: "RALPH Loop"
brand_color: "#C2410C"
local_only: false
group: "Dev Workflow"
usage: "/ralph-loop:run"
summary: "Repeatable multi-LLM hardening sweeps for codebases"
default_prompt: "Run a RALPH loop over this repo: map the next under-reviewed surfaces, get multi-LLM review, apply high-confidence fixes, document findings, and tell me the next sweep frontier."
---

# RALPH Loop

RALPH packages the recurring multi-LLM hardening sweep:

**R**econ the codebase → **A**ssemble a review packet → **L**aunch diverse reviewers → **P**atch proven findings → **H**andoff learnings.

Use it when the user asks for another sweep, a tough multi-LLM review, recurring codebase hardening, or “keep looking for untouched areas.” It extends `second-opinions`: that skill validates one change or decision; RALPH repeatedly searches the repo for the next highest-leverage surface and turns reviewer output into fixes, docs, and follow-up work.

## Operating stance

Be tough but fair. External models are collaborators, not judges. Prefer fixes that are:

- correctness, security, data loss, auth, or observability issues;
- small and locally testable;
- aligned with project conventions;
- safe for users and support teams.

Reject reviewer suggestions that are stale, hallucinated, over-engineered, already fixed, or require product decisions.

## Loop shape

### 1. Recon — choose the next frontier

Start from repo evidence, not vibes.

1. Read project instructions.
2. Check git status and issue tracker.
3. Inspect recent commits/docs/review artifacts to avoid repeating the same modules.
4. Build a frontier map of code not yet swept or newly changed.

Good frontier slices:

- user-facing views/forms/API/auth;
- background tasks/schedulers/importers;
- integrations/OAuth/webhooks/external APIs;
- billing/security/permissions;
- data sync/migrations/admin commands;
- LLM/tool-calling surfaces;
- observability and Sentry/error-handling seams;
- tests that imply important behavior but lack coverage.

If the repo has prior review docs, append “already swept” and “next frontier” notes to avoid orbiting the same planet until the flamingo gets dizzy.

### 2. Assemble — create a bounded review packet

Prefer the bundled prompt builder:

```bash
uv run "${SKILL_DIR:-${CLAUDE_SKILL_DIR}}/scripts/build_ralph_prompt.py" --focus "views, API, auth" --out-dir "$HOME/dev/agent-notes/$(basename "$PWD")"
```

If the environment lacks `SKILL_DIR`, locate the script in the skill directory or build the packet manually.

The packet should include:

- repo/product context in 5–10 lines;
- previous sweep summary or paths to review docs;
- selected file/function/error map;
- bounded excerpts, not whole giant files;
- explicit review criteria:
  - Must-fix / Should-fix / Nice-to-have / Reject;
  - correctness, refactoring, performance, security, Sentry/context;
  - user-safe errors and no secrets/PII in logs or events;
  - “small actionable fixes only.”

Keep prompts under shell argument limits. If using a CLI wrapper that passes prompt as argv, aim for <50k chars.

### 3. Launch — fan out reviewers

Use at least three diverse reviewers when available. Prefer:

- `agent --model x-ai/grok-4.3` for bluntness/edge cases;
- `agent --model '~google/gemini-pro-latest'` for systems/code reasoning;
- `agent --model deepseek/deepseek-v4-pro` for bug-hunting/value;
- or fallback to `ask-gemini`, `llm`, `codex`, `ask-copilot`, etc.

Run reviewers in parallel when tools allow. Store raw outputs under `~/dev/agent-notes/<repo>/` with model and date in the filename.

Prompt reviewers to include file/function, reason, suggested fix, severity, and a Reject/Do-not-do section.

### 4. Synthesize — classify with skepticism

Create a synthesis table:

| Reviewer item | Classification | Decision |
|---|---|---|
| Bug/security/auth/data loss | Must-fix | Patch now |
| Clear simplification/error context | Should-fix | Patch if small |
| Product/refactor idea | Follow-up | File issue |
| Hallucinated/stale/overbroad | Reject | Note why |

Important checks:

- Verify every alleged bug against actual source.
- Reproduce or reason through failures before patching.
- Watch for “reviewer line numbers” that are approximate or stale.
- If a reviewer says “syntax error,” run compile/tests before believing it.
- For Sentry fixes, capture enough context to debug but avoid raw emails, phone numbers, OAuth states, webhook URLs, passwords, tokens, service-account paths, or provider payloads.

### 5. Patch — apply only high-confidence work

Use normal project workflow and issue tracking. Patch in small commits if possible.

Common RALPH fix patterns:

- Replace raw user-facing `str(exc)` with generic copy + Sentry capture.
- Add scoped Sentry tags/context: feature, operation, safe ids, model/provider, status code.
- Hash/fingerprint sensitive correlators instead of logging raw values.
- Add per-item exception isolation in batch loops where one bad item should not abort all users.
- Validate query params and enum-like POST values before service calls.
- Debounce high-frequency writes from polling clients.
- Convert silent fallback into “fallback + observable event.”
- Add targeted tests for each fixed edge.

### 6. Harden docs — preserve the mental path

Create a review doc in the repo when appropriate:

`docs/reviews/YYYY-MM-DD-ralph-<frontier>-review.md`

Include:

- models used;
- scope/frontier;
- raw artifact paths;
- accepted fixes;
- deferred candidates;
- rejected findings and why;
- one “product learning” or operating rule.

Update core project instructions only for durable learnings that future agents should obey.

### 7. Validate, land, handoff

Run targeted tests plus the repo’s standard gates. Commit, push, close issue(s). Final answer should be concise:

- commit hash;
- frontier reviewed;
- models used;
- fixes applied;
- tests run;
- next sweep frontier if obvious.

## RALPH stop rule

Keep looping while each pass finds meaningful, distinct fixes. Stop or switch strategy when:

- reviewers mostly repeat prior findings;
- suggestions are architectural/product decisions, not hardening;
- the next frontier needs domain input;
- test debt or design debt is now more important than more review.

When stopping, name the next higher-leverage move: test suite expansion, architecture split, threat model, performance profile, visual QA, launch-sequence, etc.

## Relationship to other skills

- Use `second-opinions` inside RALPH for reviewer fan-out and classification discipline.
- Use `wide-open-brainstorm` only when reviewer output reveals product/UX direction rather than concrete code hardening.
- Use `trust-audit` when findings cluster around privacy, permissions, auth, or destructive actions.
- Use `kindness-check` when findings cluster around confusing UX, support burden, machine load, or developer maintainability.
