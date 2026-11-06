"""Video data straight from the repo's data files -> src/data.json. Run from share/video/."""
import json
S = json.load(open("../../data/mined/snapshots.json"))
# 01: hand-written .scss 48px declarations present on 1 Jan 2018 (last snapshot before $spacing-3xl), in order of first appearance
pre = next(s for s in S if s["month"] == "2018-01")
keys = sorted({(x[0], x[1]) for x in pre["lits"] if x[3] == 48.0 and x[0].endswith(".scss")})
first = {}
for s in S:
    for x in s["lits"]:
        k = (x[0], x[1])
        if x[3] == 48.0 and k in keys:
            first.setdefault(k, s["month"])
lines = sorted(keys, key=lambda k: (first[k], k))
# 03: per-label result of the nearest-token snap, in history order
R = [r for r in json.load(open("../../notes/mined_eval_rows.json")) if r["kind"] in ("exact", "near")]
R.sort(key=lambda r: r["date"])
# 04: every off-spec cluster with its outcome
C = json.load(open("../../data/mined/clusters.json"))
json.dump(dict(
    lines=[dict(file=f, prop=p, month=first[(f, p)]) for f, p in lines],
    fixes=[bool(r["nearest"]) for r in R],
    clusters=[dict(v=c["value"], label=c["label"], month=c["month"]) for c in C],
), open("src/data.json", "w"), indent=0)
print(len(lines), "lines;", len(R), "fixes,", sum(not r["nearest"] for r in R), "misses;", len(C), "clusters")
for f, p in lines: print(" ", first[(f, p)], f, p)
