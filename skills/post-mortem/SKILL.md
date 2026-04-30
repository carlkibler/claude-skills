---
name: post-mortem
description: Analyze a real failure — reconstruct what happened, find root cause, extract learnings, and feed them back into the skill collection to prevent recurrence.
display_name: "Post-Mortem"
brand_color: "#DC2626"
local_only: false
group: "Better Products"
usage: "/post-mortem:run"
summary: "Blameless post-mortem that feeds learnings back into your skill collection"
default_prompt: "Run a blameless post-mortem on what just broke. Reconstruct the timeline, find root cause, extract learnings, and tell me what to add to my pre-mortem or support-storm skills."
---

# Post-Mortem

The mirror of pre-mortem. Used AFTER something broke, not before. The goal isn't blame — it's extraction: what can we learn, and where does that learning live so the next project benefits?

## When to Use

- After a launch that generated unexpected support volume
- After a bug that reached production users
- After a process failure (deploy, migration, onboarding flow breakdown)
- After a trust incident (user data exposed, billing error, unintended mutation)
- After a failed launch or major negative user reaction

## When NOT to Use

- Before launch (use pre-mortem)
- For bugs that were caught before they hit users (those go straight to fixes)
- Blame-first analysis (a post-mortem that starts with "who screwed up" isn't a post-mortem)

---

<process>

## Phase 1: Gather the Incident Facts

Ask (or infer from context):

1. **What broke** — one sentence description of the failure
2. **When** — approximate timeline (when did it start, when was it noticed, when was it resolved)
3. **Who was affected** — which users, how many, what was their experience
4. **How it was discovered** — user report, monitoring alert, internal discovery, social media
5. **What was the fix** — what resolved it

If git log, bug reports, Slack excerpts, or error logs are available — read them.

## Phase 2: Reconstruct the Timeline

Build a factual timeline. Format:

```
[TIME] [EVENT]
T-48h: Feature deployed to production
T-24h: First user report (ignored as edge case)
T-0: Support volume spike — 15 tickets in 2 hours
T+2h: Root cause identified
T+4h: Fix deployed
T+6h: Support tickets resolved
```

## Phase 3: Root Cause Analysis (5 Whys)

Apply the 5 Whys technique:

1. Why did this happen? [immediate cause]
2. Why did [cause 1] happen? [contributing factor]
3. Why did [factor 2] exist? [systemic reason]
4. Why did [reason 3] go unaddressed? [process gap]
5. Why did [gap 4] persist? [root cause]

State the root cause explicitly: "Root cause: [X]"

Also classify the failure mode:
- **Missing check** — we didn't verify something we should have
- **Wrong assumption** — we assumed X was true; it wasn't
- **Process gap** — no process existed for this scenario
- **Communication failure** — the right person didn't know the right thing
- **Known risk accepted** — we knew this could happen, chose to proceed

## Phase 4: Multi-Perspective Analysis

Launch 2 parallel subagents with different lenses:

**Subagent 1 — User Impact Analyst**
Focus on the user experience of the failure. What did affected users actually experience? What did they feel? What did they do (contact support, churn, post publicly, complain to friends)? What was the trust damage? How long does it take them to fully recover trust?

**Subagent 2 — Systems Analyst**
Focus on the technical and process failure. What signals were available before the failure that were ignored? Where did detection fail? Where did response fail? What would have caught this earlier?

## Phase 5: Learnings Extraction

For each finding, decide where it should live:

| Finding | Route to |
|---------|----------|
| "We didn't check X before launch" | Add to pre-mortem checklist |
| "Users complained about Y" | Add to support-storm simulation list |
| "Permission Z surprised users" | Add to trust-audit surface list |
| "Onboarding step W caused confusion" | Add to first-contact red-team |
| "Decision about V had no documented rationale" | Create decision-log entry |

### Feed Learnings Back (IMPORTANT)

If any of the above skills are installed, offer to update them:

For each learning that routes to a skill:
1. State the learning explicitly
2. State which skill should incorporate it
3. Offer to show the specific addition to make to that skill's SKILL.md

Example:
```
LEARNING: Users didn't realize the app was scanning their contacts until they saw a system permission dialog.
→ Add to trust-audit: "Check: does the app request contact/location/camera access? Is the reason communicated before the system dialog?"
```

## Phase 6: Action Items

Produce a numbered list of concrete actions:
- [ ] Immediate fixes (within 24h)
- [ ] Short-term improvements (within 2 weeks)
- [ ] Process changes (ongoing)

Each action: who, what, by when (if known).

## Phase 7: Report

```
## Post-Mortem: [Incident Name]

**Date of incident:** [date]
**Duration:** [time from start to resolution]
**User impact:** [count or estimate]
**Severity:** Critical / High / Medium / Low

### Timeline
[reconstructed timeline]

### Root Cause
[root cause statement]

### Contributing Factors
[list]

### What Went Well
[what worked during the response]

### Learnings
[learnings with skill routing]

### Action Items
[numbered list]
```

</process>
