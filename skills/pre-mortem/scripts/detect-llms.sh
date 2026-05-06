#!/usr/bin/env bash
# Detect available LLM CLI tools and output a JSON-ish inventory.
# Usage: detect-llms.sh [--quiet]
#   --quiet: only output the tool names, one per line
#
# Each detected tool gets a line: NAME|INVOKE_PATTERN|MODEL_FAMILY|NOTES
# Families are deduplicated so we prefer model diversity.
# `agent` (OpenRouter) is preferred — covers all model tiers via flags.

set -uo pipefail

QUIET="${1:-}"

declare -a FOUND=()

# Add the repo's bin/ to PATH so `agent` is findable even without chezmoi install.
# This script lives at skills/<name>/scripts/ — repo root is 3 levels up.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_BIN="${SCRIPT_DIR}/../../../bin"
if [ -d "$REPO_BIN" ] && [[ ":$PATH:" != *":${REPO_BIN}:"* ]]; then
    export PATH="${REPO_BIN}:$PATH"
fi

has_secret() {
    local var_name="$1"
    bash -lc "source ~/.secrets >/dev/null 2>&1; [[ -n \"\${${var_name}:-}\" ]]" >/dev/null 2>&1
}

probe() {
    local name="$1"
    local check_cmd="$2"
    local invoke_pattern="$3"
    local model_family="$4"
    local notes="$5"

    if eval "$check_cmd" >/dev/null 2>&1; then
        FOUND+=("${name}|${invoke_pattern}|${model_family}|${notes}")
        if [[ "$QUIET" != "--quiet" ]]; then
            echo "  ✓ ${name} (${model_family}) — ${notes}" >&2
        fi
        return 0
    fi

    if [[ "$QUIET" != "--quiet" ]]; then
        echo "  ✗ ${name}" >&2
    fi
    return 1
}

[[ "$QUIET" != "--quiet" ]] && echo "Detecting available LLM CLIs..." >&2

# `agent` covers all tiers: default (gemini-2.5-flash), --fast (llama-4-scout),
# --smart (gemini-2.5-pro), --frontier (claude-opus-4-5)
probe "agent" \
    "command -v agent && has_secret OPENROUTER_API_KEY" \
    'agent "{prompt}"' \
    "openrouter" \
    "OpenRouter multi-model (--fast/--smart/--frontier)"

probe "llm" \
    "command -v llm" \
    'llm -m {model} "{prompt}"' \
    "multi" \
    "Simon Willison's llm CLI"

probe "ask-gemini" \
    "command -v ask-gemini && has_secret GEMINI_API_KEY" \
    'ask-gemini "{prompt}"' \
    "gemini" \
    "Gemini wrapper with key present" || \
probe "gemini" \
    "command -v gemini && has_secret GEMINI_API_KEY" \
    'gemini -p "{prompt}"' \
    "gemini" \
    "Gemini CLI with key present"

probe "codex" \
    "command -v codex" \
    'echo "{prompt}" | codex exec -' \
    "openai" \
    "OpenAI Codex CLI"

probe "ollama" \
    "ollama list 2>/dev/null | grep -q ." \
    'ollama run {model} "{prompt}"' \
    "local" \
    "Local models via Ollama"

[[ "$QUIET" != "--quiet" ]] && echo "" >&2

if [[ ${#FOUND[@]} -eq 0 ]]; then
    [[ "$QUIET" != "--quiet" ]] && echo "No external LLM CLIs found. Will use single-agent mode." >&2
    echo "NONE"
    exit 0
fi

declare -A SEEN_FAMILIES=()
declare -a UNIQUE=()
for entry in "${FOUND[@]}"; do
    family=$(echo "$entry" | cut -d'|' -f3)
    if [[ -z "${SEEN_FAMILIES[$family]:-}" ]]; then
        SEEN_FAMILIES[$family]=1
        UNIQUE+=("$entry")
    fi
done

if [[ "$QUIET" == "--quiet" ]]; then
    for entry in "${UNIQUE[@]}"; do
        echo "$entry" | cut -d'|' -f1
    done
else
    echo "Available (${#UNIQUE[@]} unique model families):" >&2
    for entry in "${UNIQUE[@]}"; do
        echo "$entry"
    done
fi
