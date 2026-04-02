---
name: pre-mortem
description: Run a project pre-mortem using multiple AI agents as diverse team members. Spawns parallel agents with different failure-finding mandates, synthesizes into ranked risks with mitigations. Use when starting a project, before a launch, before committing to an architecture, or when the user says "pre-mortem", "what could go wrong", "risk analysis", or "failure modes".
---

# Pre-Mortem: Multi-Agent Failure Analysis

Based on Gary Klein's pre-mortem technique (HBR 2007) and Mitchell et al.'s prospective hindsight research — imagining failure as certain generates 30% more correct failure reasons than speculative risk assessment.

## When to Use

- Before starting a significant project or feature
- Before a launch or major release
- Before committing to an architecture decision
- When the user asks "what could go wrong?" or wants risk analysis
- Sprint-level: compressed version for sprint planning

## When NOT to Use

- Trivial bug fixes or well-scoped small changes
- After the fact (use a post-mortem instead)
- When the user wants to brainstorm what to build (use brainstorming skill)

## Core Mechanism

**Prospective hindsight**: "The project has failed" (certainty) unlocks deeper analysis than "the project might fail" (speculation). The brain shifts from defending a plan to explaining an outcome.

---

<process>

## Phase 1: Gather Context (2 min)

Before spawning agents, understand what we're pre-morteming.

**If context is unclear, ask ONE question:**
"What are we pre-morteming? Give me: (a) the project/feature name, (b) a 1-3 sentence description, and (c) the timeline."

**If context exists** (from a plan, CLAUDE.md, or conversation), summarize it in 2-3 sentences and confirm with the user.

**Gather supporting context by reading:**
- Any existing plan or spec document
- CLAUDE.md project description
- Recent git log for project state
- Key architecture files if relevant

**Compose the scenario briefing** — this is the emotional hook that all agents receive:

```
PROJECT: [name]
DESCRIPTION: [what it does, who it's for]
TIMELINE: [when it ships]
STAKES: [what's riding on it — users, revenue, reputation, etc.]

THE SCENARIO: It's [timeline + buffer]. The [project] launched and it was a disaster.
[Stakeholder] called an emergency meeting. Users are [angry/confused/churning].
The team is demoralized. Everyone's asking "how did we miss this?"

Your job: explain what went wrong.
```

Tailor the scenario to feel real and specific to the project. Generic scenarios produce generic answers.

## Phase 2: Silent Individual Writing — Multi-Agent Fan-Out

This is the heart of the technique. Spawn **5-6 agents in parallel**, each with a different failure-finding mandate. The mandate matters more than the persona — tell each agent what SUCCESS looks like for their role.

### Environment Detection

First, detect what LLM tools are available. Run:

```bash
bash ${SKILL_DIR}/scripts/detect-llms.sh
```

This probes for: `llm`, `ask-gemini`, `gemini`, `ask-copilot`, `gh copilot`, `codex`, `ask-cerebras`, `ask-zai`, `ollama`, and deduplicates by model family.

**Three execution modes based on what's available:**

| Available Tools | Mode | Strategy |
|----------------|------|----------|
| 2+ external LLMs | **Full diversity** | Claude agents + external LLMs for maximum architectural divergence |
| 1 external LLM | **Hybrid** | Claude agents + one external for some divergence |
| None | **Claude-only** | All 6 roles as Claude Agent subagents with strongly differentiated prompts |

Heterogeneous model architectures produce better divergence than the same model with different prompts. But Claude-only still works — the differentiation comes from the mandates, not the models.

### Agent Roster

Each agent receives the same scenario briefing but a unique mandate:

| Role | Mandate | Failure Categories | Preferred Model |
|------|---------|-------------------|----------------|
| **The Saboteur** | "Find every technical way this could break, fail silently, or degrade. You succeed when you identify failures others would dismiss as unlikely." | Architecture, scaling, integration, data, performance | Claude (Agent) — needs codebase access |
| **The Customer** | "You are the end user. This launched and you hate it. Explain why — what's confusing, broken, or missing? You succeed when you articulate frustrations the builders would never feel." | UX, adoption, onboarding, missing features, wrong assumptions | External LLM preferred (fresh eyes) |
| **The Accountant** | "Find every way this costs more than expected — in money, time, maintenance burden, tech debt, or opportunity cost. You succeed when you surface hidden costs the team is ignoring." | Budget, timeline, maintenance, dependencies, operational overhead | Any |
| **The Pessimist** | "Assume the worst about every assumption in this plan. External dependencies will fail, timelines will slip, requirements will change. What dominoes fall? You succeed when you map cascading failures." | External risks, dependencies, scope creep, organizational chaos | Any |
| **The Historian** | "Search the codebase, git history, and any docs for evidence of past failures, technical debt, or patterns that suggest this project will hit the same walls." | Repeated mistakes, known debt, fragile areas | Claude (Agent) — needs codebase access |
| **The Newcomer** | "You've never seen this project before today. Read the description and point out everything that's unclear, assumed, or hand-waved. You succeed when you find the gaps everyone else is too close to see." | Assumptions, unclear requirements, knowledge silos | External LLM preferred (genuinely naive) |

### Prompt Template for Each Agent

```
=== PROJECT PRE-MORTEM ===

[Scenario briefing from Phase 1]

YOUR MANDATE: [mandate from roster]

FAILURE CATEGORIES to consider: [categories from roster]

INSTRUCTIONS:
1. The failure is CERTAIN — it already happened. Do not question this.
2. Write 5-8 specific, concrete reasons why it failed.
3. For each reason:
   - State what went wrong (one sentence)
   - Explain the chain of events that led to it (2-3 sentences)
   - Rate: likelihood (high/medium/low) × impact (catastrophic/major/minor)
4. Be specific to THIS project, not generic risks.
5. Uncomfortable truths are the whole point. Hold nothing back.
6. End with: "The one failure nobody wants to talk about: [your most uncomfortable prediction]"

FORMAT your response as a numbered list. No preamble, no hedging.
```

### Execution: Full Diversity Mode (external LLMs available)

Use the fan-out script for external agents, plus Claude Agent tool for Saboteur and Historian:

```bash
# Write scenario to temp file
echo "[scenario briefing]" > /tmp/pre-mortem-scenario.txt

# Run external agents in parallel (handles detection + assignment)
bash ${SKILL_DIR}/scripts/fan-out.sh /tmp/pre-mortem-scenario.txt /tmp/pre-mortem-output/
```

Simultaneously spawn Claude agents via Agent tool:
```
Agent(subagent_type="general-purpose", prompt="[saboteur prompt + instruction to read codebase]")
Agent(subagent_type="general-purpose", prompt="[historian prompt + instruction to search git/docs]")
```

**All calls in ONE message** for true parallelism.

### Execution: Claude-Only Mode (no external LLMs)

Spawn **all 6 roles as separate Claude Agent subagents** in a single message. To maximize divergence when using the same model:

1. **Vary the cognitive framing** — each agent gets a different thinking style:
   - Saboteur: "Think like a chaos engineer. What breaks under load, at scale, at 3am?"
   - Customer: "Think like someone who just downloaded this and has 30 seconds of patience."
   - Accountant: "Think like a CFO reviewing a project that's over budget. Every dollar counts."
   - Pessimist: "Think like Murphy's Law personified. Everything that can go wrong, will."
   - Historian: "Think like a detective. Search the codebase for evidence of past problems." (give codebase access)
   - Newcomer: "Think like a new hire on day one. What's confusing? What's undocumented?"

2. **Use different Agent model hints** where possible:
   - Saboteur, Historian: `model: "opus"` (deep analysis, codebase access)
   - Customer, Newcomer: `model: "sonnet"` (faster, different perspective)
   - Accountant, Pessimist: `model: "haiku"` (constrained, forces prioritization)

3. **Mandate independence** — each agent prompt must include: "Do NOT try to be balanced. Argue strongly from your assigned position. The synthesis step handles balance."

**If an external AI or subagent fails**, note it and continue — 4+ perspectives is still valuable.

## Phase 3: Round-Robin Synthesis

Once all agents have responded, run a **cross-pollination round**. This mimics Klein's round-robin where team members hear each other's ideas and add what was missed.

Use Claude (the strongest available model) to synthesize:

```
You are the pre-mortem facilitator. Six team members independently identified failure modes
for this project:

=== THE SABOTEUR (Technical) ===
[paste output]

=== THE CUSTOMER (User Experience) ===
[paste output]

=== THE ACCOUNTANT (Cost & Timeline) ===
[paste output]

=== THE PESSIMIST (External & Dependencies) ===
[paste output]

=== THE HISTORIAN (Past Patterns) ===
[paste output]

=== THE NEWCOMER (Assumptions & Gaps) ===
[paste output]

YOUR TASK:
1. DEDUPLICATE: Merge overlapping concerns into single items.
2. CROSS-POLLINATE: Identify failure chains that span multiple perspectives
   (e.g., a technical risk that causes a user experience disaster that causes budget overrun).
3. RANK by (likelihood × impact). Use a 2x2 matrix:
   - 🔴 HIGH likelihood × HIGH impact = Must address before proceeding
   - 🟠 HIGH likelihood × LOW impact OR LOW likelihood × HIGH impact = Plan mitigation
   - 🟡 LOW likelihood × LOW impact = Acknowledge and monitor
4. For EACH 🔴 and 🟠 risk, propose a CONCRETE mitigation:
   - What specific action prevents or reduces this risk?
   - Who should own it? (role, not person name)
   - When should it be done? (before X milestone)
5. OUTPUT FORMAT below.
```

## Phase 4: Present Results

Present the final pre-mortem report to the user in this format:

```markdown
# Pre-Mortem: [Project Name]
_"It's [future date]. [Project] launched and failed. Here's what went wrong."_

## 🔴 Critical Risks (Must Address)

### 1. [Risk Title]
**What goes wrong:** [one sentence]
**Chain of events:** [how it unfolds]
**Likelihood:** High | **Impact:** Catastrophic/Major
**Sources:** Saboteur, Customer (agreement = high confidence)
**Mitigation:** [specific action] → Owner: [role] → By: [milestone]

### 2. ...

## 🟠 Significant Risks (Plan Mitigation)

### 3. [Risk Title]
...

## 🟡 Watch List (Monitor)

- [Risk]: [one-line description]
- ...

## Cross-Cutting Themes
[2-3 sentences about failure patterns that appeared across multiple agents]

## The Uncomfortable Truth
[The single most important thing nobody wants to hear, synthesized from all agents' "uncomfortable predictions"]

## Recommended Next Steps
1. [ ] [Action item with owner and deadline]
2. [ ] ...
3. [ ] ...
```

## Phase 5: User Discussion

After presenting, ask:

> "Which of these feel most real to you? Anything missing that your gut tells you about?
> Want me to deep-dive any specific risk, or shall we turn the mitigations into plan items?"

If the user identifies additional risks, add them to the report. If they want to proceed, offer to:
- Add mitigations as tasks/beads
- Update an existing plan with risk-aware adjustments
- Save the report to Obsidian for reference

</process>

<anti_patterns>

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Use generic risks ("the timeline might slip") | Be specific to THIS project ("the Ollama integration has no timeout handling and will hang the queue") |
| Let agents be polite or hedging | Mandate uncomfortable honesty — that's the whole point |
| Skip the emotional scenario setup | The certainty framing is what activates prospective hindsight |
| Run agents sequentially | Parallel execution — all 6 in one message |
| Present a flat list of risks | Rank by likelihood × impact, group by severity |
| Identify risks without mitigations | Every 🔴 and 🟠 gets a concrete action |
| Use the same prompt style for all agents | Vary cognitive framing, model hints, and mandates for divergence |
| Ask "what could go wrong?" | Say "it failed — what went wrong?" (certainty, not speculation) |

</anti_patterns>

<success_criteria>

Pre-mortem is complete when:
- [ ] 5+ agents contributed independent failure analyses
- [ ] Results are deduplicated, cross-pollinated, and ranked
- [ ] Every critical/significant risk has a concrete mitigation with owner and timing
- [ ] The "uncomfortable truth" has been surfaced
- [ ] User has reviewed and added any gut-feel risks
- [ ] Next steps are clear (plan updates, tasks, or documented for reference)

</success_criteria>
