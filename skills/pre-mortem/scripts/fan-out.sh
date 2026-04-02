#!/usr/bin/env bash
# Pre-mortem fan-out: runs available external LLM agents in parallel
# Usage: fan-out.sh <scenario-file> <output-dir>
#   scenario-file: text file with the full scenario + preamble for each role
#   output-dir: directory where agent outputs land (one file per agent)
#
# Detects available LLMs at runtime. Uses what's there, skips what isn't.
# Claude-based agents (Saboteur, Historian) are handled by the skill via
# the Agent tool — this script only handles external LLMs.
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
3. For each reason:
   - State what went wrong (one sentence)
   - Explain the chain of events (2-3 sentences)
   - Rate: likelihood (high/medium/low) x impact (catastrophic/major/minor)
4. Be specific to THIS project. Generic risks are worthless here.
5. Uncomfortable truths are the whole point. Hold nothing back.
6. End with: The one failure nobody wants to talk about: [your most uncomfortable prediction]

FORMAT: numbered list. No preamble, no hedging."

# Role definitions: NAME|MANDATE|CATEGORIES
ROLES=(
    "customer|You are the end user. This launched and you hate it. Explain why — what is confusing, broken, or missing? You succeed when you articulate frustrations the builders would never feel.|UX, adoption, onboarding, missing features, wrong assumptions about users"
    "accountant|Find every way this costs more than expected — in money, time, maintenance burden, tech debt, or opportunity cost. You succeed when you surface hidden costs the team is ignoring.|Budget, timeline, maintenance, dependencies, operational overhead"
    "pessimist|Assume the worst about every assumption in this plan. External dependencies will fail, timelines will slip, requirements will change. What dominoes fall? You succeed when you map cascading failures.|External risks, dependencies, scope creep, organizational chaos"
    "newcomer|You have never seen this project before today. Read the description and point out everything that is unclear, assumed, or hand-waved. You succeed when you find the gaps everyone else is too close to see.|Assumptions, unclear requirements, knowledge silos, missing documentation"
)

# Write prompt to a temp file to avoid shell escaping issues
write_prompt() {
    local name="$1"
    local mandate="$2"
    local categories="$3"
    local prompt_file="${OUTPUT_DIR}/.prompt-${name}.txt"

    cat > "$prompt_file" <<PROMPT_EOF
${PREAMBLE}

YOUR MANDATE: ${mandate}

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
    echo "No external LLMs detected. Writing prompts for Claude-only mode." >&2
    # Write prompt files so the skill can read them and use Agent tool instead
    for role_def in "${ROLES[@]}"; do
        IFS='|' read -r name mandate categories <<< "$role_def"
        write_prompt "$name" "$mandate" "$categories"
    done
    echo "CLAUDE_ONLY" > "${OUTPUT_DIR}/.mode"
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
    IFS='|' read -r name mandate categories <<< "$role_def"
    prompt_file=$(write_prompt "$name" "$mandate" "$categories")

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
