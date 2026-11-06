"""Parse the generated TSX repo into usage sites. Detectors see only this, never truth.json."""
import json, re, sys
from pathlib import Path

PROP_TYPE = {"color": "color", "background": "color", "borderColor": "color",
             "padding": "space", "gap": "space", "margin": "space",
             "borderRadius": "radius", "fontSize": "font"}
RX_COMP = re.compile(r"export function (\w+)\(")
RX_SLOT = re.compile(r'data-slot="(\w+)"')
RX_PROP = re.compile(r"^\s*(\w+): (.+),$")
RX_TOK = re.compile(r"tokens\.(\w+)\['([^']+)'\]")


def extract(repo):
    repo = Path(repo)
    tokens = json.loads((repo / "src/tokens.ts").read_text().split("=", 1)[1].rsplit(" as const", 1)[0])
    sites, elem = [], 0
    for f in sorted((repo / "src/components").glob("*.tsx")):
        comp, slot = None, None
        for i, line in enumerate(f.read_text().splitlines(), 1):
            if m := RX_COMP.search(line):
                comp = m.group(1)
            if m := RX_SLOT.search(line):
                slot, elem = m.group(1), elem + 1
            if (m := RX_PROP.match(line)) and slot:
                prop, expr = m.groups()
                t = RX_TOK.match(expr)
                lit = None if t else expr.strip("'")
                if lit is not None and PROP_TYPE.get(prop) in ("space", "radius", "font"):
                    lit = int(lit) if lit.lstrip("-").isdigit() else lit
                sites.append(dict(id=f"{f.name}:{i}", file=str(f.relative_to(repo)), line=i, component=comp,
                                  slot=slot, elem=elem, prop=prop, type=PROP_TYPE.get(prop, "other"),
                                  token=f"{t.group(1)}.{t.group(2)}" if t else None, literal=lit))
    return tokens, sites


if __name__ == "__main__":
    tokens, sites = extract(sys.argv[1])
    lits = [{k: s[k] for k in ("id", "file", "line", "prop", "literal")} for s in sites if s["token"] is None]
    print(json.dumps(lits, indent=1))
