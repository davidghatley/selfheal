"""Mine desire-path labels from Carbon's history with monthly snapshots (first-parent, main branch).

Per snapshot t: the token values defined in SCSS (all `$name:` that resolve to px or a colour) and every
literal-only governed declaration (`prop: <one literal>;`) with its value, file and prop.
An OFF-SPEC CLUSTER at t is a value (kind, v) that no token has, used as a literal >= 3 times in >= 2 files.
Decision point = the first snapshot where a value qualifies. Outcome within the next 24 months:
  desire path (P): a token with that value is defined
  drift       (N): no token, and literal uses fall to <= 50% of the decision-time count
  unresolved     : neither (excluded from precision)
Writes data/mined/snapshots.json and data/mined/clusters.json.
"""
import json, re, subprocess, sys
from collections import Counter, defaultdict
from resolve import DEF, value, SCALE_V11

R = "/mnt/work/selfheal-repos/carbon"
GOV = r"(?:margin|padding|gap|top|right|bottom|left|inset|width|height|min-width|min-height|max-width|max-height|" \
      r"border-radius|font-size|line-height|color|background-color|background|border-color|fill|letter-spacing)" \
      r"(?:-(?:top|right|bottom|left|inline|block|start|end))*"
LDECL = re.compile(r"^(?P<file>[^:]+):\s*(?P<prop>" + GOV + r")\s*:\s*(?P<val>[^;$]+?)\s*;", re.M)
SINGLE = re.compile(r"^(?:-?\d*\.?\d+(?:px|rem)|(?:[\w-]+\.)?(?:carbon--)?(?:rem|to-rem)\(-?\d*\.?\d+px\)|#[0-9a-fA-F]{3,6})$")


def git(*a):
    return subprocess.run(["git", "-C", R, *a], capture_output=True, text=True, errors="replace").stdout


def snapshots():
    first = git("log", "--reverse", "--first-parent", "--format=%as", "HEAD").split()[0]
    y, m = map(int, first.split("-")[:2])
    out = []
    while (y, m) <= (2026, 11):
        c = git("rev-list", "--first-parent", "-1", f"--before={y:04d}-{m:02d}-01", "HEAD").strip()
        if c and (not out or out[-1][1] != c):
            out.append((f"{y:04d}-{m:02d}", c))
        m += 1
        if m > 12:
            y, m = y + 1, 1
    return out


def snap(c):
    defs = {}
    for mm in DEF.finditer(git("grep", "-h", "-E", r"^\s*\$[a-zA-Z0-9_-]+\s*:", c, "--", "*.scss")):
        defs.setdefault(mm.group(1), mm.group(2).strip())
    tok = {}
    for k in defs:
        v = value("$" + k, defs)
        if v and not (v[0] == "px" and v[1] <= 0):
            tok[k] = v
    if any(k.startswith("spacing-0") for k in defs) is False and "layout" in git("ls-tree", "--name-only", c, "packages"):
        pass
    lits = []
    raw = git("grep", "-E", r"^\s*" + GOV.replace("(?:", "(") + r"\s*:\s*[^;$]+;", c, "--", "*.scss", "*.css")  # ERE has no (?:
    for line in raw.splitlines():
        _, f, body = line.split(":", 2)
        mm = LDECL.match("x:" + body.strip())
        if not mm:
            continue
        if "node_modules" in f or "/vendor" in f or "flatpickr" in f:
            continue
        val = mm.group("val").strip()
        if not SINGLE.match(val):
            continue
        v = value(val, {})
        if v and v[0] == "px" and v[1] > 0:  # px only: v11 colour tokens are generated from JS
            lits.append((f.rsplit("/", 1)[-1], mm.group("prop"), v[0], v[1]))
    # v11 scale lives in JS; count it as defined once the v11 names are referenced
    vals = {tuple(v) for v in tok.values() if v[0] == "px"}
    if "$spacing-05" in git("grep", "-c", "-F", "$spacing-05", c, "--", "*.scss"):
        vals |= {("px", float(x)) for x in SCALE_V11.values()}
    # token references per px value (declarations of governed props that use a $token)
    refs = Counter()
    raw = git("grep", "-h", "-o", "-E", r"^\s*" + GOV.replace("(?:", "(") + r"\s*:[^;]*\$[a-zA-Z0-9_-]+", c, "--", "*.scss")
    v11 = "$spacing-05" in git("grep", "-c", "-F", "$spacing-05", c, "--", "*.scss")
    for line in raw.splitlines():
        for name in re.findall(r"\$([a-zA-Z0-9_-]+)", line):
            v = tok.get(name) or (("px", float(SCALE_V11[name])) if v11 and name in SCALE_V11 else None)
            if v and v[0] == "px":
                refs[v[1]] += 1
    return dict(tokens=sorted(vals), token_names={k: list(v) for k, v in tok.items()}, lits=lits,
                refs={str(k): n for k, n in refs.items()})


if __name__ == "__main__":
    S = snapshots()
    print(len(S), "snapshots", S[0][0], "->", S[-1][0], file=sys.stderr)
    data = []
    for ym, c in S:
        d = snap(c)
        d.update(month=ym, commit=c)
        data.append(d)
        print(ym, len(d["tokens"]), "token values", len(d["lits"]), "literals", file=sys.stderr)
    json.dump(data, open("../data/mined/snapshots.json", "w"))
