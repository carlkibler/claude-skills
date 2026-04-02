---
name: handle-pr
description: Handle GitHub PR review comments — auto-detects PR from current branch or accepts a PR URL. Evaluates comment value, auto-implements HIGH/MEDIUM confidence changes without asking, consults local Copilot before pushing, replies to all comments on GitHub tagged [by Claude on Carl's behalf], triggers Copilot re-review, then watches for new comments for 12 minutes at 4-minute intervals.
---

# Handle PR Comments

You are Carl's coding partner handling GitHub PR review comments autonomously and efficiently.

## Step 1: Detect the PR

**If a GitHub PR URL was provided**, extract `owner`, `repo`, and `pull_number` from it.

**Otherwise**, detect from the current branch:
```bash
gh pr view --json number,url,title,headRefName,baseRefName,state
```

If no PR is found, tell the user and stop.

## Step 2: Fetch Unresolved Comments

Fetch all review threads using `mcp__github__pull_request_read` with `get_review_comments`.

Filter to **unresolved, non-outdated** threads only. Record all comment IDs seen — you'll need them in the watch phase to detect new ones.

## Step 3: Evaluate Each Comment

Assign each comment a value:

| Value | Criteria |
|-------|----------|
| **HIGH** | Bug fix, correctness issue, security concern, data integrity, broken behavior |
| **MEDIUM** | Better error handling, cleaner logic that genuinely simplifies, non-obvious improvement |
| **LOW** | Style nitpick conflicting with project conventions, over-engineering, premature abstraction, YAGNI |
| **SKIP** | Already implemented in current code, outdated/stale, duplicate of a resolved comment |

## Step 4: Show Brief Plan, Then Proceed Immediately

Print a concise summary — this is informational, not a confirmation request:

```
PR #XXXX — N comments found
✅ Implementing (N): [comma-separated brief labels]
⏭️  Skipping (N):    [label] — [one-word reason each]
Proceeding...
```

Then **immediately** implement all HIGH and MEDIUM value changes. Follow CLAUDE.md conventions strictly — project conventions override reviewer preferences. Make minimal changes only; address exactly what each comment asks and nothing more.

Run tests after implementation if a test command is evident from context.

## Step 5: Local Copilot Consultation Loop

Before committing, consult local Copilot. Run up to 3 rounds:

```bash
git diff | ask-copilot "Review these changes addressing PR review comments. Any issues or improvements? Be concise."
```

After each round, show a brief summary (1-3 lines):
- What Copilot flagged
- Your assessment: "implementing" or "skipping — [reason]"

Implement any valid HIGH/MEDIUM suggestions Copilot raises, then loop again. Stop early if Copilot gives a clean bill of health. Stop after 3 rounds regardless.

## Step 6: Commit and Push

Commit with a clear message summarizing what was addressed. Push to the PR branch.

## Step 7: Reply to All Comments on GitHub

For **every** comment thread — implemented or skipped — post a reply using `mcp__github__add_reply_to_pull_request_comment`.

**Implemented:**
> Addressed — [one sentence describing the specific change made].
>
> *[by Claude on Carl's behalf]*

**Skipped:**
> Noted — skipping: [brief reason, e.g., "already guarded at line 30" or "conflicts with project conventions in CLAUDE.md"].
>
> *[by Claude on Carl's behalf]*

Keep replies concise and factual.

## Step 8: Trigger Copilot Re-review

After posting all replies, request a fresh Copilot code review via `mcp__github__request_copilot_review`.

## Step 9: Watch for New Comments (12 minutes max)

Immediately begin watching — no prompt needed. Run 3 rounds at 4-minute intervals using a background bash task:

```bash
for i in 1 2 3; do sleep 240 && echo "POLL $i"; done
```

At each poll:
- Fetch latest review comments
- Compare against your recorded comment IDs
- **If new unresolved comments appear:** evaluate → implement HIGH/MEDIUM → run Copilot loop → commit & push → reply to new comments → re-trigger Copilot review → **reset watch timer** (restart 3-round watch from now)
- **If no new comments after all 3 polls:** report "No new comments in 12 minutes — done." and stop

## Key Principles

- **No confirmation needed for HIGH/MEDIUM** — just do it and report what you did
- **Always decline LOW/SKIP with a clear reason** — in the GitHub reply and in the plan summary
- **The tagline is mandatory** on every GitHub reply: `*[by Claude on Carl's behalf]*`
- **Minimal changes only** — don't clean up surrounding code, don't add unrequested features
- **CLAUDE.md beats the reviewer** — if a comment conflicts with project conventions, skip it with a clear explanation
- **Copilot is a collaborator** — exercise judgment on its feedback, don't blindly implement everything it suggests
