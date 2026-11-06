"""Step 6: the drift-fix test on every mined system. Labels: mine.py's rule D with a generic token pattern
(SCSS $x, Less @x, CSS var(--x)), R1 rewrites skipped, shorthands split. Token values and the candidate scale
(shared px tokens, >= 3 files) come from desire_multi.defs_tokens at the label commit's parent.
A label counts when the chosen token's value is on that scale; kinds exact / near (<= 2 px) / changed.
  eval_multi.py <system>  ->  data/mined/<system>/drift.jsonl, notes/drift_multi/<system>.json
"""
import json, math, os, re, sys
from collections import Counter, defaultdict
from desire_multi import REPOS, defs_tokens, unify, SKIP
from mine import commits, pairs, STYLE, MAX_FILE_REMOVED
from resolve import value
from eval_mined import sigma, predict, FAMILY, DECL
import subprocess

TOK = re.compile(r"(\$[\w-]+|(?<![\w@])@[a-zA-Z][\w-]*|var\(--[\w-]+[^)]*\))")


def mine(R):
    byfile, removed = defaultdict(list), defaultdict(int)
    for c, f, h in commits(R):
        if not f or not STYLE.search(f) or SKIP.search(f):
            continue
        removed[(c["commit"], f)] += len(h["-"])
        for prop, old, new in pairs(h, TOK):
            byfile[(c["commit"], f)].append(dict(c, file=f, prop=prop, literal=old, token=new))
    return [l for k, ls in byfile.items() if removed[k] <= MAX_FILE_REMOVED for l in ls]


if __name__ == "__main__":
    key = sys.argv[1]
    cfg = REPOS[key]
    R, exts = cfg["path"], cfg.get("exts", ("*.scss",))
    L = mine(R)
    os.makedirs(f"../data/mined/{key}", exist_ok=True)
    with open(f"../data/mined/{key}/drift.jsonl", "w") as fo:
        for l in L:
            fo.write(json.dumps(l) + "\n")
    split = []
    for l in L:
        a, b = l["literal"].split(), re.sub(r"/\*.*?\*/", "", l["token"]).split()
        split += [dict(l, literal=x, token=y) for x, y in zip(a, b) if x != y] if len(a) == len(b) > 1 else [dict(l, token=" ".join(b))]
    cache, rows, skip = {}, [], Counter()
    for l in split:
        c = l["commit"] + "^"
        if c not in cache:
            cache[c] = defs_tokens(R, c, exts)
        defs, tok = cache[c]
        lv, tv = value(unify(l["literal"]), defs), value(unify(l["token"]), defs)
        if not (lv and tv and lv[0] == tv[0] == "px" and lv[1] > 0 and tv[1] > 0):
            skip["not a resolvable positive length"] += 1
            continue
        scale = sorted({v[1] for v in tok.values()})
        if tv[1] not in scale or len(scale) < 2:
            skip["token value not on the shared scale"] += 1
            continue
        sg = sigma(scale)
        near = min(scale, key=lambda s: abs(math.log(lv[1]) - math.log(s)) / sg[s])
        d = abs(lv[1] - tv[1])
        # near = an OFF-scale literal within 2 px of the chosen token; an on-scale literal swapped for another
        # value is a deliberate change, not drift
        kind = "exact" if d < .01 else "near" if d <= 2 and lv[1] not in scale else "changed"
        ctx = Counter()
        if kind != "exact":  # file context: token values this file already uses for the same property family
            txt = subprocess.run(["git", "-C", R, "show", f"{c}:{l['file']}"], capture_output=True, text=True, errors="replace").stdout
            for p_, v_ in DECL.findall(txt):
                if FAMILY(p_) == FAMILY(l["prop"]):
                    for t_ in TOK.findall(v_):
                        r_ = value(unify(t_), defs)
                        if r_ and r_[0] == "px" and r_[1] in scale:
                            ctx[r_[1]] += 1
        rows.append(dict(commit=l["commit"][:10], date=l["date"], author=l["author"], file=l["file"], prop=l["prop"], lit=lv[1], tok=tv[1],
                         kind=kind, exact=d < .01, nearest=near == tv[1], ctx_n=sum(ctx.values()),
                         context=predict(lv[1], scale, ctx, "mixture+context") == tv[1]))
    out = dict(system=key, mined=len(L), skipped=dict(skip), kinds=dict(Counter(r["kind"] for r in rows)))
    sub = [r for r in rows if r["kind"] in ("exact", "near")]
    if sub:
        out["exact+near"] = dict(n=len(sub), commits=len({r["commit"] for r in sub}), authors=len({r["author"] for r in sub}),
                                 nearest_correct=sum(r["nearest"] for r in sub), exact_correct=sum(r["exact"] for r in sub))
    near = [r for r in rows if r["kind"] == "near"]
    out["near only"] = dict(n=len(near), nearest_correct=sum(r["nearest"] for r in near), context_correct=sum(r["context"] for r in near),
                            with_context=sum(r["ctx_n"] > 0 for r in near))
    os.makedirs("../notes/drift_multi", exist_ok=True)
    json.dump(dict(out, rows=rows), open(f"../notes/drift_multi/{key}.json", "w"), indent=1)
    print(json.dumps(out))
