#!/usr/bin/env bash
# FILE-BASED ONLY: generates, mixes and processes IQ files. Never connect this to an SDR TX.
# Builds the image, runs pipeline.sh in a container (large IQ files stay in a Docker volume),
# copies the small outputs to ./out and scores them with the gnss-interference-monitor scorer.
set -euo pipefail
cd "$(dirname "$0")"
IMAGE=gnss-signal-chain
VOL=${VOL:-gnss-signal-chain-work}
docker image inspect "$IMAGE" >/dev/null 2>&1 || docker build -t "$IMAGE" docker/
docker volume create "$VOL" >/dev/null
ENV_ARGS=()
for v in DUR FS LAT LON H CN0_REF ATTACK_T JAM_S JAM_JN_DB SPOOF_GAIN_DB SPOOF_DELAY DRAG_ON DRAG_RAMP DRAG_HOLD SCENARIOS KEEP_IQ; do
  [ -n "${!v:-}" ] && ENV_ARGS+=(-e "$v=${!v}")
done
CID=$(docker create "${ENV_ARGS[@]+"${ENV_ARGS[@]}"}" -v "$VOL":/work/work "$IMAGE" /work/pipeline.sh)
trap 'docker rm -f "$CID" >/dev/null' EXIT
for f in pipeline.sh mix_iq.py spoof_trajectory.py extract_epochs.py gnss-sdr.conf.in; do
  docker cp "$f" "$CID":/work/
done
docker start -a "$CID"
rm -rf out && mkdir -p out
docker cp "$CID":/work/out/. out/
for s in ${SCENARIOS:-clean overpower jamspoof dragoff}; do
  echo "== $s"
  python3 score_scenario.py "out/$s.epochs.jsonl" --power-proxy "out/$s.power.csv" \
    --rtklib-pos "out/$s.rtklib.pos" --json-out "out/$s.score.json" | tee "out/$s.score.txt"
done
