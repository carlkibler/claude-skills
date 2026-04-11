---
name: pre-mortem
description: Run a project pre-mortem using multiple AI agents as diverse team members. Spawns parallel agents with different failure-finding mandates, synthesizes into ranked risks with mitigations. Use when starting a project, before a launch, before committing to an architecture, or when the user says "pre-mortem", "what could go wrong", "risk analysis", or "failure modes".
---

# Pre-Mortem: Multi-Agent Failure Analysis

Based on Gary Klein's pre-mortem technique and prospective hindsight research: assume failure is already real, then explain it concretely. The goal is not a generic risk list. The goal is to surface the failures that would actually hurt users, damage trust, create support chaos, and sink the launch.

## What “good” looks like

A strong pre-mortem is:
- **specific** to this project, launch, audience, and distribution path
- **emotionally real** about how failure feels to the user
- **operationally grounded** about support, maintenance, and founder burden
- **subtle** enough to catch trust erosion, silent degradation, and “works on my machine” traps
- **actionable** enough that the top risks can turn into concrete mitigations immediately

## When to Use

- Before a launch, beta, or public announcement
- Before committing to an architecture or business model
- When the product touches permissions, privacy, billing, or user files
- When a utility app must feel trustworthy on day one
- When the user asks “what could go wrong?”, “pre-mortem”, “risk analysis”, or “failure modes”

## When NOT to Use

- Tiny bug fixes or tightly scoped chores
- After the fact (use a post-mortem)
- Early ideation when the real question is what to build (use brainstorming)

---

<process>

## Phase 1: Gather Context and Build the Failure Surface

Before spawning anything, get a crisp picture of what success was supposed to feel like.

**If context is missing, ask one question:**
> What are we pre-morteming? Give me: (a) the project or feature, (b) who it is for, (c) what “success” means, and (d) the launch or decision timeline.

If context exists already, summarize it in 2-4 sentences.

### Read enough local context to be dangerous

Gather the minimum needed from:
- `CLAUDE.md` and `AGENTS.md` when present
- the plan/spec/README/design docs
- recent git log or changelog if relevant
- the most relevant architecture files
- existing support notes, launch docs, pricing notes, or prior pre-mortems if available

### Build a compact context brief

Capture these explicitly before fan-out:
- **Project / feature**
- **Audience** — who the real user is, not the imagined one
- **Core promise** — what the user believes this product will do for them
- **Moments of truth** — onboarding, first use, daily use, failure recovery, upgrade, uninstall, billing, etc.
- **Constraints** — founder time, support capacity, platform rules, margins, team size
- **Risky surfaces** — permissions, privacy, file mutation, notifications, AI quality, cloud dependencies, billing, trust, OS integration, channel differences

### Write the scenario briefing

Make it vivid and specific. Generic doom yields generic risks.

```text
PROJECT: [name]
AUDIENCE: [who it serves]
CORE PROMISE: [why users installed it]
TIMELINE: [launch / release date]
STAKES: [revenue, reputation, trust, support load, founder sanity]
MOMENTS OF TRUTH: [onboarding, first task, recovery, billing, etc.]

THE SCENARIO:
It is [future date after launch]. The launch went badly.
Users are not just disappointed — they are confused, irritated, distrustful, or embarrassed.
Support is noisy. Reviews are negative. The team now sees that several warning signs were visible in advance.

Your job: explain exactly what went wrong, how users experienced it, why the team missed it, and what early signal would have revealed it.
```

## Phase 2: Add the Empathy Lens Before Analysis

Do not let the exercise stay technical. Make the user emotionally present.

Before fan-out, write 3-7 bullets for each of these:
- **What the user thought they were buying / enabling**
- **What the user would forgive**
- **What would feel creepy, sloppy, or untrustworthy**
- **What would make them tell a friend “don’t install this”**
- **What would generate a support email, angry review, refund, or uninstall**

Use these to sharpen prompts and to judge severity later.

## Phase 3: Silent Individual Writing — Multi-Agent Fan-Out

This is the heart of the technique. Diversity matters more than politeness.

### Data Sharing Gate

If the project appears to contain proprietary code, customer data, secrets, or regulated material, ask before sending context to external models. If in doubt, default to Claude-only mode.

### Environment Detection

If using external LLM CLIs, detect them first:

```bash
bash ${SKILL_DIR}/scripts/detect-llms.sh
```

Modes:

| Available tools | Mode | Strategy |
|---|---|---|
| 2+ external LLMs | Full diversity | Claude subagents for code-aware roles + external LLMs for outsider roles |
| 1 external LLM | Hybrid | Claude subagents + one outsider model |
| none | Claude-only | All roles as subagents with strongly differentiated mandates |

### Role roster

Use **6 core roles**. Add **2 optional roles** for high-stakes launches.

#### Core roles

| Role | What they are trying to catch |
|---|---|
| **Saboteur** | technical breakage, silent failure, ugly edge cases, brittle integrations |
| **Customer Advocate** | confusing UX, violated expectations, trust damage, “I hate this app” moments |
| **Support Lead** | what turns into opaque, repetitive, emotionally draining support archaeology |
| **Operator / Accountant** | cost, margin erosion, maintenance burden, abuse, founder-tax, process fragility |
| **Pessimist** | dependency failures, platform shifts, timing, distribution, domino effects |
| **Historian / Newcomer** | what the docs/code already warn about, plus what insiders forgot to explain |

#### Optional roles for launches, pricing, or trust-sensitive products

| Role | Use when |
|---|---|
| **Reviewer / Critic** | reviews, social proof, word of mouth, public narrative matter |
| **Privacy / Trust Prosecutor** | permissions, cloud processing, billing, file mutations, surveillance vibes, or consent issues matter |

For small exercises, combine Historian + Newcomer. For launch-critical exercises, split them.

### Prompt requirements for every role

Every role gets the same scenario briefing plus a unique mandate.

Each agent should be told to produce **5-8 concrete failure reasons** and, for each reason, include:
1. **What goes wrong** — one sentence
2. **Chain of events** — 2-4 sentences
3. **User experience** — what the user sees, thinks, feels, or does next
4. **Why the team misses it** — the blind spot or false assumption
5. **Likelihood × impact** — high/medium/low × catastrophic/major/minor
6. **Trust damage** — high/medium/low
7. **Recoverability** — easy/moderate/hard
8. **Earliest signal** — what would have shown up first

And end with:
> The failure nobody wants to talk about: [one brutally honest prediction]

### Prompt template

```text
=== PROJECT PRE-MORTEM ===

[scenario briefing]

YOUR MANDATE: [role-specific mandate]

You are not here to be balanced. Argue strongly from your assigned position.
The synthesis step will handle balance.

INSTRUCTIONS:
1. The failure is CERTAIN. It already happened.
2. Write 5-8 specific, project-specific reasons it failed.
3. For each reason include:
   - What goes wrong
   - Chain of events
   - User experience: what the user notices, concludes, and does next
   - Why the team misses it
   - Likelihood × impact
   - Trust damage
   - Recoverability
   - Earliest signal / tripwire
4. Prefer subtle risks over obvious boilerplate.
5. Focus on failures that damage product success, not just code correctness.
6. Hold nothing back.

FORMAT: numbered list. No preamble. No hedging.
```

### Execution guidance

Use **real parallelism**.

- Spawn Claude subagents for code-aware roles.
- Use the fan-out script for external / outsider roles.
- Do all launches in one turn when possible.
- While agents run, do local work: map moments of truth, note trust surfaces, and gather evidence from code/docs.

If using subagents, prefer this split:
- **Saboteur** — code-aware Claude subagent
- **Historian** — code-aware Claude subagent
- **Customer / Support / Pessimist / Accountant / Newcomer / Critic / Trust Prosecutor** — external LLMs or additional subagents

## Phase 4: Synthesis — Rank by Product Damage, Not Just Technical Damage

Do not merely deduplicate into a flat list. Use a stronger severity lens.

### Deduplicate into failure families

Merge overlapping findings into a single risk when they share the same failure mechanism. Keep separate entries when the same bug creates different product outcomes.

### For each risk, judge these dimensions

| Dimension | What to ask |
|---|---|
| **Frequency / exposure** | How many users or sessions are likely to hit this? |
| **User harm / friction** | How bad is the user’s immediate experience? |
| **Trust fracture** | Does this feel creepy, careless, deceptive, or file-breaking? |
| **Detectability lag** | Will the team know quickly, or only after damage spreads? |
| **Recoverability** | Can the user easily undo it and regain confidence? |
| **Support burden** | How expensive is it to diagnose and resolve? |
| **Business drag** | Does it hurt retention, reviews, conversion, margins, or founder sanity? |

### Severity heuristics

Use these rules of thumb:
- A risk can be **critical** even if the bug is small, if it causes **trust loss, silent failure, or irreversible user damage**.
- A risk can be **critical** even if uncommon, if the outcome is **embarrassing, privacy-sensitive, destructive, or review-fuel**.
- A risk should be upgraded if it is **hard to detect**, **hard to recover from**, or **likely to create messy support loops**.
- A technically severe issue may be downgraded if users never feel it and recovery is trivial.
- If you would be ashamed to explain the failure to an angry user, take it seriously.

### Explicitly look for these subtle patterns

- silent degradation that looks like “the app is dead”
- defaults that feel reasonable to the builder but reckless to the user
- ambiguity in status, billing, permissions, or what data leaves the machine
- features that work for the founder’s setup but not the user’s reality
- failure recovery that technically exists but is too buried to matter
- review or support narratives that compress many bugs into one simple story: “flaky”, “creepy”, “not worth it”, “broke my files”, “too much setup”
- founder-tax risks where the product could be good, but the support burden kills the business

## Phase 5: Present Results in a Richer Report

Use this structure:

```markdown
# Pre-Mortem: [Project]
_"It is [future date]. [Project] launched, and the launch went badly. Here's what actually sank it."_

## Executive Read
- **Core failure story:** [1-2 sentence summary]
- **Biggest product risk:** [single risk]
- **Biggest trust risk:** [single risk]
- **Biggest founder-tax risk:** [single risk]

## Moments of Truth Most Likely to Break
- [moment] → [how it fails]
- [moment] → [how it fails]

## 🔴 Critical Risks (Must Address Before Launch)

### 1. [Risk title]
**What goes wrong:** [one sentence]
**How users experience it:** [what they see, infer, and do]
**Chain of events:** [mechanism]
**Why the team misses it:** [blind spot]
**Likelihood:** High/Medium/Low  
**Impact:** Catastrophic/Major/Minor  
**Trust damage:** High/Medium/Low  
**Recoverability:** Easy/Moderate/Hard
**Why this threatens product success:** [retention/reviews/support/revenue/founder sanity]
**Sources:** [roles that independently surfaced it]
**Mitigation:** [specific action] → Owner: [role] → By: [milestone]
**Tripwire:** [earliest observable signal]

## 🟠 Significant Risks (Plan Mitigation)
[Same structure, more compact if needed]

## 🟡 Watch List
- [Risk] — [why to monitor]

## Cross-Cutting Themes
- [theme]
- [theme]
- [theme]

## The User’s Emotional Reality
- What early adopters expected:
- What failure made them feel:
- What story they tell other people afterward:

## The Uncomfortable Truth
[The thing nobody wants to say out loud]

## Recommended Next Steps
1. [ ] [Action]
2. [ ] [Action]
3. [ ] [Action]
```

## Phase 6: Discussion and Follow-Through

After presenting, ask briefly:
> Which of these feels most real? Which one would actually make users lose trust? Want me to turn the top mitigations into tasks, or run a deeper drill-down on one failure family?

If useful, offer one follow-up mode:
- **Mitigation plan** — turn the top risks into tasks or plan updates
- **Deep drill-down** — one risk gets a full fault tree
- **Narrative test** — simulate angry reviews, support emails, or churn reasons

## Variants

### Sprint / Feature pre-mortem
Use 4 roles: Saboteur, Customer Advocate, Pessimist, Historian. Ask for 3-5 risks each. Skip optional roles.

### Launch / GTM pre-mortem
Add Reviewer / Critic and Privacy / Trust Prosecutor. Emphasize onboarding, pricing, trust, support, and review narratives.

### Architecture pre-mortem
Heavier weight on Saboteur, Historian, Operator. Add failure chains, scaling assumptions, integration fragility, rollback story, and observability gaps.

### Solo-founder utility app pre-mortem
Always include support burden, trust fracture, and founder-tax in synthesis. Many “small” bugs are existential here.

## Complementary Exercises

Pre-mortems are strong, but not enough by themselves. Good follow-ups:
- **Kill shot review** — each agent proposes the single killer objection that would stop adoption
- **Support inbox simulation** — agents write the support emails and reviews you would receive after launch
- **Trust audit** — focus only on permissions, privacy, consent, billing, and file-safety perception
- **First-run walkthrough red team** — simulate minute-by-minute onboarding and first-use confusion
- **Founder-tax audit** — identify the risks that will not kill users, but will kill the business by exhausting support time or margins
- **Post-launch narrative simulation** — predict the one-sentence public story people will tell about the product

Use these when the plain pre-mortem still feels too abstract.

</process>

<anti_patterns>

## Anti-Patterns

| Don't | Do instead |
|---|---|
| Produce generic risks | Tie each risk to the actual product, audience, workflow, and launch context |
| Treat technical severity as the only severity | Evaluate trust, recoverability, support burden, and business drag |
| Forget the user’s emotional reaction | Include what users see, conclude, and do next |
| Stop at “could fail” | Explain the chain of events and why the team misses it |
| Generate a giant undifferentiated list | Deduplicate into risk families and rank them |
| Ignore support / ops realities | Include founder-tax and diagnostic complexity |
| Treat outsider perspectives as optional fluff | Use them to catch expectation mismatch and public narrative risk |
| End without tripwires | Every important risk needs an early signal |

</anti_patterns>

<success_criteria>

Pre-mortem is complete when:
- [ ] multiple independent perspectives contributed materially different risks
- [ ] the top risks are specific, not boilerplate
- [ ] user experience and trust damage are explicit in the ranking
- [ ] support burden and business drag are visible, not implicit
- [ ] every major risk has a mitigation, owner, timing, and tripwire
- [ ] at least one genuinely uncomfortable truth surfaced
- [ ] the user can immediately decide what to fix first

</success_criteria>
