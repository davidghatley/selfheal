#!/usr/bin/env bash
# Step 4 fair rerun: every arm gets SANDBOXED code execution (Claude: bubblewrap Bash sandbox, writes confined to the
# workdir, no network; Codex: workspace-write sandbox). Workdirs live outside data/ so truth.json is unreachable.
# Usage: scripts/run_agents2.sh <workroot> <seed> <opus|sonnet|codex> <full|hybrid>
set -u
ROOT=$1; SEED=$2; ARM=$3; MODE=$4
P=$(cd "$(dirname "$0")/.." && pwd)
W=$ROOT/$MODE-$ARM-s$SEED; rm -rf "$W"; mkdir -p "$W"
cp -r "$P/data/s$SEED/repo/." "$W/"
"$P/.venv/bin/python" -I "$P/src/extract.py" "$W" > "$W/sites_all.json"
if [ "$MODE" = hybrid ]; then
  "$P/.venv/bin/python" -I -c "import json,sys; u=set(json.load(open(sys.argv[2]))); print(json.dumps([s for s in json.load(open(sys.argv[1])) if s['id'] in u], indent=1))" \
    "$W/sites_all.json" "$P/data/s$SEED/uncertain_ids.json" > "$W/sites.json"
else
  mv "$W/sites_all.json" "$W/sites.json"
fi
rm -f "$W/sites_all.json"
PROMPT=$(cat "$P/scripts/agent_prompt2.md")
[ "$MODE" = hybrid ] && PROMPT="$PROMPT

Note: sites.json lists only the sites that are still undecided; every other hardcoded literal in the repo has already been handled, so you only need to answer for these."
cd "$W"; t0=$(date +%s)
case $ARM in
  opus|sonnet) claude -p "$PROMPT" --model "claude-$ARM-5-5" --output-format json \
       --settings '{"sandbox":{"enabled":true,"autoAllowBashIfSandboxed":true,"allowUnsandboxedCommands":false}}' \
       --allowedTools "Read Glob Grep Write Bash" < /dev/null > run.log 2>&1 ;;
  codex) codex exec --skip-git-repo-check --sandbox workspace-write -c model_reasoning_effort=high "$PROMPT" < /dev/null > run.log 2>&1 ;;
esac
echo "$MODE $ARM s$SEED exit=$? secs=$(( $(date +%s) - t0 ))" | tee -a "$ROOT/runs.txt"
