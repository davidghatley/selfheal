"""Synthetic drift benchmark: a small React app generated from a token set, with injected drift.

Every style site gets a ground-truth action:
  bind:<token>   a hardcoded literal that should reference that token
  new:<cluster>  part of a coordinated off-spec cluster; the spec should gain a token
  leave          an intentional literal (0, 1px hairline, 100%) or an already-bound site
Drift classes: exact, near, ambiguous (between two tokens; context decides), cluster, intentional, bound.
"""
import json, random, sys
from pathlib import Path
from colorspace import hex_to_oklab, oklab_to_hex

TOKENS = {
    "color": {
        "text.primary": "#111827", "text.secondary": "#4b5563", "text.muted": "#9ca3af",
        "bg.surface": "#ffffff", "bg.subtle": "#f3f4f6", "bg.inset": "#e5e7eb",
        "brand.500": "#3b82f6", "brand.600": "#2563eb", "brand.700": "#1d4ed8",
        "danger.500": "#ef4444", "danger.600": "#dc2626", "success.600": "#16a34a",
        "border.default": "#d1d5db",
    },
    "space": {"1": 4, "2": 8, "3": 12, "4": 16, "5": 20, "6": 24, "8": 32, "10": 40, "12": 48},
    "radius": {"sm": 4, "md": 8, "lg": 12, "full": 9999},
    "font": {"xs": 12, "sm": 14, "base": 16, "lg": 18, "xl": 20, "2xl": 24, "3xl": 30},
}
PROP_TYPE = {"color": "color", "background": "color", "borderColor": "color",
             "padding": "space", "gap": "space", "margin": "space",
             "borderRadius": "radius", "fontSize": "font"}

# Component roles: each element slot has a house style (prop -> token), the "texture" context draws on.
ROLES = {
    "Button": {"root": {"background": "brand.600", "color": "bg.surface", "padding": "3", "borderRadius": "md", "fontSize": "sm"},
               "icon": {"color": "bg.surface", "margin": "2"}},
    "DangerButton": {"root": {"background": "danger.600", "color": "bg.surface", "padding": "3", "borderRadius": "md", "fontSize": "sm"}},
    "Card": {"root": {"background": "bg.surface", "borderColor": "border.default", "padding": "6", "borderRadius": "lg", "gap": "4"},
             "title": {"color": "text.primary", "fontSize": "xl", "margin": "2"},
             "body": {"color": "text.secondary", "fontSize": "base"}},
    "Badge": {"root": {"background": "bg.subtle", "color": "text.secondary", "padding": "1", "borderRadius": "full", "fontSize": "xs"}},
    "Nav": {"root": {"background": "bg.surface", "padding": "4", "gap": "6", "borderColor": "border.default"},
            "link": {"color": "brand.700", "fontSize": "sm", "padding": "2"}},
    "Field": {"root": {"gap": "2", "margin": "4"},
              "label": {"color": "text.primary", "fontSize": "sm"},
              "input": {"background": "bg.surface", "borderColor": "border.default", "padding": "3", "borderRadius": "sm", "fontSize": "base"},
              "hint": {"color": "text.muted", "fontSize": "xs"}},
    "Alert": {"root": {"background": "bg.inset", "color": "danger.600", "padding": "4", "borderRadius": "md", "gap": "3"}},
    "Toast": {"root": {"background": "text.primary", "color": "bg.surface", "padding": "4", "borderRadius": "lg", "fontSize": "sm"}},
    "Modal": {"root": {"background": "bg.surface", "padding": "8", "borderRadius": "lg", "gap": "6"},
              "title": {"color": "text.primary", "fontSize": "2xl"},
              "footer": {"gap": "3", "padding": "6", "background": "bg.subtle"}},
    "Stat": {"root": {"padding": "5", "gap": "1", "background": "bg.subtle", "borderRadius": "md"},
             "value": {"color": "text.primary", "fontSize": "3xl"},
             "label": {"color": "text.muted", "fontSize": "xs"}},
}
VARIANTS = ["", "Compact", "Large", "Inline", "Primary", "Secondary", "Ghost", "Settings", "Profile", "Billing",
            "Search", "Header", "Footer", "Sidebar", "Empty", "Error", "Summary", "Detail"]


def tok_value(t, name):
    return TOKENS[t][name]


def neighbors(t, name):
    """Adjacent tokens in value order (for ambiguous drift)."""
    if t == "color":
        lab = hex_to_oklab(TOKENS[t][name])
        others = sorted((sum((a - b) ** 2 for a, b in zip(lab, hex_to_oklab(v))), k)
                        for k, v in TOKENS[t].items() if k != name)
        return [others[0][1]]
    items = sorted(TOKENS[t].items(), key=lambda kv: kv[1])
    i = [k for k, _ in items].index(name)
    return [items[j][0] for j in (i - 1, i + 1) if 0 <= j < len(items) and items[j][1] < 1000]


def near_miss(t, name, rng):
    v = tok_value(t, name)
    if t == "color":
        rgb = [int(v[i:i + 2], 16) for i in (1, 3, 5)]
        rgb = [min(255, max(0, c + rng.choice([-3, -2, -1, 1, 2, 3]))) for c in rgb]
        return "#%02x%02x%02x" % tuple(rgb)
    if v >= 1000:
        return 999
    return v + rng.choice([-1, 1]) if v <= 12 else v + rng.choice([-2, -1, 1, 2])


def ambiguous(t, name, rng):
    """A value between the intended token and an adjacent one, often nearer the wrong one."""
    nb = neighbors(t, name)
    if not nb:
        return None, None
    other = rng.choice(nb)
    w = rng.uniform(0.45, 0.7)  # weight toward the WRONG token
    a, b = tok_value(t, name), tok_value(t, other)
    if t == "color":
        la, lb = hex_to_oklab(a), hex_to_oklab(b)
        return oklab_to_hex([x + w * (y - x) for x, y in zip(la, lb)]), other
    val = round(a + w * (b - a))
    if val in TOKENS[t].values():
        val = a + (1 if b > a else -1) * max(1, abs(b - a) // 2 - 1)
    return val, other


def fmt(t, v):
    return f"'{v}'" if t == "color" else str(v)


def generate(seed, n_components=70, p_drift=0.35):
    rng = random.Random(seed)
    sites, files = [], {}
    # Coordinated off-spec clusters: a design decision made outside the spec.
    clusters = [
        {"id": "c_purple", "type": "color", "value": "#7c3aed", "props": ["background", "color"], "jitter": 1},
        {"id": "c_space18", "type": "space", "value": 18, "props": ["padding", "gap"], "jitter": 0},
        {"id": "c_radius6", "type": "radius", "value": 6, "props": ["borderRadius"], "jitter": 0},
    ]
    cluster_comps = {c["id"]: set(rng.sample(range(n_components), 9)) for c in clusters}
    names_used = set()
    for ci in range(n_components):
        role = rng.choice(list(ROLES))
        name = role
        while name in names_used:
            name = rng.choice(VARIANTS) + role + (str(rng.randint(2, 9)) if rng.random() < 0.3 else "")
        names_used.add(name)
        lines = ["import { tokens } from '../tokens';", "", f"export function {name}() {{", "  return ("]
        slots = ROLES[role]
        depth = 2
        open_tags = []
        for si, (slot, style) in enumerate(slots.items()):
            tag = "div" if slot == "root" else ("span" if slot in ("label", "hint", "icon") else "div")
            ind = "  " * depth
            lines.append(f"{ind}<{tag} data-slot=\"{slot}\" style={{{{")
            for prop, tname in style.items():
                t = PROP_TYPE[prop]
                cls, val, truth = "bound", None, "leave"
                r = rng.random()
                cl = next((c for c in clusters if ci in cluster_comps[c["id"]] and prop in c["props"]
                           and not c.get("_used", {}).get(ci)), None)
                if cl:
                    cl.setdefault("_used", {})[ci] = True
                    cls, truth = "cluster", f"new:{cl['id']}"
                    val = cl["value"]
                    if cl["jitter"] and rng.random() < 0.4:
                        val = near_miss_hex(val, rng)
                elif r < p_drift:
                    kind = rng.choices(["exact", "near", "ambiguous"], [0.35, 0.3, 0.35])[0]
                    if kind == "exact":
                        val = tok_value(t, tname)
                    elif kind == "near":
                        val = near_miss(t, tname, rng)
                    else:
                        val, _ = ambiguous(t, tname, rng)
                        if val is None:
                            kind, val = "exact", tok_value(t, tname)
                    cls, truth = kind, f"bind:{t}.{tname}"
                if cls == "bound":
                    expr = f"tokens.{t}['{tname}']"
                else:
                    expr = fmt(t, val)
                lineno = len(lines) + 1
                lines.append(f"{ind}  {prop}: {expr},")
                sites.append(dict(id=f"{name}.tsx:{lineno}", file=f"src/components/{name}.tsx", line=lineno,
                                  component=name, role=role, slot=slot, depth=si, prop=prop, type=t,
                                  literal=None if cls == "bound" else val, token=f"{t}.{tname}" if cls == "bound" else None,
                                  cls=cls, truth=truth))
            # intentional literals
            if rng.random() < 0.25:
                prop, v = rng.choice([("borderWidth", "1"), ("margin", "0"), ("width", "'100%'"), ("flex", "1"), ("padding", "0")])
                lineno = len(lines) + 1
                lines.append(f"{ind}  {prop}: {v},")
                sites.append(dict(id=f"{name}.tsx:{lineno}", file=f"src/components/{name}.tsx", line=lineno,
                                  component=name, role=role, slot=slot, depth=si, prop=prop,
                                  type=PROP_TYPE.get(prop, "other"), literal=v.strip("'"), token=None,
                                  cls="intentional", truth="leave"))
            lines.append(f"{ind}}}}}>")
            if slot == "root":
                open_tags.append(tag)
                depth += 1
            else:
                lines.append(f"{ind}  {slot}")
                lines.append(f"{ind}</{tag}>")
        for tag in reversed(open_tags):
            depth -= 1
            lines.append(f"{'  ' * depth}</{tag}>")
        lines += ["  );", "}", ""]
        files[f"src/components/{name}.tsx"] = "\n".join(lines)
    files["src/tokens.ts"] = "export const tokens = " + json.dumps(TOKENS, indent=2) + " as const;\n"
    return files, sites


def near_miss_hex(v, rng):
    rgb = [int(v[i:i + 2], 16) for i in (1, 3, 5)]
    rgb = [min(255, max(0, c + rng.choice([-2, -1, 1, 2]))) for c in rgb]
    return "#%02x%02x%02x" % tuple(rgb)


if __name__ == "__main__":
    seed, out = int(sys.argv[1]), Path(sys.argv[2])
    files, sites = generate(seed)
    for p, txt in files.items():
        (out / "repo" / p).parent.mkdir(parents=True, exist_ok=True)
        (out / "repo" / p).write_text(txt)
    (out / "truth.json").write_text(json.dumps(sites, indent=1))
    from collections import Counter
    print(seed, len(sites), dict(Counter(s["cls"] for s in sites)))
