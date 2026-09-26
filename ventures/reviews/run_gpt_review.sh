#!/usr/bin/env bash
# Second-opinion review of PLAN.md by an OpenAI model through the Codex CLI
# (`npm install -g @openai/codex`, then `codex login` with your ChatGPT account
# or OPENAI_API_KEY set). Usage:
#   MODEL=<model id your account offers> ./reviews/run_gpt_review.sh
# Writes reviews/<date>-gpt-review.md. Leave MODEL empty to use Codex's default.
set -euo pipefail
cd "$(dirname "$0")/.."

command -v codex >/dev/null || { echo "codex CLI not found: npm install -g @openai/codex" >&2; exit 1; }

out="reviews/$(date -u +%F)-gpt-review.md"
prompt="$(cat reviews/review_prompt.md)

=== PLAN.md ===
$(cat PLAN.md)

=== Earlier review (Claude) ===
$(cat reviews/2026-09-26-claude-adversarial-review.md)"

args=(exec --sandbox read-only)
[[ -n "${MODEL:-}" ]] && args+=(--model "$MODEL")

codex "${args[@]}" "$prompt" | tee "$out"
echo "Saved $out"
