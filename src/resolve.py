"""Resolve SCSS token values at a given commit: every `$name: value` definition in the repo's .scss files,
evaluated to px (lengths) or a hex string (colours). Unresolvable values stay None."""
import re, subprocess
from functools import lru_cache

DEF = re.compile(r"^[ \t]*\$([\w-]+)[ \t]*:[ \t]*([^;\n]+?)\s*(?:!default)?\s*;", re.M)


@lru_cache(maxsize=256)
def defs_at(repo, commit):
    out = subprocess.run(["git", "-C", repo, "grep", "-h", "-E", r"^\s*\$[a-zA-Z0-9_-]+\s*:", commit, "--", "*.scss"],
                         capture_output=True, text=True, errors="replace").stdout
    d = {}
    for m in DEF.finditer(out):
        d.setdefault(m.group(1), m.group(2).strip())  # first definition wins
    return d


NUM = r"(-?\d*\.?\d+)"
# Carbon v11 generates these from JS (packages/layout); values unchanged since v10's carbon--spacing-NN.
SCALE_V11 = {**{f"spacing-{i:02d}": v for i, v in enumerate([2, 4, 8, 12, 16, 24, 32, 40, 48, 64, 80, 96, 160], 1)},
             **{f"layout-{i:02d}": v for i, v in enumerate([16, 24, 32, 48, 64, 96, 160], 1)}}


def value(expr, defs, depth=0):
    """-> ('px', float) | ('color', '#rrggbb') | None"""
    if expr is None or depth > 12:
        return None
    e = expr.strip()
    if e.startswith("(") and e.endswith(")"):
        e = e[1:-1].strip()
    e = re.sub(r"\s*!default$", "", e)
    if m := re.fullmatch(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})", e):
        h = m.group(1).lower()
        return ("color", "#" + ("".join(c * 2 for c in h) if len(h) == 3 else h))
    if m := re.fullmatch(NUM + r"px", e):
        return ("px", float(m.group(1)))
    if m := re.fullmatch(NUM + r"rem", e):
        return ("px", float(m.group(1)) * 16)
    if m := re.fullmatch(NUM + r"em", e):
        return ("px", float(m.group(1)) * 16)
    if e in ("0",):
        return ("px", 0.0)
    if m := re.fullmatch(r"(?:[\w-]+\.)?(?:carbon--)?(?:rem|to-rem|px-to-rem)\((.+)\)", e):
        return value(m.group(1), defs, depth + 1)
    if m := re.fullmatch(r"(?:[\w-]+\.)?(?:carbon--)?mini-units\(" + NUM + r"\)", e):
        return ("px", float(m.group(1)) * 8)
    if m := re.fullmatch(r"(?:[\w-]+\.)?\$([\w-]+)", e):
        name = m.group(1)
        if name not in defs and name.replace("carbon--", "") in SCALE_V11:
            return ("px", float(SCALE_V11[name.replace("carbon--", "")]))
        return value(defs.get(name) or defs.get("carbon--" + name) or defs.get(name.replace("carbon--", "")), defs, depth + 1)
    if m := re.fullmatch(r"var\(--(?:#\{\$prefix\}|cds)-([\w-]+)(?:,\s*(.+))?\)", e):
        return value("$" + m.group(1), defs, depth + 1) or value(m.group(2), defs, depth + 1)
    if m := re.fullmatch(r"(.+?)\s*\*\s*" + NUM, e):
        v = value(m.group(1), defs, depth + 1)
        return ("px", v[1] * float(m.group(2))) if v and v[0] == "px" else None
    if m := re.fullmatch(r"-\s*(.+)", e):
        v = value(m.group(1), defs, depth + 1)
        return ("px", -v[1]) if v and v[0] == "px" else None
    return None


def token_table(repo, commit):
    """All definitions resolved at a commit: name -> (kind, value)."""
    defs = defs_at(repo, commit)
    t = {}
    for k, v in defs.items():
        r = value(v, defs)
        if r:
            t[k] = r
    return t, defs
