---
name: run
description: Use when completing complex implementations, making design decisions, or needing validation from a different AI perspective before committing major changes. Detects available code agents and routes to the best one found.
---

# Second Opinions

Get validation from a different AI before committing. You and the user share the same blind spots — you're the same model, trained on the same data. A different architecture catches different things.

## When to Use

**Mandatory:**
- Complex multi-file changes before merge
- Design decisions with multiple valid approaches
- After 2+ hours on a single approach (tunnel vision risk)
- Security-sensitive or performance-critical code

**Skip for:** trivial fixes, style questions, crystal-clear requirements

## Agent Detection

Use the shared detection script from the `pre-mortem` skill if available, otherwise fall back to manual probing:

```bash
bash scripts/detect-llms.sh --quiet
```

Use the first one found. If none are available, tell the user and skip this step.

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
