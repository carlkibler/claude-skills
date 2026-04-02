---
name: getting-second-opinions
description: Use when completing complex implementations, making design decisions, or needing validation from different AI perspectives before committing major changes
---

# Getting Second Opinions

Use GitHub Copilot CLI (`copilot`) to get validation from different AI models (Claude, GPT) for critical decisions.

**Core principle:** Your perspective is valuable, but different models catch different issues.

## When to Use

**Mandatory:**
- Complex implementation before merge (multi-file, architectural changes)
- Design decisions with multiple valid approaches
- After spending 2+ hours on single approach
- Uncertain about correctness despite passing tests

**Optional but valuable:**
- Pre-merge validation for important features
- Architectural trade-off decisions
- Performance-critical code
- Security-sensitive implementations

**DO NOT use for:**
- Trivial changes (typo fixes, simple updates)
- Style/linting questions (use ruff)
- When requirements are crystal clear

## Quick Reference

| Scenario | Models to Use | Focus |
|----------|--------------|-------|
| Code review | gpt-5.4-codex (preferred) | Correctness, bugs, edge cases |
| Design decision | gpt-5.4-codex (preferred) | Architecture, trade-offs, alternatives |
| Performance | gpt-5.4-codex (preferred) | Optimization, bottlenecks |
| Security | gpt-5.4-codex (preferred) | Vulnerabilities, attack vectors |

## Implementation

### Basic Pattern

```bash
# 1. Prepare your question/context
QUESTION="I implemented X using approach Y. Are there issues I'm missing?"

# 2. Get opinion from gpt-5.4-codex (preferred model)
copilot --model gpt-5.4-codex --prompt "$QUESTION" --allow-all-tools

# 3. Analyze insights
```

### Pre-Merge Review

```bash
# Ask for review using gpt-5.4-codex (preferred)
copilot --model gpt-5.4-codex --allow-all-tools --prompt "Review my git changes for production readiness.

Show me the diff from main branch and check for:
- Correctness and edge cases
- Architecture and design
- Performance implications
- Security concerns"
```

### Design Decision Validation

```bash
# When choosing between approaches
copilot --model gpt-5.4-codex --allow-all-tools --prompt "I need to implement real-time notifications. Considering:

Option A: WebSockets + Redis queue (current implementation, 3hrs invested)
Option B: Server-Sent Events + PostgreSQL NOTIFY
Option C: Django Channels

Which approach best fits Django apps with:
- 1000 concurrent users expected
- Deploying to Heroku/AWS
- Team prefers simple solutions

What are the trade-offs I'm not seeing?"
```

## Available Models

**Preferred Model**:
- `gpt-5.4-codex` - **Use this model for all code reviews** - specialized for code analysis, bug detection, and technical validation

**Alternative Models** (use only if gpt-5.4-codex is unavailable):
- `claude-sonnet-4.5` - Most capable Claude
- `claude-sonnet-4` - Fast, balanced
- `gpt-5` - Latest GPT

**Strategy**: Use `gpt-5.4-codex` as the primary model for code review and validation.

## Common Mistakes

| Mistake | Why It's Wrong | Fix |
|---------|---------------|-----|
| "Tests pass, don't need review" | Tests only cover known cases | Get external validation anyway |
| "Too confident to need a check" | Overconfidence causes blindspots | Confidence is when you need it most |
| "Already invested 3 hours" | Sunk cost isn't validation | Time spent ≠ correctness |
| "Only ask when uncertain" | You don't know what you don't know | Ask even when confident |
| "Use single model" | One perspective misses issues | 2-3 different models minimum |

## Red Flags - STOP and Get Second Opinion

These thoughts mean STOP and use copilot:
- "Code works in my tests" (tests don't prove correctness)
- "I've spent X hours on this" (sunk cost isn't validation)
- "Linting passed" (style ≠ correctness)
- "I'm confident this is right" (overconfidence = blindspot)
- "Other tasks are waiting" (time pressure causes mistakes)
- "It's obviously the best approach" (obvious to you ≠ optimal)

## Rationalization Table

| Excuse | Reality |
|--------|---------|
| "Tests pass, must be correct" | Tests only check known scenarios, not edge cases or design flaws |
| "Linting is clean" | Style checks don't validate logic, correctness, or architecture |
| "I'm confident" | Confidence correlates with blindspots; get external validation |
| "Already spent 3 hours" | Time invested doesn't validate approach; sunk cost fallacy |
| "Too simple to need review" | Simple code has subtle bugs; external eyes catch them |
| "Other tasks waiting" | Time pressure causes mistakes; 5 minutes now saves hours later |
| "I'll ask if problems emerge" | Problems emerge after merge; prevent instead of fix |
| "My analysis is sufficient" | Single perspective misses issues; diversity catches more |

## Integration with Workflows

**Pre-Merge**:
1. Complete implementation
2. Run tests, linting
3. Get copilot review from 2 models
4. Address feedback
5. Merge

**Design Decisions**:
1. Identify options
2. Implement prototype (if needed)
3. Get copilot opinions from 2-3 models
4. Synthesize insights
5. Decide with confidence

**Complex Features**:
1. Implement in stages
2. Get copilot validation at each stage
3. Adjust based on feedback
4. Final review before merge

## The Bottom Line

**Passing tests doesn't mean code is optimal.**

**Your perspective is limited by your experience, biases, and knowledge.**

**Different AI models have different training, strengths, and perspectives.**

**5 minutes getting a second opinion can prevent hours of debugging or refactoring.**

**Use copilot proactively, not reactively.**
