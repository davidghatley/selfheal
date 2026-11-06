"""Re-run the nearest-token predictions on mined Carbon labels against git (no saved rows). Run from src/."""
import json, sys, os
sys.path.insert(0, os.getcwd())
from eval_mined import scale_at, file_context, predict
L = json.load(open("../data/mined/carbon_resolved.json"))
n = ok_near = ok_exact = 0
for l in L:
    if l["kind"] not in ("exact", "near") or l["lit_v"][0] != "px" or l["lit_v"][1] <= 0:
        continue
    scale, defs = scale_at(l["commit"] + "^")
    if l["tok_v"][1] not in scale:
        continue
    n += 1
    ok_near += predict(l["lit_v"][1], scale, {}, "nearest") == l["tok_v"][1]
    ok_exact += predict(l["lit_v"][1], scale, {}, "exact") == l["tok_v"][1]
print(json.dumps({"n": n, "nearest": round(ok_near / n, 3), "exact": round(ok_exact / n, 3), "nearest_correct": ok_near}))
