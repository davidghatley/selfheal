# On-screen claims

Every number in the video, the frames it appears in, where it comes from, and what `share/recompute.py` got when
re-deriving it from the repo's data (output in `share/claims.json`; the Carbon nearest-token figure was also re-run
against git by `share/recheck_mined.py`). The video reads `claims.json` directly, so the render can't drift from it.

| Beat | On-screen claim | Shown | Source (data → script) | Recomputed | Status |
|---|---|---|---|---|---|
| 01 | 14 hand-written `48px` declarations, 10 files, no 48px token | "14 TIMES · 10 FILES · 0 TOKENS", 14 code lines | `data/mined/snapshots.json` (snapshot 2018-01 = Carbon on 1 Jan 2018, commit 16e35e0b) | 14 uses, 10 files, 0 font sizes | ✅ `.scss` only (see note 1) |
| 01 | Date runs FEB 2016 → JAN 2018 | counter | first snapshot with a hand-written non-font 48px: 2016-02 | 2016-02 | ✅ |
| 02 | `$spacing-3xl → 48px`, added 17 Jan 2018, PR #506 | code card, footer | Carbon git: `25f6afefc8` "feat(components): Add spacing variables (#506)", `$spacing-3xl: $spacing-baseline * 3`; resolved to 48px in `snapshots.json` 2018-02 `token_names` | `['spacing-3xl']` at 48px | ✅ |
| 02 | "Two years later" | big line | 2016-02 → 2018-01 | 23 months | ✅ (rounded) |
| 03 | 157 real drift fixes, 20 commits | label, footer | `data/mined/carbon_resolved.json` → `src/eval_mined.py` → `notes/mined_eval_rows.json` (exact + near labels) | 157 labels, 20 commits | ✅ |
| 03 | 97.5%, 153 of 157 | big number, running text | same; re-run against git by `recheck_mined.py` | 0.975, 153/157 | ✅ |
| 03 | 4 vermilion cells | grid | rows where nearest ≠ human's token | 4 | ✅ |
| 04 | 116 off-spec values kept repeating | big line, dots | `src/clusters.py` over `snapshots.json` (≥3 uses in ≥2 files, value no token has) | 116, identical to `data/mined/clusters.json` | ✅ |
| 04 | 7 became tokens: 2, 4, 32, 40, 48, 56, 300 px | big line, label | same; label `desire` | 7, those values | ✅ small sample, said on screen |
| 04 | 47 faded, 46 stayed without a token, 12 got a token nobody moved to, 4 too recent | small print | same; labels drift / unresolved / coincident / censored | 47 / 46 / 12 / 4 | ✅ |
| 04 | 48px and 42px, FEB 2016, 3 uses, 3 files each | cards | same; `pair_48px`, `pair_42px` | both 2016-02, 3, 3 | ✅ counts include compiled CSS (note 1) |
| 04 | 48px "By Jan 2018 became $spacing-3xl"; 42px "Faded. No token." | reveal | labels desire (tokened 2018-02 snapshot) / drift (share of literals halved within 24 months) | desire / drift | ✅ |
| 05.1 | Pick the right token: 189 of 191 right (synthetic) | test 01 | 5 synthetic seeds → `src/iterate.py` one-shot posteriors, ambiguous-class sites the model binds | 189/191 | ⚠️ the doc and brief say 98.9%; 189/191 = 98.95%, which rounds to 99.0%. Shown as "189 of 191" (note 2) |
| 05.2 | Every repeating value called a new token: 13% right on Carbon, 7 of 54 real | test 02 | `clusters.json`, desire / (desire + drift) | 0.13, 7 vs 47 | ✅ |
| 05.2 | Synthetic: 55% | test 02 | `src/detect.py` mixture + context `new_P`, mean of 5 seeds | 0.551 | ✅ |
| 05.3 | Simulated history: 55% → 87% | test 03 | `src/simhist.py` votes filter on the same 5 seeds (history is simulated, not data) | 0.551 → 0.870 | ✅ labelled "SIM." |
| 05.3 | Carbon: 13% → 14% | test 03 | `src/timefeat_carbon.py` pre-specified votes precision vs base rate | 0.130 → 0.136 | ✅ |
| 05.4 | Opus 5.5 96.9%, Codex 91.4%, our model 89.7%, Sonnet 5.5 84.4% | test 04 bars and note | `notes/agents2/full-*.json` (each run's actions) scored by `src/score.py`; model = mixture + context | 0.969 / 0.914 / 0.897 / 0.844 | ✅ synthetic, labelled |

Numbers kept off screen on purpose: AUC (0.71 → 0.61 on Carbon) because the audience doesn't use it; the 20%
spot-check error on mined labels, which applies mostly to the "value changed" labels the 157 exclude.

## Notes
1. The cluster miner (`src/desire.py`) counts compiled `.css` bundles as uses. Beat 01 uses hand-written `.scss` only.
   The 116 / 7 counts and the 3-use / 3-file cards are the miner's as committed, so compiled CSS can push a value
   over the "3 uses" threshold. Re-mining without `.css` would change the 116; that hasn't been done.
2. `notes/reliability_ambiguous.json` had no producing script; the 189/191 is now recomputed in `recompute.py`.
   The doc's "98.9%" should read 99.0% (or 189 of 191).
