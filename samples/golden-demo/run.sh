#!/bin/sh
# One command: two SITL flights (monitor, baseline), navdash/1 conversion, summary.
#   ./run.sh                          # v1: both runs, ~6 min, output in runs/ and runs/navdash/
#   ./run.sh monitor                  # one run (no conversion)
#   ./run.sh --v2                     # v2: injected coherent drag, replayed real visual geoloc, SS FDE + PL
#   ./run.sh --v2 --live              # v2 with live ALIKED+LightGlue matching in the loop (speedup 1)
#   ./run.sh [--v2] --update-reference   # also refresh the committed reference (data/ or data/v2/)
# Env: PYTHON (needs pymavlink), IMAGE, PORT (host port for SERIAL1, default 15766), NAME,
#      SPEEDUP, SEED; v2 knobs SPOOF (position|coherent|none), RATE (m/s), DETECTOR (chi2|ss|ss+vel).
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
PYTHON=${PYTHON:-python3}
IMAGE=${IMAGE:-nav-sitl-ardupilot:copter-4.6.3}
PORT=${PORT:-15766}
NAME=${NAME:-golden-sitl}
SEED=${SEED:-7}
V2=0; LIVE=0; UPDATE=0; MODES=""
for arg in "$@"; do
    case "$arg" in
        --v2) V2=1 ;;
        --live) V2=1; LIVE=1 ;;
        --update-reference) UPDATE=1 ;;
        monitor|baseline) MODES="$MODES $arg" ;;
        *) echo "unknown argument: $arg"; exit 2 ;;
    esac
done
MODES=${MODES:-monitor baseline}

if [ "$V2" = 1 ]; then
    VGEO=replay; [ "$LIVE" = 1 ] && VGEO=live
    SPEEDUP=${SPEEDUP:-1}
    PARMS="golden.parm inject.parm v2.parm"
    HOME_LOC="41.301800,-81.751397,290,0"          # vgeo_real.HOME, over the NAIP window
    ARGS="--gps inject --spoof ${SPOOF:-coherent} --rate ${RATE:-1} --vgeo $VGEO --detector ${DETECTOR:-ss+vel} --alt 150 --vio-to-ap --extnav reference"
    TAG=v2; [ "$LIVE" = 1 ] && TAG=v2-live
    REF="$HERE/data/$TAG"
else
    SPEEDUP=${SPEEDUP:-1}
    PARMS="golden.parm"
    HOME_LOC="-35.363261,149.165230,584,353"       # ArduPilot CMAC default
    ARGS=""
    TAG=v1; REF="$HERE/data"
fi

"$PYTHON" -c "import pymavlink" || { echo "need pymavlink: pip install pymavlink==2.4.50"; exit 1; }
docker image inspect "$IMAGE" >/dev/null 2>&1 || \
    docker build -f "$HERE/../sitl-docker/Dockerfile.ardupilot" -t "$IMAGE" "$HERE/../sitl-docker"

mkdir -p "$HERE/runs"
cleanup() { docker rm -f "$NAME" >/dev/null 2>&1 || true; }
trap cleanup EXIT INT TERM

DEFAULTS=/ardupilot/Tools/autotest/default_params/copter.parm
for p in $PARMS; do DEFAULTS="$DEFAULTS,/$p"; done

for mode in $MODES; do
    cleanup
    # docker cp, not a bind mount: macOS Docker Desktop does not share /tmp by default.
    docker create --name "$NAME" -p "127.0.0.1:$PORT:5762" -e "SITL_SPEEDUP=$SPEEDUP" -e "SITL_HOME=$HOME_LOC" \
        "$IMAGE" --defaults "$DEFAULTS" >/dev/null
    for p in $PARMS; do docker cp "$HERE/$p" "$NAME:/$p"; done
    docker start "$NAME" >/dev/null
    echo "== $TAG $mode: SITL $NAME on tcp:127.0.0.1:$PORT, speedup $SPEEDUP"
    # shellcheck disable=SC2086
    "$PYTHON" "$HERE/companion.py" --connect "tcp:127.0.0.1:$PORT" --mode "$mode" --seed "$SEED" $ARGS \
        --log "$HERE/runs/$TAG-$mode.raw.jsonl"
    docker logs "$NAME" > "$HERE/runs/$TAG-$mode.sitl.log" 2>&1 || true
done
cleanup

if [ -f "$HERE/runs/$TAG-monitor.raw.jsonl" ] && [ -f "$HERE/runs/$TAG-baseline.raw.jsonl" ]; then
    OUT="$HERE/runs/navdash-$TAG"
    [ "$UPDATE" = 1 ] && OUT="$REF"
    "$PYTHON" "$HERE/to_navdash.py" "$HERE/runs/$TAG-monitor.raw.jsonl" "$HERE/runs/$TAG-baseline.raw.jsonl" --out "$OUT"
    echo "dashboard input: $OUT"
fi
