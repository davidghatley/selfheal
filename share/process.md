# Research repo → vertical video post (process notes, skill draft)

## Surprises (logged as they happened)

1. **One headline number had no script.** `notes/reliability_ambiguous.json` (189 of 191 ambiguous bindings correct)
   was written ad hoc during step 1; no committed script produces it. `share/recompute.py` now recomputes it from the
   seeds (189/191, matches). Skill rule: a number without a producing script gets recomputed or doesn't go on screen.
2. **The cluster miner counts compiled CSS.** `src/desire.py` greps `*.css` too, so built bundles
   (`bluemix-components.css`, `main.css`) count as "uses". 48px peaks at 27 "uses" in Nov 2016, but only 11 are
   hand-written `.scss`. On screen I use hand-written `.scss` only: 14 declarations in 10 files on 1 Jan 2018, none of
   them font sizes. The 116 / 7 cluster counts are the miner's as committed (thresholds include compiled CSS); noted in
   claims.md, not re-mined.
3. **"Frontier agents beat the model" is true only for some.** Opus 5.5 (0.969) and Codex (0.914) beat the model
   (0.897); Sonnet 5.5 (0.844) does not. The test shows all four bars and says "the best agents".
4. **The real-data version of "typo or new token" is worse than the synthetic one.** Synthetic new-token precision is
   0.55; on Carbon, calling every repeated off-spec value a new token is right 7 of 54 times (13%). The test shows
   Carbon as the headline and synthetic as the secondary number, which also sets up the time-features test (14% vs 13%).
5. **No reusable vertical template in tasty_tunez.** The vertical (`DiveV` in `promo/src/tunez/Dive.tsx`) is one
   bespoke composition. Its palette (`P`), fonts (`F`, `useHouseFonts`), label styles (`label`, `px`, `sig`) and type
   motion (`Hop`, `TypeOn`, `Slot`, `Words`) are importable; the chrome (chapter label, cell progress bar, rules,
   footer) and the dh card are not exported, so they are re-implemented here from that file.
6. **A headline number was rounded down in the doc.** 189/191 = 98.95%, which rounds to 99.0%; the doc and brief say
   98.9%. The first render showed "99.0%" next to a brief that said 98.9%, so the test now shows "189 of 191 right".
   The doc still says 98.9% and should be corrected.
7. **A line the brief suggested overstated the data.** "A repeated typo and a real decision look the same": nothing
   says 42px was a typo, only that it faded. The beat says "In one snapshot, they look the same."
8. **Tick 35's 9 reads as a 3 at 20–24 px.** "191" rendered as "131". Digits in that face stay out of key facts;
   numbers go in Stem 7 or Hoop.

## What I did (generic: research repo → vertical post)

1. **Find the style source.** Locate the existing promo pipeline (here `tasty_tunez/promo`: Remotion, `cuts/*.json`
   timelines, `src/tunez/*`, `tools/build-*.sh`, `sfx/` cue sheets). Render a contact sheet of the reference vertical
   (`ffmpeg -vf "fps=1/3,scale=270:-1,tile=8x3"`) and read its composition source for the chrome, grid and type rules.
2. **Find the real moment.** Search the research data for one concrete, checkable instance that carries the whole
   story (here 48px in Carbon, traced month by month in `snapshots.json` and confirmed in git with `git log -S`).
   Check it holds up when filtered strictly (hand-written files only, no compiled output).
3. **Recompute every number.** Write `share/recompute.py`, which re-derives each on-screen figure from raw data, never
   from a summary JSON, and writes `claims.json`. Where a figure came from saved predictions, re-run the prediction
   too (`recheck_mined.py`). The video imports `claims.json`, so the screen and the claims can't disagree.
4. **Storyboard → timeline.** Beats as a table (time, chapter, one big line, visual, footer), committed before any
   code. Times go in `timeline.json`, which both the picture and the cue sheet read.
5. **Build the composition beside the research, not inside the style repo.** `share/video/` symlinks `kit` →
   the style repo and `node_modules` → its `node_modules`, imports the house palette, fonts and type motion from it,
   and renders with `--public-dir=kit/public`. The style repo is untouched.
6. **Data prep script.** `prep.py` turns repo data into `src/data.json` (the 14 code lines, the 157 per-fix results,
   the 116 clusters), so the grids and dots on screen are the real records.
7. **Draft, review, fix.** Render a draft (`--x264-preset=veryfast`), extract 1 fps sheets, read every frame. Fix
   (text that is clipped, wrapped badly, illegible, or overstated), re-render single stills to confirm, then render the
   final and re-check at 2 fps with half-second offsets.
8. **Sound.** A procedural cue sheet (`cue.py`) against the same timeline: a quiet pad and accents, mastered to
   −14 LUFS. Nothing in it is needed to follow the video.
9. **Stills.** A square `<Still>` composition that re-crops the strongest beat, and a poster frame from the vertical.
10. **Words.** Caption (3–5 lines, plain, ending on the question), a one-line Discord version, `claims.md`.

Build: `cd share/video && ./build.sh` (prep, sound, render, mux, stills; ~4 min on CPU). Recompute first if data changed.

## Reused from tasty_tunez (unchanged)
- Palette `P`, fonts `F` and `useHouseFonts` (Stem 7, Hoop, Tick 35, Hopscotch woff2 in `promo/public/tunez/`).
- `label`, `px`, `sig` styles; `Hop`, `TypeOn`, `Slot`, `Words` type motion; `cells`, `on`, `arrive` helpers.
- The DiveV layout: 48 px margins, chapter label + cell progress bar + rules at 88 px and H−120, footer at H−96,
  "N tests" rows with a chart left and label/result/note right; the dh mark end card (copied, not exported).
- The `sfx` engine (`python3 -m sfx`), its generators and mastering; Remotion 4.0.529 and its browser setup.

## Manual (judgement calls a skill can't automate yet)
- Picking the real moment and the side-by-side pair (48px vs 42px: same month, same counts, different fates).
- Deciding which candidate numbers go on screen and how to word them for designers ("our model", "in-between values",
  no AUC), and which suggested lines overstate the data.
- Choosing the hero visual for the square still.
- Reading the frames and spotting clipping, illegible glyphs, and lines up too briefly.

## Parameters a skill would need
| Parameter | Here |
|---|---|
| research repo + data paths | `selfheal`: `data/mined/*.json`, `notes/*.json` |
| style repo + composition to imitate | `tasty_tunez/promo`, `src/tunez/Dive.tsx` (`DiveV`) |
| format, fps, length | 1080×1920, 30 fps, 72 s; square 1080×1080 still |
| beats (chapter, big line, visual kind, data key) | `timeline.json` + `storyboard.md` |
| claims: id → recompute function → display format | `recompute.py` → `claims.json` |
| audience + jargon blocklist | senior product designers; no AUC, no "Gaussian", no math notation |
| footer / link | `close.link` in `timeline.json` (placeholder now) |
| sign-off card | dh mark, name, tagline |
| sound | pad key and chords, accent map per beat kind, target LUFS |
| encode | H.264 `--x264-preset=veryfast --crf=18`, AAC 192k |

Visual kinds that generalise: typed code lines, a cell grid of per-item outcomes, a dot field with highlighted items,
side-by-side identical cards with a reveal, test rows with cell bar charts, a question plate, an end card.
A skill would ship these as components that take `data.json` slices, with the chrome and the review loop built in.

## Still open
- The link in the close and on the end card is a placeholder ("LINK GOES HERE"); set `close.link` and rerun `build.sh`.
- The doc's 98.9% should be corrected to 99.0% (189 of 191).
