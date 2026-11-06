"""Healer experiments (Plan steps 4-5).
1. one-shot vs lowest-entropy-first iterative healing (WFC-style): does committing confident sites first
   sharpen the context prior for ambiguous ones?
2. behaviour preservation: perceptual change per fix, and how many fixes an ε gate would block
3. energy before/after, and idempotence (healing a healed repo is a no-op)
4. spec evolution: after adding the proposed tokens, how many other sites change their reading (lens PutGet)
"""
import copy, json, math, re, shutil, sys
from collections import Counter
from pathlib import Path
from extract import extract
from detect import Space, mixture, context_prior, governed, lits, AMBIG
from score import score
from collections import defaultdict


def tok_expr(k):
    t, name = k.split(".", 1)
    return f"tokens.{t}['{name}']"


def apply(repo, out, actions, sites, tokens):
    """Rewrite literals to token references; add new tokens to tokens.ts for 'new:' groups."""
    shutil.rmtree(out, ignore_errors=True); shutil.copytree(repo, out)
    tokens = copy.deepcopy(tokens)
    by = {s["id"]: s for s in sites}
    edits = defaultdict(dict)
    for sid, a in actions.items():
        s = by[sid]
        if a.startswith("bind:"):
            edits[s["file"]][s["line"]] = (s["prop"], tok_expr(a[5:]))
        elif a.startswith("new:"):
            _, t, v = a.split(":", 2)
            name = "x" + re.sub(r"\W", "", str(v))
            tokens[t][name] = int(v) if t != "color" else v
            edits[s["file"]][s["line"]] = (s["prop"], tok_expr(f"{t}.{name}"))
    for f, lines in edits.items():
        p = Path(out) / f
        L = p.read_text().splitlines()
        for ln, (prop, expr) in lines.items():
            ind = L[ln - 1][:len(L[ln - 1]) - len(L[ln - 1].lstrip())]
            L[ln - 1] = f"{ind}{prop}: {expr},"
        p.write_text("\n".join(L) + "\n")
    (Path(out) / "src/tokens.ts").write_text("export const tokens = " + json.dumps(tokens, indent=2) + " as const;\n")
    return tokens


def entropy(s, sp, bound, elems):
    prior = context_prior(s, bound, elems)
    lp = {k: -0.5 * m * m + math.log(prior.get(k, 0) + 1e-3) for m, k in sp.ranked(s)}
    z = max(lp.values()); ps = {k: math.exp(v - z) for k, v in lp.items()}
    tot = sum(ps.values())
    return -sum(p / tot * math.log(p / tot) for p in ps.values() if p > 0)


def iterative(repo, work, frac=0.25):
    """Lowest-entropy-first: each round commit the most certain quarter of remaining bind decisions, re-read."""
    tokens, sites = extract(repo)
    final = {}
    cur = Path(work) / "it0"; shutil.copytree(repo, cur, dirs_exist_ok=True)
    first = mixture(tokens, sites)
    for sid, a in first.items():  # spec-evolution and leave decisions are made once, up front
        if not a.startswith("bind:"):
            final[sid] = a
    rnd = 0
    while True:
        tokens, sites = extract(cur)
        sp = Space(tokens)
        bound, elems = defaultdict(list), defaultdict(list)
        for s in sites:
            elems[s["elem"]].append(s)
            if s["token"]:
                bound[s["prop"]].append(s)
        todo = [s for s in lits(sites) if governed(s) and s["id"] not in final]
        if not todo:
            break
        acts = mixture(tokens, sites)
        todo.sort(key=lambda s: entropy(s, sp, bound, elems))
        commit = todo[:max(1, int(len(todo) * frac))]
        step = {s["id"]: acts[s["id"]] for s in commit if acts[s["id"]].startswith("bind:")}
        for s in commit:
            final[s["id"]] = acts[s["id"]]
        rnd += 1
        nxt = Path(work) / f"it{rnd}"
        apply(cur, nxt, step, sites, tokens)
        cur = nxt
    return final, rnd


def change(s, k, sp, tokens):
    """Perceptual change a fix makes: OKLab ΔE×100 for colour, px for sizes."""
    t, name = k.split(".", 1)
    v = tokens[t][name]
    if t == "color":
        a, b = Space.embed(t, s["literal"]), Space.embed(t, v)
        return 100 * math.dist(a, b)
    return abs(min(float(v), 999) - min(float(s["literal"]), 999))  # pill radii look the same past ~999px


def energy(tokens, sites):
    """E = Σ m(u)^2 to the nearest token (literals) + pairwise disagreement among same-slot same-prop
    bound siblings across components of the same family + λ·(# literals in governed props)."""
    sp = Space(tokens)
    unary = sum(min(sp.ranked(s))[0] ** 2 for s in lits(sites) if governed(s))
    fam = defaultdict(Counter)
    for s in sites:
        if s["token"]:
            fam[(re.findall(r"[A-Z][a-z]+", s["component"])[-1], s["slot"], s["prop"])][s["token"]] += 1
    pair = sum(sum(c.values()) - max(c.values()) for c in fam.values())
    viol = sum(1 for s in lits(sites) if governed(s))
    return dict(unary=round(unary, 1), pairwise=pair, violations=viol, E=round(unary + pair + 1.0 * viol, 1))


def main(d, work):
    d, work = Path(d), Path(work)
    shutil.rmtree(work, ignore_errors=True); work.mkdir(parents=True)
    truth = json.loads((d / "truth.json").read_text())
    T = {s["id"]: s for s in truth}
    tokens, sites = extract(d / "repo")
    sp = Space(tokens)
    res = {}
    one = mixture(tokens, sites)
    res["one_shot"] = score(truth, one)
    it, rounds = iterative(d / "repo", work)
    res["iterative"] = score(truth, it); res["iterative"]["rounds"] = rounds

    # behaviour preservation for the one-shot fixes
    ch = defaultdict(list)
    for sid, a in one.items():
        if a.startswith("bind:"):
            ch[T[sid]["cls"]].append(change(by_id(sites)[sid], a[5:], sp, tokens))
    res["change"] = {c: dict(n=len(v), mean=round(sum(v) / len(v), 2), max=round(max(v), 2),
                             over_eps=sum(x > 2.0 for x in v)) for c, v in ch.items()}

    healed = work / "healed"
    new_tokens = apply(d / "repo", healed, one, sites, tokens)
    t2, s2 = extract(healed)
    res["energy_before"] = energy(tokens, sites); res["energy_after"] = energy(t2, s2)
    again = mixture(t2, s2)
    res["idempotent"] = all(a == "leave" for a in again.values())
    res["second_pass_changes"] = sum(a != "leave" for a in again.values())

    # lens PutGet: read the ORIGINAL code under the evolved spec
    _, s_orig = extract(d / "repo")
    evolved = mixture(new_tokens, s_orig)
    flips = [sid for sid in one if one[sid].startswith("bind:") and evolved[sid] != one[sid]]
    res["putget_flips"] = len(flips)
    res["putget_flips_wrong"] = sum(evolved[f] != T[f]["truth"] for f in flips)
    res["putget_flip_examples"] = [(f, T[f]["literal"], one[f], evolved[f], T[f]["truth"]) for f in flips[:6]]
    # GetPut: does evolving again keep growing the spec?
    grown = {a for a in evolved.values() if a.startswith("new:")}
    res["second_evolution_new_tokens"] = len(grown)
    return res


def by_id(sites):
    return {s["id"]: s for s in sites}


if __name__ == "__main__":
    seeds = sys.argv[2:] or ["1", "2", "3", "4", "5"]
    allr = {s: main(f"{sys.argv[1]}/s{s}", f"../out/heal/s{s}") for s in seeds}
    json.dump(allr, open("../notes/heal.json", "w"), indent=1, default=str)
    for s, r in allr.items():
        print(f"seed {s}: one-shot amb={r['one_shot']['ambiguous']:.2f} acc={r['one_shot']['action_acc']:.2f} | "
              f"iterative amb={r['iterative']['ambiguous']:.2f} acc={r['iterative']['action_acc']:.2f} rounds={r['iterative']['rounds']} | "
              f"E {r['energy_before']['E']}->{r['energy_after']['E']} idempotent={r['idempotent']} | "
              f"putget flips={r['putget_flips']} (wrong {r['putget_flips_wrong']}) | regrow={r['second_evolution_new_tokens']}")
        print("   change:", r["change"])
