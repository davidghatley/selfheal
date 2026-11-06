"""Sound for the SelfHeal vertical: a quiet D minor pad and accents, every time from src/timeline.json.
Run from share/video:  PYTHONPATH=kit python3 -m sfx cue.py --timeline src/timeline.json --out out/sfx.wav
Nothing here carries meaning the picture doesn't; the video works muted.
"""
from sfx.synth import blip, chime, click, pad, pop, whoosh

TARGET_LUFS = -14.0
D = [146.83, 174.61, 220.0]; BB = [116.54, 146.83, 174.61]; F = [174.61, 220.0, 261.63]; C = [130.81, 164.81, 196.0]
DMIN = [293.66, 329.63, 349.23, 392.0, 440.0, 466.16, 523.25, 587.33]


def score(mix, tl):
    put = mix.put
    total = tl["total"]
    # pad: chord every 4 s, cycling i - VI - III - VII, out before the end card settles
    chords = [(k * 4.0, [D, BB, F, C][k % 4]) for k in range(int(total // 4) + 1)]
    l, r = pad(total, chords)
    mix.put_stereo(0, l, r, gain=0.22)
    m, q, s, p, ts, c = (tl[k] for k in ("moment", "question", "solved", "problem", "tests", "close"))
    # 01: a keystroke burst per typed line, a pop per tally number
    for i in range(14):
        mix.typing(m["lines"] + i * m["step"], m["lines"] + i * m["step"] + 0.22, 6, gain=(0.08, 0.14))
    for i in range(3):
        put(m["tally"] + i * 0.12, pop(700 + i * 120, 1100 + i * 150), 0.14)
    # 02: footsteps wearing the path, a chime when it's paved
    for k in range(0, 34, 2):
        put(q["path"] + k * 0.05, click(1500 + k * 20, 0.03), 0.06, -0.3 + k * 0.02)
    put(q["paved"], chime([DMIN[0], DMIN[2], DMIN[4]], dur=1.8, tau=0.7), 0.12)
    # 03: the grid fills, the number lands
    for k in range(0, 157, 8):
        put(s["grid"] + k * s["step"], click(1800 + k * 4, 0.025), 0.05, 0.2)
    put(s["num"], pop(500, 900), 0.18)
    # 04: dots, the seven light, the reveal
    put(p["dots"], whoosh(1.6, 600, 2600, peak=0.5), 0.08)
    for i in range(7):
        put(p["light"] + i * 0.07, blip(DMIN[i], dur=0.3, tau=0.1), 0.1, -0.4 + i * 0.13)
    put(p["cards"], whoosh(0.5, 2400, 600, peak=0.4), 0.1)
    put(p["reveal"], pop(400, 800), 0.18)
    # 05: one pop per test, a note when its verdict lands
    for i, t in enumerate(ts["rows"]):
        put(t, pop(700 + i * 80, 1100 + i * 90), 0.14, -0.4 if i % 2 else 0.4)
        put(t + 1.6, blip(DMIN[i * 2], dur=0.35, tau=0.12), 0.12)
    # 06: the question, then the mark builds
    put(c["q"], chime([DMIN[0] / 2, DMIN[2] / 2, DMIN[4] / 2], dur=2.4, tau=0.9), 0.14)
    for k in range(21):
        put(c["dh"] + k * 0.05, click(1700 + k * 50, 0.03), 0.06, 0.2)
