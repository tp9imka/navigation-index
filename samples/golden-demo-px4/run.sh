#!/bin/sh
# Golden demo on PX4 v1.17 SIH: two flights (monitor, baseline), navdash/1 conversion, summary,
# comparison with the ArduPilot golden-demo v2 reference.
#   ./run.sh                          # coherent 1 m/s drag, replayed real visual geoloc, ss+vel, ~7 min
#   ./run.sh monitor                  # one flight only (no conversion)
#   SPOOF=position RATE=3 ./run.sh    # other attacks (SPOOF=position|coherent|none)
#   ./run.sh --update-reference       # also refresh the committed data/
# Env: IMAGE, CLIENT_IMAGE, NAME (container prefix), SEED, SPOOF, RATE, DETECTOR, TAG, PYTHON
#      (host python for the conversion; stdlib is enough).
# PX4 SITL only talks MAVLink to localhost, so the companion runs in a client container that
# shares the PX4 container's network namespace (same pattern as samples/sitl-docker).
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../.." && pwd)
PYTHON=${PYTHON:-python3}
IMAGE=${IMAGE:-nav-sitl-px4:v1.17.0}
CLIENT_IMAGE=${CLIENT_IMAGE:-nav-sitl-client:latest}
NAME=${NAME:-px4golden}
SEED=${SEED:-7}
UPDATE=0; MODES=""
for arg in "$@"; do
    case "$arg" in
        --update-reference) UPDATE=1 ;;
        monitor|baseline) MODES="$MODES $arg" ;;
        *) echo "unknown argument: $arg"; exit 2 ;;
    esac
done
MODES=${MODES:-monitor baseline}
SPOOF=${SPOOF:-coherent}; RATE=${RATE:-1}
TAG=${TAG:-px4}
HOME_LAT=41.301800; HOME_LON=-81.751397; HOME_ALT=290   # golden-demo vgeo table home (NAIP window)

build() { docker image inspect "$1" >/dev/null 2>&1 || docker build -f "$ROOT/samples/sitl-docker/$2" -t "$1" "$ROOT/samples/sitl-docker"; }
build "$IMAGE" Dockerfile.px4          # ~26 min on first build
build "$CLIENT_IMAGE" Dockerfile.client

mkdir -p "$HERE/runs"
SITL="$NAME-sitl"; CLIENT="$NAME-client"
cleanup() { docker rm -f "$CLIENT" "$SITL" >/dev/null 2>&1 || true; }
trap cleanup EXIT INT TERM

for mode in $MODES; do
    cleanup
    docker run -d --name "$SITL" -e PX4_HOME_LAT=$HOME_LAT -e PX4_HOME_LON=$HOME_LON -e PX4_HOME_ALT=$HOME_ALT \
        "$IMAGE" >/dev/null
    # SIH's simulated GPS off, MAVLink HIL_GPS accepted. SENS_EN_GPSSIM is read at boot only and
    # its compiled default (0) equals the value we want, so PX4_PARAM_ cannot set it: save + restart.
    sleep 8
    docker exec "$SITL" sh -c 'cd /px4/rootfs && /px4/bin/px4-param set SENS_EN_GPSSIM 0 >/dev/null &&
        /px4/bin/px4-param set MAV_USEHILGPS 1 >/dev/null && /px4/bin/px4-param save'
    docker restart "$SITL" >/dev/null
    docker run -d --name "$CLIENT" --network "container:$SITL" --entrypoint sh "$CLIENT_IMAGE" -c "mkdir -p /nav && exec sleep infinity" >/dev/null
    # docker cp, not a bind mount: macOS Docker Desktop does not share /tmp by default.
    sleep 8
    COPYFILE_DISABLE=1 tar --no-xattrs --no-mac-metadata -C "$ROOT" --exclude runs --exclude screenshots --exclude __pycache__ --exclude 'data/v2*' \
        -cf - samples/golden-demo samples/golden-demo-px4 samples/altpnt-integrity templates/project-repo/src \
        | docker cp - "$CLIENT:/nav"
    echo "== $TAG $mode: PX4 SIH $SITL, companion in $CLIENT"
    docker exec "$CLIENT" python -u /nav/samples/golden-demo-px4/companion_px4.py --mode "$mode" --seed "$SEED" \
        --spoof "$SPOOF" --rate "$RATE" --detector "${DETECTOR:-ss+vel}" --log "/nav/$TAG-$mode.raw.jsonl"
    docker cp "$CLIENT:/nav/$TAG-$mode.raw.jsonl" "$HERE/runs/$TAG-$mode.raw.jsonl"
    docker logs "$SITL" > "$HERE/runs/$TAG-$mode.px4.log" 2>&1 || true
done
cleanup

if [ -f "$HERE/runs/$TAG-monitor.raw.jsonl" ] && [ -f "$HERE/runs/$TAG-baseline.raw.jsonl" ]; then
    OUT="$HERE/runs/navdash-$TAG"
    [ "$UPDATE" = 1 ] && OUT="$HERE/data"
    "$PYTHON" "$HERE/to_navdash_px4.py" "$HERE/runs/$TAG-monitor.raw.jsonl" "$HERE/runs/$TAG-baseline.raw.jsonl" --out "$OUT"
    echo "dashboard input: $OUT"
fi
