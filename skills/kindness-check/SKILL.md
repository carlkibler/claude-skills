---
name: kindness-check
description: Review code, products, or features through four empathy lenses (user, machine, developer, support) to surface quality issues that pure technical review misses. Use when preparing for launch, after major features, or when something "works but feels wrong." Produces both positive and negative findings — celebrates what's kind and flags what's cruel.
---

# Empathy Audit

A structured review that asks: *who does this code serve, and how does it treat them?*

Technical reviews catch bugs. Empathy audits catch the things that make users uninstall, machines overheat, developers quit, and support people burn out. They also catch the things worth celebrating — the thoughtful defaults, the generous error messages, the code that's a pleasure to read.

## When to Use

- Before a launch, beta, or public release
- After completing a major feature or refactor
- When a product "works" but something feels off
- When support tickets are accumulating but tests are green
- Periodically on long-running products (quarterly health check)

## When NOT to Use

- Tiny bug fixes or single-line changes
- Pure infrastructure/CI changes with no user surface
- Early prototypes where the design is still fluid

---

<process>

## Phase 1: Scope and Context

Before reviewing, establish the review surface:

1. **Read project docs** — `CLAUDE.md`, README, architecture docs
2. **Identify the audience** — who uses this? what do they care about?
3. **Map the hot paths** — what code runs most often? what touches user files/data?
4. **Size the review** — pick the scope:

| Scope | What to review | Time |
|---|---|---|
| **Focused** | One feature or subsystem (3-8 files) | Quick |
| **Module** | A full module/layer (10-20 files) | Medium |
| **Full** | Entire codebase | Use multi-agent fan-out |

For a **full** audit, use the multi-agent approach in Phase 3. For focused/module, a single pass through all four lenses is fine.

## The Finding Format

Every finding — across all four lenses — follows the same chain: **situation → consequence → action**. This is what makes an empathy audit actionable instead of decorative.

```
### [Short title]
- **Lens:** User / Machine / Developer / Support
- **Type:** POSITIVE or NEGATIVE
- **Situation:** [A concrete scenario. Who is involved, what are they doing, what happens. 2-3 sentences written as a story, not a code description.]
- **Consequence:** [What the person or machine experiences as a result. Be emotionally precise for people — not "frustrated" but "confused and wondering if the app is broken." Be physically precise for machines — not "uses memory" but "grows by ~1KB per failure, never pruned, reaching tens of MB after months of uptime."]
- **Evidence:** [file:function or file:line — the specific code responsible]
- **Action:** [A specific, implementable change. Must be concrete enough that a developer could start working on it without asking a follow-up question. For positives: what to preserve and why.]
```

### What makes a good finding vs. a bad one

**Bad (vague symptom → vague fix):**
> "Silent failures could confuse users. Consider adding better error handling."

This is useless. What silent failure? Which user? What error handling?

**Good (concrete situation → clear consequence → specific action):**
> **Situation:** A user changes their macOS screenshot format to HEIC in System Settings. They take a screenshot. ScreenSage's watcher sees the new file, but `ImageProcessor.isSupportedImageFormat` rejects it because only PNG/JPG are supported. The file is silently skipped — no notification, no history entry, no log visible to the user.
>
> **Consequence:** The user waits, nothing happens, they assume the app is broken. They may try restarting, checking settings, or uninstalling — never realizing the format is the issue. This is the #1 "why doesn't it work?" support email waiting to happen.
>
> **Evidence:** `ImageProcessor.swift:106` — `isSupportedImageFormat` only accepts `["png", "jpg", "jpeg"]`
>
> **Action:** When a watched folder contains image files in unsupported formats, show a one-time notification: "ScreenSage saw a .heic screenshot but can only rename PNG and JPG files right now. You can change your screenshot format in System Settings > Screenshots." Log it to history as `skipped` with the reason.

Notice:
- The situation tells a story you can picture
- The consequence explains *why it matters*, not just *that it's bad*
- The evidence points to the exact code
- The action is specific enough to implement without further questions

## The Four Lenses

Each lens has a distinct perspective and examines different code. They are designed to find different things — resist the urge to merge them.

### Lens 1: User Empathy

**Perspective:** You are the person who installed this because it promised to solve a problem. You don't know or care how it works internally.

**What to examine:**
- Error messages — do they explain *why* and *what to do next*?
- Silent failures — does the app ever fail without telling the user?
- Defaults — safe for a first-time user, or optimized for the developer's setup?
- Waiting — are there "dead air" moments with no progress indicator?
- Destructive actions — do file mutations have clear confirmation and undo?
- Notifications — helpful or spammy? Present when critical or absent?
- Privacy — does the user know what data leaves their machine?
- Cognitive load — does the user need to understand internals to use it?

**What this lens catches that others miss:**
- The moment a user decides "this app is broken" (even when it isn't)
- The gap between what the product promises and what the experience delivers
- Settings that feel reasonable to the builder but reckless to the user
- Features that work but feel creepy, sloppy, or untrustworthy

<examples>

**Example positive finding:**
```
### Error messages guide users to fix the problem themselves
- Lens: User Empathy
- Type: POSITIVE
- Situation: A user's OpenRouter API key expires. The next screenshot triggers a 401. The app pauses automation and shows the menu bar status: "AI setup needed" with a primary action "Fix AI settings" that opens Preferences directly to the API key field.
- Consequence: The user understands what happened and can fix it in under 30 seconds without contacting support. They feel competent, not blamed.
- Evidence: SharedTypes.swift — AIError.userFacingMessage returns specific, actionable strings for each error type. AppWatchState.primaryActionTitle provides a one-click path to resolution.
- Action: Preserve this pattern. When adding new error types, always include (1) what went wrong in plain language, (2) what the user should do, and (3) a direct link to the fix.
```

**Example negative finding:**
```
### Burst pause during presentations leaves user stranded
- Lens: User Empathy
- Type: NEGATIVE
- Situation: A developer is giving a live demo, rapidly taking screenshots to document steps. After the 20th screenshot in 10 seconds, ScreenSage silently pauses all processing. A notification says "Large batch paused" but the user is focused on their demo and misses it.
- Consequence: The user finishes their demo, expects 30 renamed screenshots, and finds them all still named "Screenshot 2026-...". They feel betrayed — the app stopped working at the exact moment they needed it most, without clearly telling them.
- Evidence: ProcessingQueue.swift:438 — burst detection at 20 files / 10 seconds triggers `pauseByUser()`.
- Action: Instead of silently pausing, show a persistent menu bar badge or change the status icon. Consider raising the threshold to 50, or making it configurable. At minimum, the resume should be one click from the menu bar, not buried.
```

</examples>

---

### Lens 2: Machine Empathy

**Perspective:** You are the computer. You have finite battery, CPU, memory, disk, and network. Every cycle this app burns is a cycle stolen from something else.

**What to examine:**
- Polling vs. events — timers that could be callbacks, notifications, or FSEvents
- Wake frequency — how often does the app wake the CPU when nothing is happening?
- Unbounded growth — collections, caches, or dictionaries that accumulate without pruning
- Network discipline — redundant calls, retries without backoff, downloading more than needed
- Disk I/O — constant small writes, temp files not cleaned up
- Image/media — full-resolution assets when thumbnails would do
- Background behavior — work happening when the user isn't looking
- File descriptors / connections — properly closed? Reused?

**What this lens catches that others miss:**
- The "fan spin" — technically correct code that makes the laptop hot
- The "battery thief" — background activity that drains power without user benefit
- The "slow leak" — growth that only matters after weeks of uptime in a menu bar app
- Timers that could be event-driven

<examples>

**Example negative finding:**
```
### Failure tracker grows unbounded over app lifetime
- Lens: Machine Empathy
- Type: NEGATIVE
- Situation: ScreenSage runs in the menu bar 24/7. Each time a file fails processing, its path is added to `repeatedFailureCounts`. This dictionary is never pruned — not on success, not on timer, not on app state change.
- Consequence: After months of uptime processing hundreds of files, this dictionary accumulates hundreds of entries consuming memory that serves no purpose. For a menu bar app that users expect to be invisible, any unbounded growth is a violation of trust with the machine.
- Evidence: ProcessingQueue.swift:130 — `private var repeatedFailureCounts: [String: Int] = [:]` — no pruning logic exists anywhere in the file.
- Action: Add a prune step to the existing `checkForStuckItems()` 60-second timer: remove entries older than 1 hour or with counts below the action threshold. Alternatively, switch to a fixed-size LRU.
```

**Example positive finding:**
```
### Directory watching uses FSEvents, not polling
- Lens: Machine Empathy
- Type: POSITIVE
- Situation: The DirectoryWatcher uses DispatchSource file system events to detect new screenshots, waking only when the OS signals a change.
- Consequence: Zero CPU cost when no screenshots are being taken. The Mac can sleep peacefully. This is exactly the right pattern for a menu bar app.
- Evidence: DirectoryWatcher.swift:119 — `DispatchSource.makeFileSystemObjectSource` with appropriate event masks.
- Action: Preserve this. If adding new watched resources (e.g., watching for settings changes), use the same event-driven pattern rather than introducing timers.
```

</examples>

---

### Lens 3: Developer Empathy

**Perspective:** You are the next person — human or AI — who opens this codebase at 2 AM to fix a production bug. You've never seen it before.

**What to examine:**
- God objects — files or classes doing too many things
- Naming — do names tell you what things *do*, or do you need to read the implementation?
- Coupling — how many singletons must you understand to change one thing?
- Consistency — does the codebase follow its own conventions?
- Hidden side effects — does calling a function change state you wouldn't expect?
- Error tracing — can you follow a failure from log to responsible code in 60 seconds?
- Test clarity — do tests explain behavior, or are they puzzles?
- Architecture legibility — can you understand the system from the directory structure?

**What this lens catches that others miss:**
- The "fear of breaking" — code that works but nobody dares touch
- The "archaeology problem" — understanding requires git blame, not reading code
- The "clever trap" — impressive code that creates maintenance debt
- The "welcome mat" — code that's genuinely pleasant to work in

<examples>

**Example negative finding:**
```
### ProcessingQueue is a 1400-line god object
- Lens: Developer Empathy
- Type: NEGATIVE
- Situation: A new developer needs to fix a bug where AI descriptions sometimes contain markdown formatting. They open ProcessingQueue.swift looking for the sanitization logic. The file is 1400 lines containing file I/O, AI orchestration, state management, response sanitization, notification dispatch, circuit breaking, burst detection, and queue diagnostics.
- Consequence: The developer spends 20 minutes finding `sanitizeDescription` buried at line 1058 because there's no clear boundary between concerns. They're afraid to change it because every function touches shared mutable state. A 10-minute fix takes an hour.
- Evidence: ProcessingQueue.swift — 1390 lines, 5+ singleton dependencies, handles 7+ distinct responsibilities.
- Action: Extract `sanitizeDescription` and response validation into a standalone `CaptionSanitizer` struct with its own tests. This is the lowest-risk first step — it's a pure function with no state dependencies. Future extractions: circuit breaker logic, burst detection, queue diagnostics.
```

**Example positive finding:**
```
### Error taxonomy makes failure handling predictable
- Lens: Developer Empathy
- Type: POSITIVE
- Situation: A developer needs to add handling for a new API error code. They look at AIError and immediately see the pattern: each case has `isTerminal`, `isRetryable`, `shouldStopAutomation`, `userFacingMessage`, and `errorCode`. Adding a new case is obvious — follow the existing pattern.
- Consequence: The developer adds the new case in 5 minutes with confidence. The enum's behavioral properties mean the rest of the codebase handles it correctly without changes.
- Evidence: SharedTypes.swift:109-208 — AIError enum with computed behavioral properties.
- Action: Preserve this pattern. It's a genuine pleasure to extend. When adding new error surfaces (e.g., StoreKit errors), model them the same way.
```

</examples>

---

### Lens 4: Support Empathy

**Perspective:** You answer the email when a user says "it's broken." Every silent failure is a mystery you must solve with a vague user report and whatever breadcrumbs the app left behind.

**What to examine:**
- Logging — if this fails, will logs show *what input* caused it and *what state* the system was in?
- Error specificity — does the user see "Something went wrong" or a message that helps them self-fix?
- Diagnostics — can you export a redacted bundle? Is there a "system check"?
- Silent drops — code paths where work is skipped with no log, no notification, no history entry
- Self-service — can the user fix common problems without contacting you?
- Feedback channels — is it easy to report? Does the report include useful context?
- State visibility — can you tell what the app is currently doing?

**What this lens catches that others miss:**
- The "20-email thread" — a problem that takes excessive back-and-forth to diagnose
- The "ghost failure" — something went wrong but there's zero evidence
- The "works on my machine" — failures only in user environments you never tested
- The "brilliant diagnostics" — systems that make support a pleasure

<examples>

**Example negative finding:**
```
### Skipped files leave no trace for support to investigate
- Lens: Support Empathy
- Type: NEGATIVE
- Situation: A user reports "ScreenSage stopped working." Support asks them to send a diagnostics bundle. The bundle shows healthy status, valid API key, watched folder accessible. Everything looks fine. But the user's screenshots are all .heic files, which ScreenSage silently skips — no log line, no history entry, no notification.
- Consequence: Support cannot determine the cause from the diagnostics bundle alone. They ask the user to take a test screenshot, the user takes another .heic, nothing happens, support is stumped. The resolution requires 4+ emails and eventually asking "what format are your screenshots?" — something the diagnostics should have surfaced automatically.
- Evidence: IngestReconciler.swift:225 — `.ignored(.unsupportedFormat)` increments a counter in the folder summary but never appears in user-visible history or diagnostics export.
- Action: Add a "skipped files" section to the diagnostics summary showing the last 10 skipped files with their ignore reasons. For `unsupportedFormat` specifically, show a one-time notification on first encounter.
```

**Example positive finding:**
```
### Feedback bundle is a support person's dream
- Lens: Support Empathy
- Type: POSITIVE
- Situation: A user clicks "Send Feedback." ScreenSage automatically builds a zip containing redacted settings, recent processing history, unified logs, crash reports, a menu state snapshot, and a README explaining what each file contains. API keys and full home directory paths are stripped.
- Consequence: Support receives a single attachment that contains everything needed to diagnose 90% of issues. No back-and-forth asking "what provider are you using?" or "can you check your settings?" The first reply can be a solution, not a question.
- Evidence: FeedbackReporter.swift:181-198 — `makeBundlePayload` assembles all diagnostic context. DiagnosticsExporter.swift:201 — `redactSensitiveText` strips API keys and paths.
- Action: Preserve this. It's genuinely excellent. Consider adding the "skipped files" data mentioned above to the diagnostics summary so format-mismatch issues become visible in the bundle too.
```

</examples>

---

## Phase 3: Execution

### Single-agent mode (focused/module scope)

Read the relevant source files, then make one pass through each lens sequentially. Produce findings for all four lenses before synthesizing.

### Multi-agent mode (full scope)

For full codebase audits, use parallel agents for efficiency and perspective diversity.

#### Environment Detection

```bash
bash "${SKILL_DIR}/scripts/detect-llms.sh" --quiet 2>/dev/null || \
  for t in ask-gemini ask-copilot ask-cerebras ask-zai; do command -v "$t" >/dev/null 2>&1 && echo "$t"; done
```

#### Agent Assignment

Assign lenses to maximize perspective diversity:

| Lens | Best agent type | Why |
|---|---|---|
| User Empathy | External LLM (fresh eyes) | No familiarity bias — sees the product as a user would |
| Machine Empathy | Code-aware subagent | Needs to read actual implementations, timers, loops |
| Developer Empathy | Code-aware subagent | Needs to evaluate naming, structure, coupling |
| Support Empathy | External LLM + code-aware | External for "what would confuse a user?", code-aware for "is this logged?" |

When dispatching to external LLMs, include:
1. The lens prompt (from Phase 2)
2. The relevant source code (pipe file contents)
3. A brief project description (1-3 sentences)

When dispatching to subagents, include:
1. The lens prompt
2. Instructions to read specific files
3. The project CLAUDE.md for context

#### Prompt Template for External LLMs

```
You are conducting an empathy audit of [PROJECT] — [1-sentence description].

[LENS PROMPT FROM PHASE 2]

Here is the code to review:

[SOURCE CODE]

Produce 5-10 findings. Include BOTH positive and negative findings.
For each finding, use the output format specified in the lens prompt.
Be specific — cite function names, patterns, and line-level observations.
Do not hedge or soften negative findings. Do not be sycophantic about positive ones.
```

#### Prompt Template for Subagents

```
You are conducting an empathy audit of this codebase through the [LENS NAME] lens.

[LENS PROMPT FROM PHASE 2]

Read these files: [FILE LIST]
Also read CLAUDE.md for project context.

Produce 5-10 findings. Include BOTH positive and negative findings.
Be specific — cite file:line references.
```

## Phase 4: Synthesis

After collecting findings from all four lenses, synthesize into a single report.

### Deduplication

Merge findings that describe the same underlying issue from different lenses. Note which lenses independently surfaced it — convergence increases severity.

### Severity Assessment

Rate each finding:

| Severity | Criteria |
|---|---|
| **Critical** | Causes data loss, trust damage, silent failure, or would generate support emails |
| **Important** | Degrades experience, wastes resources, or creates maintenance burden |
| **Minor** | Suboptimal but not harmful — improvement opportunity |
| **Positive** | Worth celebrating and preserving — document so it doesn't get lost in a refactor |

Upgrade severity when:
- Multiple lenses independently surface the same issue
- The issue is invisible to the user (silent failure)
- The issue compounds over time (memory leak, growing support burden)
- The emotional injury is shame, betrayal, or helplessness

### Report Structure

```markdown
# Empathy Audit: [Project]
_Reviewed: [date]_

## Summary
- **Strongest quality:** [the best positive finding — one sentence]
- **Biggest risk:** [the most damaging negative finding — one sentence]
- **Most surprising finding:** [something a technical review would have missed — one sentence]

## Critical Findings

[Each finding uses the full format: title, lens, situation, consequence, evidence, action.
Critical = causes data loss, trust damage, silent failure, or support emails.]

## Important Findings

[Same format. Important = degrades experience, wastes resources, or creates maintenance burden.]

## Minor Findings

[Can be abbreviated — title, lens, one-line situation, evidence, action.]

## Positive Findings (Preserve These)

[Full format. These protect against regression — document them so future refactors
don't accidentally destroy what's working well.]

## Cross-Lens Patterns

[Issues surfaced by 2+ lenses independently. These are systemic — fixing them
often addresses multiple findings at once. For each pattern, list which lenses
surfaced it and what the common root cause is.]

## Decision List

[The point of the audit. Each item is a decision the team can make now.]

| # | Decision | Addresses | Effort | Risk if skipped |
|---|---|---|---|---|
| 1 | [specific action] | [finding title(s)] | [S/M/L] | [what happens if you don't] |
| 2 | [specific action] | [finding title(s)] | [S/M/L] | [what happens if you don't] |
| 3 | [specific action] | [finding title(s)] | [S/M/L] | [what happens if you don't] |
```

The **Decision List** is the most important part of the report. It transforms findings into choices. Every critical and important finding must appear in at least one decision row. If a finding doesn't map to a decision, it's an observation, not a finding — move it to a footnote or cut it.

## Phase 5: Follow-Up

After presenting the report, offer:

> Which findings resonate? Want me to turn the top items into tasks, go deeper on one lens, or run a targeted audit on a specific subsystem?

</process>

<anti_patterns>

## Anti-Patterns

| Don't | Do instead |
|---|---|
| Write a finding without a concrete scenario | Every finding must tell a story: who, what they're doing, what happens |
| Write an action you couldn't start implementing today | "Improve error handling" is not an action. "Add a notification in `IngestReconciler` when a file is skipped for unsupported format" is |
| Produce only negative findings | Positives protect against regression — document what's worth preserving |
| Use generic labels ("could be more efficient") | Name the specific function, file, and line |
| Conflate lenses | Keep findings lens-specific; note convergence in the Cross-Lens Patterns section |
| Describe symptoms without consequences | "This dictionary grows" is a symptom. "After 3 months of uptime, this consumes 50MB of memory on a machine the user expects to be idle" is a consequence |
| Soften findings to be polite | Be direct. The user needs to make decisions, not feel good |
| Produce findings that don't appear in the Decision List | If it's not worth deciding on, it's not worth reporting |
| Skip the positive findings | They're as valuable as negatives — they show what to protect during refactors |

</anti_patterns>

<success_criteria>

The audit is complete when:
- [ ] All four lenses produced findings with specific evidence
- [ ] Both positive and negative findings are present
- [ ] At least one finding would not have appeared in a standard code review
- [ ] Findings include emotional impact, not just technical assessment
- [ ] Cross-lens patterns are identified
- [ ] The user has a prioritized action list
- [ ] The report is specific enough that a developer could act on each finding without further investigation

</success_criteria>
