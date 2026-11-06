# Mining labels from Carbon history (2026-11-05)

Repo: carbon-design-system/carbon, 15,000 commits, 2015-06 to 2026-11 (clone in /mnt/work/selfheal-repos).

## Drift labels (src/mine.py, src/label_carbon.py)
- D1: in one non-merge commit, within one zero-context hunk of a .scss/.css file, a removed `prop: <literal>`
  is paired with an added declaration of the SAME prop whose value is a token reference with no literal left.
  Literal = px/rem/em length, hex, rgb(a). Token = `$name`, `ns.$name`, `var(--cds-…)`.
- R1: skip (commit, file) pairs that remove > 200 lines (rewrites, vendored CSS); added after the spot-check.
- Shorthands (`0 1rem` -> `0 $spacing-md`) split into one label per changed position.
- Values resolved at the label commit's parent from every `$name:` definition (rem x16, mini-units x8,
  arithmetic, var chains); v11 scale names fall back to the JS-generated scale (unchanged since v10).
- Kinds: exact (same value), near (<= 2 px apart), changed (value changed while tokenizing).

Counts: 269 pairs from 64 commits / 29 authors -> 262 after R1 -> 291 after shorthand split ->
204 resolved -> 192 scorable px labels on the spacing scale: 134 exact, 23 near, 35 changed.
The 157 exact+near labels come from 20 commits.

Spot-check (notes/spotcheck.md): 20 random labels, 4 errors (20%): 1 mispairing in a vendored rewrite (now removed
by R1), 3 redesigns, all kind=changed. Headline drift accuracy therefore uses exact+near only.

## Desire-path labels (src/desire.py, src/clusters.py)
137 monthly first-parent snapshots. Per snapshot: px token values, literal-only declarations, token references.
- Off-spec cluster: a px value no token has, used as a literal >= 3 times in >= 2 files; decision point = first such month.
- desire: a token with that value appears within 24 months AND the token's share of that value's uses rises >= 0.2
  from the month before the token to 12 months after (the literals migrated).
- coincident: a token with that value appears but the literals do not migrate (a value match, not the cluster).
- drift: no token within 24 months and the value's share of all literals halves (fixed or removed).
- unresolved: neither; censored: under 24 months of future.
Raw decline counts were confounded by codebase growth (the 2018-12 monorepo move doubled literal counts), hence shares.

Counts: 116 clusters: 7 desire, 12 coincident, 47 drift, 46 unresolved, 4 censored. All 19 token-creating
clusters date from 2015-2018, when the scale was being built.

## v2 rules, more systems (2026-11-06; src/desire_multi.py, src/clusters.py, src/grid_test.py)
Same monthly snapshots, three changes, applied to Carbon and Elastic EUI:
- Hand-written `.scss` only: compiled `.css`, vendor, dist/build, docs/site/storybook/examples and tests skipped.
  (v1 counted Carbon's compiled bundles: in mid-2016 they were 312 of 371 "literals".)
- A token is a shared variable: a `$name` that resolves to px AND is referenced from >= 3 files.
  (v1 counted any variable, including component-local ones like `$foo-height: 48px`.)
- Outcomes split by what happened the month the token arrived: **single** (< 4 new token values that month,
  literals migrate >= +0.2 share), **scale event** (>= 4 new values, literals migrate), **coincident** (no migration),
  drift / unresolved / censored as before.

Counts (notes/grid_test.json):
- Carbon: 94 clusters: 1 single (2px), 5 scale event (all the Jan 2018 spacing scale, PR #506: 4, 8, 24, 32, 48),
  5 coincident, 37 drift, 41 unresolved, 5 censored.
- EUI (7.3k commits, 2017-2026): 17 clusters: 3 single (12, 20, 48 px), 2 scale event (8, 16 px: the Oct 2017
  KUI -> EUI rewrite), 5 drift, 7 unresolved.
- GitLab UI: 0 clusters. It styles through utility classes, so hand-typed SCSS values never pile up.

Drift-fix replication (exact + near, nearest token = the human's choice): Polaris 13 of 14 (7 commits;
src/eval_polaris.py, scales by naming era), EUI 6 of 6 (3 commits; src/eval_scss.py). Both small.
