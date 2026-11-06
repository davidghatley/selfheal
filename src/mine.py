"""Mine drift labels from a design-system repo's git history.

Rule D (drift): in one non-merge commit, within one hunk of a style file, a removed line `prop: <literal>`
is paired with an added line for the SAME prop whose value is a token reference and contains no literal.
Literal = a px/rem/em length, a hex colour, or rgb()/rgba(). Token reference = repo-specific pattern (TOKEN_RX).
Each pair is one label: (commit, date, author, file, prop, literal, token).

Usage: mine.py <repo> <name> <out.jsonl>
"""
import json, re, subprocess, sys

STYLE = re.compile(r"\.(s?css|less)$")
TOKEN_RX = {
    # Carbon: $spacing-05, $text-primary, theme.$layer-01, spacing.$spacing-05, $carbon--spacing-05, var(--cds-…)
    "carbon": re.compile(r"(\$[\w-]+(?<!\$prefix)|\b\w+\.\$[\w-]+|var\(--(?:#\{\$prefix\}|cds)-[\w-]+\))"),
    # Polaris: var(--p-space-400), spacing(tight), color(ink, lighter), font-size(body)
    "polaris": re.compile(r"(var\(--p-[\w-]+\)|\b(?:spacing|color|font-size|border-radius|border-width)\([^)]*\))"),
    # Primer: var(--base-size-16), var(--fgColor-default), var(--space-small)
    "primer": re.compile(r"var\(--[\w-]+(?:,[^)]*)?\)"),
}
LIT = re.compile(r"(?<![\w$-])(-?\d*\.?\d+(?:px|rem|em)\b|#[0-9a-fA-F]{3,8}\b|rgba?\([^)]*\))")
DECL = re.compile(r"^\s*([a-z-]+)\s*:\s*(.+?)\s*;?\s*(?://.*)?$")
GOVERNED = re.compile(r"^(margin|padding|gap|row-gap|column-gap|top|right|bottom|left|inset|width|height|min-|max-|"
                      r"border-radius|border(-\w+)?-radius|font-size|line-height|color|background(-color)?|"
                      r"border(-\w+)?(-color)?|outline(-color)?|fill|stroke|box-shadow|letter-spacing)")


def commits(repo):
    p = subprocess.Popen(["git", "-C", repo, "log", "--no-merges", "-p", "-U0", "--no-color", "--no-renames",
                          "--format=@@@%H\t%as\t%ae", "--", "*.scss", "*.css", "*.less"],
                         stdout=subprocess.PIPE, text=True, errors="replace")
    cur, f, hunk = None, None, None
    for line in p.stdout:
        line = line.rstrip("\n")
        if line.startswith("@@@"):
            if hunk:
                yield cur, f, hunk
            h, d, a = line[3:].split("\t")
            cur, f, hunk = dict(commit=h, date=d, author=a), None, None
        elif line.startswith("+++ "):
            if hunk:
                yield cur, f, hunk
            f, hunk = line[6:], None
        elif line.startswith("@@"):
            if hunk:
                yield cur, f, hunk
            hunk = {"-": [], "+": []}
        elif hunk is not None and line[:1] in "+-" and not line.startswith(("+++", "---")):
            hunk[line[0]].append(line[1:])
    if hunk:
        yield cur, f, hunk


MAX_FILE_REMOVED = 200  # R1: a commit removing more lines than this from one file is a rewrite; pairing is unreliable


def pairs(hunk, tok):
    rem = [(m.group(1), m.group(2)) for l in hunk["-"] if (m := DECL.match(l))]
    add = [(m.group(1), m.group(2)) for l in hunk["+"] if (m := DECL.match(l))]
    used = set()
    for prop, old in rem:
        if not GOVERNED.match(prop) or not LIT.search(old) or tok.search(old):
            continue
        for j, (p2, new) in enumerate(add):
            if j in used or p2 != prop:
                continue
            if tok.search(new) and not LIT.search(tok.sub("", new)):
                used.add(j)
                yield prop, old, new
                break


if __name__ == "__main__":
    repo, name, out = sys.argv[1:4]
    tok = TOKEN_RX[name]
    from collections import defaultdict
    byfile, removed = defaultdict(list), defaultdict(int)
    for c, f, h in commits(repo):
        if not f or not STYLE.search(f) or "node_modules" in f:
            continue
        removed[(c["commit"], f)] += len(h["-"])
        for prop, old, new in pairs(h, tok):
            byfile[(c["commit"], f)].append(dict(c, file=f, prop=prop, literal=old, token=new))
    n = skipped = 0
    with open(out, "w") as fo:
        for key, labels in byfile.items():
            if removed[key] > MAX_FILE_REMOVED:
                skipped += len(labels); continue
            for l in labels:
                fo.write(json.dumps(l) + "\n"); n += 1
    print(name, n, "labels;", skipped, "skipped by R1")
