---
name: trust-audit
description: This skill should be used when evaluating whether a product, feature, onboarding flow, permission request, billing model, privacy posture, or file/data mutation behavior will feel trustworthy, creepy, deceptive, risky, or surprisingly unsafe to users. It is especially useful for AI products, utilities, menu bar apps, billing changes, and launch readiness reviews.
---

# Trust Audit

Use this skill to answer the question beneath many launch failures: **“Will a normal user feel safe, respected, and in control?”**

A trust audit is not a security review. It is a perception-and-reality review of the places where users feel:
- watched
- tricked
- over-charged
- surprised by file or data changes
- unsure what the product is really doing
- trapped when something goes wrong

## When to Use

Use this skill when reviewing:
- onboarding or first-run flows
- permission prompts and explanations
- privacy and AI data flows
- billing, credits, trials, renewals, or BYOK setups
- features that rename, move, delete, sync, upload, or otherwise mutate user data
- products where “creepy”, “shady”, or “I don’t trust it” would be fatal

## Core Principle

Trust breaks when there is a mismatch between:
1. **what the user thinks will happen**
2. **what actually happens**
3. **how reversible and well-explained it feels**

Audit both the reality and the vibe. A technically defensible flow can still feel shady.

<process>

## Step 1: Gather the trust surface

Read enough context to map:
- target user
- product promise
- first-run flow
- permissions requested
- what data leaves the device
- what files or records get changed
- billing or credit mechanics
- failure and recovery paths

Then summarize in 5-10 bullets:
- what the user believes they are agreeing to
- what the product actually does
- where a mismatch might exist

## Step 2: Inspect the five trust surfaces

Evaluate each of these explicitly.

### 1. Consent and comprehension
Ask:
- Does the user understand what they are enabling?
- Is important information explained **before** the scary system prompt or pricing moment?
- Is consent meaningful, or buried behind momentum?

### 2. Data and privacy reality
Ask:
- What leaves the machine?
- What is stored, for how long, and by whom?
- Is there any “surprise cloud” moment?
- Would a privacy-sensitive user feel misled if they learned the full data path later?

### 3. File and state safety
Ask:
- Does the product modify user files or important state?
- Could it break organization, aliases, scripts, expectations, or downstream workflows?
- Is there a visible, believable undo or recovery story?

### 4. Billing and fairness
Ask:
- Could a user reasonably feel tricked on price, credits, quotas, renewals, or provider costs?
- Is the distinction between app purchase, subscription, AI usage, and BYOK painfully clear?
- Would a user say “wait, I thought this was included”?

### 5. Degraded-mode honesty
Ask:
- When the product is partially broken, does it look healthy anyway?
- Does the user understand whether it is paused, misconfigured, rate-limited, offline, blocked, or waiting?
- Could the product silently fail in a way that makes the user blame themselves?

## Step 3: Generate trust failures

Produce 6-12 concrete trust risks. For each, include:
- **Trust failure** — one sentence
- **What the user expected**
- **What actually happens**
- **Why it feels bad** — creepy, deceptive, careless, destructive, unfair, etc.
- **Likely reaction** — support email, uninstall, refund, bad review, internal IT rejection, etc.
- **Severity** — low/medium/high
- **Trust fracture type** — consent / privacy / pricing / file safety / silent failure / recovery
- **Repair move** — the most direct product or copy change

## Step 4: Distinguish vibes from actual danger

Split findings into:
- **Trust theater** — looks scary but is mostly messaging / framing
- **Real trust hazard** — real risk, real surprise, or real damage

Do not flatten them together.

## Step 5: Present the audit

Use this format:

```markdown
# Trust Audit: [Product / Feature]

## Executive Read
- Biggest trust risk:
- Most likely “creepy” interpretation:
- Most likely “I got tricked” interpretation:
- Most dangerous file/data surprise:

## Trust Surface Map
- Consent:
- Data flow:
- File/state mutation:
- Billing:
- Degraded-mode honesty:

## High-Risk Trust Failures

### 1. [Title]
**Trust failure:**
**What the user expected:**
**What actually happens:**
**Why this feels bad:**
**Likely reaction:**
**Type:**
**Repair move:**

## Medium-Risk Trust Failures
...

## Trust Theater vs Real Hazard
- Trust theater:
- Real hazard:

## Copy / UX Fixes to Make Immediately
1. [ ]
2. [ ]
3. [ ]

## The Sentence Users Might Say
> “[one-sentence trust-damaging story]”
```

## Success Criteria

The audit is complete when it identifies:
- what the user thinks is happening
- where that belief is wrong or incomplete
- which mismatch will feel worst
- which fix most increases user trust fastest

</process>
