#!/usr/bin/env bash
# Run frontier agent harnesses on the benchmark. Workdirs live outside data/ so truth.json is unreachable.
# Usage: scripts/run_agents.sh <workroot> <seed> <arm>   arm in: opus sonnet codex gemini
set -u
ROOT=$1; SEED=$2; ARM=$3
P=$(cd "$(dirname "$0")/.." && pwd)
W=$ROOT/$ARM-s$SEED; rm -rf "$W"; mkdir -p "$W"
cp -r "$P/data/s$SEED/repo/." "$W/"
"$P/.venv/bin/python" -I "$P/src/extract.py" "$W" > "$W/sites.json"
PROMPT=$(cat "$P/scripts/agent_prompt.md")
cd "$W"
t0=$(date +%s)
case $ARM in
  opus|sonnet) claude -p "$PROMPT" --model "claude-$ARM-5-5" --allowedTools "Read Glob Grep Write" --disallowedTools "Bash" \
                 --output-format json > run.log 2>&1 ;;
  codex) codex exec --skip-git-repo-check --sandbox workspace-write -c model_reasoning_effort=high "$PROMPT" > run.log 2>&1 ;;
  gemini) gemini -m gemini-3.5-flash --approval-mode auto_edit -p "$PROMPT" > run.log 2>&1 ;;
esac
echo "$ARM s$SEED exit=$? secs=$(( $(date +%s) - t0 ))" | tee -a "$ROOT/runs.txt"
