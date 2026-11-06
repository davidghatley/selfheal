"""v2 outcome labels for every off-spec cluster of one system (rules in docs/mining.md, "v2 rules").
  single       a token with the value arrives within 24 months, < 4 new token values that month, literals migrate (+0.2 share)
  scale event  the same, in a month with >= 4 new token values (a scale built or rebuilt)
  coincident   a token arrives but the literals don't move onto it
  drift / unresolved / censored  as in clusters.py
Each row also carries decision-time snapshot features.
"""
import importlib, math, os

POSITIVE = ("single", "scale event")


def load(key):
    os.environ["SNAP"] = f"../data/mined/{key}/snapshots_v2.json"
    import clusters as K
    importlib.reload(K)
    return K


def rows(key):
    K = load(key)
    idx = {s["month"]: i for i, s in enumerate(K.S)}
    out = []
    for c in K.clusters():
        if c["tokened"]:
            j = idx[c["tokened"]]
            mig = K.share(K.S[min(j + 12, len(K.S) - 1)], c["value"]) - K.share(K.S[max(j - 1, 0)], c["value"])
            new = {t[1] for t in K.S[j]["tokens"]} - {t[1] for t in K.S[j - 1]["tokens"]}
            lab = ("scale event" if len(new) >= 4 else "single") if mig >= 0.2 else "coincident"
        else:
            lab = c["label"]
        s = K.S[c["idx"]]
        toks = sorted(t[1] for t in s["tokens"])
        out.append(dict(system=key, value=c["value"], month=c["month"], idx=c["idx"], label=lab, n=c["n"], files=c["files"],
                        tokened=c["tokened"], grid4=float(c["value"] % 4 == 0), grid8=float(c["value"] % 8 == 0),
                        gap=min([abs(math.log(c["value"] / t)) for t in toks] or [3.0]),
                        rel=c["n"] / max(1, len(s["lits"]))))
    return out, K
