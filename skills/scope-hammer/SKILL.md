---
name: scope-hammer
description: Ruthlessly compress brainstorm output into a shippable MVP — classify ideas as DELETE / MOCK / ALREADY EXISTS / SHIP and surface the shortest path to launch.
display_name: "Scope Hammer"
brand_color: "#F97316"
local_only: false
group: "Better Products"
usage: "/scope-hammer:run"
summary: "Compress brainstorm output into MVP scope with DELETE/MOCK/ALREADY EXISTS/SHIP classification"
default_prompt: "Apply the scope hammer to this brainstorm or feature list. Classify everything as DELETE, MOCK, ALREADY EXISTS, or SHIP. Give me the shortest path to a launchable MVP."
---

# Scope Hammer

The brainstorm produced 30 ideas. The scope hammer asks: which 5 do you actually need to ship?

Companion to `wide-open-brainstorm`. Where brainstorm goes wide, scope-hammer goes ruthless.

## When to Use

- After a brainstorm session
- When a feature list has grown unmanageable
- When the team is debating too many options and needs a forcing function
- When "MVP" has quietly expanded to "everything"
- When someone asks "what's the minimum we need to launch?"

## When NOT to Use

- Before brainstorming (you need ideas before you can kill them)
- When the goal is exhaustive requirements gathering
- When stakeholders need to see all options (use brainstorm output; this skill produces the answer)

---

<process>

## Phase 1: Load the Input

Accept one of:
- The output of a wide-open-brainstorm session (pasted or from context)
- A feature list, backlog, or spec
- A verbal description ("we're thinking of building X with features A, B, C, D, E...")

If the input is vague, ask: "Give me the list of features or ideas you want me to scope."

Extract the **core goal** first: "What does this product need to do to be worth using on day one?"

## Phase 2: Classify Each Item

For every idea or feature in the input, apply exactly one classification:

### Classifications

**DELETE** — This will never be in the product. Reasons:
- Adds complexity without adding core value
- Solves a problem users don't have yet
- Duplicates something else in the list
- Is actually a distraction from the core loop
- Would require significant infrastructure not justified by usage

**MOCK** — The user thinks they need this, but a fake version will do for launch. Examples:
- Manual process behind a button (instead of automation)
- Static content instead of dynamic CMS
- CSV import instead of API integration
- Human review instead of AI (at first)
- Hardcoded list instead of user-configured settings

**ALREADY EXISTS** — A standard library, tool, or service already does this. Don't build it. Examples:
- Auth → use an auth provider
- Payments → use Stripe
- Email → use Resend/Postmark
- Analytics → use Plausible/PostHog
- Search → use Algolia (or Postgres full-text for small scale)

**SHIP** — This is core. Users cannot get value without it. Ship this first.

### Classification Rules

- Everything starts as DELETE. Earn its way to SHIP.
- MOCK is underused. Push more items to MOCK.
- If you can't describe why a SHIP item directly serves day-one user value, reconsider.
- Maximum 5 SHIP items for an MVP. If you have 8, go back and mock or delete 3.

## Phase 3: Parallel Ruthlessness Check

Launch a second analysis as a subagent with the mandate: "Here is the proposed MVP scope (SHIP items only). Challenge it. Find: (1) SHIP items that could be MOCKed for launch without users noticing, (2) SHIP items that are actually implicit in other SHIP items, (3) anything that will block day-one launch but isn't in the SHIP list."

Incorporate findings into the final output.

## Phase 4: MVP Specification

Produce:

### The Core Loop
One paragraph: what does the user do from first launch to first value? This is the path the MVP must make possible. Everything else is optional.

### SHIP Items (numbered, max 5)
For each: what it does, why it's required (not just nice-to-have), estimated complexity (S/M/L/XL).

### MOCK Items (numbered)
For each: what we'd fake, how we'd fake it, when we'd replace it with real implementation.

### ALREADY EXISTS Items (numbered)
For each: which tool/service handles it, link if obvious.

### DELETE Items (brief list)
Just names — no need to justify each one in detail. "These don't make the cut for v1."

### Launch Sequence Estimate
Rough order of implementation: what must be built first (blocking), what can be built in parallel, what can be built post-launch.

### The Honest Summary
One paragraph: "To launch this, you need to build X, Y, and Z. Everything else is a future version. The first version can be live in [rough estimate] if you start with [first thing]."

</process>
