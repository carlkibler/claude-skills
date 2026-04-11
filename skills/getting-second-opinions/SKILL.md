---
name: run
description: Use when completing complex implementations, making design decisions, or needing validation from different AI perspectives before committing major changes. Invokes GitHub Copilot CLI with gpt-5.3-codex for code review, architecture validation, and pre-merge checks.
---

# Getting Second Opinions

Use GitHub Copilot CLI to validate work with a different model architecture before committing.

**Core insight:** You and the user share the same blind spots — you're the same model family, trained on the same data. A different architecture catches different things.

## When to Use

**Mandatory:**
- Complex multi-file changes before merge
- Design decisions with multiple valid approaches
- After 2+ hours on a single approach (tunnel vision risk)
- Security-sensitive or performance-critical code

**Skip for:** trivial fixes, style questions, crystal-clear requirements

## How

### Pre-Merge Review (Most Common)

```bash
copilot --model gpt-5.3-codex --allow-read-tools --prompt "Review my git changes for production readiness.

Show me the diff from main branch and check for:
- Correctness and edge cases
- Architecture and design
- Performance implications
- Security concerns"
```

### Design Decision Validation

```bash
copilot --model gpt-5.3-codex --allow-read-tools --prompt "[Describe the options and constraints. Ask: What trade-offs am I not seeing?]"
```

### Targeted Question

```bash
copilot --model gpt-5.3-codex --prompt "[Specific question about the implementation]"
```

## Interpreting Results

Copilot is a **collaborator, not an authority.** Classify each piece of feedback:

| Category | Action |
|----------|--------|
| **Must-fix** | Bug, security issue, correctness problem → implement immediately |
| **Should-fix** | Genuine simplification, better error handling → implement if clean |
| **Nice-to-have** | Alternative approach, style preference → mention to user |
| **Reject** | Over-engineering, conflicts with project conventions → skip with reason |

If Copilot and your analysis disagree, explain the disagreement to the user and let them decide.

## Available Models

**Primary:** `gpt-5.3-codex` — specialized for code analysis, the strongest reviewer available

**Fallbacks** (if gpt-5.3-codex is unavailable):
- `gpt-5` — general-purpose, still strong
- `claude-sonnet-4.6` — different architecture, good for diversity of perspective

**Detection:** If `copilot` command is not available, tell the user to install GitHub Copilot CLI (`gh extension install github/gh-copilot`) or skip this step.

## The Red Flags

These thoughts mean STOP and get a second opinion:
- "It works in my tests" — tests only prove known scenarios
- "I've spent 3 hours on this" — sunk cost isn't validation
- "I'm confident this is right" — confidence correlates with blind spots
- "It's obviously the best approach" — obvious to you ≠ optimal

**5 minutes of external validation prevents hours of debugging.**
