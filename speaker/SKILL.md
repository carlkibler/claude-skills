---
name: speaker
description: "Build a comprehensive, honest profile of the user from their digital footprint (Claude Code history, project files, dotfiles, git config, memories, and conversation patterns). Produces multiple output documents: a personal portrait, a professional portrait, a working-with-me guide for AI assistants, and a compact system prompt. Inspired by Orson Scott Card's Speaker for the Dead — truthful, fair, and in service of the person. Use when asked to profile me, get to know me, build a context document, create my AI assistant profile, speaker, or similar requests to understand who the user is."
---

# Speaker

> "The Speaker told the truth... not as the world saw them, but as they truly were."

## Philosophy

This skill builds a truthful, multidimensional portrait of a person from their digital footprint.
It is modeled on the "Speaker for the Dead" concept from Orson Scott Card: the goal is to tell the
truth about who someone is — not to flatter, not to judge, but to *understand* and *serve*.

**Core principles:**

- **Truth over comfort, kindness over cruelty.** Report what the evidence shows. Frame it with
  respect. Never sanitize away a real pattern, but never weaponize one either.
- **Evidence-based.** Every claim should trace to observable data — conversation logs, project
  structure, code choices, git history, configuration files. If it can't be evidenced, flag it as
  inference and explain why.
- **Multidimensional.** People are not their job title. Capture the professional, the personal,
  the creative, the quirky. What someone builds on weekends tells you as much as what they
  build at work.
- **Useful.** The output is not a biography — it's operational context. Every section should help
  an AI (or human) work with this person more effectively.

## When to Use

Trigger on requests like:

- "profile me", "get to know me", "build my profile"
- "create context for my AI assistant"
- "speaker" or "speak for me"
- "help another Claude understand me"
- "build a working-with-me guide"
- "what do you know about me"
- Requests for resume context, LinkedIn material, or personal brand documents

## Data Collection

### Phase 1: Discovery

Before analyzing anything, map what data sources exist. Not all users will have all sources.
Run discovery in parallel where possible.

**Source 1: Claude Code Environment**
```
~/.claude/CLAUDE.md                          # Global instructions — personality, preferences, rules
~/.claude/settings.json                      # Tool preferences, model choices
~/.claude/history.jsonl                      # Conversation history (display field = user messages)
~/.claude/projects/*/memory/                 # Per-project memories (feedback, user, project, reference types)
~/.claude/projects/*/memory/MEMORY.md        # Memory indexes
~/.claude/agents/                            # Custom agent definitions
~/.claude/skills/                            # Installed skills
~/.claude/bin/                               # Custom scripts and tools
```

**Source 2: Project Ecosystem**
```
~/dev/                                       # Work repositories
~/dev/me/ (or similar personal dir)          # Personal repositories
*/CLAUDE.md                                  # Per-project instructions
*/README.md                                  # Project descriptions
*/.beads/                                    # Task tracking (if present)
```

**Source 3: Shell & System Configuration**
```
~/.bashrc or ~/.zshrc                        # Shell config — aliases, functions, env vars, PATH
~/.bash_profile or ~/.zprofile               # Login shell config
~/.gitconfig                                 # Git identity, aliases, preferences
~/.ssh/config                                # Connection patterns (work vs personal hosts)
~/.aws/config                                # Cloud account structure (if applicable)
```

**Source 4: Conversation History Analysis**

The `~/.claude/history.jsonl` file is the richest source of communication style data. Each line
is a JSON object with a `display` field containing the user's message and a `project` field
showing which project they were working in.

Extract:
- **Project frequency counts** — which projects get the most attention (reveals real priorities)
- **Message length distribution** — terse vs. verbose communicator
- **Vocabulary patterns** — technical depth, formality level, humor frequency
- **Emotional signals** — caps usage, punctuation patterns, frustration/excitement markers
- **Typo patterns** — fast typer who doesn't proofread vs. careful writer
- **Delegation style** — gives detailed specs vs. terse goals vs. step-by-step instructions
- **Correction patterns** — how they course-correct when you go wrong

### Phase 2: Deep Reading

Read all discovered sources. Use subagents to parallelize across categories:
- Agent 1: All memory files and MEMORY.md indexes
- Agent 2: All CLAUDE.md files (global + per-project)
- Agent 3: Shell/git/system configuration
- Agent 4: Conversation history sampling and analysis
- Agent 5: Project README files and structure

For conversation history, sample broadly — take messages from the beginning, middle, and recent
history. Focus on messages between 20-500 characters (too short = "yes"/"ok", too long = pasted
content). Aim for 50-100 representative samples.

## Analysis Framework

After collecting data, analyze across these dimensions. See `references/analysis-framework.md`
for the full analytical rubric with questions and evidence patterns for each dimension.

### Dimensions

1. **Professional Identity** — Role, seniority, domain expertise, career trajectory
2. **Technical Profile** — Languages, frameworks, infrastructure, architecture patterns, tool preferences
3. **Communication Style** — Formality, verbosity, emotional expression, delegation patterns
4. **Cognitive Style** — How they approach problems, make decisions, handle uncertainty
5. **Values & Priorities** — What they optimize for, what frustrates them, what impresses them
6. **Creative & Personal** — Side projects, hobbies, interests, aesthetic preferences
7. **Working Relationship Patterns** — How they collaborate with AI, what they expect, how they give feedback

### Bias Guardrails

**During analysis, actively guard against:**

- **Halo effect:** A person's technical skill doesn't mean they're right about everything. Note
  areas of strength AND areas where evidence is thin.
- **Confirmation bias:** Don't cherry-pick messages that support a narrative. If someone is
  usually terse but occasionally writes long thoughtful messages, report both patterns.
- **Flattery creep:** It is tempting to write profiles that read like recommendation letters.
  Resist. Report patterns as patterns. "Prefers to work fast and sometimes skips testing
  steps" is more useful than "moves at an impressive pace."
- **Deficit framing:** Don't frame neutral traits as problems. Terse communication is a style,
  not a flaw. Heavy side-project activity is a pattern, not workaholism (unless there's
  evidence of burnout).
- **Gender/identity assumptions:** Use the pronouns and identity markers the person uses in
  their own writing. If unclear, use their name or "they."
- **Projection of values:** If someone doesn't write tests, don't assume they don't value
  testing — maybe they just test differently. Let evidence speak.
- **Recency bias:** Don't over-weight recent conversations. Someone's most active project this
  month may not reflect their long-term identity.

## Output Documents

Produce up to four documents, stored in the user's preferred temp/output directory. Ask the user
which outputs they want, or produce all four by default.

### 1. Personal Portrait (`portrait-personal.md`)

The "Speaker for the Dead" document. Who this person really is — not their resume, their *self*.

**Structure:**
- Opening: 2-3 sentences that capture the essence (the "if you only read this" summary)
- What they build and why — their projects as self-expression
- How they think — cognitive patterns, decision-making, what they optimize for
- What they care about — values evidenced by behavior, not stated values
- The texture — quirks, humor, aesthetic taste, the small things that make them *them*
- Closing: The through-line — what connects all of this into a coherent person

**Critical writing prompts:**

- **Find the central tension.** Every person has a defining contradiction — two forces that
  coexist and drive them. The person who starts 45 projects but writes "I want stability." The
  person who moves fast but insists on dry-run defaults. Name it explicitly. The tension IS the
  person — don't resolve it, honor it.
- **Identify the most revealing single data point.** Across all the evidence, one fact will tell
  you more about this person than any paragraph of analysis. An essay title, a shell function
  name, a project they keep coming back to, a correction they made. Find it and let it anchor
  the portrait.
- **Longer messages are diagnostic.** When a typically terse person writes at length, pay
  attention to *what* triggers verbosity. It usually reveals what they're protecting or what
  genuinely excites them.

**Tone:** Warm but honest. Like a close friend who knows you well enough to be truthful. Never
sycophantic, never clinical.

### 2. Professional Portrait (`portrait-professional.md`)

The document a hiring manager, recruiter, or professional contact should read.

**Structure:**
- Role and positioning (current + aspirational)
- Technical depth — languages, frameworks, cloud, architecture, with evidence of depth level
- Domain expertise — industries, compliance frameworks, specialized knowledge
- Leadership signals — team building, mentoring, architectural decision-making
- Project portfolio — work AND personal, showing range and initiative
- Working style — how they operate day-to-day, what kind of team/org they thrive in

**Proficiency calibration:** For each technical area, assign an evidence-based depth level:

- **Expert:** Daily use, custom tooling, deep configuration, architectural decisions.
  Evidence: high session counts, detailed CLAUDE.md, performance optimization work.
- **Proficient:** Regular use, comfortable across the surface area, some customization.
  Evidence: moderate session counts, working configurations, shipped projects.
- **Familiar:** Has used it, can navigate it, reaches for it when appropriate.
  Evidence: occasional sessions, follows existing patterns rather than creating new ones.

Always show the evidence for the rating. "Expert — 1,136 sessions, custom management commands,
startup optimization from 5s to 1.2s" is credible. "Expert" alone is not.

**Tone:** Professional but not stiff. Third-person. Backed by evidence. Useful for resume
updates, LinkedIn, cover letter context, or interview prep.

### 3. Working-With-Me Guide (`working-with-me.md`)

Direct instructions for an AI assistant or collaborator.

**Structure:**
- Communication quick-reference (how they talk, what signals mean what)
- Response calibration (length, tone, when to be proactive vs. wait)
- Technical environment (key tools, directory structure, common commands)
- Do's and Don'ts (specific, evidenced, actionable)
- What impresses them / what annoys them
- Domain knowledge expected

**Tone:** Imperative, second-person, like CLAUDE.md instructions. Optimized for AI consumption.

### 4. System Prompt (`system-prompt.md`)

A compact (under 1000 word) version of the Working-With-Me Guide, formatted for direct injection into
an AI assistant's system prompt. Everything essential, nothing wasted.

**Structure:** Single flowing document with short sections. No tables or complex formatting.
Must work in any LLM's system prompt field.

## Workflow

### Step 1: Discover
Run Phase 1 discovery. Report what sources were found and their sizes. Ask the user if there
are additional data sources to include (e.g., specific directories, exported chat logs, notes).

### Step 2: Collect
Run Phase 2 deep reading with parallel subagents. This is the most token-intensive step.

### Step 3: Analyze
Apply the analysis framework across all seven dimensions. Compile evidence for each finding.
Flag inferences that are weakly supported.

### Step 4: Draft
Write all requested output documents. Apply bias guardrails during writing.

### Step 5: Present
Share the outputs with the user. Invite feedback. Note that the profile is a snapshot — it
reflects who they are *now*, from the evidence available, and should be updated over time.

### Step 6: Iterate
If the user identifies inaccuracies or missing dimensions, update the documents. The user
knows themselves better than any analysis — their corrections are data too.

## Tips for Effective Profiles

- **Let the projects tell the story.** What someone builds on their own time — the names they
  choose, the problems they solve, the technologies they reach for — reveals more than any
  self-description.
- **Patterns over instances.** A single angry message doesn't mean someone is angry. Look for
  patterns across dozens or hundreds of interactions.
- **The gap between stated and revealed preferences is interesting.** If someone says they value
  testing but their history shows they skip it when under pressure, that tension is worth
  noting (gently).
- **Quantify where possible.** "Works across many projects" is less useful than "5,988
  conversation entries across 50+ projects, with the top 3 accounting for 52% of activity."
- **Name the through-line.** Every person has one — the thread that connects their disparate
  activities into a coherent identity. Finding it is the difference between a list of facts
  and a portrait.

## Model Recommendations

The personal portrait quality depends heavily on the writing model's ability to synthesize
narrative from evidence. For best results:

- **Opus-class models:** Best for the personal portrait and through-line identification.
  These models produce the narrative cohesion and insight density the portrait demands.
- **Sonnet-class models:** Good for the professional portrait, working-with-me guide, and
  system prompt. These are more structured documents where clarity matters more than voice.
- **Haiku-class models:** Suitable for data collection, discovery scripts, and stats
  generation. Save the expensive context for synthesis, not scanning.

When running all four documents, consider using subagents with model overrides: opus for
the personal portrait, sonnet for the other three.
