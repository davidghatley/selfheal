# Step 5: more design systems (2026-11-06)

**Question:** does the Carbon result hold elsewhere, and can anything tell a future token from drift?

1. **Fixing drift replicates, on small samples.** Nearest token = the human's choice: Carbon 153/157, Polaris 13/14,
   EUI 6/6. Few single-literal swaps survive in those histories (Polaris migrated with codemods, `polaris-migrator`;
   EUI moved to CSS-in-JS), so the samples are small.
2. **Carbon's "7 desire paths" were mostly one decision.** With tokens defined as shared variables, 5 of Carbon's
   token-earning values arrived together in the Jan 2018 spacing scale (PR #506). Only 2px was added on its own. The
   v1 labels also counted component-local variables as tokens. The video's "7 became tokens" is true of v1 labels
   but the 7 are not independent.
3. **Values mostly earn tokens in batches.** Pooled (Carbon + EUI): 11 positives = 4 single additions + 7 in scale
   events, vs 42 drift. When teams build or rebuild a scale, they codify what's already typed.
4. **Prevalence predicts, history didn't.** Direct AUC (bootstrap 95% CI) on the 53 pooled clusters:
   share of all hand-typed values 0.87 (0.76–0.95); on the 4px grid 0.74 (0.61–0.84); files 0.71; uses 0.69;
   decision year 0.56 (so not just "early values win"). LOO logistic on size features 0.81 (0.68–0.92).
   The 4px-grid rule catches 10 of 11 positives but flags 18 drift values too (precision 0.36 vs base 0.21).
5. **GitLab UI has no clusters at all**: utility-class styling leaves almost no hand-typed values to drift.

Caveats: 11 positives across 2 systems, 7 of them from 2 scale events; features chosen after looking at Carbon v1;
rel and size are measured at the first month a value qualified.

Next: per-line blame for time features on v2 labels; Polaris desire paths (needs per-era token tables); a CSS-in-JS
system (Atlassian, Primer) where tokens are TS objects.
