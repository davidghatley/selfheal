# Step 6: every open design system I could mine (2026-11-06)

**Systems (15 with desire-path labels):** Carbon, Elastic EUI, Bootstrap (Less → SCSS), Primer CSS, Material
Components Web, Ant Design (Less), GOV.UK Frontend, USWDS, Clarity, Spectrum CSS (CSS custom properties),
Foundation, Semantic UI (Less theme files), PatternFly, Salesforce Lightning, Blueprint. Clones in
/mnt/work/selfheal-repos. Mined with `desire_multi.py` (SCSS, Less and CSS variables), labelled with `v2labels.py`,
time features from per-line `git blame` (`timefeat_v2.py`), pooled in `pooled_v2.py`, drift fixes in `eval_multi.py`.

Not usable: GitLab UI (utility classes, no clusters), Bulma (indented Sass), Atlassian (public mirror is squashed
bot commits; tokenization largely by codemod, so labels would measure the codemod), Primer React and Polaris v12+
(tokens in TS / CSS-in-JS; Polaris covered by scale tables in step 5).

## 1. Fixing drift: solved for exact matches, ~4 in 5 for real near-misses

`notes/drift_multi/*.json`, `notes/drift_multi_summary.json`. 937 scorable single-value drift fixes in 10 systems.

| Kind | n | Nearest token = human's choice | 95% CI (commit bootstrap) |
|---|---|---|---|
| exact (literal already equals a token's value) | 695 | 100% | — |
| near (OFF-scale literal, within 2 px) | 103 (41 commits) | **81.6%** | 70.5–90.7% |
| near, without Ant Design | 67 | 73.1% | 56.4–85.1% |
| near, with file context (mixture + context) | 103 | 80.6% | 69.0–89.5% |
| changed (> 2 px, or an on-scale value swapped) | 139 | (a design change, not drift) | |

The earlier "97.5%" (Carbon) and "153 of 157" are right but mostly exact matches (134 of 157), which any
exact-match linter catches. On values genuinely off the scale, nearest-token snapping picks the human's token about
four times in five, and file context doesn't move it (31 of 103 near-misses have any same-property token use in
their file). Per system (near): Ant Design 35/36, Carbon 18/20, Bootstrap 13/16, GOV.UK 9/11, Primer 8/14, Clarity 0/4.

## 2. Which repeated values earn a token

`notes/pooled_v2.json`. 230 resolved clusters: 73 earned a token (23 single additions, 50 in scale events) vs 157
drift. 18 positives are component variables and 23 are Semantic UI's single theming event (`notes/spotcheck_v2.md`).
AUCs are direct (no fitting) unless "model"; CIs resample systems, then clusters.

| Cut | pos / neg | share of typed values | uses | files | burst | authors | survival | snapshot model, held-out system | + time |
|---|---|---|---|---|---|---|---|---|---|
| all 15 systems | 73 / 157 | 0.69 (0.48–0.82) | 0.73 | 0.70 | 0.65 | 0.40 | 0.50 | 0.71 (0.57–0.81) | 0.75 |
| without Semantic UI | 50 / 155 | 0.75 (0.60–0.84) | 0.70 | 0.68 | 0.64 | 0.47 | 0.46 | 0.69 (0.56–0.80) | 0.71 |
| without Semantic UI, Clarity | 43 / 135 | 0.74 (0.56–0.85) | 0.72 | 0.69 | 0.62 | 0.49 | 0.44 | 0.68 (0.54–0.81) | 0.70 |
| system-level tokens only, without Semantic UI | 32 / 155 | 0.77 (0.61–0.87) | 0.71 | 0.69 | 0.65 | 0.47 | 0.45 | 0.68 (0.52–0.83) | 0.66 |

- **Prevalence is the signal, and it transfers.** A model trained on the other systems ranks a held-out system's
  clusters at 0.68–0.71 AUC in every cut. The single best feature is the value's share of all hand-typed values.
- **History adds little.** Time features alone: 0.56–0.58 held-out (CIs include 0.5). On top of the snapshot:
  -0.02 to +0.04. Burst (values typed in a tight window) is the only time signal with lift; fewer authors leans
  positive; survival is flat or backwards in every cut. The pre-specified votes rule flags 91% of clusters
  (precision 0.31 = base rate).
- **The 4px grid doesn't generalise** (0.74 on Carbon + EUI; 0.56–0.62 pooled).
- **Tokens mostly arrive in batches**: 50 of 73 in months that added >= 4 token values at once.
- **As a ranking tool** (`notes/pooled_ranking.json`): each system's top 20% by the held-out model are real future
  tokens 43–51% of the time vs base rates of 24–32%, catching a third of them.

## What changes in the story

1. "Your linter already handles this" holds for exact matches; for off-scale values it's ~80%, and context doesn't help.
2. "Nothing predicts desire paths" was a Carbon-only result. Across 15 systems, how common a value is predicts it
   moderately and transfers; time history still adds almost nothing.
3. The decision is mostly made in batches, when a team builds or rebuilds its scale.

Caveats: positives cluster in a few events per system (CIs resample systems to reflect that); the "token" rule
(shared by >= 3 files) is a heuristic, checked by hand in notes/spotcheck_v2.md; features measured at the first month
a value qualified; Polaris and others migrated partly with codemods, which can make labels reflect a tool's rule.
