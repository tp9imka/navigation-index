#!/bin/sh
# Headless capture of templates/demo-dashboard replaying results/navdash at frame T (default 198 = last).
# Reuses ../golden-demo/screenshot.mjs (Chrome + Node 22+).   ./screenshot.sh [T] [out.jpg]
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../.." && pwd)
T=${1:-198}
OUT=${2:-$HERE/results/screenshots/two-source-t$T.jpg}
PORT=${HTTP_PORT:-15781}
mkdir -p "$(dirname "$OUT")"
python3 -m http.server "$PORT" --bind 127.0.0.1 --directory "$ROOT" >/dev/null 2>&1 &
SRV=$!
trap 'kill $SRV 2>/dev/null || true' EXIT
sleep 1
node "$ROOT/samples/golden-demo/screenshot.mjs" \
    "http://127.0.0.1:$PORT/templates/demo-dashboard/index.html?manifest=../../samples/two-source-integrity-vpair/results/navdash/manifest.json&t=$T&follow=0" \
    "$OUT" ${CHROME:+"$CHROME"}
