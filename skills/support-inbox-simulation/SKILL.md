---
name: support-inbox-simulation
description: This skill should be used when predicting what support emails, refund requests, app reviews, bug reports, and confused user complaints a product launch or feature change will generate. It is especially useful for launch readiness, onboarding review, diagnosing support burden, and finding the gaps between what builders think is obvious and what users will actually report.
---

# Support Inbox Simulation

Use this skill to simulate the messy human exhaust of a launch: vague bug reports, annoyed reviews, refund requests, and exhausted follow-up threads.

This skill is for answering:
- What will users actually say when this breaks?
- Which failures become expensive to diagnose?
- Which support issues compress into the public story of the product?

## When to Use

Use this skill when reviewing:
- launch readiness
- onboarding and activation
- support tooling and diagnostics
- pricing or packaging changes
- status and failure messaging
- any feature likely to produce “not working” tickets

## Core Principle

A support burden is not just the number of issues. It is:
- how vague the first report is
- how many rounds it takes to diagnose
- how emotionally charged the issue feels
- whether the same confusion repeats across users

<process>

## Step 1: Gather the likely support context

Read enough context to understand:
- target user sophistication
- launch channel
- product promise
- likely failure points
- what diagnostics/support summary currently exist
- what support actions are currently easy vs annoying

Then list:
- the 5-10 most likely reasons someone would contact support
- the 3-5 most likely reasons they would not contact support and instead churn, refund, or complain publicly

## Step 2: Simulate the inbox

Generate a realistic mix of artifacts:
- 4-8 support emails or chat messages
- 3-5 App Store / public reviews
- 2-4 refund requests or cancellation notes
- 2-3 “this is probably user error but still your problem” complaints

Make them feel real:
- incomplete facts
- emotional language
- wrong assumptions
- screenshots described badly
- contradictory details
- users blaming the product, themselves, or the platform

## Step 3: Triage each artifact

For each simulated item, add:
- **What really happened**
- **Why the user described it this way**
- **What facts are missing for diagnosis**
- **How many back-and-forths it would probably take**
- **How fixable the support burden is** — product fix / copy fix / diagnostics fix / docs fix / unavoidable

## Step 4: Find the support sinkholes

Identify the issues that are worst because they are:
- frequent but vague
- rare but emotionally explosive
- difficult to distinguish from user error
- impossible to resolve without diagnostics the product does not collect
- repetitive enough to become founder-tax

## Step 5: Present the simulation

Use this format:

```markdown
# Support Inbox Simulation: [Product / Feature]

## Executive Read
- Most likely support subject line:
- Most expensive recurring ticket:
- Most likely refund reason:
- Public review story most likely to spread:

## Simulated Inbox

### Support Emails
#### 1. Subject: ...
[message]
**What really happened:**
**Missing facts:**
**Estimated support rounds:**
**Best fix type:**

### Public Reviews
#### 1. ★★☆☆☆ “...”
[review]
**Underlying issue:**
**What story this reinforces:**

### Refund / Cancellation Notes
...

## Support Sinkholes
- [Issue] — why it will eat time
- [Issue] — why diagnostics fail

## Highest-Leverage Support Fixes
1. [ ]
2. [ ]
3. [ ]

## Support Summary / Diagnostics Missing Today
- [missing field]
- [missing field]
- [missing field]
```

## Success Criteria

The simulation is successful when it makes support feel painfully concrete and identifies:
- what users will actually say
- what facts support will be missing
- which issues become founder-tax
- which single diagnostics or UX fix would cut the burden most

</process>
