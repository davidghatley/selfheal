"""Step 5: v2 outcome labels across design systems, and whether 'is it on the grid?' predicts which repeated values
earn a token. Positive = a token with the value arrives within 24 months and the code moves onto it (share +0.2);
split into a single addition (< 4 new token values that month) or a scale event (>= 4). Negative = drift.
Features are known at decision time only. Leave-one-out logistic regression, pooled over systems.
  SNAPS="carbon eui" grid_test.py  ->  notes/grid_test.json
"""
import json, math, os
from collections import Counter
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

SYSTEMS = os.environ.get("SNAPS", "carbon eui").split()
rows = []
for key in SYSTEMS:
    os.environ["SNAP"] = f"../data/mined/{key}/snapshots_v2.json"
    import importlib, clusters as K
    importlib.reload(K)
    idx = {s["month"]: i for i, s in enumerate(K.S)}
    for c in K.clusters():
        lab = None
        if c["tokened"]:
            j = idx[c["tokened"]]
            mig = K.share(K.S[min(j + 12, len(K.S) - 1)], c["value"]) - K.share(K.S[max(j - 1, 0)], c["value"])
            new = {t[1] for t in K.S[j]["tokens"]} - {t[1] for t in K.S[j - 1]["tokens"]}
            if mig >= 0.2:
                lab = "scale event" if len(new) >= 4 else "single"
            else:
                lab = "coincident"
        elif c["label"] == "drift":
            lab = "drift"
        else:
            lab = c["label"]
        s = K.S[c["idx"]]
        toks = sorted(t[1] for t in s["tokens"])
        rows.append(dict(system=key, value=c["value"], month=c["month"], label=lab, n=c["n"], files=c["files"],
                         grid4=float(c["value"] % 4 == 0), grid8=float(c["value"] % 8 == 0),
                         gap=min([abs(math.log(c["value"] / t)) for t in toks] or [3.0]),
                         rel=c["n"] / max(1, len(s["lits"]))))

D = [r for r in rows if r["label"] in ("single", "scale event", "drift")]
y = np.array([r["label"] != "drift" for r in D], int)
out = {"labels": {k: dict(Counter(r["label"] for r in rows if r["system"] == k)) for k in SYSTEMS},
       "positives": [(r["system"], r["value"], r["month"], r["label"]) for r in D if r["label"] != "drift"],
       "n_pos": int(y.sum()), "n_neg": int(len(y) - y.sum()), "base_rate": round(float(y.mean()), 3)}
for f in ("grid4", "grid8"):
    on = np.array([r[f] for r in D]) == 1
    out[f"{f}_rule"] = dict(precision=round(float(y[on].mean()), 3) if on.any() else None, recall=round(float(y[on].sum() / y.sum()), 3),
                            flagged=int(on.sum()), pos_on=int(y[on].sum()), neg_on=int((1 - y[on]).sum()))
sets = {"size (uses, files, share)": ["n", "files", "rel"], "distance to nearest token": ["gap"], "on the 4px grid": ["grid4"],
        "on the 8px grid": ["grid8"], "size + grid": ["n", "files", "rel", "grid4", "grid8"]}
for name, cols in sets.items():
    X = np.array([[math.log1p(r[k]) if k in ("n", "files") else r[k] for k in cols] for r in D], float)
    X = (X - X.mean(0)) / (X.std(0) + 1e-9)
    p = np.array([LogisticRegression(class_weight="balanced").fit(X[np.arange(len(y)) != k], y[np.arange(len(y)) != k]).predict_proba(X[k:k + 1])[0, 1]
                  for k in range(len(y))])
    out[name] = dict(auc=round(roc_auc_score(y, p), 3))
# leave-one-system-out for the grid rule: does it transfer?
for k in SYSTEMS:
    sub = [(r, yy) for r, yy in zip(D, y) if r["system"] == k]
    on = [yy for r, yy in sub if r["grid4"]]
    out[f"grid4_in_{k}"] = dict(precision=round(sum(on) / len(on), 3) if on else None, flagged=len(on),
                                base=round(sum(yy for _, yy in sub) / len(sub), 3), n=len(sub))
json.dump(dict(out, rows=rows), open("../notes/grid_test.json", "w"), indent=1)
for k, v in out.items():
    print(f"{k:28s} {v}")
