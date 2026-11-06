#!/bin/sh
# Headless capture of the dashboard replaying data/ at time T (default 100 s). Needs Chrome + Node 22+.
#   ./screenshot.sh [T] [out.jpg]          DATA=data/v2 ./screenshot.sh 60 screenshots/v2-t60.jpg
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../.." && pwd)
T=${1:-100}
DATA=${DATA:-data}
OUT=${2:-$HERE/screenshots/golden-t$T.jpg}
PORT=${HTTP_PORT:-15768}
mkdir -p "$(dirname "$OUT")"
python3 -m http.server "$PORT" --bind 127.0.0.1 --directory "$ROOT" >/dev/null 2>&1 &
SRV=$!
trap 'kill $SRV 2>/dev/null || true' EXIT
sleep 1
node "$HERE/screenshot.mjs" \
    "http://127.0.0.1:$PORT/templates/demo-dashboard/index.html?manifest=../../samples/golden-demo/$DATA/manifest.json&t=$T&follow=0" \
    "$OUT" ${CHROME:+"$CHROME"}
