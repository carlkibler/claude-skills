---
name: launch-sequence
description: Run the full pre-launch gauntlet (first-contact → support-storm → trust-audit → pre-mortem) and get a single GO/CAUTION/NO-GO verdict.
display_name: "Launch Sequence"
brand_color: "#0D9488"
local_only: false
group: "Better Products"
usage: "/launch-sequence:run"
summary: "Full pre-launch gauntlet with GO/CAUTION/NO-GO verdict"
default_prompt: "Run the full pre-launch sequence on this product or feature. Surface every risk across first-run experience, support load, trust surface, and catastrophic failure modes."
---

# Launch Sequence

The pre-launch gauntlet. Chains four analysis skills into a single synthesized verdict so you can't accidentally skip one.

## When to Use

- Before any public launch, beta, or major feature release
- When you want one command instead of four
- When you need a board-ready risk summary

## When NOT to Use

- Bug fixes or small incremental changes
- Pure internal tools with no new user-facing behavior
- When you've already run all four constituent skills recently

---

<process>

## Phase 1: Context Capture

Ask (or infer from context) the minimum needed to run the gauntlet:

1. **What** — the product, feature, or launch being evaluated
2. **Who** — the target user and how they discover/install it
3. **When** — launch timeline (hard date? soft launch? beta?)
4. **Success** — what does a good first week look like?

If all four are clear from context, proceed immediately without asking.

## Phase 2: Parallel Analysis

Launch all four constituent analysis passes in parallel as subagents. Each subagent gets the same context brief plus its specific mandate.

### Context Brief (inject into each subagent)
```
PRODUCT: [product name and one-line description]
AUDIENCE: [who this is for]
LAUNCH: [when and how]
SUCCESS: [what good looks like]
```

### Subagent Mandates

**Subagent 1 — First-Run Red-Team** (mandate of first-contact skill)
Simulate the experience of a brand-new user encountering this product for the first time. Find every place they get confused, think it's broken, fail to understand the value, or abandon setup. Look for: unclear onboarding, missing zero-state guidance, confusing first action, misleading UI text, setup friction that filters out valid users.

**Subagent 2 — Support Load Forecast** (mandate of support-storm skill)
Simulate the first 2 weeks of support emails, 1-star reviews, Reddit posts, and bug reports this launch will generate. Generate 10-15 realistic examples. Identify which signal a product bug vs. user confusion vs. unmet expectation. Find the 3 changes that would eliminate the most tickets.

**Subagent 3 — Trust Surface Audit** (mandate of trust-audit skill)
Audit this product for everything that could make a user feel unsafe, surveilled, surprised, or deceived. Cover: permissions requested vs. permissions needed, data retention and deletion, billing surprises, silent mutations to user files or state, anything that "feels creepy" even if technically legal.

**Subagent 4 — Pre-Mortem** (mandate of pre-mortem skill)
Assume it is 6 months after launch and the product failed. Write the postmortem. What were the actual causes? Find the top 5-7 failure modes most specific to THIS product and audience. For each: estimated probability, user impact, recovery path. Rank by (probability × impact).

## Phase 3: Synthesis and Verdict

After all four subagents complete, synthesize their findings:

### Blocking Issues (must fix before launch)
Issues that appear in 2+ analyses or represent catastrophic user harm.

### Non-Blocking Issues (fix post-launch)
Single-analysis findings that are real but survivable.

### Verdict

Choose one:

**🟢 GO** — No blocking issues. Non-blocking issues are documented. Launch when ready.

**🟡 CAUTION** — 1-2 blocking issues with clear, fast fixes. Launch after addressing.

**🔴 NO-GO** — 3+ blocking issues or one catastrophic finding. Fix before launching.

### Output Format

```
## Launch Sequence Report

**Verdict: [🟢 GO / 🟡 CAUTION / 🔴 NO-GO]**

### Blocking Issues
- [Issue from which analysis] [description] [suggested fix]

### Non-Blocking Issues
- [Issue] [suggested fix]

### Key Themes
[2-3 sentences on the most common cross-analysis patterns]

### What to Do Next
[Numbered list of immediate actions, ordered by priority]
```

</process>
