"""Drift detectors. Each returns {site_id: action} for every literal site.
Actions: 'bind:<type>.<token>', 'new:<group>', 'leave'.
"""
import math, re
from collections import Counter, defaultdict
from colorspace import hex_to_oklab

GOVERNED = ("color", "space", "radius", "font")
AMBIG = 1.0  # m above this to every token: not a plausible typo of any one token


def governed(s):
    """Shared trivial rule for every method: only governed props with non-zero literals are candidates."""
    return s["type"] in GOVERNED and s["literal"] not in (0, "0")


# ---------- geometry: per-token mixture components ----------
class Space:
    """Token values embedded in a perceptual space: OKLab for color, log-px for sizes.
    Each token is a Gaussian with spread sigma_k = half the gap to its nearest neighbour token
    (spread declared by the scale's own geometry)."""

    def __init__(self, tokens):
        self.emb, self.sig = {}, {}
        for t in GOVERNED:
            pts = {f"{t}.{k}": self.embed(t, v) for k, v in tokens[t].items()}
            self.emb[t] = pts
            for k, p in pts.items():
                gap = min(dist(p, q) for j, q in pts.items() if j != k)
                self.sig[k] = gap / 2
        self.exact = {(t, norm(v)): f"{t}.{k}" for t in GOVERNED for k, v in tokens[t].items()}

    @staticmethod
    def embed(t, v):
        return hex_to_oklab(v) if t == "color" else [math.log(max(float(v), 0.5))]

    def m(self, s, k):
        return dist(self.embed(s["type"], s["literal"]), self.emb[s["type"]][k]) / self.sig[k]

    def ranked(self, s):
        return sorted((self.m(s, k), k) for k in self.emb[s["type"]])


def dist(p, q):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(p, q)))


def norm(v):
    return v.lower() if isinstance(v, str) else v


# ---------- baselines ----------
def exact_match(tokens, sites):
    sp = Space(tokens)
    return {s["id"]: ("bind:" + sp.exact[(s["type"], norm(s["literal"]))]
                      if governed(s) and (s["type"], norm(s["literal"])) in sp.exact else "leave")
            for s in lits(sites)}


def nearest(tokens, sites, tau=3.0):
    sp = Space(tokens)
    out = {}
    for s in lits(sites):
        if not governed(s):
            out[s["id"]] = "leave"; continue
        m, k = sp.ranked(s)[0]
        out[s["id"]] = f"bind:{k}" if m <= tau else "leave"
    return out


def nearest_repeat(tokens, sites, min_count=5):
    """Heuristic-tool stand-in: nearest token, but a non-token value repeated >= min_count times becomes a new token."""
    sp = Space(tokens)
    out = nearest(tokens, sites)
    cnt = Counter((s["type"], norm(s["literal"])) for s in lits(sites) if governed(s))
    for s in lits(sites):
        key = (s["type"], norm(s["literal"]))
        if governed(s) and key not in sp.exact and cnt[key] >= min_count:
            out[s["id"]] = f"new:{key[0]}:{key[1]}"
    return out


# ---------- the paper's method ----------
def suffix(name):
    return re.findall(r"[A-Z][a-z]+", name)[-1]


def context_prior(s, bound, elems, K=15):
    """Efros–Leung style: find token-bound sites with the same prop whose neighbourhood best matches
    this site's (same slot, same component family, same sibling bindings), and let them vote."""
    mine = {(b["prop"], b["token"]) for b in elems[s["elem"]] if b["token"]}
    scored = []
    for b in bound.get(s["prop"], ()):
        if b["elem"] == s["elem"]:
            continue
        theirs = {(x["prop"], x["token"]) for x in elems[b["elem"]] if x["token"]}
        sim = 2.0 * (b["slot"] == s["slot"]) + 2.0 * (suffix(b["component"]) == suffix(s["component"])) \
            + 3.0 * len(mine & theirs) / max(1, len(mine | theirs))
        scored.append((sim, b["token"]))
    scored.sort(reverse=True)
    votes = Counter()
    for sim, tok in scored[:K]:
        votes[tok] += math.exp(sim)
    z = sum(votes.values()) or 1
    return {k: v / z for k, v in votes.items()}


def mixture(tokens, sites, use_context=True, alpha=1.0, eps=0.15, tau=4.0, min_group=5, min_comps=4):
    sp = Space(tokens)
    bound, elems = defaultdict(list), defaultdict(list)
    for s in sites:
        elems[s["elem"]].append(s)
        if s["token"]:
            bound[s["prop"]].append(s)
    L = [s for s in lits(sites) if governed(s)]
    out = {s["id"]: "leave" for s in lits(sites)}

    def posterior(s):
        prior = context_prior(s, bound, elems) if use_context else {}
        lp = {}
        for m, k in sp.ranked(s):
            p = prior.get(k, 0.0)
            lp[k] = -0.5 * m * m + (alpha * math.log(p + 1e-3) if use_context else 0.0)
        best = max(lp, key=lp.get)
        return best, sp.m(s, best), prior

    post = {s["id"]: posterior(s) for s in L}

    # spec evolution: dense groups of near-identical literals that no single token explains
    groups = group_literals(L, sp, eps)
    for g in groups:
        if len(g) < min_group or len({s["component"] for s in g}) < min_comps:
            continue
        if sp.ranked(g[0])[0][0] <= 0.3:   # a token already sits at the group's centre
            continue
        if use_context:
            maps = Counter(post[s["id"]][0] for s in g)
            top, n = maps.most_common(1)[0]
            mean_m = sum(sp.m(s, top) for s in g) / len(g)
            explained = n / len(g) >= 0.6 and mean_m <= AMBIG
        else:
            explained = sp.ranked(g[0])[0][0] <= AMBIG
        if not explained:
            for s in g:
                out[s["id"]] = f"new:{s['type']}:{norm(g[0]['literal'])}"
    for s in L:
        if out[s["id"]] == "leave":
            best, m, _ = post[s["id"]]
            out[s["id"]] = f"bind:{best}" if m <= tau else "leave"
    return out


def group_literals(L, sp, eps):
    """Single-linkage groups within eps (OKLab units for color, log units for sizes)."""
    groups = []
    for t in GOVERNED:
        pts = [(s, sp.embed(t, s["literal"])) for s in L if s["type"] == t]
        parent = list(range(len(pts)))

        def find(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]; i = parent[i]
            return i
        e = eps * (0.1 if t == "color" else 0.1)
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):
                if dist(pts[i][1], pts[j][1]) <= e:
                    parent[find(i)] = find(j)
        by = defaultdict(list)
        for i, (s, _) in enumerate(pts):
            by[find(i)].append(s)
        groups += list(by.values())
    return groups


def lits(sites):
    return [s for s in sites if s["token"] is None]


METHODS = {
    "exact": exact_match,
    "nearest": nearest,
    "nearest+repeat": nearest_repeat,
    "mixture": lambda T, S: mixture(T, S, use_context=False),
    "mixture+context": mixture,
}
