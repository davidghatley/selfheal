"""Score the step-4 runs: full and hybrid, per arm, with time, cost (Claude: reported API-equivalent USD) and tokens."""
import json, re, statistics as st, subprocess, sys
from collections import defaultdict
from pathlib import Path
from score import score, run_methods

WR = Path(sys.argv[1])
secs = {}
for l in (WR / "runs.txt").read_text().splitlines():
    m, a, s, ex, t = re.match(r"(\w+) (\w+) s(\d) exit=(\d+) secs=(\d+)", l).groups()
    secs[(m, a, s)] = (int(ex), int(t))
rows = defaultdict(list)
for (m, a, s), (ex, t) in sorted(secs.items()):
    d = WR / f"{m}-{a}-s{s}"
    truth = json.load(open(f"../data/s{s}/truth.json"))
    try:
        acts = json.load(open(d / "actions.json"))
    except Exception as e:
        print("MISSING", m, a, s, e); continue
    n_sites = len(json.load(open(d / "sites.json")))
    missing = n_sites - len(set(acts) & {x["id"] for x in json.load(open(d / "sites.json"))})
    if m == "hybrid":
        merged = json.load(open(f"../data/s{s}/hybrid_model.json")); merged.update({k: v for k, v in acts.items() if k not in merged})
        acts = merged
    sc = score(truth, acts)
    log = (d / "run.log").read_text(errors="replace")
    cost = tok = None
    if a in ("opus", "sonnet"):
        j = json.loads(log[log.index("{"):])
        cost = j.get("total_cost_usd")
        u = j.get("usage", {}); tok = sum(u.get(k, 0) for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens"))
        bash = log.count('"Bash"')
    else:
        mm = re.search(r"tokens used\s*\n?\s*([\d,]+)", log); tok = int(mm.group(1).replace(",", "")) if mm else None
    rows[(m, a)].append(dict(seed=s, secs=t, cost=cost, tokens=tok, missing=missing, **{k: sc[k] for k in ("action_acc", "ambiguous", "near", "cluster", "new_P")}))
meth = [run_methods(f"../data/s{s}") for s in "12345"]
out = {"mixture+context": {k: st.mean(r["mixture+context"][k] for r in meth) for k in ("action_acc", "ambiguous", "near", "cluster", "new_P")},
       "nearest": {k: st.mean(r["nearest"][k] for r in meth) for k in ("action_acc", "ambiguous", "near", "cluster", "new_P")}}
for (m, a), R in rows.items():
    agg = {k: round(st.mean(r[k] for r in R), 3) for k in ("action_acc", "ambiguous", "near", "cluster", "new_P", "secs")}
    agg["acc_sd"] = round(st.stdev(r["action_acc"] for r in R), 3) if len(R) > 1 else 0
    agg["cost_usd"] = round(st.mean(r["cost"] for r in R), 3) if R[0]["cost"] is not None else None
    agg["tokens"] = int(st.mean(r["tokens"] for r in R if r["tokens"])) if any(r["tokens"] for r in R) else None
    agg["n"] = len(R); agg["missing_ids"] = sum(r["missing"] for r in R)
    out[f"{m}:{a}"] = agg
for k, v in out.items():
    print(f"{k:16s}", {x: (round(y, 3) if isinstance(y, float) else y) for x, y in v.items()})
json.dump({"agg": out, "rows": {f"{m}:{a}": R for (m, a), R in rows.items()}}, open("../notes/agents2.json", "w"), indent=1)
