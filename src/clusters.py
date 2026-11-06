"""Off-spec clusters and their outcome labels from data/mined/snapshots.json (rules in desire.py's docstring)."""
import json, os, sys
from collections import Counter, defaultdict
S = json.load(open(os.environ.get("SNAP", "../data/mined/snapshots.json")))
HORIZON, MIN_N, MIN_FILES = 24, 3, 2
REDESIGN = float(os.environ.get("REDESIGN", "0"))  # v2: 0.4 = >= 40% of token values new that month


def uses(s, v):
    return [l for l in s["lits"] if l[3] == v]


def share(s, v):
    """Token references' share of all uses of value v."""
    r, n = s["refs"].get(str(v), 0), len(uses(s, v))
    return r / (r + n) if r + n else 0.0


def rel(s, v):
    """v's share of all literals (normalises for codebase growth and file duplication)."""
    return len(uses(s, v)) / max(1, len(s["lits"]))


def churn(j):
    """Share of the token values at snapshot j that were not tokens at j-1."""
    if j == 0:
        return 1.0
    now, before = {t[1] for t in S[j]["tokens"]}, {t[1] for t in S[j - 1]["tokens"]}
    return len(now - before) / max(1, len(now))


def clusters():
    seen, out = set(), []
    for i, s in enumerate(S):
        toks = {t[1] for t in s["tokens"]}
        vals = Counter(l[3] for l in s["lits"])
        for v, n in vals.items():
            if v in seen or v in toks:
                continue
            u = uses(s, v)
            if n >= MIN_N and len({l[0] for l in u}) >= MIN_FILES:
                seen.add(v)
                fut = S[i + 1:i + 1 + HORIZON]
                tokened = next((f["month"] for f in fut if v in {t[1] for t in f["tokens"]}), None)
                end = fut[-1] if fut else s
                n_end = len(uses(end, v))
                if tokened and REDESIGN and churn(next(k for k, f in enumerate(S) if f["month"] == tokened)) >= REDESIGN:
                    lab = "redesign"  # the value arrived in a scale rewrite, not as a response to use
                elif tokened:
                    # desire path only if the literals then migrate: uses fall >= 30% from the month before the token to 12 months after
                    j = next(k for k, f in enumerate(S) if f["month"] == tokened)
                    lab = "desire" if share(S[min(j + 12, len(S) - 1)], v) - share(S[max(j - 1, 0)], v) >= 0.2 else "coincident"
                elif len(fut) < HORIZON:
                    lab = "censored"
                elif rel(end, v) <= 0.5 * rel(s, v):
                    lab = "drift"
                else:
                    lab = "unresolved"
                out.append(dict(value=v, month=s["month"], idx=i, n=n, files=len({l[0] for l in u}),
                                n_end=n_end, label=lab, tokened=tokened))
    return out


if __name__ == "__main__":
    C = clusters()
    json.dump(C, open("../data/mined/clusters.json", "w"), indent=0)
    print(Counter(c["label"] for c in C))
    for c in C:
        if c["label"] == "desire":
            print(" desire", c["value"], c["month"], "->", c["tokened"], "n", c["n"], "files", c["files"])
