#!/bin/sh
# One command: two SITL flights (monitor, baseline), navdash/1 conversion, summary.
#   ./run.sh                 # both runs, ~8 min
#   ./run.sh monitor         # one run
# Env: PYTHON (needs pymavlink), IMAGE, PORT (host port for SERIAL1, default 15766).
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
PYTHON=${PYTHON:-python3}
IMAGE=${IMAGE:-nav-sitl-ardupilot:copter-4.6.3}
PORT=${PORT:-15766}
NAME=${NAME:-golden-sitl}
MODES=${*:-monitor baseline}

"$PYTHON" -c "import pymavlink" || { echo "need pymavlink: pip install pymavlink==2.4.50"; exit 1; }
docker image inspect "$IMAGE" >/dev/null 2>&1 || \
    docker build -f "$HERE/../sitl-docker/Dockerfile.ardupilot" -t "$IMAGE" "$HERE/../sitl-docker"

mkdir -p "$HERE/runs"
cleanup() { docker rm -f "$NAME" >/dev/null 2>&1 || true; }
trap cleanup EXIT INT TERM

for mode in $MODES; do
    cleanup
    # docker cp, not a bind mount: macOS Docker Desktop does not share /tmp by default.
    docker create --name "$NAME" -p "127.0.0.1:$PORT:5762" "$IMAGE" \
        --defaults /ardupilot/Tools/autotest/default_params/copter.parm,/golden.parm >/dev/null
    docker cp "$HERE/golden.parm" "$NAME:/golden.parm"
    docker start "$NAME" >/dev/null
    echo "== $mode: SITL $NAME on tcp:127.0.0.1:$PORT"
    "$PYTHON" "$HERE/companion.py" --connect "tcp:127.0.0.1:$PORT" --mode "$mode" \
        --log "$HERE/runs/$mode.raw.jsonl"
    docker logs "$NAME" > "$HERE/runs/$mode.sitl.log" 2>&1 || true
done
cleanup

if [ -f "$HERE/runs/monitor.raw.jsonl" ] && [ -f "$HERE/runs/baseline.raw.jsonl" ]; then
    "$PYTHON" "$HERE/to_navdash.py" "$HERE/runs/monitor.raw.jsonl" "$HERE/runs/baseline.raw.jsonl" \
        --out "$HERE/data"
fi
