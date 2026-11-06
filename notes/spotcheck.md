# Carbon label spot-check (2026-11-05)

20 labels drawn with random.seed(20) from data/mined/carbon_resolved.json, judged by reading each diff hunk.
Raw hunks: notes/spotcheck_raw.txt.

| # | label | verdict |
|---|---|---|
| 1 | padding-right rem(50px) -> $spacing-09 + $spacing-03 | correct (token arithmetic; unscorable) |
| 2 | margin-right rem(16px) -> $spacing-md | correct |
| 3 | width rem(48px) -> $input-xl-height | correct (component token) |
| 4 | margin-left rem(12px) -> $spacing-sm | correct |
| 5 | right rem(40px) -> $carbon--spacing-05 | ERROR: redesign (toggle repositioned 40 -> 16 px) |
| 6 | inset-inline-end to-rem(96px) -> $spacing-12 | correct |
| 7 | margin-top 1rem -> $spacing-md | correct |
| 8 | padding 0.75rem -> $spacing-sm (shorthand part) | correct |
| 9 | right 0.5rem -> $carbon--spacing-05 | ERROR: redesign (8 -> 16 px in a feature commit) |
| 10 | height rem(32px) -> $input-sm-height | correct |
| 11 | color #393939 -> $text-04 | ERROR: mispaired inside a 750-line vendored-CSS rewrite |
| 12 | padding-top rem(8px) -> $spacing-xs | correct |
| 13 | margin-top rem(6px) -> $spacing-xs | correct (near miss snapped) |
| 14 | margin-top rem(20px) -> $spacing-lg | correct (off-scale value snapped up) |
| 15 | padding-bottom rem(12px) -> $spacing-sm | correct |
| 16 | padding 1rem -> $carbon--spacing-05 (shorthand part) | correct |
| 17 | padding 2rem -> $spacing-xl (shorthand part) | correct |
| 18 | padding-left rem(12px) -> $spacing-sm | correct |
| 19 | margin-right rem(2px) -> $spacing-sm | ERROR: redesign (2 px equals $spacing-3xs exactly; author chose 12 px) |
| 20 | padding-bottom 0.125rem -> $spacing-3xs | correct |

Error rate 4/20 = 20%: 1 mispairing (5%), 3 redesigns (15%). All 3 redesigns are kind=changed.
Rules added after this check: R1 skip hunks with > 40 removed lines; R2 kind=changed labels are excluded
from the drift headline and reported separately as "tokenized with a value change".
