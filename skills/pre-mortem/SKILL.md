---
name: pre-mortem
description: Run a project pre-mortem using multiple AI agents as diverse team members. Spawns parallel agents with different failure-finding mandates, synthesizes into ranked risks with mitigations. Use when starting a project, before a launch, before committing to an architecture, or when the user says "pre-mortem", "what could go wrong", "risk analysis", or "failure modes".
---

# Pre-Mortem: Multi-Agent Failure Analysis

Based on Gary Klein's pre-mortem technique and prospective hindsight research: assume failure is already real, then explain it concretely. The goal is not a generic risk list. The goal is to surface the failures that would actually hurt users, damage trust, create support chaos, and sink the launch.

## What "good" looks like

A strong pre-mortem is:
- **specific** to this project, launch, audience, and distribution path
- **emotionally real** about how failure feels to the user
- **operationally grounded** about support, maintenance, and founder burden
- **subtle** enough to catch trust erosion, silent degradation, and "works on my machine" traps
- **actionable** enough that the top risks can turn into concrete mitigations immediately
- **perspectivally diverse** — not just roles but genuinely different emotional registers, priors, and tolerance for risk

## When to Use

- Before a launch, beta, or public announcement
- Before committing to an architecture or business model
- When the product touches permissions, privacy, billing, or user files
- When a utility app must feel trustworthy on day one
- When the user asks "what could go wrong?", "pre-mortem", "risk analysis", or "failure modes"

## When NOT to Use

- Tiny bug fixes or tightly scoped chores
- After the fact (use a post-mortem)
- Early ideation when the real question is what to build (use brainstorming)

---

<process>

## Phase 1: Gather Context and Build the Failure Surface

Before spawning anything, get a crisp picture of what success was supposed to feel like.

**If context is missing, ask one question:**
> What are we pre-morteming? Give me: (a) the project or feature, (b) who it is for, (c) what "success" means, and (d) the launch or decision timeline.

If context exists already, summarize it in 2-4 sentences.

### Read enough local context to be dangerous

Gather the minimum needed from:
- `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` when present
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
- **What would make them tell a friend "don't install this"**
- **What would generate a support email, angry review, refund, or uninstall**

Use these to sharpen prompts and to judge severity later.

## Phase 3: Silent Individual Writing — Multi-Agent Fan-Out

This is the heart of the technique. Diversity of perspective matters more than coverage or politeness.

### Data Sharing Gate

If the project appears to contain proprietary code, customer data, secrets, or regulated material, ask before sending context to external models. If in doubt, default to **single-agent mode** (all roles as subagents of the running agent with strongly differentiated mandates).

### Environment Detection

The skill ships with a detection script at `scripts/detect-llms.sh` inside the skill directory. Run it using the skill's bundled path:

```bash
# The skill's scripts live at ${SKILL_DIR} (set by the host agent on install):
bash "${SKILL_DIR}/scripts/detect-llms.sh"

# Fallback if SKILL_DIR isn't set — inline detection:
for tool in ask-gemini ask-copilot ask-cerebras ask-zai gemini llm codex; do
  command -v "$tool" >/dev/null 2>&1 && echo "found: $tool"
done
```

If neither the script nor the variable is available, skip detection and default to single-agent mode. The fallback is always safe.

Modes:

| Available tools | Mode | Strategy |
|---|---|---|
| 2+ external LLMs | Full diversity | Subagents of the running agent for code-aware roles + external LLMs for outsider roles |
| 1 external LLM | Hybrid | Subagents of the running agent + one outsider model |
| none | Single-agent | All roles as subagents with strongly differentiated mandates and emotional registers |

### Role roster

Use **6 core roles** minimum. Add **specialized roles** for high-stakes launches. Assign each role a distinct **emotional register** — not just a functional lens but a visceral posture. Same facts read very differently through fear vs. contempt vs. grief.

#### Core roles

| Role | What they catch | Emotional register |
|---|---|---|
| **Saboteur** | Technical breakage, silent failure, ugly edge cases, brittle integrations | Cold glee — enjoys finding the seam that tears |
| **Customer Advocate** | Confusing UX, violated expectations, trust damage, "I hate this app" moments | Protective anger — speaks for the user who deserved better |
| **Support Lead** | Opaque, repetitive, emotionally draining support archaeology | Exhausted resignation — has seen this exact ticket before |
| **Operator / Accountant** | Cost, margin erosion, maintenance burden, abuse, maintenance drag, process fragility | Dry alarm — watching the numbers quietly get worse |
| **Pessimist** | Dependency failures, platform shifts, timing, distribution, domino effects | Grim satisfaction — told you so, saw it coming |
| **Historian** | What docs/code already warned about, what insiders forgot to explain, what failed at similar products | Mournful clarity — this was all in the record |

#### Perspective-expanding roles (add at least 2 per exercise)

| Role | What they catch | Emotional register |
|---|---|---|
| **Burned Expert** | Pattern-matches to prior failures at similar products — carries scar tissue and justified skepticism | Controlled fury — watched a nearly identical thing collapse, not again |
| **Emotional Witness** | Psychological impact on users: shame, anxiety, helplessness, betrayal — not UX friction, but human cost | Raw empathy — describes what it feels like in the body when the product fails you |
| **Outsider / Cultural Stranger** | Assumptions the team never questioned because everyone in the room shares them; what non-default users experience | Bewildered estrangement — doesn't understand the jargon and that's the point |
| **Devil's Advocate** | Defends the thing nobody wants to say — "actually the core assumption is wrong" | Calm heresy — not being contrarian, being honest about the thing the team voted to stop talking about |
| **Reviewer / Critic** | Reviews, social proof, word of mouth, public narrative | Performative disappointment — writes the 2-star review in their head while reading the docs |
| **Privacy / Trust Prosecutor** | Permissions, cloud processing, billing, file mutations, surveillance vibes, consent theater | Principled outrage — every ambiguity is treated as a deliberate violation |

For small exercises: use 4 core + 2 perspective-expanding roles (Burned Expert + Outsider recommended as defaults).
For launch-critical exercises: use all 6 core + Reviewer/Critic + Privacy Prosecutor + Emotional Witness.
Never use fewer than 4 roles. Homogenous analysis produces homogenous blind spots.

### Prompt requirements for every role

Every role gets the same scenario briefing plus a unique mandate that includes the emotional register.

Each agent should be told to produce **5-8 concrete failure reasons** and, for each reason, include:
1. **What goes wrong** — one sentence
2. **Chain of events** — 2-4 sentences
3. **User experience** — what the user sees, thinks, feels, or does next
4. **Emotional impact** — the specific emotion the user feels at the moment of failure (not just "frustrated" — grief? shame? violated? gaslit?)
5. **Why the team misses it** — the blind spot or false assumption
6. **Likelihood × impact** — high/medium/low × catastrophic/major/minor
7. **Trust damage** — high/medium/low
8. **Recoverability** — easy/moderate/hard
9. **Earliest signal** — what would have shown up first

And end with:
> The failure nobody wants to talk about: [one brutally honest prediction]

### Prompt template

```text
=== PROJECT PRE-MORTEM ===

[scenario briefing]

YOUR ROLE: [role name]
YOUR EMOTIONAL REGISTER: [role emotional register — e.g., "controlled fury: you've seen this exact pattern collapse before and you're not going to be polite about it"]
YOUR MANDATE: [role-specific mandate]

You are not here to be balanced. Argue strongly from your assigned position and emotional register.
Do not soften your findings. Do not add disclaimers. The synthesis step will handle balance.

INSTRUCTIONS:
1. The failure is CERTAIN. It already happened.
2. Write 5-8 specific, project-specific reasons it failed.
3. For each reason include:
   - What goes wrong
   - Chain of events
   - User experience: what the user notices, concludes, and does next
   - Emotional impact: the specific emotion the user feels at this moment (be precise — not "frustrated" but "betrayed", "stupid", "gaslit", etc.)
   - Why the team misses it
   - Likelihood × impact
   - Trust damage
   - Recoverability
   - Earliest signal / tripwire
4. Prefer subtle risks over obvious boilerplate.
5. Focus on failures that damage product success, not just code correctness.
6. Hold nothing back.
7. End with: "The failure nobody wants to talk about: [one brutally honest prediction]"

FORMAT: numbered list. No preamble. No hedging. Write as your character — in that emotional register.
```

### Execution guidance

Use **real parallelism**.

- Spawn subagents of the running agent for code-aware roles (Saboteur, Historian, Burned Expert).
- Use the fan-out script for outsider and emotional roles where external LLMs are available: `bash "${SKILL_DIR}/scripts/fan-out.sh" scenario.txt output/`
- Do all launches in one turn when possible.
- While agents run, do local work: map moments of truth, note trust surfaces, gather evidence from code/docs.

Preferred split when multiple models are available:
- **Saboteur, Historian, Burned Expert** — code-aware subagents (can read source, git log, architecture)
- **Customer Advocate, Support Lead, Pessimist, Emotional Witness, Outsider, Critic, Trust Prosecutor, Devil's Advocate** — external LLMs or additional subagents with no source access (fresh eyes only)

If only one model/agent is available, use it for all roles with strongly differentiated mandates. The emotional register differentiation is what prevents them from collapsing into the same answer.

## Phase 3.5 (Optional): Cross-Pollination Round

After collecting first-round responses, run a second round where each agent sees a digest of the other perspectives and responds to them.

Use this when:
- Agents produced surprisingly different threat models
- One agent surfaced something the others ignored entirely
- The synthesis feels too neat — real disagreement should feel messy

**How to run it:**

1. Compile a 1-paragraph digest per role: "The [Role] found [2-3 key risks]. Their most surprising finding was [X]."
2. Send each agent a follow-up prompt:

```text
=== CROSS-POLLINATION: SECOND ROUND ===

You just wrote your initial pre-mortem analysis as [Role].

Here is what the other perspectives found:

[digest of other roles' findings]

YOUR TASK:
1. Identify 1-2 findings from other roles that you think are WRONG or OVERBLOWN. Explain why from your position.
2. Identify 1 finding that you missed in your first pass that now strikes you as genuinely important.
3. Revise or sharpen your single most important risk in light of this new information.
4. Note if any combination of risks creates a cascading failure the others didn't see.

Stay in character. Your emotional register is [register]. Don't become diplomatic.
```

3. Capture the exchange verbatim — this is source material for the process log.

## Phase 4: Synthesis — Rank by Product Damage, Not Just Technical Damage

Do not merely deduplicate into a flat list. Use a stronger severity lens.

### Deduplicate into failure families

Merge overlapping findings into a single risk when they share the same failure mechanism. Keep separate entries when the same bug creates different product outcomes.

### For each risk, judge these dimensions

| Dimension | What to ask |
|---|---|
| **Frequency / exposure** | How many users or sessions are likely to hit this? |
| **User harm / friction** | How bad is the user's immediate experience? |
| **Emotional injury** | What specific emotion does failure produce — and does it damage the relationship permanently? |
| **Trust fracture** | Does this feel creepy, careless, deceptive, or file-breaking? |
| **Detectability lag** | Will the team know quickly, or only after damage spreads? |
| **Recoverability** | Can the user easily undo it and regain confidence? |
| **Support burden** | How expensive is it to diagnose and resolve? |
| **Business drag** | Does it hurt retention, reviews, conversion, margins, or founder sanity? |
| **Narrative compression** | Will multiple different bugs get told as one story? ("it's just broken") |

### Severity heuristics

Use these rules of thumb:
- A risk can be **critical** even if the bug is small, if it causes **trust loss, silent failure, or irreversible user damage**.
- A risk can be **critical** even if uncommon, if the outcome is **embarrassing, privacy-sensitive, destructive, or review-fuel**.
- A risk should be upgraded if it is **hard to detect**, **hard to recover from**, or **likely to create messy support loops**.
- A risk should be upgraded if the emotional injury it produces is **shame, betrayal, or helplessness** — these don't recover with a patch.
- A technically severe issue may be downgraded if users never feel it and recovery is trivial.
- If you would be ashamed to explain the failure to an angry user, take it seriously.

### Explicitly look for these subtle patterns

- silent degradation that looks like "the app is dead"
- defaults that feel reasonable to the builder but reckless to the user
- ambiguity in status, billing, permissions, or what data leaves the machine
- features that work for the founder's setup but not the user's reality
- failure recovery that technically exists but is too buried to matter
- emotional injuries that users can't articulate — they just stop using it
- review or support narratives that compress many bugs into one simple story: "flaky", "creepy", "not worth it", "broke my files", "too much setup"
- maintenance drag risks where the product could be good, but the support burden kills the business
- insider assumptions that the Outsider or Devil's Advocate spotted but the technical roles missed

## Phase 5: Present Results — Two Documents

Produce **two separate documents**:

### Document 1: The Pre-Mortem Report

```markdown
# Pre-Mortem: [Project]
_"It is [future date]. [Project] launched, and the launch went badly. Here's what actually sank it."_

## Executive Read
- **Core failure story:** [1-2 sentence summary]
- **Biggest product risk:** [single risk]
- **Biggest trust risk:** [single risk]
- **Biggest emotional injury risk:** [single risk — the one that breaks the relationship]
- **Biggest maintenance drag risk:** [single risk]

## Moments of Truth Most Likely to Break
- [moment] → [how it fails] → [what the user feels]
- [moment] → [how it fails] → [what the user feels]

## 🔴 Critical Risks (Must Address Before Launch)

### 1. [Risk title]
**What goes wrong:** [one sentence]
**How users experience it:** [what they see, infer, and do]
**Emotional impact:** [the specific emotion — be precise]
**Chain of events:** [mechanism]
**Why the team misses it:** [blind spot]
**Likelihood:** High/Medium/Low  
**Impact:** Catastrophic/Major/Minor  
**Trust damage:** High/Medium/Low  
**Recoverability:** Easy/Moderate/Hard
**Why this threatens product success:** [retention/reviews/support/revenue/founder sanity]
**Sources:** [roles that independently surfaced it]
**Dissent:** [any role that pushed back on this risk — and why]
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

## The User's Emotional Reality
- What early adopters expected:
- What failure made them feel:
- The specific moment the relationship broke:
- What story they tell other people afterward:

## The Uncomfortable Truth
[The thing nobody wants to say out loud]

## Recommended Next Steps
1. [ ] [Action]
2. [ ] [Action]
3. [ ] [Action]
```

### Document 2: The Process Log — "How the Pre-Mortem Ran"

This is the meta-document. It shows the work, not just the conclusions. Save it alongside the report.

```markdown
# Pre-Mortem Process Log: [Project]
_Generated: [date]. This document records what happened during the pre-mortem, not just what it found._

## Agents and Roles

| Agent / Model | Role | Emotional Register | Prompt Variant |
|---|---|---|---|
| [model or "subagent-1"] | Saboteur | Cold glee | Standard + code access |
| [model or "subagent-2"] | Emotional Witness | Raw empathy | Standard, no code access |
| [model or "external tool"] | Burned Expert | Controlled fury | Standard + prior-failure framing |
| ... | ... | ... | ... |

## Scenario Briefing Sent

> [verbatim briefing text sent to all agents]

## What Each Agent Returned

### Saboteur ([model])
**Top 3 risks surfaced:**
1. [risk]
2. [risk]
3. [risk]
**Their "failure nobody wants to talk about":** [verbatim]
**Surprising finding:** [what this role caught that others missed]

### [Next role...]
[Same structure]

## Cross-Pollination Round (if run)

### Round 2 Prompt Digest
[The digest sent to each agent]

### Exchanges and Disagreements
- **[Role A] challenged [Role B]'s finding that [X]:** "[verbatim quote or paraphrase]"
- **[Role B] responded:** "[verbatim quote or paraphrase]"
- **Resolution:** [how synthesis handled it — accepted, rejected, escalated to critical]

### What Changed After Cross-Pollination
- [Risk upgraded/downgraded/merged because of cross-pollination]
- [New cascading failure identified]
- [Finding that appeared in round 1 but was retracted after challenge]

## Where Perspectives Converged
- [Risk X was surfaced by N roles independently — this convergence increased severity rating]
- [Risk Y appeared in 4 of 6 roles with different framings — synthesis merged into one entry]

## Where Perspectives Clashed
- [Role A rated Risk X as critical; Role B rated it watch-list. Synthesis reasoning: ...]
- [The Devil's Advocate disputed the Burned Expert's core assumption. Outcome: ...]

## Synthesis Judgment Calls
- [Decision made during synthesis that wasn't obvious — and why]
- [Risk that was downgraded despite strong advocacy from one role — reason]

## Process Quality Notes
- Roles that felt too similar (potential for future differentiation): [list]
- Roles that punched above their weight (surfaced unique risks): [list]
- Gaps in perspective coverage for this type of project: [list]
- Recommended additional roles for a follow-up exercise: [list]
```

## Phase 6: Discussion and Follow-Through

After presenting both documents, ask briefly:
> Which of these feels most real? Which one would actually make users lose trust — or feel betrayed? Want me to turn the top mitigations into tasks, run a deeper drill-down on one failure family, or run the cross-pollination round if we skipped it?

If useful, offer one follow-up mode:
- **Mitigation plan** — turn the top risks into tasks or plan updates
- **Deep drill-down** — one risk gets a full fault tree
- **Narrative test** — simulate angry reviews, support emails, or churn reasons
- **Cross-pollination** — run the second round if skipped, or extend it with new roles

## Variants

### Sprint / Feature pre-mortem
Use 4 roles: Saboteur, Customer Advocate, Pessimist, Historian + Burned Expert. Ask for 3-5 risks each. Skip optional roles. Still produce both documents.

### Launch / GTM pre-mortem
Add Reviewer / Critic, Privacy / Trust Prosecutor, Emotional Witness, and Devil's Advocate. Emphasize onboarding, pricing, trust, support, and review narratives. Run the cross-pollination round.

### Architecture pre-mortem
Heavier weight on Saboteur, Historian, Operator, Burned Expert. Add failure chains, scaling assumptions, integration fragility, rollback story, and observability gaps.

### Solo-founder utility app pre-mortem
Always include support burden, trust fracture, Emotional Witness, and maintenance drag in synthesis. Many "small" bugs are existential here.

## Complementary Exercises

Pre-mortems are strong, but not enough by themselves. Good follow-ups:
- **Kill shot review** — each agent proposes the single killer objection that would stop adoption
- **Support inbox simulation** — agents write the support emails and reviews you would receive after launch
- **Trust audit** — focus only on permissions, privacy, consent, billing, and file-safety perception
- **First-run walkthrough red team** — simulate minute-by-minute onboarding and first-use confusion
- **Maintenance drag audit** — identify the risks that will not kill users, but will kill the business by exhausting support time or margins
- **Post-launch narrative simulation** — predict the one-sentence public story people will tell about the product

Use these when the plain pre-mortem still feels too abstract.

</process>

<anti_patterns>

## Anti-Patterns

| Don't | Do instead |
|---|---|
| Produce generic risks | Tie each risk to the actual product, audience, workflow, and launch context |
| Treat technical severity as the only severity | Evaluate trust, recoverability, support burden, and business drag |
| Forget the user's emotional reaction | Include the specific emotion at the moment of failure — not just "frustrated" |
| Stop at "could fail" | Explain the chain of events and why the team misses it |
| Generate a giant undifferentiated list | Deduplicate into risk families and rank them |
| Ignore support / ops realities | Include maintenance drag and diagnostic complexity |
| Treat outsider perspectives as optional fluff | Use them to catch expectation mismatch and public narrative risk |
| End without tripwires | Every important risk needs an early signal |
| Name the running agent in prompts | Use role names, not "Claude" or "Gemini" — any agent might be running this |
| Give every role the same emotional register | Differentiate the posture — fear, fury, grief, and contempt find different failures |
| Skip the process log | The conversation and disagreements are valuable — document them |
| Treat role outputs as equally weighted | Note convergence and divergence; independent agreement increases severity |

</anti_patterns>

<success_criteria>

Pre-mortem is complete when:
- [ ] multiple independent perspectives contributed materially different risks
- [ ] roles had distinct emotional registers, not just distinct domains
- [ ] the top risks are specific, not boilerplate
- [ ] user experience AND emotional impact are explicit in the ranking
- [ ] support burden and business drag are visible, not implicit
- [ ] every major risk has a mitigation, owner, timing, and tripwire
- [ ] at least one genuinely uncomfortable truth surfaced
- [ ] at least one finding came from an outsider/emotional role that technical roles missed
- [ ] the user can immediately decide what to fix first
- [ ] a process log was produced showing who said what and where perspectives clashed

</success_criteria>
