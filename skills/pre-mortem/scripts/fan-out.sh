#!/usr/bin/env bash
# Pre-mortem fan-out: runs available external LLM agents in parallel
# Usage: fan-out.sh <scenario-file> <output-dir>
#   scenario-file: text file with the full scenario + preamble for each role
#   output-dir: directory where agent outputs land (one file per agent)
#
# Detects available LLMs at runtime. Uses what's there, skips what isn't.
# Code-aware roles (Saboteur, Historian, Burned Expert) are handled by the
# running agent via subagents — this script handles outsider/external LLM roles.
#
# Exit: 0 if at least one agent succeeded, 1 if all failed

set -euo pipefail

SCENARIO_FILE="${1:?Usage: fan-out.sh <scenario-file> <output-dir>}"
OUTPUT_DIR="${2:?Usage: fan-out.sh <scenario-file> <output-dir>}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

mkdir -p "$OUTPUT_DIR"

SCENARIO=$(cat "$SCENARIO_FILE")

PREAMBLE="=== PROJECT PRE-MORTEM ===

${SCENARIO}

INSTRUCTIONS:
1. The failure is CERTAIN — it already happened. Do not question this.
2. Write 5-8 specific, concrete reasons why it failed.
3. For each reason include:
   - What goes wrong (one sentence)
   - Chain of events (2-4 sentences)
   - User experience: what the user notices, concludes, and does next
   - Emotional impact: the precise emotion the user feels at the moment of failure (not just 'frustrated' — name it specifically: ashamed, gaslit, abandoned, betrayed, etc.)
   - Why the team misses it
   - Likelihood (high/medium/low) x impact (catastrophic/major/minor)
   - Trust damage (high/medium/low)
   - Recoverability (easy/moderate/hard)
   - Earliest signal / tripwire
4. Be specific to THIS project. Generic risks are worthless here.
5. Focus on failures that damage product success, not just code correctness.
6. Uncomfortable truths are the whole point. Hold nothing back.
7. Write in your assigned emotional register — don't become neutral.
8. End with: The failure nobody wants to talk about: [your most uncomfortable prediction]

FORMAT: numbered list. No preamble, no hedging."

# Role definitions: NAME|MANDATE|EMOTIONAL_REGISTER|CATEGORIES
ROLES=(
    "customer|You are the user advocate. This launched and users are disappointed, confused, or angry. Surface the exact moments where expectations are violated and trust erodes. Describe what users feel at the precise moment of failure — not just frustrated, but which specific emotion: betrayed, embarrassed, gaslit, patronized. You succeed when you articulate what the builders would rationalize away.|Protective anger — you speak for the person who deserved better and didn't get it|Onboarding, daily UX, expectation mismatch, trust loss, emotional injury, uninstall triggers"
    "support|You run support for this product after launch. Find the failures that generate vague, repetitive, emotionally draining tickets that are hard to diagnose. You have seen this exact class of ticket before. You succeed when you expose hidden support burden and diagnostic blind spots — and the specific despair of the user who gives up without ever emailing.|Exhausted resignation — you know how this ends, you've typed this reply a hundred times|Support burden, missing diagnostics, confusing states, documentation gaps, maintenance drag, silent churn"
    "accountant|Find every way this costs more than expected — in money, time, maintenance burden, abuse, margin erosion, tech debt, or opportunity cost. You succeed when you surface hidden costs the team is ignoring, especially the ones that only become visible 6 months after launch.|Dry alarm — you watch the numbers quietly deteriorate while everyone else celebrates|Budget, margin, maintenance, abuse, operational overhead, deferred cost, opportunity cost"
    "pessimist|Assume the worst about every external dependency, platform, timing decision, and distribution channel in this plan. External things will fail, shift, or betray. What dominoes fall? You succeed when you map cascading failures nobody bothered to trace.|Grim satisfaction — you called it, you always call it, nobody listens until it's too late|External risks, dependencies, platform shifts, timing, scope creep, domino effects"
    "burned_expert|You have watched a nearly identical product fail before. You carry scar tissue from that experience. You are not being contrarian — you are pattern-matching to documented, prior, painful failure. You succeed when you force the team to confront the part of the plan that is most similar to something that already went wrong.|Controlled fury — you tried to warn someone last time and they didn't listen either|Prior failure patterns, assumptions that looked safe until they weren't, second-order consequences, recovery debt"
    "emotional_witness|You are not focused on UX or features. You focus entirely on the psychological and emotional experience of users when something goes wrong. Not just 'they are frustrated' but: do they feel stupid? Abandoned? Violated? Ashamed? These emotional injuries outlast the bug. You succeed when you name what users feel in their bodies when this product fails them.|Raw empathy — you describe what the failure feels like, not what it is technically|Shame, helplessness, grief, betrayal, anxiety, loss of trust, the emotional cost of not getting what you were promised"
    "outsider|You have never worked in this domain and have no patience for insider assumptions. You bring a completely adjacent frame. Everything the team treats as obvious, you treat as suspicious. You succeed when you surface the assumption that everyone in the room shares — and that real users don't.|Bewildered estrangement — you genuinely don't understand why this was built this way, and that's exactly the point|Insider assumptions, domain jargon, non-default users, accessibility, cultural mismatch, 'this only works if you already know'"
    "critic|You are an early reviewer, blogger, or skeptical power user composing your 2-star review while reading the onboarding docs. Find the narrative that compresses many issues into one damaging public story. You succeed when you predict the review headline, the tweet, or the Hacker News thread title.|Performative disappointment — you wanted to like it|Public narrative, reviews, word of mouth, credibility, positioning, reputational compression"
)

# Write prompt to a temp file to avoid shell escaping issues
write_prompt() {
    local name="$1"
    local mandate="$2"
    local register="$3"
    local categories="$4"
    local prompt_file="${OUTPUT_DIR}/.prompt-${name}.txt"

    cat > "$prompt_file" <<PROMPT_EOF
${PREAMBLE}

YOUR ROLE: ${name}
YOUR EMOTIONAL REGISTER: ${register}
YOUR MANDATE: ${mandate}

You are not here to be balanced. Stay in your emotional register. Argue from your assigned position.
The synthesis step will handle balance.

FAILURE CATEGORIES to consider: ${categories}
PROMPT_EOF
    echo "$prompt_file"
}

# Try to run a prompt through an LLM tool, writing output to file
# Uses temp file for prompt to avoid shell escaping nightmares
run_with_tool() {
    local tool="$1"
    local name="$2"
    local prompt_file="$3"
    local outfile="${OUTPUT_DIR}/${name}.txt"
    local prompt
    prompt=$(cat "$prompt_file")

    echo ">>> ${name} → ${tool}" >&2

    case "$tool" in
        ask-gemini|ask-copilot|ask-cerebras|ask-zai)
            "$tool" "$prompt" > "$outfile" 2>/dev/null
            ;;
        llm)
            llm "$prompt" > "$outfile" 2>/dev/null
            ;;
        gemini)
            gemini -p "$prompt" > "$outfile" 2>/dev/null
            ;;
        gh-copilot)
            gh copilot --prompt "$prompt" > "$outfile" 2>/dev/null
            ;;
        codex)
            echo "$prompt" | codex exec - > "$outfile" 2>/dev/null
            ;;
        *)
            echo "!!! Unknown tool: ${tool}" >&2
            return 1
            ;;
    esac

    local lines
    lines=$(wc -l < "$outfile" | tr -d ' ')
    if [[ "$lines" -lt 3 ]]; then
        echo "!!! ${name} produced only ${lines} lines — likely failed" >&2
        return 1
    fi

    echo "<<< ${name} done (${lines} lines)" >&2
    return 0
}

# --- Detect available tools ---
echo "=== Pre-mortem fan-out ===" >&2

AVAILABLE=()
if [[ -x "${SCRIPT_DIR}/detect-llms.sh" ]]; then
    while IFS= read -r line; do
        [[ "$line" == "NONE" ]] && break
        tool_name=$(echo "$line" | cut -d'|' -f1)
        AVAILABLE+=("$tool_name")
    done < <("${SCRIPT_DIR}/detect-llms.sh" 2>/dev/null)
fi

if [[ ${#AVAILABLE[@]} -eq 0 ]]; then
    echo "No external LLMs detected. Writing prompts for single-agent mode." >&2
    # Write prompt files so the running agent can dispatch subagents instead
    for role_def in "${ROLES[@]}"; do
        IFS='|' read -r name mandate register categories <<< "$role_def"
        write_prompt "$name" "$mandate" "$register" "$categories"
    done
    echo "SINGLE_AGENT" > "${OUTPUT_DIR}/.mode"
    echo "Prompt files written to ${OUTPUT_DIR}/.prompt-*.txt" >&2
    exit 0
fi

echo "Using: ${AVAILABLE[*]}" >&2
echo "EXTERNAL" > "${OUTPUT_DIR}/.mode"

# --- Assign tools to roles (round-robin across available tools) ---
PIDS=()
NAMES=()
SUCCEEDED=0
FAILED_COUNT=0
tool_idx=0

for role_def in "${ROLES[@]}"; do
    IFS='|' read -r name mandate register categories <<< "$role_def"
    prompt_file=$(write_prompt "$name" "$mandate" "$register" "$categories")

    tool="${AVAILABLE[$tool_idx]}"
    tool_idx=$(( (tool_idx + 1) % ${#AVAILABLE[@]} ))

    run_with_tool "$tool" "$name" "$prompt_file" &
    PIDS+=($!)
    NAMES+=("$name")
done

# Wait for all
for i in "${!PIDS[@]}"; do
    if wait "${PIDS[$i]}"; then
        SUCCEEDED=$((SUCCEEDED + 1))
    else
        echo "!!! ${NAMES[$i]} failed" >&2
        FAILED_COUNT=$((FAILED_COUNT + 1))
    fi
done

echo "--- Fan-out: ${SUCCEEDED}/${#ROLES[@]} agents succeeded ---" >&2

# Clean up prompt temp files
rm -f "${OUTPUT_DIR}"/.prompt-*.txt

[[ $SUCCEEDED -gt 0 ]] && exit 0 || exit 1
