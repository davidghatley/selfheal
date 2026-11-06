"""Step 5: the drift test on another SCSS design system (EUI). Like eval_mined.py, without Carbon's special cases.
Candidate tokens = the system's size scale at the label commit's parent (names matching SCALE), resolved by resolve.py.
  eval_scss.py eui  ->  notes/eui_eval.json
"""
import json, math, re, sys
from collections import Counter
from resolve import defs_at, value
from eval_mined import sigma

CFG = {"eui": dict(path="/mnt/work/selfheal-repos/eui", scale=re.compile(r"^euiSize(XXS|XS|S|M|L|XL|XXL|XXXL|XXXXL)?$"))}

if __name__ == "__main__":
    key = sys.argv[1]
    cfg = CFG[key]
    L = [json.loads(l) for l in open(f"../data/mined/{key}.jsonl")]
    pairs = []
    for l in L:
        a, b = l["literal"].split(), re.sub(r"/\*.*?\*/", "", l["token"]).split()
        pairs += [dict(l, literal=x, token=y) for x, y in zip(a, b) if x != y] if len(a) == len(b) > 1 else [dict(l, token=" ".join(b))]
    rows, skip = [], Counter()
    for l in pairs:
        defs = defs_at(cfg["path"], l["commit"] + "^")
        lv, tv = value(l["literal"], defs), value(l["token"], defs)
        if not (lv and tv and lv[0] == tv[0] == "px" and lv[1] > 0 and tv[1] > 0):
            skip["not a resolvable positive length"] += 1
            continue
        scale = sorted({v[1] for k in defs if cfg["scale"].match(k) and (v := value("$" + k, defs)) and v[0] == "px" and v[1] > 0})
        if tv[1] not in scale:
            skip["token value off the size scale"] += 1
            continue
        sg = sigma(scale)
        near = min(scale, key=lambda s: abs(math.log(lv[1]) - math.log(s)) / sg[s])
        d = abs(lv[1] - tv[1])
        rows.append(dict(commit=l["commit"][:8], lit=lv[1], tok=tv[1], kind="exact" if d < .01 else "near" if d <= 2 else "changed",
                         exact=lv[1] == tv[1], nearest=near == tv[1]))
    out = {"skipped": dict(skip), "kinds": dict(Counter(r["kind"] for r in rows))}
    sub = [r for r in rows if r["kind"] in ("exact", "near")]
    if sub:
        out["exact+near"] = dict(n=len(sub), commits=len({r["commit"] for r in sub}), nearest_correct=sum(r["nearest"] for r in sub),
                                 nearest=round(sum(r["nearest"] for r in sub) / len(sub), 3), exact=round(sum(r["exact"] for r in sub) / len(sub), 3))
    json.dump(dict(out, rows=rows), open(f"../notes/{key}_eval.json", "w"), indent=1)
    print(out)
