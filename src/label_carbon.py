"""Resolve each mined Carbon label's literal and token to values at the label commit's parent."""
import json, collections, re, sys
from resolve import defs_at, value
R = sys.argv[1] if len(sys.argv) > 1 else "/mnt/work/selfheal-repos/carbon"
LITX = re.compile(r"(?:[\w.-]*(?:rem|mini-units)\([^)]*\)|-?\d*\.?\d+(?:px|rem|em)\b|#[0-9a-fA-F]{3,6}\b)")
TOKX = re.compile(r"-?(?:[\w-]+\.)?\$[\w-]+|var\(--[^)]*\)")
RAW = [json.loads(l) for l in open("../data/mined/carbon.jsonl")]
L = []
for l in RAW:  # shorthand: '0 1.25rem 0 0.5rem' -> '0 $spacing-lg 0 $spacing-xs' gives one label per changed position
    a, b = l["literal"].split(), l["token"].split()
    if len(a) > 1 and len(a) == len(b):
        for i, (x, y) in enumerate(zip(a, b)):
            if x != y and LITX.fullmatch(x) and TOKX.fullmatch(y):
                L.append(dict(l, literal=x, token=y, part=i))
    else:
        L.append(l)
res = collections.Counter()
for l in L:
    defs = defs_at(R, l["commit"] + "^")
    lit, tk = LITX.findall(l["literal"]), TOKX.findall(l["token"])
    # one label per declaration: only single-value literals and single-token replacements are scorable
    l["lit_v"] = value(lit[0], defs) if len(lit) == 1 else None
    l["tok_name"] = tk[0] if len(tk) == 1 else None
    l["tok_v"] = value(tk[0], defs) if len(tk) == 1 else None
    if not l["lit_v"] or not l["tok_v"]:
        l["kind"] = "unresolved"
    elif l["lit_v"][0] != l["tok_v"][0]:
        l["kind"] = "kind_mismatch"
    elif l["lit_v"] == l["tok_v"]:
        l["kind"] = "exact"
    elif l["lit_v"][0] == "px" and abs(l["lit_v"][1] - l["tok_v"][1]) <= 2:
        l["kind"] = "near"
    else:
        l["kind"] = "changed"
    res[l["kind"]] += 1
print(res)
json.dump(L, open("../data/mined/carbon_resolved.json", "w"), indent=0)
