---
name: run
description: This skill should be used when designing, implementing, or running parallel isolated app testing for desktop apps, menu bar apps, local tools, or other products with shared local state. It is especially useful when multiple app instances might collide on defaults, app support paths, temp files, watched folders, notifications, launch agents, permissions, or other machine-local side effects.
---

# Parallel Isolated App Testing

Use this skill to turn “let’s run multiple copies in parallel” from a flaky little chaos goblin into a repeatable testing system.

This skill is for situations like:
- desktop or menu bar apps with local state
- GUI apps where parallel QA would be valuable
- apps that need per-instance defaults, files, fixtures, or logs
- release testing that should split across multiple lanes or agents
- products where naive multi-instance launching would cause collisions, false failures, or state pollution

## When to Use

Use this skill when:
- a user wants parallel app testing
- a project needs isolated QA lanes
- multiple agents should exercise different app scenarios concurrently
- an app needs a test mode, fixture mode, or per-instance state roots
- there is a risk of collision across local state or OS integrations

Use it before blindly launching multiple copies of an app that share:
- preferences / `UserDefaults`
- app support or cache directories
- temporary exports or generated files
- watched folders
- notifications
- launch-at-login helpers
- update channels
- permission-dependent UI flows
- singleton / duplicate-instance guards

## Core Principle

Parallel app testing is only useful when failures mean something.

If two instances can silently interfere with each other, the result is not parallel testing. It is a theatrical performance by raccoons.

The goal is to create **isolated, attributable, repeatable test lanes** where each instance has:
- its own state
- its own inputs
- its own logs and artifacts
- a clear scenario assignment
- a clear teardown path

## Quick Start

When asked to set up parallel app testing:

1. Identify all shared-state and side-effect collision surfaces.
2. Decide whether parallel instances are safe at all.
3. If not safe, define the required app test-mode seams.
4. Implement or document the per-instance launch contract.
5. Create a helper launcher that defaults to safe dry-run behavior.
6. Add one or more fixture profiles that land the app in useful states.
7. Split testing into non-colliding lanes.
8. Capture logs, DB state, screenshots, and findings per lane.
9. File follow-up issues for missing seams or blockers.

For a deeper checklist, load [references/collision-checklist.md](references/collision-checklist.md).
For a repeatable execution playbook, load [references/parallel-playbook.md](references/parallel-playbook.md).
For launcher design, load [references/launcher-template.md](references/launcher-template.md).
For fixture design, load [references/fixture-design.md](references/fixture-design.md).
For common failure interpretation, load [references/troubleshooting.md](references/troubleshooting.md).

<process>

## Step 1: Decide whether parallel copies make sense

Do not assume that parallel copies are a good idea just because they sound efficient.

First classify the target app:
- **Safe now** — already supports isolated state roots and suppressible side effects
- **Safe with light seams** — needs a small test mode or launcher contract
- **Unsafe for parallel UI** — deep singleton assumptions, shared global mutation, or OS integrations make parallel copies misleading

If unsafe, say so directly and recommend:
- one real UI instance
- plus parallel unit/integration/fake-provider lanes instead

## Step 2: Map collision surfaces

Read the app code and identify all places where multiple instances would interfere.

At minimum inspect:
- preferences storage
- app support / cache / temp paths
- key stores and credentials
- file watchers and monitored folders
- notification delivery
- launch agents / login items / auto-start helpers
- auto-updaters and distribution integrations
- duplicate-instance guards
- first-run / onboarding state
- diagnostics / export output paths
- local databases, lock files, queues, sockets, or named pipes

Use the checklist in [references/collision-checklist.md](references/collision-checklist.md).

Produce a short table:
- collision surface
- current behavior
- risk level
- required isolation or suppression

## Step 3: Define the isolated launch contract

Create a standard per-instance contract.

At minimum, each isolated instance should be able to specify:
- instance ID
- defaults suite name or equivalent
- app state root
- app-support root
- temp root
- screenshot / input fixture root when relevant
- log file path or discoverable log location
- optional fixture profile

Prefer explicit launch arguments and matching environment variables.

A strong contract usually includes flags like:
- `--ui-test-mode`
- `--instance-id <id>`
- `--state-root <path>`
- `--defaults-suite <suite>`
- `--fixture <profile>`

Adjust names to the project, but keep the pattern consistent.

## Step 4: Suppress unsafe side effects in test mode

In isolated test mode, suppress or stub side effects that should not fire during QA.

Typical examples:
- launch-at-login registration
- updater startup
- notification authorization prompts or delivery
- migration helpers that touch shared machine state
- account import from global user secrets
- singleton enforcement that prevents test copies
- analytics or telemetry not needed for local smoke

Do not suppress behavior that the test lane is explicitly trying to verify unless the lane is clearly marked as a stubbed lane.

## Step 5: Add fixture profiles

A parallel-testing system is not complete if every instance lands in useless onboarding.

Add fixture profiles that preseed the minimum state needed for useful test lanes. Use [references/fixture-design.md](references/fixture-design.md) to keep fixtures narrow, deterministic, and documented.

Common profiles:
- `smoke-ready` — bypass onboarding, point to isolated input folder, disable noisy prompts
- `misconfigured-auth` — force auth error state
- `paused` — start in paused mode
- `history-seeded` — preload recent items for History/diagnostics smoke
- `feedback-ready` — support summary and exports can be exercised without first-run blockers
- `fake-provider` — deterministic processing without live network/model dependencies

Document exactly what each fixture seeds and what it does *not* seed.

## Step 6: Create a helper launcher

Always prefer a helper script over expecting humans or agents to hand-type long launch commands. Use [references/launcher-template.md](references/launcher-template.md) as the starting shape.

The helper should:
- default to dry run
- print resolved paths and the exact launch command
- choose the right build or binary
- avoid stale build selection when possible
- support background launch and kill flows
- create required directories
- apply fixture seeding before launch when needed
- write or expose a per-instance log path

A good helper removes 80% of “whoops, wrong build / wrong suite / wrong root” failures.

## Step 7: Split into non-colliding lanes

Assign each lane a distinct purpose.

Good parallel lane splits:
- feedback / diagnostics export lane
- preferences / history / about/help lane
- onboarding / first-run lane
- file-watcher / queue / rename lane
- error-state recovery lane
- trust / permissions lane

For each lane, define:
- instance name
- fixture profile
- input root
- scenario goal
- artifact destinations
- teardown command

Do not let lanes share input folders, DBs, temp roots, or defaults suites.

## Step 8: Validate isolation before trusting results

Before deeper QA, prove that isolation actually works.

At minimum verify:
- multiple instances can launch concurrently
- each instance creates separate state roots
- each instance writes to its own DB/log/temp locations
- watched folders are distinct
- one instance’s actions do not appear in the other’s history or logs
- teardown cleanly removes or stops only the intended instance

If isolation is not proven, stop calling the setup “parallel-safe.”

## Step 9: Run smoke scenarios and collect artifacts

For each lane, collect:
- launch command
- PID or instance identifier
- fixture profile used
- log excerpts
- relevant DB/file evidence
- screenshots if possible
- failures, blockers, and suspected missing seams

If deeper UI automation is blocked by OS permissions, say so explicitly instead of pretending the lane was fully exercised. Use [references/troubleshooting.md](references/troubleshooting.md) to interpret common blockers honestly.

## Step 10: Close the loop

At the end, produce:
- what parallel testing can already verify
- what remains blocked
- which fixture/seam/tooling gaps are next highest leverage
- follow-up issues for each meaningful blocker

Use this format:

```markdown
# Parallel Isolated App Testing: [Product]

## Executive Read
- Parallel-safe today:
- Biggest current blocker:
- Highest-leverage next seam:
- Recommended lane split:

## Isolation Contract
- Instance ID:
- State root:
- Defaults suite:
- Fixture profiles:
- Helper script:

## Collision Surfaces
| Surface | Risk | Current Handling | Remaining Gap |
|---|---|---|---|

## Validation
- [ ] Two or more instances launched concurrently
- [ ] Separate state roots confirmed
- [ ] Separate logs confirmed
- [ ] Separate DB/history confirmed
- [ ] No cross-talk observed

## Lane Results
### Lane A — [name]
- Fixture:
- Goal:
- Result:
- Artifacts:
- Blockers:

### Lane B — [name]
- Fixture:
- Goal:
- Result:
- Artifacts:
- Blockers:

## Follow-Up Work
1. [ ]
2. [ ]
3. [ ]
```

## Reusable Patterns

Keep these patterns consistent across projects:

### 1. Isolation contract pattern
- one instance name
- one state root
- one defaults suite
- one fixture profile
- one log file

### 2. Dry-run-first launcher pattern
Never make the default action mutate the machine.
Show the command first. Launch only with an explicit live flag.

### 3. Fixture ladder pattern
Start with `smoke-ready`, then add narrower fixtures only when a real testing need appears.
Do not create a giant omnifixture that tries to represent the entire app.

### 4. Honest blocker reporting pattern
If accessibility, screen capture, backend availability, or another dependency blocks deeper QA, report that as a blocker rather than inventing confidence.

## Concrete Mini Examples

### Example: Menu bar app with watched folders
Needed seams:
- duplicate-instance bypass
- defaults suite override
- app-support override
- temp root override
- watched-folder fixture root
- notification suppression

Likely first fixtures:
- `smoke-ready`
- `fake-provider`
- `feedback-ready`

### Example: Desktop app with export bundles
Needed seams:
- temp/export root override
- stable per-instance logs
- fixture for seeded recent history

Likely parallel lanes:
- exports / diagnostics lane
- history / filters lane
- settings / help lane

## Success Criteria

This work is successful when:
- the app’s parallel-testing safety is stated honestly
- shared-state collisions are mapped, not hand-waved
- isolated launches are easy and repeatable
- at least one useful fixture profile exists
- parallel lanes produce attributable results
- blockers are converted into crisp follow-up work

</process>
