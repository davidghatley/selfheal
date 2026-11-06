"""Step 5: replicate the Carbon drift test on Shopify Polaris (data/mined/polaris.jsonl, mined by mine.py).
Spacing only; shorthands split into one label per changed position: `prop: <length>` -> `prop: spacing(x)` | `var(--p-space-N)`.
Token values come from Polaris's published scales, by naming era:
  v1-v8  spacing(<variant>)  from @shopify/polaris-tokens (npm, not in this repo): extra-tight 4, tight 8,
                              base-tight 12, base 16, loose 20, extra-loose 32 (px)
  v9-v11 --p-space-N          N x 4 px; 05 = 2, 025 = 1           (polaris-tokens/src, checked in git)
  v12+   --p-space-NNN        NNN / 100 x 4 px (size.ts); scale adds 150 = 6 px
Scored like eval_mined.py: does the nearest token on that era's scale equal the value the human chose?
"""
import json, math, re
from collections import Counter

SPACING = {"extra-tight": 4, "tight": 8, "base-tight": 12, "base": 16, "": 16, "loose": 20, "extra-loose": 32}
V9 = sorted({1, 2} | {n * 4 for n in (1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 28, 32)})
V12 = sorted({1, 2, 4, 6, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96, 112, 128})
LIT = re.compile(r"^(-?\d*\.?\d+)(px|rem)$")


def token(t):
    if m := re.fullmatch(r"spacing\(([\w-]*)\)", t):
        return SPACING.get(m.group(1)), sorted(set(SPACING.values()))
    if m := re.fullmatch(r"var\(--p-space-(\d+)\)", t):
        n = m.group(1)
        if len(n) >= 3:
            return int(n) / 100 * 4, V12
        return ({"05": 2, "025": 1}.get(n) or int(n) * 4), V9
    return None, None


def nearest(v, scale):
    lg = [math.log(s) for s in scale]
    sig = {s: min(abs(a - b) for b in lg if b != a) / 2 for s, a in zip(scale, lg)}
    return min(scale, key=lambda s: abs(math.log(v) - math.log(s)) / sig[s])


if __name__ == "__main__":
    rows, skip = [], Counter()
    pairs = []
    for l in map(json.loads, open("../data/mined/polaris.jsonl")):
        a, b = l["literal"].split(), l["token"].split()
        if len(a) == len(b) > 1:  # shorthand: one label per changed position
            pairs += [dict(l, literal=x, token=y) for x, y in zip(a, b) if x != y]
        else:
            pairs.append(l)
    for l in pairs:
        m = LIT.match(l["literal"].strip())
        tv, scale = token(l["token"].strip())
        if not m or tv is None:
            skip["not a single spacing value"] += 1
            continue
        v = float(m.group(1)) * (16 if m.group(2) == "rem" else 1)
        if v <= 0 or tv <= 0:
            skip["zero/negative"] += 1
            continue
        kind = "exact" if abs(v - tv) < 0.01 else "near" if abs(v - tv) <= 2 else "changed"
        rows.append(dict(commit=l["commit"][:8], date=l["date"], lit=v, tok=tv, kind=kind,
                         exact=v in scale and v == tv, nearest=nearest(v, scale) == tv))
    out = {"skipped": dict(skip), "kinds": dict(Counter(r["kind"] for r in rows))}
    for k in ("exact", "near", "changed", "exact+near"):
        sub = [r for r in rows if (r["kind"] in ("exact", "near") if k == "exact+near" else r["kind"] == k)]
        if sub:
            out[k] = dict(n=len(sub), commits=len({r["commit"] for r in sub}), exact=round(sum(r["exact"] for r in sub) / len(sub), 3),
                          nearest=round(sum(r["nearest"] for r in sub) / len(sub), 3), nearest_correct=sum(r["nearest"] for r in sub))
    json.dump(dict(out, rows=rows), open("../notes/polaris_eval.json", "w"), indent=1)
    for k, v in out.items():
        print(k, v)
