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
    "bootstrap": dict(path="/mnt/work/selfheal-repos/bootstrap", exts=("*.scss", "*.less")),
    "primer-css": dict(path="/mnt/work/selfheal-repos/primer-css"),
    "blueprint": dict(path="/mnt/work/selfheal-repos/blueprint"),
    "mdc-web": dict(path="/mnt/work/selfheal-repos/mdc-web"),
    "ant-design": dict(path="/mnt/work/selfheal-repos/ant-design", exts=("*.less",)),
    "govuk-frontend": dict(path="/mnt/work/selfheal-repos/govuk-frontend"),
    "uswds": dict(path="/mnt/work/selfheal-repos/uswds"),
    "spectrum-css": dict(path="/mnt/work/selfheal-repos/spectrum-css", exts=("*.css",)),
    "foundation": dict(path="/mnt/work/selfheal-repos/foundation"),
    "patternfly": dict(path="/mnt/work/selfheal-repos/patternfly", exts=("*.scss", "*.css")),
    "lightning": dict(path="/mnt/work/selfheal-repos/lightning"),
    "clarity": dict(path="/mnt/work/selfheal-repos/clarity"),
    "semantic-ui": dict(path="/mnt/work/selfheal-repos/semantic-ui", exts=("*.less", "*.variables", "*.overrides")),
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


LESS_DEF = re.compile(r"^[ \t]*@([\w-]+)[ \t]*:[ \t]*([^;\n{}]+?)\s*;", re.M)
CSS_DEF = re.compile(r"^[ \t]*--([\w-]+)[ \t]*:[ \t]*([^;\n{}]+?)\s*;", re.M)
REF = re.compile(r"\$([a-zA-Z0-9_-]+)|(?<![\w@])@([a-zA-Z][\w-]*)|var\(\s*--([\w-]+)")


def unify(expr):
    """Less @x and CSS var(--x, fallback) -> the resolver's $x / $--x."""
    expr = re.sub(r"var\(\s*--([\w-]+)\s*(?:,[^)]*)?\)", r"$--\1", expr)
    return re.sub(r"(?<![\w@])@([a-zA-Z][\w-]*)", r"$\1", expr)


def ref_names(body):
    return [a or b or ("--" + c) for a, b, c in REF.findall(body)]


def snap(R, c, carbon_v11=False, exts=("*.scss",)):
    defs, tok = defs_tokens(R, c, exts)
    return _snap(R, c, defs, tok, carbon_v11, exts)


def defs_tokens(R, c, exts=("*.scss",)):
    """All variable definitions at commit c (SCSS $x, Less @x, CSS --x; unified for resolve.value) and the shared
    px tokens among them (referenced from >= MIN_REF_FILES files)."""
    defs = {}
    patt = {"*.scss": (r"^\s*\$[a-zA-Z0-9_-]+\s*:", DEF, ""), "*.less": (r"^\s*@[a-zA-Z][a-zA-Z0-9_-]*\s*:", LESS_DEF, ""),
            "*.css": (r"^\s*--[a-zA-Z0-9_-]+\s*:", CSS_DEF, "--")}
    for ext in exts:
        g, rx, pre = patt.get(ext, patt["*.less"])  # other extensions (Semantic UI's *.variables) are Less
        for line in git(R, "grep", "-E", g, c, "--", ext).splitlines():
            _, f, body = line.split(":", 2)
            if SKIP.search(f):
                continue
            if mm := rx.match(body):
                defs.setdefault(pre + mm.group(1), unify(mm.group(2).strip()))
        if ext == "*.scss" and "*.css" in exts:  # custom properties set inside .scss too
            for line in git(R, "grep", "-E", patt["*.css"][0], c, "--", ext).splitlines():
                _, f, body = line.split(":", 2)
                if not SKIP.search(f) and (mm := CSS_DEF.match(body)):
                    defs.setdefault("--" + mm.group(1), unify(mm.group(2).strip()))
    tok_all = {k: v for k in defs if (v := value("$" + k, defs)) and v[0] == "px" and v[1] > 0}
    users = {}
    for line in git(R, "grep", "-o", "-E", r"(\$[a-zA-Z0-9_-]+|@[a-zA-Z][a-zA-Z0-9_-]*|var\(\s*--[a-zA-Z0-9_-]+)", c, "--", *exts).splitlines():
        _, f, name = line.split(":", 2)
        name = re.sub(r"^(\$|@|var\(\s*)", "", name)
        if not SKIP.search(f) and name in tok_all:
            users.setdefault(name, set()).add(f)
    tok = {k: v for k, v in tok_all.items() if len(users.get(k, ())) >= MIN_REF_FILES}
    return defs, tok


def _snap(R, c, defs, tok, carbon_v11, exts):
    vals = {tuple(v) for v in tok.values()}
    v11 = carbon_v11 and "$spacing-05" in git(R, "grep", "-c", "-F", "$spacing-05", c, "--", "*.scss")
    if v11:
        vals |= {("px", float(x)) for x in SCALE_V11.values()}
    lits, refs = [], Counter()
    raw = git(R, "grep", "-E", r"^\s*" + GOV.replace("(?:", "(") + r"\s*:\s*[^;]+;", c, "--", *exts)
    for line in raw.splitlines():
        _, f, body = line.split(":", 2)
        if SKIP.search(f):
            continue
        body = body.strip()
        names = ref_names(body)
        if names or "$" in body:
            for name in names:
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
        d = snap(cfg["path"], c, cfg.get("carbon_v11", False), cfg.get("exts", ("*.scss",)))
        d.update(month=ym, commit=c)
        data.append(d)
        print(ym, len(d["tokens"]), "token values", len(d["lits"]), "literals", file=sys.stderr, flush=True)
    os.makedirs(f"../data/mined/{key}", exist_ok=True)
    json.dump(data, open(f"../data/mined/{key}/snapshots_v2.json", "w"))
