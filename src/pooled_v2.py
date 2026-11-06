"""Step 6: pooled evidence across every mined design system (v2 labels, per-line blame time features).
Reads notes/timefeat_v2.json (run timefeat_v2.py with SNAPS=<all systems> first).
  - per-system counts and base rates
  - direct AUC per feature with a system-clustered bootstrap CI (resample systems, then clusters)
  - leave-one-out and leave-one-SYSTEM-out logistic AUC for snapshot, time, both
  - sensitivity: positives restricted to hand-checked system-level tokens (COMPONENT lists the rest)
-> notes/pooled_v2.json
"""
import json, math
from collections import Counter, defaultdict
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

POS = ("single", "scale event")
# Hand check (notes/spotcheck_v2.md): positives whose new token is a component variable, or ambiguous, not a system token.
COMPONENT = {("carbon", 2.0), ("eui", 20.0), ("eui", 48.0), ("bootstrap", 24.0), ("mdc-web", 56.0), ("mdc-web", 7.0),
             ("govuk-frontend", 1.0), ("clarity", 8.0), ("clarity", 24.0), ("clarity", 4.0), ("clarity", 16.0),
             ("clarity", 12.0), ("clarity", 10.666672), ("clarity", 240.0), ("ant-design", 40.0), ("ant-design", 6.0),
             ("patternfly", 20.0), ("lightning", 32.0)}
SNAP = ["rel", "files", "n"]
TIME = ["burst", "authors", "span", "survival"]
rng = np.random.default_rng(0)


def X_of(D, cols):
    X = np.array([[math.log1p(d[k]) if k in ("n", "files", "authors") else d[k] for k in cols] for d in D], float)
    return (X - X.mean(0)) / (X.std(0) + 1e-9)


def clustered_ci(D, y, score):
    sys_ = sorted({d["system"] for d in D})
    by = defaultdict(list)
    for i, d in enumerate(D):
        by[d["system"]].append(i)
    a = []
    for _ in range(2000):
        idx = [i for s in rng.choice(sys_, len(sys_)) for i in rng.choice(by[s], len(by[s]))]
        yy = y[idx]
        if 0 < yy.sum() < len(yy):
            a.append(roc_auc_score(yy, score[idx]))
    return [round(float(np.percentile(a, 2.5)), 2), round(float(np.percentile(a, 97.5)), 2)]


def analyse(D, y):
    out = {"n_pos": int(y.sum()), "n_neg": int(len(y) - y.sum()), "base_rate": round(float(y.mean()), 3)}
    for k in ("rel", "files", "n", "grid4", "gap", "burst", "authors", "span", "survival"):
        sc = np.array([d[k] for d in D], float)
        out[f"direct {k}"] = dict(auc=round(roc_auc_score(y, sc), 3), ci=clustered_ci(D, y, sc))
    for name, cols in {"snapshot": SNAP, "time": TIME, "snapshot+time": SNAP + TIME, "snapshot+grid": SNAP + ["grid4"]}.items():
        X = X_of(D, cols)
        loo = np.array([LogisticRegression(class_weight="balanced").fit(X[np.arange(len(y)) != k], y[np.arange(len(y)) != k]).predict_proba(X[k:k + 1])[0, 1] for k in range(len(y))])
        loso = np.zeros(len(y))
        for s in {d["system"] for d in D}:
            te = np.array([d["system"] == s for d in D])
            if y[~te].min() == y[~te].max():
                continue
            loso[te] = LogisticRegression(class_weight="balanced").fit(X[~te], y[~te]).predict_proba(X[te])[:, 1]
        out[f"model {name}"] = dict(loo_auc=round(roc_auc_score(y, loo), 3), loso_auc=round(roc_auc_score(y, loso), 3),
                                    loso_ci=clustered_ci(D, y, loso))
    return out


if __name__ == "__main__":
    rows = json.load(open("../notes/timefeat_v2.json"))["rows"]
    D = [d for d in rows if d["label"] in POS + ("drift",)]
    y = np.array([d["label"] in POS for d in D], int)
    res = {"per_system": {s: dict(Counter(d["label"] for d in D if d["system"] == s)) for s in sorted({d["system"] for d in D})}}
    res["all positives"] = analyse(D, y)
    Ds = [d for d in D if not (d["label"] in POS and (d["system"], d["value"]) in COMPONENT)]
    ys = np.array([d["label"] in POS for d in Ds], int)
    res["system-level positives only"] = analyse(Ds, ys)
    for drop in (("semantic-ui",), ("semantic-ui", "clarity")):
        De = [d for d in D if d["system"] not in drop]
        res[f"without {', '.join(drop)}"] = analyse(De, np.array([d["label"] in POS for d in De], int))
    Dsl = [d for d in Ds if d["system"] != "semantic-ui"]
    res["system-level only, without semantic-ui"] = analyse(Dsl, np.array([d["label"] in POS for d in Dsl], int))
    sc = [d for d in D if d["label"] in POS]
    res["positive kinds"] = dict(Counter(d["label"] for d in sc))
    json.dump(res, open("../notes/pooled_v2.json", "w"), indent=1)
    for k, v in res.items():
        if isinstance(v, dict) and "n_pos" in v:
            print(f"== {k}: {v['n_pos']} pos / {v['n_neg']} neg, base {v['base_rate']}")
            for kk, vv in v.items():
                if kk.startswith(("direct", "model")):
                    print(f"   {kk:24s} {vv}")
        else:
            print(k, v)
