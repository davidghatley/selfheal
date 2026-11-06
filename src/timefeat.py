"""Step 3 (synthetic): new-token decisions with and without time features, 5 seeds."""
import json, statistics as st
from extract import extract
from detect import mixture
from score import score
from simhist import simulate, features, desire_votes

rows = {}
for seed in "12345":
    H = simulate(int(seed))
    truth = json.load(open(f"../data/s{seed}/truth.json"))
    T, S = extract(f"../data/s{seed}/repo")
    base = score(truth, mixture(T, S))
    timed = score(truth, mixture(T, S, group_filter=lambda g: desire_votes(features(g, H)) >= 2))
    rows[seed] = dict(snapshot=base, time=timed)
    print(seed, " ".join(f"{k}: newP {v['new_P']:.2f} cluster {v['cluster']:.2f} amb {v['ambiguous']:.2f} near {v['near']:.2f} acc {v['action_acc']:.2f} |"
                         for k, v in rows[seed].items()))
for k in ("snapshot", "time"):
    print(k, {m: f"{st.mean(rows[s][k][m] for s in rows):.2f}±{st.stdev(rows[s][k][m] for s in rows):.2f}"
              for m in ("new_P", "cluster", "ambiguous", "near", "action_acc")})
json.dump(rows, open("../notes/timefeat_synthetic.json", "w"), indent=1)
