# Analysis Framework — Detailed Rubric

This reference provides the full analytical rubric for each dimension of a Speaker profile.
For each dimension, it lists the key questions to answer, where to find evidence, and common
patterns to look for.

## 1. Professional Identity

**Key questions:**
- What is their current role and level? (IC, lead, manager, director, VP?)
- What do they aspire to? (job search signals, personal site messaging, resume context)
- How long have they been in this domain? (depth of tooling, vocabulary sophistication)
- Do they still write code, or have they moved to pure management?
- What industry/domain do they work in? (healthcare, finance, retail, etc.)

**Evidence sources:**
- Git config (name, email — personal vs work)
- CLAUDE.md files (project descriptions reveal role)
- Personal site or portfolio projects
- Memory files (project type memories often mention team dynamics)
- Conversation history (do they debug production, or delegate that?)

**Common patterns:**
- **The Coding Leader:** Still writes code daily despite leadership title. Evidence: high
  conversation count in application repos, not just infra/process repos.
- **The Specialist:** Deep in one domain. Evidence: most projects cluster in one technology area.
- **The Generalist:** Wide range of technologies and project types. Evidence: conversation
  history spans many different tech stacks.
- **Career Transition:** Evidence of learning new technologies, redesigning personal sites,
  writing thought-leadership content.

## 2. Technical Profile

**Key questions:**
- What languages do they use most? (project configs, CLAUDE.md, file extensions in repos)
- What's their infrastructure stack? (AWS/GCP/Azure, CDK/Terraform/Pulumi)
- What frameworks? (Django/Rails/Express, React/Vue/Svelte)
- What's their depth level — surface user or deep expert? (custom tooling = deep)
- What development tools do they choose? (editor, terminal, package manager, linter)
- Do they prefer convention or configuration? (framework choices reveal this)

**Evidence sources:**
- CLAUDE.md files (technical instructions, stack descriptions)
- Shell config (PATH entries, tool initializations, aliases, env vars)
- Git config (diff tool, merge strategy, aliases)
- Project structure (monorepo vs polyrepo, testing patterns)
- Custom scripts in ~/.local/bin/ or similar
- Package managers used (pip/uv/pdm/poetry for Python; npm/yarn/pnpm for JS)

**Depth indicators:**
- **Surface:** Uses framework defaults, follows tutorials, few custom configs
- **Proficient:** Custom CLAUDE.md with specific patterns, linting rules, test commands
- **Expert:** Custom tooling (scripts, agents, skills), performance optimization work,
  infrastructure-as-code, multi-account cloud architectures
- **Architect:** Makes and documents architectural decisions, multi-system design,
  compliance/security frameworks

## 3. Communication Style

**Key questions:**
- How verbose are they? (average message length, one-liner vs paragraph ratio)
- How formal? (contractions, slang, emoji use, punctuation)
- How do they express frustration? (caps, terse corrections, rhetorical questions)
- How do they express satisfaction? (explicit praise, silence, moving on)
- Do they explain their reasoning, or just give instructions?
- How do they handle ambiguity? (ask clarifying questions vs. make assumptions)
- Do they proofread? (typo frequency, self-correction patterns)

**Evidence sources:**
- Conversation history (primary source — sample broadly)
- Memory files of type "feedback" (explicit corrections to AI behavior)
- CLAUDE.md global preferences (stated communication preferences)

**Common patterns:**
- **The Commander:** Short imperative messages, expects inference, corrects tersely.
  Evidence: high ratio of <50 char messages, few questions asked.
- **The Collaborator:** Longer messages with context, asks for input, discusses tradeoffs.
  Evidence: messages include "what do you think" or "should we."
- **The Narrator:** Provides detailed context and reasoning with instructions.
  Evidence: messages often >200 chars, include background information.
- **The Switcher:** Communication style shifts by context — terse for routine tasks,
  detailed for novel problems. Evidence: bimodal message length distribution.

**Emotional markers to track:**
- ALL CAPS = emphasis or frustration
- Multiple punctuation (!! or ??) = surprise or emphasis
- Ellipsis (...) = trailing thought or hesitation
- Typo density = typing speed / proofreading priority
- "just" and "simply" = may indicate frustration with complexity
- Humor frequency = personality warmth indicator

## 4. Cognitive Style

**Key questions:**
- Are they theory-first or evidence-first? (do they hypothesize then test, or look at data then theorize?)
- How do they break down problems? (phased approach, parallel exploration, depth-first)
- How do they handle uncertainty? (gather more data, make a call and iterate, ask for opinions)
- Do they document decisions? (ADRs, CLAUDE.md memories, commit messages)
- How do they validate work? (tests, manual checks, dry runs, peer review)

**Evidence sources:**
- Conversation history (how they initiate complex tasks)
- Memory files (decision documentation patterns)
- CLAUDE.md instructions (testing and safety requirements)
- Project structure (test directories, CI config, documentation)
- Script safety patterns (dry-run defaults, `--live` flags)

**Common patterns:**
- **The Empiricist:** Measures before deciding. Evidence: benchmarks, profiling, A/B testing,
  "show me the data" messages.
- **The Systematizer:** Builds frameworks and processes. Evidence: phased approaches, task
  tracking, orchestration tools, naming conventions.
- **The Pragmatist:** Does what works now, refactors later. Evidence: "don't over-engineer,"
  direct approaches, minimal abstractions.
- **The Cautious Builder:** Safety-first with dry runs, rollback plans, pre-mortems.
  Evidence: `--live` flags, verification steps, explicit safety requirements.

## 5. Values & Priorities

**Key questions:**
- What do they optimize for? (speed, correctness, elegance, simplicity, cost)
- What frustrates them? (look at corrections, complaints, negative feedback)
- What impresses them? (look at positive reactions, "yes exactly" moments)
- How do they balance speed vs quality?
- How do they think about cost? (token optimization, cloud costs, time investment)
- What do they explicitly reject? (anti-patterns, things they've told Claude NOT to do)

**Evidence sources:**
- Feedback-type memory files (strongest source — explicit preference statements)
- CLAUDE.md global and project-level instructions
- Conversation corrections (patterns in what they reject)
- Tool choices (cheap/fast vs. expensive/thorough indicates priority)

**Red flags to note honestly (not judgmentally):**
- Skipping tests when in a hurry (stated vs. revealed testing values)
- Committing directly to main (velocity vs. safety tradeoff)
- Long sessions without breaks (engagement vs. sustainability)
- Many abandoned projects (exploration vs. follow-through pattern)

**Frame these as patterns, not character flaws.** "Evidence shows testing is sometimes skipped
under time pressure, suggesting velocity is prioritized when stakes feel manageable."

## 6. Creative & Personal

**Key questions:**
- What do they build when nobody's watching? (personal projects)
- What names do they choose for projects? (reveals humor, interests, aesthetic)
- What hobbies or interests surface? (non-code mentions in history or configs)
- What's their aesthetic taste? (design choices, font preferences, color palettes)
- What media do they consume? (book references, cultural references in code/names)
- Do they teach or share knowledge? (blog posts, teaching, mentoring signals)

**Evidence sources:**
- Personal project directories and READMEs
- Project naming patterns (creative names = expressive personality)
- Personal site design choices
- Cultural references in conversation history
- Teaching/mentoring signals (AP CS, blog posts, documentation thoroughness)
- Shell functions and aliases (personalization reveals personality)

**The naming analysis is uniquely revealing:**
- Whimsical names (e.g., "flame-and-forget", "dungeon-achievements") suggest playfulness
- Descriptive names (e.g., "redox-tools", "command-center-etl") suggest pragmatism
- The mix of both reveals the range

## 7. Working Relationship Patterns

**Key questions:**
- How do they delegate? (detailed specs vs. goals vs. "just do it")
- How do they handle mistakes? (patient correction vs. terse redirection)
- Do they trust AI judgment or verify everything? (level of autonomy granted)
- What's their feedback cycle? (immediate correction vs. batch review)
- Do they iterate or plan-then-execute? (incremental vs. big-bang approach)
- What makes a session feel successful? (outputs, learning, progress, resolution)

**Evidence sources:**
- Conversation history (delegation and correction patterns)
- Feedback-type memories (explicit working relationship preferences)
- Session patterns (long single-topic vs. rapid multi-topic switching)
- Subagent/parallel work usage (comfort with AI autonomy)

**Common relationship patterns:**
- **The Peer:** Treats AI as a capable colleague. Evidence: gives context, accepts pushback,
  asks for opinions.
- **The Director:** Treats AI as a skilled executor. Evidence: imperative instructions, expects
  inference, corrects without explaining why.
- **The Student:** Uses AI to learn. Evidence: asks "why", requests explanations, explores
  unfamiliar territory.
- **The Partner:** Blend of the above depending on domain familiarity. Evidence: directive in
  areas of expertise, collaborative in new areas.

## Cross-Dimensional Insights

The most valuable findings often emerge from *connections between dimensions*:

- Technical depth + personal projects = what they'd build if they had infinite time
- Communication style + correction patterns = how to calibrate responses
- Cognitive style + values = what kind of solution they'll accept
- Professional identity + creative projects = the gap between what they do and who they are
- Working relationship + delegation style = how much context to provide unsolicited

## The Central Tension

Every person has a defining contradiction — two forces that coexist and create the engine
that drives their behavior. Finding and naming this tension is the single most important
analytical task in the personal portrait.

**How to find it:**
- Look for patterns that seem to oppose each other across dimensions
- Check stated values against revealed behavior (from conversation samples)
- Compare the scope of their projects against how they talk about change
- Note where they invest time vs. what they say they care about

**Examples of central tensions:**
- Explorer vs. guardian: Starts many projects but demands production stability
- Speed vs. rigor: Types fast, ships fast, but insists on dry-run safety and pre-mortems
- Independent builder vs. team leader: 45 solo projects but works daily with a team
- Perfectionist vs. pragmatist: Meticulous shell config but ships with known tech debt

**The tension is not a flaw to resolve — it IS the person.** Name it in the opening of the
personal portrait and let it organize the narrative. Don't try to reconcile it.

## The Most Revealing Data Point

Across all evidence, one fact will be disproportionately revealing. It might be:
- A project name that captures their humor and values
- A shell function that embodies their philosophy
- An essay title that shows what they really care about
- A correction pattern that reveals a hard-won lesson
- An activity boundary (e.g., near-zero weekends) that shows a deliberate life choice

**How to identify it:** After completing the full analysis, ask: "If I could only tell
someone one thing about this person, what would it be?" The answer is the most revealing
data point. It should appear prominently in the personal portrait, often as an anchor for
the closing section.

## Verbosity Triggers

When a typically terse communicator writes at length, the topic is diagnostic. Catalog
what triggers verbose messages:

- Pushback on scope creep → values stability and predictability
- Detailed technical briefs for novel problems → invests in problems they find interesting
- Emotional outbursts ("holy hell", caps emphasis) → identifies what drains patience
- Gratitude overflow ("thank you" repeated) → identifies what provides genuine relief

The pattern of *when* someone switches registers reveals more than the content of any
single message.

## Strength of Evidence Scale

When writing the profile, rate the confidence of each finding:

- **Strong:** Multiple independent data points across different sources (e.g., conversation
  patterns + CLAUDE.md instructions + project structure all agree)
- **Moderate:** Clear pattern from one rich source (e.g., 50+ conversation samples showing
  terse communication)
- **Inferred:** Reasonable conclusion from indirect evidence (e.g., "likely values testing
  based on test directory structure, though conversation history shows tests are sometimes
  skipped")
- **Speculative:** Single data point or ambiguous evidence — flag explicitly

Default to understating confidence rather than overstating it.
