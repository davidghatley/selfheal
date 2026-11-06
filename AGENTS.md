# selfheal

Research code for the "Self-Healing Design Systems" doc (https://claude.ai/artifact/Qf6dBua3ZFmZJZBiJjNNVP):
drift detection as inference under a token mixture + context field, a healer, and spec evolution, compared
against exact-match / nearest-token heuristics and frontier agent harnesses (Claude Code, Codex, Gemini CLI).

## Rules
- Ask before downloads > 10 GB, sudo, or touching other projects' envs. Never delete; move aside.
- GPU (not needed here) only through `~/anime-pipeline/tools/gpu_run`.
- Agent runs: workdirs outside `data/` so `truth.json` is unreachable; no unrestricted shell for agents.

## Run
```
uv venv -p 3.12 .venv && VIRTUAL_ENV=.venv uv pip install numpy scipy scikit-learn
for s in 1 2 3 4 5; do .venv/bin/python src/gen.py $s data/s$s; done   # benchmark
cd src && ../.venv/bin/python bench.py                                    # all methods, 5 seeds
scripts/run_agents.sh <workroot> <seed> <opus|sonnet|codex|gemini>       # agent arm
.venv/bin/python src/score.py data/s1 <workroot>/opus-s1/actions.json    # score an agent
```

## Layout
- `src/gen.py` benchmark generator (tokens, roles, drift injection, truth labels)
- `src/extract.py` repo -> usage sites (all detectors see only this)
- `src/detect.py` methods; `src/score.py`, `src/bench.py` scoring
- `src/heal.py` healer + spec evolution experiments
- `notes/` results JSON and write-ups

## Traps
- The benchmark is synthetic and written by the same author as the method: context is informative by construction.
  Report that, and keep the agent arm (which sees the same context) as the fair comparison.
