#!/usr/bin/env bash
# Build several synthetic test pairs from the same OpenAerialMap ortho and geolocate each.
# Usage: ./run_cases.sh   (PYTHON defaults to python3; needs internet the first time)
set -euo pipefail
cd "$(dirname "$0")"
PY=${PYTHON:-python3}
run() {  # name, crop_px, make_test_pair args...
  local name=$1 crop=$2; shift 2
  local dir=data/$name
  [ -f "$dir/pair.json" ] || "$PY" make_test_pair.py --out "$dir" "$@" >/dev/null
  read -r tlat tlon plat plon < <("$PY" -c "import json;d=json.load(open('$dir/pair.json'));print(*d['truth_latlon'],*d['prior_latlon'])")
  echo "== $name (crop ${crop}px; $*)"
  "$PY" geolocalize.py --frame "$dir/drone_frame.jpg" --tile "$dir/map_tile.tif" \
    --prior "$plat" "$plon" --truth "$tlat" "$tlon" --crop-px "$crop" 2>/dev/null
}
run base       1536
run yaw60      1536 --yaw-deg 60
run yaw135     1536 --yaw-deg 135
run tilt20     1536 --tilt 0.20
run prior150   1536 --prior-offset-m 150
run crop2048   2048
run edge       1536 --center-frac 0.15 0.2 --prior-offset-m 250

# Negative control: a frame from a different survey (Batumi, OpenAerialMap, CC-BY 4.0)
# matched against the Tbilisi map. A correct gate prints "no reliable fix".
OTHER_URL=https://oin-hotosm-temp.s3.us-east-1.amazonaws.com/65056d734a35b70001c38d46/0/65056d734a35b70001c38d47.tif
[ -f data/other/pair.json ] || "$PY" make_test_pair.py --url "$OTHER_URL" --out data/other >/dev/null
read -r plat plon < <("$PY" -c "import json;d=json.load(open('data/base/pair.json'));print(*d['prior_latlon'])")
echo "== negative control: Batumi frame vs Tbilisi map"
"$PY" geolocalize.py --frame data/other/drone_frame.jpg --tile data/base/map_tile.tif \
  --prior "$plat" "$plon" --crop-px 1536 2>/dev/null
