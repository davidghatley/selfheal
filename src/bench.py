"""Aggregate all METHODS over seeds: mean (sd) per metric."""
import json, statistics as st, sys
from score import run_methods
seeds = sys.argv[1:] or ["1", "2", "3", "4", "5"]
rows = [run_methods(f"../data/s{s}") for s in seeds]
out = {}
for m in rows[0]:
    out[m] = {k: (st.mean(r[m][k] for r in rows), st.stdev(r[m][k] for r in rows)) for k in rows[0][m]}
    print(f"{m:16s}", " ".join(f"{k}={a:.2f}±{b:.2f}" for k, (a, b) in out[m].items()))
json.dump(out, open("../notes/bench_methods.json", "w"), indent=1)
