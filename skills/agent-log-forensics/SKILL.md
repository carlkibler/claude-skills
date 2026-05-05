---
name: agent-log-forensics
description: Scan Claude/Codex session logs to find agent behavior patterns, Toolsmith adoption gaps, repeated frustrations, and candidates for new skills/tools.
display_name: "Agent Log Forensics"
brand_color: "#6D28D9"
local_only: true
group: "Dev Workflow"
usage: "/agent-log-forensics:run"
summary: "Turn local and remote agent session logs into workflow improvements"
default_prompt: "Scan recent Claude and Codex session logs on this machine and any named remote hosts. Report Toolsmith adoption, lost opportunities, recurring frustrations, and concrete new skills/scripts to add. Keep examples privacy-light."
---

# Agent Log Forensics

Use this when the goal is not one bug fix, but making the human+agent system smarter after observing real sessions.

Third-order stance: skip the obvious "agent forgot tool" answer. Ask what hidden loop, missing affordance, brittle instruction, or human workaround made the tool forgettable in the first place. Prefer new mental paths over more reminders.

## When to Use

- The user asks whether agents are using a tool, skill, MCP server, or workflow
- The user wants "lost opportunities" where agents should have used better tools
- The user asks for patterns in interactions, repeated frustrations, jank, or productivity bottlenecks
- The user asks "why did that take so many turns?", "why did you struggle?", or "how do we level this up?"
- You need to turn observed behavior into new user-level skills, scripts, or project instructions

## When NOT to Use

- One isolated transcript or pasted error is enough
- The user asks for a narrow code change unrelated to agent behavior
- Logs may contain sensitive data and the user did not ask for forensic analysis

---

<process>

## Phase 1: Scope the Observation Window

Default to the last 7 days unless the user names a different range. Include remote hosts explicitly named by the user, commonly `vesta`.

Prefer Toolsmith's built-in scanner when available:

```bash
toolsmith scan-agent-logs --days 7 --max-examples 12
toolsmith opportunities --days 7 --max-examples 8
toolsmith scan-agent-logs --days 7 --remote vesta --max-examples 12
```

If the scanner is not installed yet, say that and fall back to a lightweight count of recent `~/.claude/projects/**/*.jsonl` and `~/.codex/sessions/**/*.jsonl` files rather than dumping raw prompts.

## Phase 2: Preserve Privacy

- Do not paste raw user prompts or full transcript content.
- Redact home paths, secrets, tokens, keys, cookies, project-private filenames when they look sensitive.
- Prefer counts, categories, tool names, workspace basenames, and short sanitized examples.
- Treat shell commands with secrets as sensitive snippets.

## Phase 3: Classify Findings

Create five sections:

1. **Tool adoption** — registered vs actually called, by agent/client, with evidence counts.
2. **Lost opportunities** — where the agent used a worse tool. Separate hard misses from candidates.
3. **Behavior/productivity themes** — repeated user frustrations, recurring workflow patterns, and quality gaps.
4. **Shadow workflows** — places the human manually intervened, re-ran commands, pasted exact instructions, or corrected the agent after loops. Treat these as highest-value skill/script candidates.
5. **Silence anomalies** — expected logs, tool calls, or telemetry are missing. Lack of evidence can mean broken instrumentation, not success.

For Toolsmith, classify:

- Hard miss: native `Read`/`Edit`/`Write`, `cat`, `nl`, or broad `sed -n` on >200-line files.
- Candidate: `apply_patch` on a large file after a search/read could have used anchors, but may still be acceptable.
- Positive adoption: `file_skeleton`, `find_and_anchor`, `get_function`, `anchored_read`, `anchored_edit`, `symbol_replace`.

## Phase 4: Convert Observations Into Improvements

For each repeated pattern, propose one of:

- **Skill** — when judgment, sequencing, or cross-tool behavior matters.
- **Script** — when the action is deterministic and repeatable.
- **Project instruction** — when it is repo-specific and should activate automatically.
- **Tool/MCP improvement** — when missing affordances prevent agents from doing the right thing.

Use this table:

| Signal | Better artifact |
|---|---|
| Same review checklist repeated | Skill |
| Same shell command chain repeated | Script |
| Same repo-specific gotcha repeated | CLAUDE.md / AGENTS.md update |
| Agents know the right thing but forget | Prompt snippet / guardrail |
| Agents cannot inspect evidence cheaply | Toolsmith/MCP feature |
| User manually intervenes after agent loops | Skill or deterministic helper that removes the human bridge |
| Expected telemetry is silent | Logging/instrumentation fix before drawing conclusions |
| Same failure appears across projects | User-level skill plus project opt-out, not per-repo copy-paste |

## Phase 5: Third-order Synthesis

After listing findings, do one further pass:

- First-order: what tool or skill should have been used?
- Second-order: why did the agent not choose it under real pressure?
- Third-order: what new path would make the better behavior feel inevitable, delightful, or weirdly obvious next time?

Name the proposed path in memorable language, for example "shadow workflow collector", "silence detector", "release exit-door drill", or "jank weather report".

## Phase 6: Write the Report

Store reports in:

- Temporary artifacts: `~/dev/agent-notes/<project>/`
- Durable reports: Obsidian project folder if the user asks or the work should guide future sessions

Include:

- Date range and hosts
- What was scanned
- Adoption verdict
- Lost-opportunity examples, sanitized
- Skills/scripts/tools to add next
- Third-order ideas worth trying even if they sound whimsical
- Follow-up observation plan

</process>

<scripts>

Use `scripts/collect_toolsmith_scan.py` to run local and remote Toolsmith scans and write a combined Markdown report.

</scripts>

<interlocks>

- Use `remote-host-verifier` when comparing a command across local and remote hosts.
- Use `skill-creator` when turning findings into new skills.
- Use `status-copy-trust-audit` when confusing CLI output appears repeatedly in logs.
- Use `beads-knowledge` or the project tracker to preserve hard-won patterns that should not be rediscovered.
- Use `quick-check --cheap` for broad synthesis and a different model's view before writing new skills.

</interlocks>
