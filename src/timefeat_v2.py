"""Time features under v2 labels, from per-line blame at the decision commit (replaces timefeat_carbon's per-file
author approximation). For each off-spec cluster at its decision month:
  burst     share of the value's current lines that were written inside the densest 60-day window
  authors   distinct authors of those lines
  span      days between the oldest and newest of those lines (log1p)
  survival  lines present now / distinct (file, prop) uses of the value ever seen up to now (snapshots)
Positive = single or scale event, negative = drift (v2labels.py). Pooled over systems, leave-one-out logistic.
  SNAPS="carbon eui ..." timefeat_v2.py  ->  notes/timefeat_v2.json
"""
import json, math, os, re, subprocess
from collections import defaultdict
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from desire import LDECL, SINGLE
from desire_multi import REPOS
from resolve import value
from simhist import desire_votes
from v2labels import rows as v2rows, POSITIVE


def blame_lines(R, commit, path):
    out = subprocess.run(["git", "-C", R, "blame", "--line-porcelain", commit, "--", path],
                         capture_output=True, text=True, errors="replace").stdout
    rec, res = {}, []
    for line in out.splitlines():
        if line.startswith("author-mail "):
            rec["a"] = line[12:].strip("<>")
        elif line.startswith("author-time "):
            rec["t"] = int(line[12:])
        elif line.startswith("\t"):
            res.append((rec.get("a"), rec.get("t"), line[1:]))
            rec = {}
    return res


def feats(row, K, R, cache):
    v, s = row["value"], K.S[row["idx"]]
    paths = {l[4] for l in s["lits"] if l[3] == v}
    lines = []
    for p in paths:
        key = (s["commit"], p)
        if key not in cache:
            cache[key] = blame_lines(R, s["commit"], p)
        for a, t, txt in cache[key]:
            mm = LDECL.match("x:" + txt.strip())
            if mm and SINGLE.match(mm.group("val").strip()) and value(mm.group("val").strip(), {}) == ("px", v):
                lines.append((a, t))
    if not lines:
        return None
    ts = sorted(t for _, t in lines)
    best = max(sum(1 for x in ts if a <= x <= a + 60 * 86400) for a in ts)
    ever = {(l[0], l[1]) for snap in K.S[:row["idx"] + 1] for l in snap["lits"] if l[3] == v}
    now = {(l[0], l[1]) for l in s["lits"] if l[3] == v}
    return dict(burst=best / len(ts), authors=len({a for a, _ in lines}), span=math.log1p((ts[-1] - ts[0]) / 86400),
                survival=len(now) / max(1, len(ever)), lines=len(lines))


if __name__ == "__main__":
    systems = os.environ.get("SNAPS", "carbon eui").split()
    D = []
    for key in systems:
        rows, K = v2rows(key)
        cache = {}
        for r in rows:
            if r["label"] in POSITIVE + ("drift",):
                f = feats(r, K, REPOS[key]["path"], cache)
                if f:
                    D.append(dict(r, **f))
        print(key, "scored", sum(1 for d in D if d["system"] == key), flush=True)
    y = np.array([d["label"] in POSITIVE for d in D], int)
    out = {"n_pos": int(y.sum()), "n_neg": int(len(y) - y.sum()), "base_rate": round(float(y.mean()), 3),
           "medians": {lab: {k: round(float(np.median([d[k] for d in D if (d["label"] in POSITIVE) == lab])), 2)
                             for k in ("burst", "authors", "span", "survival", "rel")} for lab in (True, False)}}
    rng = np.random.default_rng(0)

    def ci(sc):
        a = [roc_auc_score(y[i], sc[i]) for i in (rng.integers(0, len(y), len(y)) for _ in range(2000)) if 0 < y[i].sum() < len(i)]
        return [round(float(np.percentile(a, 2.5)), 2), round(float(np.percentile(a, 97.5)), 2)]
    for k in ("burst", "authors", "span", "survival", "rel", "grid4"):
        sc = np.array([d[k] for d in D], float)
        out[f"direct {k}"] = dict(auc=round(roc_auc_score(y, sc), 3), ci=ci(sc))
    sets = {"snapshot (rel, files, uses)": ["rel", "files", "n"], "time (burst, authors, span, survival)": ["burst", "authors", "span", "survival"],
            "snapshot + time": ["rel", "files", "n", "burst", "authors", "span", "survival"]}
    for name, cols in sets.items():
        X = np.array([[math.log1p(d[k]) if k in ("n", "files", "authors") else d[k] for k in cols] for d in D], float)
        X = (X - X.mean(0)) / (X.std(0) + 1e-9)
        p = np.array([LogisticRegression(class_weight="balanced").fit(X[np.arange(len(y)) != k], y[np.arange(len(y)) != k]).predict_proba(X[k:k + 1])[0, 1] for k in range(len(y))])
        out[f"LOO {name}"] = dict(auc=round(roc_auc_score(y, p), 3), ci=ci(p))
    votes = np.array([desire_votes(d) >= 2 for d in D])
    out["pre-specified votes"] = dict(precision=round(float(y[votes].mean()), 3) if votes.any() else None, flagged=int(votes.sum()),
                                      recall=round(float(y[votes].sum() / y.sum()), 3))
    json.dump(dict(out, rows=D), open("../notes/timefeat_v2.json", "w"), indent=1)
    for k, v in out.items():
        print(f"{k:42s} {v}")
