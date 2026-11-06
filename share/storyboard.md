# Storyboard: "When does a value earn a token?"

Vertical 1080×1920, 30 fps, 72 s. Built in the tasty_tunez promo style: paper `#eeede7`, ink `#16181d`, cobalt
`#2236b0`, vermilion `#ee5228` (once per beat), Hopscotch for the one big line, Tick 35 labels, Stem 7 numbers,
Hoop for running text. Chrome on every plate: typed chapter label top left (`01 · THE MOMENT`), a six-cell progress
bar top right, rules under the header and over the footer, a small source footer.

Audience: senior product designers. Sound off must work: every beat's point is in its big line.
Every number traces to `claims.md`.

| # | Time | Chapter | Big line (Hopscotch) | Visual | Footer |
|---|---|---|---|---|---|
| 01 | 0.0–9.0 | THE MOMENT | "Someone typed 48px." → "Again." → "And again." | 14 real declarations type in one per 0.3 s, file name muted, `48px` in vermilion (`_card.scss  height: 48px;`, `_modal.scss  margin-bottom: 48px;` …). A Stem 7 date counter rolls FEB 2016 → JAN 2018. Tally lands at 6.6 s: `14 TIMES · 10 FILES · NO TOKEN` | CARBON DESIGN SYSTEM · IBM · REAL GIT HISTORY, MINED LOCALLY |
| 02 | 9.0–20.0 | THE QUESTION | "A mistake? Or a decision the system hasn't caught up to yet?" → "A desire path." (with running text: "The shortcut people wear into the grass, where they actually walk instead of the paved route.") → "Two years later, Carbon paved it." | Pixel lawn: faint grass cells, a paved L of cobalt cells, a diagonal worn path stepping in cell by cell in vermilion. Label: "DESIRE PATH · THE TRAIL WORN WHERE PEOPLE ACTUALLY WALK". At 16.5 s the diagonal turns cobalt (paved) and a code card types `$spacing-3xl → 48px · ADDED 17 JAN 2018` | same |
| 03 | 20.0–30.0 | WHAT'S SOLVED | "Your linter already handles this." | 157 cells (16 × 10 grid) fill one per 25 ms: cobalt = nearest token is what the human picked, vermilion = it wasn't (4 cells). Stem 7 number rolls to `97.5%`. Running text: "Snap to the nearest token: it picks what the human picked, 153 of 157." | 157 REAL DRIFT FIXES · 20 COMMITS · CARBON 2015–2026 |
| 04 | 30.0–44.0 | THE REAL PROBLEM | "116 values kept repeating. 7 became tokens." → "In one snapshot, they look the same." | 116 dots build in cells; at 33 s seven light vermilion (2, 4, 32, 40, 48, 56, 300 px). At 37 s the dots slide up and two identical cards appear: `48px · FEB 2016 · 3 USES · 3 FILES` and `42px · FEB 2016 · 3 USES · 3 FILES`. At 40.5 s outcomes reveal: 48px → BECAME `$spacing-3xl`; 42px → "Faded. No token." Small print: "7 IS A SMALL SAMPLE." | 116 OFF-SPEC CLUSTERS · ≥3 USES IN ≥2 FILES · 24-MONTH OUTCOME |
| 05 | 44.0–61.0 | 4 TESTS | (none; the rows carry it) | Four rows like the tunez ten tests, one every ~3.6 s: tiny chart left, label + result + verdict right. 01 PICK THE RIGHT TOKEN · SYNTHETIC: "189 of 191 right" · SOLVED. 02 TYPO OR NEW TOKEN? · Carbon 13% vs synthetic 55% · "13% right on Carbon: 7 of 54 real" · OPEN. 03 ADD TIME HISTORY (burst, authors, survival): two bar pairs, simulated 55 → 87%, Carbon 13 → 14% · "Near chance on Carbon" · OPEN. 04 FRONTIER AGENTS · SYNTHETIC: Opus 5.5 96.9, Codex 91.4, our model 89.7, Sonnet 5.5 84.4 · "The best agents win" · AGENTS AHEAD. | SYNTHETIC = 5 GENERATED REPOS · CARBON = REAL HISTORY |
| 06 | 61.0–72.0 | YOUR TURN | "Picking the token is solved." → "How does your team decide when a value earns a token?" | Paper, the question large. A link line under it (placeholder until chosen). 68.0 s: the dh mark builds cell by cell, "David Hatley · design · AI/ML · generative tools". | LINK (placeholder) |

## Sound
Procedural only (tasty_tunez `sfx` engine): a soft pad bed in D minor, a key click per typed line in 01, cell clicks
for the lawn and grids, pops for the four tests, one chime when the token is paved (02) and one when the question
lands (06). Mastered to −14 LUFS. Nothing carries meaning that the screen doesn't.

## Square still (1080×1080)
Beat 04's reveal: the two identical cards (48px vs 42px, same month, same counts) with their outcomes, under the line
"In one snapshot, a habit and a typo look the same."

## Changes after review
See process.md: 98.9% became "189 of 191" (it rounds to 99.0%), test 02 leads with Carbon, the habit/typo line was
cut (42px is not known to be a typo), and the desire-path beat gained one plain sentence.
