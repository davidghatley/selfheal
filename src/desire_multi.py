"""Desire-path snapshots for any SCSS design system (generalises desire.py; rules in docs/mining.md).

Per monthly first-parent snapshot: token values (every `$name:` in .scss that resolves to px), literal-only governed
declarations in HAND-WRITTEN .scss (no .css, no vendor/dist/build/node_modules), and token references per px value.
Unlike desire.py (Carbon, the committed headline), compiled CSS is never counted.

  desire_multi.py <repo-key>   ->  data/mined/<key>/snapshots_v2.json
v2 (2026-11-06): docs/site folders skipped; a token must be referenced from >= 3 files.
"""
import json, os, re, subprocess, sys
from collections import Counter
from resolve import DEF, value, SCALE_V11
from desire import GOV, LDECL, SINGLE

REPOS = {
    "carbon": dict(path="/mnt/work/selfheal-repos/carbon", carbon_v11=True),
    "eui": dict(path="/mnt/work/selfheal-repos/eui"),
    "gitlab": dict(path="/mnt/work/selfheal-repos/gitlab-ui"),
}
SKIP = re.compile(r"(node_modules|/vendor/|^vendor/|/dist/|^dist/|/build/|flatpickr|\.min\.|(^|/)docs?/|doc_site|website|storybook|/examples?/|\.stories\.|/test/|__tests__)")
MIN_REF_FILES = 3  # v2: a token is a shared variable, referenced from >= 3 files


def git(R, *a):
    return subprocess.run(["git", "-C", R, *a], capture_output=True, text=True, errors="replace").stdout


def snapshots(R):
    first = git(R, "log", "--reverse", "--first-parent", "--format=%as", "HEAD").split()[0]
    y, m = map(int, first.split("-")[:2])
    out = []
    while (y, m) <= (2026, 11):
        c = git(R, "rev-list", "--first-parent", "-1", f"--before={y:04d}-{m:02d}-01", "HEAD").strip()
        if c and (not out or out[-1][1] != c):
            out.append((f"{y:04d}-{m:02d}", c))
        m += 1
        if m > 12:
            y, m = y + 1, 1
    return out


def snap(R, c, carbon_v11=False):
    defs = {}
    raw = git(R, "grep", "-E", r"^\s*\$[a-zA-Z0-9_-]+\s*:", c, "--", "*.scss")
    for line in raw.splitlines():
        _, f, body = line.split(":", 2)
        if SKIP.search(f):
            continue
        if mm := DEF.match(body):
            defs.setdefault(mm.group(1), mm.group(2).strip())
    tok_all = {k: v for k in defs if (v := value("$" + k, defs)) and v[0] == "px" and v[1] > 0}
    users = {}
    for line in git(R, "grep", "-o", "-E", r"\$[a-zA-Z0-9_-]+", c, "--", "*.scss").splitlines():
        _, f, name = line.split(":", 2)
        if not SKIP.search(f) and name[1:] in tok_all:
            users.setdefault(name[1:], set()).add(f)
    tok = {k: v for k, v in tok_all.items() if len(users.get(k, ())) >= MIN_REF_FILES}
    vals = {tuple(v) for v in tok.values()}
    v11 = carbon_v11 and "$spacing-05" in git(R, "grep", "-c", "-F", "$spacing-05", c, "--", "*.scss")
    if v11:
        vals |= {("px", float(x)) for x in SCALE_V11.values()}
    lits, refs = [], Counter()
    raw = git(R, "grep", "-E", r"^\s*" + GOV.replace("(?:", "(") + r"\s*:\s*[^;]+;", c, "--", "*.scss")
    for line in raw.splitlines():
        _, f, body = line.split(":", 2)
        if SKIP.search(f):
            continue
        body = body.strip()
        if "$" in body:
            for name in re.findall(r"\$([a-zA-Z0-9_-]+)", body):
                v = tok.get(name) or (("px", float(SCALE_V11[name])) if v11 and name in SCALE_V11 else None)
                if v:
                    refs[v[1]] += 1
            continue
        mm = LDECL.match("x:" + body)
        if not mm or not SINGLE.match(mm.group("val").strip()):
            continue
        v = value(mm.group("val").strip(), {})
        if v and v[0] == "px" and v[1] > 0:
            lits.append((f.rsplit("/", 1)[-1], mm.group("prop"), v[0], v[1], f))
    return dict(tokens=sorted(vals), token_names={k: list(v) for k, v in tok.items()}, lits=lits,
                refs={str(k): n for k, n in refs.items()})


if __name__ == "__main__":
    key = sys.argv[1]
    cfg = REPOS[key]
    S = snapshots(cfg["path"])
    print(key, len(S), "snapshots", S[0][0], "->", S[-1][0], file=sys.stderr)
    data = []
    for ym, c in S:
        d = snap(cfg["path"], c, cfg.get("carbon_v11", False))
        d.update(month=ym, commit=c)
        data.append(d)
        print(ym, len(d["tokens"]), "token values", len(d["lits"]), "literals", file=sys.stderr, flush=True)
    os.makedirs(f"../data/mined/{key}", exist_ok=True)
    json.dump(data, open(f"../data/mined/{key}/snapshots_v2.json", "w"))
