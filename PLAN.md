# Plan

Goal: show that treating design-system consistency as inference (token mixture + context field) beats
heuristic drift detection, measure frontier agents on the same task, and test healing/spec-evolution laws.

- [x] Synthetic benchmark with ground truth (exact, near, ambiguous, cluster, intentional) — 2026-11-05
- [x] Baselines: exact match, nearest token, nearest + repeat-count
- [x] Mixture detector, with and without context field
- [x] Agent arm (seeds 1-2): Opus 5.5 0.94, Codex 0.93, Sonnet 0.88; mixture+context 0.93. Gemini CLI unauthenticated
- [x] Healer: lowest-entropy-first iteration, energy, behavior preservation, idempotence
- [x] Spec evolution: new tokens; lens-law / oscillation tests
- [ ] Real-repo check (an open-source app with tokens)
- [x] First write-up into the doc (2026-11-05)

## Decisions
- 2026-11-05: Σ_k declared by scale geometry (half the gap to the nearest token, OKLab for color, log-px for sizes).
- 2026-11-05: Agents get file tools only (no unrestricted shell); Codex keeps its workspace-write sandbox.
- 2026-11-05: Cluster rule fixed: a token at a group's centre explains it (otherwise the spec regrew every pass).
