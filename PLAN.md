# Plan

Goal: show that treating design-system consistency as inference (token mixture + context field) beats
heuristic drift detection, measure frontier agents on the same task, and test healing/spec-evolution laws.

- [x] Synthetic benchmark with ground truth (exact, near, ambiguous, cluster, intentional) — 2026-11-05
- [x] Baselines: exact match, nearest token, nearest + repeat-count
- [x] Mixture detector, with and without context field
- [x] Agent arm (seeds 1-2): Opus 5.5 0.94, Codex 0.93, Sonnet 0.88; mixture+context 0.93. Gemini CLI unauthenticated
- [x] Healer: lowest-entropy-first iteration, energy, behavior preservation, idempotence
- [x] Spec evolution: new tokens; lens-law / oscillation tests
- [x] Real-repo check: Carbon history mined (docs/mining.md); nearest 0.975 vs mixture+context 0.962 on 157 labels
- [x] Iteration fixes: earlier degradation was a healer bug; all variants equal one-shot
- [x] Time features: help on simulated history (newP 0.55->0.87), not on Carbon (AUC 0.71 -> 0.61)
- [x] Matched-tools agent rerun, 5 seeds: Opus 0.969, Codex 0.914, Sonnet 0.844; hybrid helps Sonnet only
- [x] Step 5, more systems: drift fix replicates (Polaris 13/14, EUI 6/6); v2 labels show Carbon's desire paths were mostly one scale event; share of typed values predicts (AUC 0.87, Carbon+EUI) — notes/step5.md
- [x] Step 6, 15 systems: near-miss snapping 82% (103 off-scale fixes, CI 71-91%), context adds nothing; prevalence predicts token-earning values across systems (held-out AUC 0.68-0.71), time history adds ~0 — notes/step6.md
- [ ] Package the benchmark (synthetic + mined splits); Gemini CLI needs auth
- [x] First write-up into the doc (2026-11-05)

## Decisions
- 2026-11-05: Σ_k declared by scale geometry (half the gap to the nearest token, OKLab for color, log-px for sizes).
- 2026-11-05: Agents get file tools only (no unrestricted shell); Codex keeps its workspace-write sandbox.
- 2026-11-05: Cluster rule fixed: a token at a group's centre explains it (otherwise the spec regrew every pass).
- 2026-11-05: Step 4 agents all get sandboxed code execution (Claude bubblewrap sandbox; Codex workspace-write).
- 2026-11-05: Mined Carbon labels are the headline; synthetic results are secondary (author overlap).
- 2026-11-06: v2 mining rules (hand-written .scss only, tokens = vars used in >= 3 files, single vs scale-event outcomes); v1 Carbon numbers stay as the committed headline, v2 reported alongside.
- 2026-11-06: Repo made public (MIT).
- 2026-11-06: 'near' drift = off-scale literal only; Atlassian excluded (squashed bot mirror, codemod-driven tokenization).
