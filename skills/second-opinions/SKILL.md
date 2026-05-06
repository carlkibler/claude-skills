---
name: second-opinions
description: Get validation from a different AI model before committing major changes — detects available LLM CLIs and routes to the best one.
display_name: "Second Opinions"
brand_color: "#4F46E5"
local_only: false
group: "Dev Workflow"
usage: "/second-opinions:run"
summary: "Get a second opinion from a different AI on complex changes"
default_prompt: "Get a second opinion on this implementation or design decision and summarize the strongest agreement, disagreement, and actionable feedback."
---

# Second Opinions

Get validation from a different AI before committing. Any single model — regardless of which one is running — has blind spots shaped by its training, context, and the conversation so far. A different architecture, temperature, or framing catches different things.

## When to Use

**Mandatory:**
- Complex multi-file changes before merge
- Design decisions with multiple valid approaches
- After 2+ hours on a single approach (tunnel vision risk)
- Security-sensitive or performance-critical code

**Skip for:** trivial fixes, style questions, crystal-clear requirements

## Agent Detection

Use the bundled detection script, with an inline fallback if `SKILL_DIR` isn't set:

```bash
bash "${SKILL_DIR}/scripts/detect-llms.sh" --quiet 2>/dev/null || \
  for t in agent ask-gemini codex llm; do command -v "$t" >/dev/null 2>&1 && echo "$t"; done
```

Use the first one found. If none are available, tell the user and skip this step.

## Model Selection

Second opinions are about **deep analysis**, not speed. Use the smartest model available:

| Tool | For deep analysis | For quick checks |
|---|---|---|
| `agent` | `agent --frontier` (claude-opus-4-5) | `agent --smart` (gemini-2.5-pro) |
| `ask-gemini` | `ask-gemini --pro` (Gemini Pro) | `ask-gemini` (Gemini Flash) |

When this skill is invoked for **pre-merge review, design validation, or architecture decisions**, prefer `agent --frontier` (or `ask-gemini --pro` if agent unavailable). For quick sanity checks or brainstorming, `agent --smart` is fine.

## How to Ask

The prompt is the same regardless of agent — adapt the invocation to whatever's available. The `detect-llms.sh` script outputs `NAME|INVOKE_PATTERN|MODEL_FAMILY|NOTES` — use the `INVOKE_PATTERN` field, substituting `{prompt}` with your actual prompt.

### Pre-Merge Review (Most Common)

Show the diff and ask for a production-readiness check:

```
Review my git changes for production readiness.

Show the diff from main and check for:
- Correctness and edge cases
- Architecture and design
- Performance implications
- Security concerns
```

### Design Decision Validation

Describe the options and constraints, then ask: *What trade-offs am I not seeing?*

### Targeted Question

Ask one specific question about the implementation — don't fish for general feedback.

## Interpreting Results

The other agent is a **collaborator, not an authority.** Classify each piece of feedback:

| Category | Action |
|----------|--------|
| **Must-fix** | Bug, security issue, correctness problem → implement immediately |
| **Should-fix** | Genuine simplification, better error handling → implement if clean |
| **Nice-to-have** | Alternative approach, style preference → mention to user |
| **Reject** | Over-engineering, conflicts with project conventions → skip with reason |

If the other agent and your analysis disagree, explain the disagreement to the user and let them decide.

## The Red Flags

These thoughts mean STOP and get a second opinion:
- "It works in my tests" — tests only prove known scenarios
- "I've spent 3 hours on this" — sunk cost isn't validation
- "I'm confident this is right" — confidence correlates with blind spots
- "It's obviously the best approach" — obvious to you ≠ optimal

**5 minutes of external validation prevents hours of debugging.**
