#!/bin/sh
# One command: ArduPlane SITL flights per scenario (in parallel, one container each), then the
# navdash/1 conversion and summary.
#   ./run.sh                              # baseline day night dr, ~5 min wall at speedup 5
#   ./run.sh day dr                       # a subset
#   ./run.sh --update-reference           # also refresh the committed data/
# Env: PYTHON (needs pymavlink), IMAGE, PORT0 (first host port, default 15841), SPEEDUP (5),
#      SEED (7), SPOOF (coherent|position|none), RATE (m/s, 1), TAG (run name prefix, "ref"),
#      EXTRA (more companion_fw.py arguments, e.g. "--ref vo").
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
PYTHON=${PYTHON:-python3}
IMAGE=${IMAGE:-plane-sitl-ardupilot:4.6.3}
BASE_IMAGE=${BASE_IMAGE:-nav-sitl-ardupilot:copter-4.6.3}
PORT0=${PORT0:-15841}
SPEEDUP=${SPEEDUP:-5}
SEED=${SEED:-7}
SPOOF=${SPOOF:-coherent}
RATE=${RATE:-1}
TAG=${TAG:-ref}
UPDATE=0; SCENARIOS=""
for arg in "$@"; do
    case "$arg" in
        --update-reference) UPDATE=1 ;;
        baseline|day|night|dr) SCENARIOS="$SCENARIOS $arg" ;;
        *) echo "unknown argument: $arg"; exit 2 ;;
    esac
done
SCENARIOS=${SCENARIOS:-baseline day night dr}

"$PYTHON" -c "import pymavlink" || { echo "need pymavlink: pip install pymavlink==2.4.50"; exit 1; }
if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
    docker image inspect "$BASE_IMAGE" >/dev/null 2>&1 || \
        docker build -f "$HERE/../sitl-docker/Dockerfile.ardupilot" -t "$BASE_IMAGE" "$HERE/../sitl-docker"
    docker build -f "$HERE/Dockerfile.plane" --build-arg "BASE=$BASE_IMAGE" -t "$IMAGE" "$HERE"
fi
mkdir -p "$HERE/runs"
NAMES=""
cleanup() { for n in $NAMES; do docker rm -f "$n" >/dev/null 2>&1 || true; done; }
trap cleanup EXIT INT TERM

i=0; PIDS=""
for s in $SCENARIOS; do
    name="plane-sitl-$TAG-$s"; port=$((PORT0 + i)); i=$((i + 1))
    NAMES="$NAMES $name"
    docker rm -f "$name" >/dev/null 2>&1 || true
    # docker cp, not a bind mount: macOS Docker Desktop does not share /tmp by default.
    PARMS="fw.parm"; [ "$s" = dr ] && PARMS="fw.parm dr.parm"
    DEFAULTS=/ardupilot/Tools/autotest/models/plane.parm
    for p in $PARMS; do DEFAULTS="$DEFAULTS,/$p"; done
    docker create --name "$name" -p "127.0.0.1:$port:5762" -e "SITL_SPEEDUP=$SPEEDUP" "$IMAGE" \
        --defaults "$DEFAULTS" >/dev/null
    for p in $PARMS; do docker cp "$HERE/$p" "$name:/$p"; done
    docker start "$name" >/dev/null
    echo "== $s: SITL $name on tcp:127.0.0.1:$port, speedup $SPEEDUP"
    "$PYTHON" "$HERE/companion_fw.py" --connect "tcp:127.0.0.1:$port" --scenario "$s" --seed "$SEED" \
        --spoof "$SPOOF" --rate "$RATE" ${EXTRA:-} --quiet --log "$HERE/runs/$TAG-$s.raw.jsonl" > "$HERE/runs/$TAG-$s.out" 2>&1 &
    PIDS="$PIDS $!"
done
FAIL=0
for p in $PIDS; do wait "$p" || FAIL=1; done
for s in $SCENARIOS; do
    docker logs "plane-sitl-$TAG-$s" > "$HERE/runs/$TAG-$s.sitl.log" 2>&1 || true
    echo "-- $s"; tail -3 "$HERE/runs/$TAG-$s.out"
done
cleanup
[ "$FAIL" = 0 ] || { echo "a flight failed, see runs/$TAG-*.out"; exit 1; }

OUT="$HERE/runs/navdash-$TAG"
[ "$UPDATE" = 1 ] && OUT="$HERE/data"
"$PYTHON" "$HERE/to_navdash_fw.py" --runs "$HERE/runs" --tag "$TAG" --out "$OUT"
echo "dashboard input: $OUT"
