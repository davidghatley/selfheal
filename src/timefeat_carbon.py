"""Step 3 (Carbon): time features for off-spec clusters, using only history up to each decision month.
  burst    share of the cluster's current uses that first appeared in its densest 2-month window
  authors  distinct authors of commits touching those files in the months the uses first appeared
  survival uses present at decision / uses of that value ever seen before (persisted vs already fixed)
Snapshot features: n uses, n files, log-distance to the nearest token in sigma units, share of all literals.
Era baseline: the decision month alone. Leave-one-out logistic regression on desire vs drift.
"""
import json, math, subprocess
from collections import defaultdict
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from simhist import desire_votes

R = "/mnt/work/selfheal-repos/carbon"
S = json.load(open("../data/mined/snapshots.json"))
C = json.load(open("../data/mined/clusters.json"))


def ids(s, v):
    return {(l[0], l[1]) for l in s["lits"] if l[3] == v}


def month_add(ym, k):
    y, m = map(int, ym.split("-"))
    m += k
    y, m = y + (m - 1) // 12, (m - 1) % 12 + 1
    return f"{y:04d}-{m:02d}"


def authors(files_months):
    a = set()
    for f, ym in files_months:
        out = subprocess.run(["git", "-C", R, "log", "--first-parent", "--format=%ae", f"--since={month_add(ym, -1)}-01",
                              f"--until={ym}-01", "--", f":(glob)**/{f}"], capture_output=True, text=True).stdout
        a |= set(out.split())
    return a


def feats(c):
    i, v = c["idx"], c["value"]
    now = ids(S[i], v)
    first, ever = {}, set()
    for s in S[:i + 1]:
        for x in ids(s, v):
            first.setdefault(x, s["month"]); ever.add(x)
    months = sorted(first[x] for x in now)
    best = max(sum(1 for m in months if a <= m <= month_add(a, 1)) for a in months)
    toks = sorted(t[1] for t in S[i]["tokens"] if t[1] > 0)
    lg = [math.log(t) for t in toks]
    sig = {t: (min(abs(a - b) for b in lg if b != a) / 2 if len(lg) > 1 else 1.0) for t, a in zip(toks, lg)}
    m = min(abs(math.log(v) - math.log(t)) / sig[t] for t in toks) if toks else 9.0
    au = authors({(x[0], first[x]) for x in now})
    return dict(burst=best / len(months), authors=len(au), survival=len(now) / len(ever),
                n=len(now), files=len({x[0] for x in now}), m_nearest=min(m, 9.0),
                rel=len(now) / max(1, len(S[i]["lits"])), era=i)


if __name__ == "__main__":
    rows = []
    for c in C:
        if c["label"] in ("desire", "drift", "coincident"):
            rows.append(dict(c, **feats(c)))
    json.dump(rows, open("../notes/carbon_cluster_features.json", "w"), indent=0)
    D = [r for r in rows if r["label"] in ("desire", "drift")]
    y = np.array([r["label"] == "desire" for r in D], int)
    print("desire", y.sum(), "drift", len(y) - y.sum())
    for lab in ("desire", "drift", "coincident"):
        g = [r for r in rows if r["label"] == lab]
        print(f"  {lab:10s}", {k: round(float(np.median([r[k] for r in g])), 2) for k in ("burst", "authors", "survival", "n", "m_nearest", "era")})
    sets = {"era only": ["era"], "snapshot": ["n", "files", "m_nearest", "rel"], "time": ["burst", "authors", "survival"],
            "snapshot+time": ["n", "files", "m_nearest", "rel", "burst", "authors", "survival"]}
    res = {}
    for name, cols in sets.items():
        X = np.array([[math.log1p(r[k]) if k in ("n", "files", "authors") else r[k] for k in cols] for r in D], float)
        X = (X - X.mean(0)) / (X.std(0) + 1e-9)
        p = np.zeros(len(y))
        for k in range(len(y)):
            tr = np.arange(len(y)) != k
            p[k] = LogisticRegression(C=1.0, class_weight="balanced").fit(X[tr], y[tr]).predict_proba(X[k:k + 1])[0, 1]
        pred = p >= 0.5
        P = (pred & (y == 1)).sum() / max(1, pred.sum()); Rc = (pred & (y == 1)).sum() / y.sum()
        res[name] = dict(auc=round(roc_auc_score(y, p), 3), precision=round(float(P), 3), recall=round(float(Rc), 3), flagged=int(pred.sum()))
        print(f"{name:14s}", res[name])
    votes = np.array([desire_votes(r) >= 2 for r in D])
    res["pre-specified votes"] = dict(precision=round(float((votes & (y == 1)).sum() / max(1, votes.sum())), 3),
                                      recall=round(float((votes & (y == 1)).sum() / y.sum()), 3), flagged=int(votes.sum()))
    res["all clusters (snapshot rule)"] = dict(precision=round(float(y.mean()), 3), recall=1.0, flagged=len(y))
    print("pre-specified votes", res["pre-specified votes"], "| all-new baseline", res["all clusters (snapshot rule)"])
    json.dump(res, open("../notes/timefeat_carbon.json", "w"), indent=1)
