#!/bin/sh
# Headless capture of the dashboard replaying data/ at time T (default 900 s). Needs Chrome +
# Node 22+. screenshot.mjs is samples/golden-demo/screenshot.mjs with its own debug port.
#   ./screenshot.sh [T] [out.jpg]          DATA=runs/navdash-ref ./screenshot.sh 400
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../.." && pwd)
T=${1:-900}
DATA=${DATA:-data}
OUT=${2:-$HERE/screenshots/fw-t$T.jpg}
PORT=${HTTP_PORT:-15849}
mkdir -p "$(dirname "$OUT")"
python3 -m http.server "$PORT" --bind 127.0.0.1 --directory "$ROOT" >/dev/null 2>&1 &
SRV=$!
trap 'kill $SRV 2>/dev/null || true' EXIT
sleep 1
node "$HERE/screenshot.mjs" \
    "http://127.0.0.1:$PORT/templates/demo-dashboard/index.html?manifest=../../samples/golden-demo-fixedwing/$DATA/manifest.json&t=$T&follow=0" \
    "$OUT" ${CHROME:+"$CHROME"}
