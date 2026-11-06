"""Step 1: why iterative healing degraded, and three fixes.
Variants (all keep the one-shot 'new'/'leave' decisions; they differ only in how bindings are chosen):
  one_shot     posterior from the original code
  hard_lef     lowest-entropy-first with hard commits fed back as context (the degrading baseline)
  frozen       lowest-entropy-first, context prior frozen to the original code
  bp           soft updates: literal neighbours vote with their current beliefs (damped mean-field BP)
  calibrated   lowest-entropy-first, but only commit sites whose temperature-calibrated confidence >= 0.9
Calibration: temperature fit on the other 4 seeds (leave-one-seed-out), reliability bins + ECE.
"""
import json, math, sys
from collections import Counter, defaultdict
from pathlib import Path
from extract import extract
from detect import Space, mixture, governed, lits, suffix
from score import score

K = 15


def sim(a, b, elems):
    mine = {(x["prop"], x["token"]) for x in elems[a["elem"]] if x["token"]}
    theirs = {(x["prop"], x["token"]) for x in elems[b["elem"]] if x["token"]}
    return 2.0 * (a["slot"] == b["slot"]) + 2.0 * (suffix(a["component"]) == suffix(b["component"])) \
        + 3.0 * len(mine & theirs) / max(1, len(mine | theirs))


class Model:
    def __init__(self, tokens, sites):
        self.sp, self.sites = Space(tokens), sites
        self.elems = defaultdict(list)
        for s in sites:
            self.elems[s["elem"]].append(s)
        self.L = [s for s in lits(sites) if governed(s)]
        self.loglik = {s["id"]: {k: -0.5 * m * m for m, k in self.sp.ranked(s)} for s in self.L}
        # neighbour lists over ALL same-prop sites (bound and literal), with similarity weights
        byprop = defaultdict(list)
        for s in sites:
            if s["token"] or (governed(s) and s["literal"] is not None):
                byprop[s["prop"]].append(s)
        self.nb = {}
        for s in self.L:
            c = sorted(((sim(s, v, self.elems), v) for v in byprop[s["prop"]] if v["elem"] != s["elem"]),
                       key=lambda x: -x[0])
            self.nb[s["id"]] = c

    def posterior(self, sid, labels, T=1.0, include_literals=True):
        """labels: site id -> {token: prob} for sites that vote; bound sites vote one-hot."""
        votes, n = Counter(), 0
        for w, v in self.nb[sid]:
            lab = {v["token"]: 1.0} if v["token"] else (labels.get(v["id"]) if include_literals else None)
            if not lab:
                continue
            for k, p in lab.items():
                votes[k] += math.exp(w) * p
            n += 1
            if n >= K:
                break
        z = sum(votes.values()) or 1
        lp = {k: (l + math.log(votes.get(k, 0) / z + 1e-3)) / T for k, l in self.loglik[sid].items()}
        mx = max(lp.values())
        ex = {k: math.exp(v - mx) for k, v in lp.items()}
        tot = sum(ex.values())
        return {k: v / tot for k, v in ex.items()}


def ent(p):
    return -sum(x * math.log(x) for x in p.values() if x > 0)


def run_variant(M, variant, T=1.0, frac=0.25, thresh=0.9, iters=10, damp=0.5):
    ids = [s["id"] for s in M.L]
    if variant == "one_shot" or variant == "frozen":
        # frozen prior: committed fixes never re-enter the context, so every posterior equals the one-shot one
        return {i: M.posterior(i, {}, T, include_literals=False) for i in ids}
    if variant == "bp":
        bel = {i: M.posterior(i, {}, T, include_literals=False) for i in ids}
        for _ in range(iters):
            new = {i: M.posterior(i, bel, T) for i in ids}
            bel = {i: {k: damp * bel[i].get(k, 0) + (1 - damp) * new[i].get(k, 0) for k in new[i]} for i in ids}
        return bel
    # hard lowest-entropy-first, optionally gated by calibrated confidence
    committed, final = {}, {}
    todo = set(ids)
    while todo:
        post = {i: M.posterior(i, committed, T, include_literals=True) for i in todo}
        order = sorted(todo, key=lambda i: ent(post[i]))
        if variant == "calibrated":
            take = [i for i in order if max(post[i].values()) >= thresh][:max(1, int(len(todo) * frac))]
            if not take:  # nothing confident left: decide the rest without feeding them back
                for i in todo:
                    final[i] = post[i]
                break
        else:
            take = order[:max(1, int(len(todo) * frac))]
        for i in take:
            final[i] = post[i]
            committed[i] = {max(post[i], key=post[i].get): 1.0}
            todo.discard(i)
    return final


def actions(M, beliefs, tokens, sites):
    base = mixture(tokens, sites)
    out = dict(base)
    for i, p in beliefs.items():
        if base[i].startswith("bind:"):
            out[i] = "bind:" + max(p, key=p.get)
    return out


def reliability(pairs, bins=10):
    """pairs: (confidence, correct). Returns bins and expected calibration error."""
    B = defaultdict(list)
    for c, ok in pairs:
        B[min(bins - 1, int(c * bins))].append((c, ok))
    rows, ece, n = [], 0.0, len(pairs)
    for b in sorted(B):
        cs = [c for c, _ in B[b]]; oks = [o for _, o in B[b]]
        conf, acc = sum(cs) / len(cs), sum(oks) / len(oks)
        rows.append(dict(bin=b / bins, n=len(cs), conf=round(conf, 3), acc=round(acc, 3)))
        ece += len(cs) / n * abs(conf - acc)
    return rows, round(ece, 4)


def conf_pairs(M, beliefs, truth, act):
    T_ = {s["id"]: s for s in truth}
    out = []
    for i, p in beliefs.items():
        if act[i].startswith("bind:") and T_[i]["truth"].startswith("bind:"):
            k = max(p, key=p.get)
            out.append((p[k], f"bind:{k}" == T_[i]["truth"]))
    return out


def fit_T(models_truths):
    best = None
    for T in [0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0]:
        nll = 0
        for M, truth, tokens, sites in models_truths:
            T_ = {s["id"]: s for s in truth}
            b = run_variant(M, "one_shot", T)
            for i, p in b.items():
                t = T_[i]["truth"]
                if t.startswith("bind:"):
                    nll -= math.log(p.get(t[5:], 0) + 1e-9)
        if best is None or nll < best[1]:
            best = (T, nll)
    return best[0]


if __name__ == "__main__":
    seeds = sys.argv[1:] or ["1", "2", "3", "4", "5"]
    data = {}
    for s in seeds:
        tokens, sites = extract(f"../data/s{s}/repo")
        truth = json.loads(Path(f"../data/s{s}/truth.json").read_text())
        data[s] = (Model(tokens, sites), truth, tokens, sites)
    res = {}
    for s in seeds:
        M, truth, tokens, sites = data[s]
        T = fit_T([data[o] for o in seeds if o != s])
        r = {"T": T}
        for v in ["one_shot", "hard_lef", "frozen", "bp", "calibrated"]:
            Tv = T if v == "calibrated" else 1.0
            b = run_variant(M, v, Tv)
            a = actions(M, b, tokens, sites)
            sc = score(truth, a)
            r[v] = {"ambiguous": round(sc["ambiguous"], 3), "action_acc": round(sc["action_acc"], 3)}
            if v in ("one_shot", "bp", "hard_lef"):
                r[v]["rel_raw"], r[v]["ece_raw"] = reliability(conf_pairs(M, b, truth, a))
                bc = run_variant(M, v, T)
                r[v]["rel_cal"], r[v]["ece_cal"] = reliability(conf_pairs(M, bc, truth, actions(M, bc, tokens, sites)))
        res[s] = r
        print(f"seed {s} T={T}: " + " | ".join(f"{v} amb={r[v]['ambiguous']:.2f}" for v in
              ["one_shot", "hard_lef", "frozen", "bp", "calibrated"]) +
              f" | ECE one-shot {r['one_shot']['ece_raw']}->{r['one_shot']['ece_cal']}")
    json.dump(res, open("../notes/iterate.json", "w"), indent=1)
