"""Score {site_id: action} against truth. Usage: score.py <data_dir> [actions.json ...]  (no files: run all METHODS)."""
import json, sys
from collections import defaultdict
from pathlib import Path
from extract import extract
from detect import METHODS

CLASSES = ["exact", "near", "ambiguous", "cluster", "intentional"]


def correct(pred, truth):
    if truth.startswith("new:"):
        return pred.startswith("new:")
    return pred == truth


def score(truth, pred):
    per = defaultdict(lambda: [0, 0])
    tp = fp = fn = 0
    for s in truth:
        if s["cls"] == "bound":
            continue
        p = pred.get(s["id"], "leave")
        per[s["cls"]][0] += correct(p, s["truth"]); per[s["cls"]][1] += 1
        flag_t, flag_p = s["truth"] != "leave", p != "leave"
        tp += flag_t and flag_p; fp += flag_p and not flag_t; fn += flag_t and not flag_p
    pn = [s for s in truth if pred.get(s["id"], "leave").startswith("new:")]
    n_ok = sum(v[0] for v in per.values()); n = sum(v[1] for v in per.values())
    row = {c: per[c][0] / per[c][1] for c in CLASSES if per[c][1]}
    row["action_acc"] = n_ok / n
    row["detect_P"] = tp / max(1, tp + fp); row["detect_R"] = tp / max(1, tp + fn)
    row["new_P"] = sum(s["truth"].startswith("new:") for s in pn) / len(pn) if pn else 1.0
    return row


def run_methods(d):
    d = Path(d)
    truth = json.loads((d / "truth.json").read_text())
    tokens, sites = extract(d / "repo")
    return {name: score(truth, fn(tokens, sites)) for name, fn in METHODS.items()}


if __name__ == "__main__":
    d = Path(sys.argv[1])
    truth = json.loads((d / "truth.json").read_text())
    if len(sys.argv) > 2:
        for f in sys.argv[2:]:
            print(f, json.dumps({k: round(v, 3) for k, v in score(truth, json.loads(Path(f).read_text())).items()}))
    else:
        for name, row in run_methods(d).items():
            print(f"{name:16s}", " ".join(f"{k}={v:.2f}" for k, v in row.items()))
