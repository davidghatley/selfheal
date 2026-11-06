"""Simulated git history for the synthetic seeds (step 3). An ASSUMPTION, not data: the processes below encode the
hypothesis that design decisions arrive in bursts from few authors and persist, while typos trickle in from many
authors and earlier copies get fixed. Noise keeps it from being trivially separable:
  - true clusters: burst (1-2 commits, <= 14 days, 1 author) with p = 0.7, else trickle (60-240 days, 2-4 authors)
  - drift sites: independent days over two years, Zipf authors over a pool of 12;
    with p = 0.25 a value's copies in one component family land in a single copy-paste commit
  - fixed earlier copies ("ghosts"): drift values Poisson(1.5); cluster values Poisson(0.3)
Writes data/sN/history.json.
"""
import json, random, sys
from collections import defaultdict
from pathlib import Path

AUTHORS = [f"dev{i}" for i in range(12)]
W = [1 / (i + 1) for i in range(12)]


def poisson(rng, lam):
    k, p, L = 0, 1.0, pow(2.718281828, -lam)
    while True:
        p *= rng.random()
        if p < L:
            return k
        k += 1


def simulate(seed):
    rng = random.Random(1000 + seed)
    truth = json.loads(Path(f"../data/s{seed}/truth.json").read_text())
    lit = [s for s in truth if s["cls"] not in ("bound", "intentional")]
    hist, ghosts, commit = {}, defaultdict(int), 0
    by_cluster = defaultdict(list)
    for s in lit:
        if s["truth"].startswith("new:"):
            by_cluster[s["truth"]].append(s)
    for cid, sites in by_cluster.items():
        if rng.random() < 0.7:
            start, a = rng.randint(200, 650), rng.choice(AUTHORS)
            commits = [commit + 1, commit + 2]; commit += 2
            for s in sites:
                hist[s["id"]] = dict(day=start + rng.randint(0, 14), author=a, commit=rng.choice(commits))
        else:
            start, span = rng.randint(100, 450), rng.randint(60, 240)
            team = rng.sample(AUTHORS, rng.randint(2, 4))
            for s in sites:
                commit += 1
                hist[s["id"]] = dict(day=start + rng.randint(0, span), author=rng.choice(team), commit=commit)
        for s in sites:
            ghosts[f"{s['type']}:{s['literal']}"] += 0  # touch key
        ghosts[f"{sites[0]['type']}:{sites[0]['literal']}"] += poisson(rng, 0.3)
    fam = defaultdict(list)
    for s in lit:
        if not s["truth"].startswith("new:"):
            fam[(s["type"], s["literal"], s["role"])].append(s)
    for key, sites in fam.items():
        if len(sites) > 1 and rng.random() < 0.25:
            commit += 1
            d, a = rng.randint(0, 720), rng.choices(AUTHORS, W)[0]
            for s in sites:
                hist[s["id"]] = dict(day=d, author=a, commit=commit)
        else:
            for s in sites:
                commit += 1
                hist[s["id"]] = dict(day=rng.randint(0, 720), author=rng.choices(AUTHORS, W)[0], commit=commit)
    for s in lit:
        if not s["truth"].startswith("new:"):
            k = f"{s['type']}:{s['literal']}"
            if k not in ghosts:
                ghosts[k] = poisson(rng, 1.5)
    return dict(sites=hist, ghosts=dict(ghosts))


def features(members, H):
    """Per group: burst = share of uses inside the densest 30-day window; authors = distinct authors;
    survival = present copies / (present + earlier copies already fixed)."""
    days = sorted(H["sites"][s["id"]]["day"] for s in members)
    best = max(sum(1 for d in days if a <= d <= a + 30) for a in days)
    k = f"{members[0]['type']}:{members[0]['literal']}"
    g = H["ghosts"].get(k, 0)
    return dict(burst=best / len(days), authors=len({H["sites"][s["id"]]["author"] for s in members}),
                survival=len(members) / (len(members) + g))


def desire_votes(f):
    """Pre-specified (not tuned): one vote each for burst >= 0.6, authors <= 2, survival >= 0.75."""
    return (f["burst"] >= 0.6) + (f["authors"] <= 2) + (f["survival"] >= 0.75)


if __name__ == "__main__":
    for s in sys.argv[1:] or "12345":
        json.dump(simulate(int(s)), open(f"../data/s{s}/history.json", "w"))
    print("ok")
