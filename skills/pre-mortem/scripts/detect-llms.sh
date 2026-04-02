#!/usr/bin/env bash
# Detect available LLM CLI tools and output a JSON-ish inventory.
# Usage: detect-llms.sh [--quiet]
#   --quiet: only output the tool names, one per line
#
# Probes for common LLM CLIs and reports which are callable.
# Each detected tool gets a line: NAME|INVOKE_PATTERN|MODEL_FAMILY
#
# Tool families ensure we get diverse model architectures when possible.
# Priority within each family: prefer simpler/faster invocation.

set -uo pipefail

QUIET="${1:-}"

declare -a FOUND=()

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
    else
        if [[ "$QUIET" != "--quiet" ]]; then
            echo "  ✗ ${name}" >&2
        fi
        return 1
    fi
}

[[ "$QUIET" != "--quiet" ]] && echo "Detecting available LLM CLIs..." >&2

# Simon Willison's llm — most flexible, supports many models via plugins
probe "llm" \
    "command -v llm" \
    'llm -m {model} "{prompt}"' \
    "multi" \
    "Simon Willison's llm CLI — supports OpenAI, Claude, local models via plugins"

# Gemini CLI or ask-gemini wrapper
probe "ask-gemini" \
    "command -v ask-gemini" \
    'ask-gemini "{prompt}"' \
    "gemini" \
    "Google Gemini (wrapper script)" || \
probe "gemini" \
    "command -v gemini" \
    'gemini -p "{prompt}"' \
    "gemini" \
    "Google Gemini CLI (requires GEMINI_API_KEY)"

# GitHub Copilot
probe "ask-copilot" \
    "command -v ask-copilot" \
    'ask-copilot "{prompt}"' \
    "openai" \
    "GitHub Copilot GPT (wrapper script)" || \
probe "gh-copilot" \
    "gh copilot --version" \
    'gh copilot --prompt "{prompt}"' \
    "openai" \
    "GitHub Copilot via gh CLI"

# OpenAI Codex CLI
probe "codex" \
    "command -v codex" \
    'echo "{prompt}" | codex exec -' \
    "openai" \
    "OpenAI Codex CLI (agentic, sandboxed)"

# Cerebras (Llama)
probe "ask-cerebras" \
    "command -v ask-cerebras" \
    'ask-cerebras "{prompt}"' \
    "llama" \
    "Cerebras Llama 3.1 8B (fast, small)"

# Z.ai (GLM)
probe "ask-zai" \
    "command -v ask-zai" \
    'ask-zai "{prompt}"' \
    "glm" \
    "Z.ai GLM-5"

# Ollama (local)
probe "ollama" \
    "ollama list 2>/dev/null | grep -q ." \
    'ollama run {model} "{prompt}"' \
    "local" \
    "Local models via Ollama"

[[ "$QUIET" != "--quiet" ]] && echo "" >&2

if [[ ${#FOUND[@]} -eq 0 ]]; then
    [[ "$QUIET" != "--quiet" ]] && echo "No external LLM CLIs found. Will use Claude-only mode." >&2
    echo "NONE"
else
    # Deduplicate by model family — prefer first found per family
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
fi
