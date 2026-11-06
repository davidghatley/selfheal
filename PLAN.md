# Plan

Goal: show that treating design-system consistency as inference (token mixture + context field) beats
heuristic drift detection, measure frontier agents on the same task, and test healing/spec-evolution laws.

- [x] Synthetic benchmark with ground truth (exact, near, ambiguous, cluster, intentional) — 2026-11-05
- [x] Baselines: exact match, nearest token, nearest + repeat-count
- [x] Mixture detector, with and without context field
- [ ] Agent arm: Claude Opus 5.5, Sonnet 5.5, Codex (gpt-6.1-terra), Gemini 3.5 Flash
- [ ] Healer: lowest-entropy-first iteration, energy, behavior preservation, idempotence
- [ ] Spec evolution: new tokens; lens-law / oscillation tests
- [ ] Real-repo check (an open-source app with tokens)
- [ ] Write-up into the doc

## Decisions
- 2026-11-05: Σ_k declared by scale geometry (half the gap to the nearest token, OKLab for color, log-px for sizes).
- 2026-11-05: Agents get file tools only (no unrestricted shell); Codex keeps its workspace-write sandbox.
