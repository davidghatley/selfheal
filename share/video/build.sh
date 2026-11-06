#!/bin/sh
# SelfHeal vertical end to end. Run from share/video/. Needs kit -> tasty_tunez/promo and node_modules -> kit/node_modules.
#   (cd ../../src && ../.venv/bin/python ../share/recompute.py)   # numbers -> share/claims.json (3-4 min)
set -e
python3 prep.py
PYTHONPATH=kit python3 -m sfx cue.py --timeline src/timeline.json --out out/sfx.wav
R="--public-dir=kit/public --browser-executable=/usr/bin/chromium --log=error"
npx remotion render src/index.ts SelfHealV out/selfheal-silent.mp4 $R --codec=h264 --x264-preset=veryfast --crf=18 --concurrency=8
ffmpeg -v error -y -i out/selfheal-silent.mp4 -i out/sfx.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -movflags +faststart -shortest ../selfheal-vertical.mp4
npx remotion still src/index.ts SelfHealSquare ../selfheal-square.png $R
npx remotion still src/index.ts SelfHealV ../selfheal-poster.png --frame=1230 $R
echo done
