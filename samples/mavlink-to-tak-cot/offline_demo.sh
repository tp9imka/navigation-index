#!/usr/bin/env bash
# Offline end-to-end run: fake autopilot (UDP MAVLink) => bridge.py (pymavlink + PyTAK) => local CoT sink.
# Usage: ./offline_demo.sh [tcp|udp]   (PYTHON defaults to python3)
set -euo pipefail
cd "$(dirname "$0")"
PY=${PYTHON:-python3}
MODE=${1:-tcp}
EVENTS=5
if [ "$MODE" = udp ]; then
  SINK_ARGS=(--udp --port 16969); COT_URL=udp+wo://127.0.0.1:16969
else
  SINK_ARGS=(--port 18087); COT_URL=tcp://127.0.0.1:18087
fi
"$PY" cot_sink.py "${SINK_ARGS[@]}" --count "$EVENTS" &
SINK=$!
sleep 1
"$PY" fake_autopilot.py --out udpout:127.0.0.1:14550 --seconds 15 &
AP=$!
"$PY" bridge.py --mavlink udpin:127.0.0.1:14550 --cot-url "$COT_URL" --callsign UAV-1 2>/dev/null &
BR=$!
wait "$SINK"
kill "$BR" "$AP" 2>/dev/null || true
wait 2>/dev/null || true
