"""Score drift detectors on history-mined Carbon labels (px only).
Candidate tokens = the spacing scale defined at the label commit's parent. A prediction is correct when the
chosen token's value equals the value of the token the human picked (several tokens share values).
Context prior = token values the same file already used for the same property family at the parent commit.
"""
import json, math, re, subprocess, sys
from collections import Counter, defaultdict
from resolve import defs_at, value, SCALE_V11

R = "/mnt/work/selfheal-repos/carbon"
SCALE_NAME = re.compile(r"^(carbon--)?(spacing|layout)-(\d\d|\dxs|xs|sm|md|lg|xl|\dxl)$")
FAMILY = lambda p: re.sub(r"-(top|right|bottom|left|inline|block|start|end)+", "", p.replace("inset-", "inset"))
DECL = re.compile(r"^\s*([a-z-]+)\s*:\s*([^;]+);", re.M)
TOKX = re.compile(r"(?:[\w-]+\.)?\$[\w-]+")


def scale_at(commit):
    defs = defs_at(R, commit)
    vals = {}
    for k in list(defs) + list(SCALE_V11):
        if SCALE_NAME.match(k):
            v = value("$" + k, defs)
            if v and v[0] == "px" and v[1] > 0:
                vals[k] = v[1]
    return sorted(set(vals.values())), defs


def file_context(commit, path, prop, defs):
    txt = subprocess.run(["git", "-C", R, "show", f"{commit}:{path}"], capture_output=True, text=True, errors="replace").stdout
    c = Counter()
    for p, v in DECL.findall(txt):
        if FAMILY(p) != FAMILY(prop):
            continue
        for t in TOKX.findall(v):
            r = value(t, defs)
            if r and r[0] == "px" and r[1] > 0:
                c[r[1]] += 1
    return c


def sigma(scale):
    lg = [math.log(v) for v in scale]
    return {v: min(abs(a - b) for b in lg if b != a) / 2 for v, a in zip(scale, lg)}


def predict(lit, scale, ctx, method, alpha=1.0):
    if method == "exact":
        return lit if lit in scale else None
    sg = sigma(scale)
    m = {v: abs(math.log(lit) - math.log(v)) / sg[v] for v in scale}
    if method == "nearest":
        return min(m, key=m.get)
    z = sum(ctx.values())
    lp = {v: -0.5 * m[v] ** 2 + alpha * math.log((ctx.get(v, 0) + 0.5) / (z + 0.5 * len(scale))) for v in scale}
    return max(lp, key=lp.get)


if __name__ == "__main__":
    L = json.load(open("../data/mined/carbon_resolved.json"))
    rows, skipped = [], Counter()
    for l in L:
        if l["kind"] not in ("exact", "near", "changed") or l["lit_v"][0] != "px" or l["lit_v"][1] <= 0:
            skipped[l["kind"] if l["kind"] not in ("exact", "near", "changed") else "nonpositive/color"] += 1
            continue
        scale, defs = scale_at(l["commit"] + "^")
        if l["tok_v"][1] not in scale:
            skipped["token value off the scale"] += 1
            continue
        ctx = file_context(l["commit"] + "^", l["file"], l["prop"], defs)
        r = dict(kind=l["kind"], lit=l["lit_v"][1], tok=l["tok_v"][1], commit=l["commit"][:8], date=l["date"])
        for meth in ("exact", "nearest", "mixture+context"):
            r[meth] = predict(l["lit_v"][1], scale, ctx, meth) == l["tok_v"][1]
        r["ctx_n"] = sum(ctx.values())
        rows.append(r)
    json.dump(rows, open("../notes/mined_eval_rows.json", "w"), indent=0)
    print("skipped:", dict(skipped))
    out = {}
    for kind in ("exact", "near", "changed", "exact+near"):
        sub = [r for r in rows if (r["kind"] in ("exact", "near")) if kind == "exact+near"] if kind == "exact+near" \
            else [r for r in rows if r["kind"] == kind]
        out[kind] = {"n": len(sub), **{m: round(sum(r[m] for r in sub) / len(sub), 3) for m in ("exact", "nearest", "mixture+context")}}
        print(kind, out[kind])
    # bootstrap by commit (labels cluster in a few big commits)
    import random
    random.seed(0)
    sub = [r for r in rows if r["kind"] in ("exact", "near")]
    byc = defaultdict(list)
    for r in sub:
        byc[r["commit"]].append(r)
    keys = list(byc)
    diffs = []
    for _ in range(2000):
        s = [r for k in random.choices(keys, k=len(keys)) for r in byc[k]]
        diffs.append(sum(r["mixture+context"] - r["nearest"] for r in s) / len(s))
    diffs.sort()
    out["ctx_minus_nearest_ci95"] = (round(diffs[50], 3), round(diffs[1949], 3))
    out["n_commits"] = len(keys)
    print("mixture+context - nearest on exact+near, commit-bootstrap 95% CI:", out["ctx_minus_nearest_ci95"], "commits", len(keys))
    json.dump(out, open("../notes/mined_eval.json", "w"), indent=1)
