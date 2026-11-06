"""Step 4 hybrid split: the model resolves confident sites, the agent gets the rest.
Confident = calibrated (T fit leave-one-seed-out) binding confidence >= 0.9 and not in a proposed new-token group,
or a non-governed/zero literal (left by rule). Writes data/sN/hybrid_model.json and data/sN/uncertain_ids.json.
Usage: hybrid.py split | hybrid.py merge <seed> <agent_actions.json>"""
import json, sys
from extract import extract
from detect import mixture, governed, lits
from iterate import Model, run_variant, fit_T

THRESH = 0.9


def split(seeds="12345"):
    data = {}
    for s in seeds:
        t, S = extract(f"../data/s{s}/repo")
        data[s] = (Model(t, S), json.load(open(f"../data/s{s}/truth.json")), t, S)
    for s in seeds:
        M, truth, t, S = data[s]
        T = fit_T([data[o] for o in seeds if o != s])
        bel = run_variant(M, "one_shot", T)
        acts = mixture(t, S)
        model, unc = {}, []
        for x in lits(S):
            a = acts[x["id"]]
            if not governed(x):
                model[x["id"]] = a
            elif a.startswith("bind:") and max(bel[x["id"]].values()) >= THRESH:
                model[x["id"]] = a
            else:
                unc.append(x["id"])
        json.dump(model, open(f"../data/s{s}/hybrid_model.json", "w"))
        json.dump(unc, open(f"../data/s{s}/uncertain_ids.json", "w"))
        print(s, "model", len(model), "agent", len(unc), f"({len(unc) / (len(unc) + len(model)):.0%})")


if __name__ == "__main__":
    if sys.argv[1] == "split":
        split()
    else:
        s, f = sys.argv[2], sys.argv[3]
        m = json.load(open(f"../data/s{s}/hybrid_model.json"))
        m.update({k: v for k, v in json.load(open(f)).items() if k not in m})
        print(json.dumps(m))
