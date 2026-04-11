---
name: first-run-red-team
description: This skill should be used when red-teaming a product’s onboarding, installation, activation, first-run, and first-success experience. It is especially useful for launch readiness, utilities, menu bar apps, permission-heavy software, AI products, and any workflow where one confusing first impression can cause immediate abandonment.
---

# First-Run Red Team

Use this skill to attack the first 5-15 minutes of the product experience.

A first-run red team is about finding where a new user:
- gets confused
- hesitates
- grants a permission without understanding it
- denies a permission and never recovers
- thinks the app is broken
- never reaches the promised “aha” moment

## When to Use

Use this skill when reviewing:
- install flow
- onboarding
- permission requests
- setup checklists
- first successful action
- first failure recovery
- menu bar or background apps where state is easy to miss

## Core Principle

The first-run experience fails when the product asks the user to do too much, trust too much, or infer too much before value is obvious.

<process>

## Step 1: Map the first-run path

Build a minute-by-minute path from:
- discovery / install
- launch
- first window or menu
- setup tasks
- permission prompts
- first success moment
- first screenshot / first sync / first alert / first rename / first whatever the product does
- first failure state and recovery

If there are multiple likely paths, audit the default path first.

## Step 2: Simulate multiple user mindsets

At minimum, simulate these personas:
- **In a hurry** — wants value in under 2 minutes
- **Skeptical** — suspicious of permissions, billing, AI, or privacy
- **Normal but inattentive** — will miss subtle text and icon changes
- **Slightly unlucky** — hits one bad edge case early

For each persona, walk the path step by step.

## Step 3: Find first-run failure points

Look for:
- unexplained permissions
- unclear prerequisites
- too many decisions too early
- jargon, hidden defaults, or settings that matter more than they look
- moments where the app appears idle or dead
- weak proof that setup succeeded
- confusing recovery after a denial, skip, or transient failure
- ways an early failure poisons the user’s mental model permanently

## Step 4: Score the friction

For each failure point, include:
- **Moment**
- **What the user is trying to do**
- **What blocks or confuses them**
- **Likely user interpretation**
- **Abandonment risk** — low/medium/high
- **Recovery quality** — good/weak/bad
- **Fastest fix** — product / copy / diagnostics / state visibility / defaults

## Step 5: Present the walkthrough

Use this format:

```markdown
# First-Run Red Team: [Product / Feature]

## Executive Read
- First-run step most likely to lose the user:
- Permission moment most likely to fail:
- Moment where the app most likely looks dead:
- Fastest improvement to lift activation:

## First-Run Timeline
1. [step]
2. [step]
3. [step]

## Failure Points

### 1. [Title]
**Moment:**
**User goal:**
**What goes wrong:**
**Likely interpretation:**
**Abandonment risk:**
**Recovery quality:**
**Fastest fix:**

## Persona Notes
### In a hurry
- ...
### Skeptical
- ...
### Normal but inattentive
- ...
### Slightly unlucky
- ...

## Activation Killers
- [issue]
- [issue]
- [issue]

## Highest-Leverage First-Run Fixes
1. [ ]
2. [ ]
3. [ ]
```

## Success Criteria

The red team is complete when it identifies:
- where the user is most likely to bail
- where the app most likely looks broken or suspicious
- where a denied permission or skipped step becomes unrecoverable
- the smallest changes that would materially improve activation

</process>
