"""Recompute every number that goes on screen in the share video, from the repo's data, not from saved summaries.
Run from src/:  cd src && ../.venv/bin/python ../share/recompute.py
Writes share/claims.json (claim id -> recomputed value) and prints a table.
Agent results need the step-4 agent workdirs (path in AGENTS2 below); they are skipped if missing.
"""
import json, os, statistics as st, sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, os.getcwd())
from extract import extract
from detect import mixture
from score import score
from iterate import Model, run_variant, actions
from clusters import clusters

AGENTS2 = Path(os.environ.get("AGENTS2", "/tmp/claude-1000/-home-davidhatley-Projects/4e715895-1995-4f37-ad87-bef3d061a4a6/scratchpad/agents2"))
SEEDS = "12345"
out = {}

# 01 · 48px in Carbon before spacing-3xl (hand-written .scss only; compiled .css excluded)
S = json.load(open("../data/mined/snapshots.json"))
first = next(s["month"] for s in S if any(x[3] == 48.0 and x[0].endswith(".scss") and x[1] != "font-size" for x in s["lits"]))
pre = next(s for s in S if s["month"] == "2018-01")  # last snapshot before spacing-3xl (added 2018-01-17, 25f6afefc8)
lits48 = [x for x in pre["lits"] if x[3] == 48.0 and x[0].endswith(".scss")]
tok = next(s["month"] for s in S if ("px", 48.0) in [tuple(t) for t in s["tokens"]])
names = [k for k, v in next(s for s in S if s["month"] == tok)["token_names"].items() if v == ["px", 48.0]]
out["48_first_snapshot"] = first
out["48_uses_before_token"] = len(lits48)
out["48_files_before_token"] = len({x[0] for x in lits48})
out["48_font_size_uses"] = sum(x[1] == "font-size" for x in lits48)
out["48_token_snapshot"] = tok
out["48_token_names"] = names
out["48_files"] = sorted({x[0] for x in lits48})

# 03 · nearest-token snap on mined Carbon drift fixes (rows hold one prediction per label per method)
R = [r for r in json.load(open("../notes/mined_eval_rows.json")) if r["kind"] in ("exact", "near")]
out["carbon_fix_labels"] = len(R)
out["carbon_fix_commits"] = len({r["commit"] for r in R})
out["carbon_nearest_acc"] = round(sum(r["nearest"] for r in R) / len(R), 3)
out["carbon_exact_acc"] = round(sum(r["exact"] for r in R) / len(R), 3)
out["carbon_already_exact"] = sum(r["kind"] == "exact" for r in R)

# 04 · off-spec clusters re-derived from the monthly snapshots
C = clusters()
lab = Counter(c["label"] for c in C)
out["carbon_clusters"] = len(C)
out["carbon_cluster_labels"] = dict(lab)
out["carbon_desire_values"] = sorted((c["value"], c["month"], c["tokened"]) for c in C if c["label"] == "desire")
for v in (48.0, 42.0):  # the side-by-side pair: same month, same counts, different outcomes
    c = next(c for c in C if c["value"] == v)
    out[f"pair_{int(v)}px"] = dict(month=c["month"], uses=c["n"], files=c["files"], label=c["label"], tokened=c["tokened"])
saved = json.load(open("../data/mined/clusters.json"))
out["clusters_match_saved"] = [(c["value"], c["label"]) for c in C] == [(c["value"], c["label"]) for c in saved]

# 05a/b · synthetic: binding accuracy on ambiguous drift, and new-token precision
pairs, newP, model_acc = [], [], []
for s in SEEDS:
    tokens, sites = extract(f"../data/s{s}/repo")
    truth = json.load(open(f"../data/s{s}/truth.json"))
    M = Model(tokens, sites)
    b = run_variant(M, "one_shot")
    a = actions(M, b, tokens, sites)
    T_ = {x["id"]: x for x in truth}
    for i in b:
        if T_[i]["cls"] == "ambiguous" and a[i].startswith("bind:") and T_[i]["truth"].startswith("bind:"):
            pairs.append(a[i] == T_[i]["truth"])
    sc = score(truth, mixture(tokens, sites))
    newP.append(sc["new_P"]); model_acc.append(sc["action_acc"])
out["synth_ambiguous_bind_correct"] = f"{sum(pairs)}/{len(pairs)}"
out["synth_ambiguous_bind_acc"] = round(sum(pairs) / len(pairs), 3)
out["synth_newtoken_precision"] = round(st.mean(newP), 3)
out["synth_model_action_acc"] = round(st.mean(model_acc), 3)

# 05c · time features: synthetic (simulated history) and Carbon
from simhist import simulate, features, desire_votes
tp = []
for s in SEEDS:
    H = simulate(int(s))
    truth = json.load(open(f"../data/s{s}/truth.json"))
    tokens, sites = extract(f"../data/s{s}/repo")
    tp.append(score(truth, mixture(tokens, sites, group_filter=lambda g: desire_votes(features(g, H)) >= 2))["new_P"])
out["synth_time_newtoken_precision"] = round(st.mean(tp), 3)
import timefeat_carbon as TC  # module-level code only loads data
import math, numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
rows = [dict(c, **TC.feats(c)) for c in TC.C if c["label"] in ("desire", "drift")]
y = np.array([r["label"] == "desire" for r in rows], int)
def loo_auc(cols):
    X = np.array([[math.log1p(r[k]) if k in ("n", "files", "authors") else r[k] for k in cols] for r in rows], float)
    X = (X - X.mean(0)) / (X.std(0) + 1e-9)
    p = [LogisticRegression(C=1.0, class_weight="balanced").fit(X[np.arange(len(y)) != k], y[np.arange(len(y)) != k]).predict_proba(X[k:k + 1])[0, 1] for k in range(len(y))]
    return round(roc_auc_score(y, p), 3)
snap = ["n", "files", "m_nearest", "rel"]; tim = ["burst", "authors", "survival"]
out["carbon_auc_snapshot"] = loo_auc(snap)
out["carbon_auc_snapshot_time"] = loo_auc(snap + tim)
out["carbon_auc_time"] = loo_auc(tim)
votes = np.array([desire_votes(r) >= 2 for r in rows])
out["carbon_votes_precision"] = round(float((votes & (y == 1)).sum() / votes.sum()), 3)
out["carbon_base_rate"] = round(float(y.mean()), 3)
out["carbon_desire_vs_drift"] = f"{int(y.sum())} vs {int(len(y) - y.sum())}"

# 05d · agents with sandboxed code execution, 5 seeds, full repo
if AGENTS2.exists():
    for arm in ("opus", "codex", "sonnet"):
        acc = []
        for s in SEEDS:
            truth = json.load(open(f"../data/s{s}/truth.json"))
            acc.append(score(truth, json.load(open(AGENTS2 / f"full-{arm}-s{s}" / "actions.json")))["action_acc"])
        out[f"agent_{arm}_action_acc"] = round(st.mean(acc), 3)
else:
    print("agent workdirs missing:", AGENTS2, file=sys.stderr)

json.dump(out, open("../share/claims.json", "w"), indent=1)
for k, v in out.items():
    print(f"{k:34s} {v}")
