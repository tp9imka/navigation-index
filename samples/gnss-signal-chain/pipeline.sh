#!/usr/bin/env bash
# Runs inside the gnss-signal-chain container. Generates IQ FILES ONLY - nothing is transmitted.
# gps-sdr-sim streams 16-bit IQ through FIFOs into mix_iq.py; only the mixed 8-bit file is
# written (DUR*FS*2 bytes), processed by GNSS-SDR, then deleted unless KEEP_IQ=1.
set -euo pipefail
W=${W:-/work/work}; OUT=${OUT:-/work/out}
DUR=${DUR:-150}; FS=${FS:-2000000}
LAT=${LAT:-30.286502}; LON=${LON:-120.032669}; H=${H:-100}
NAV=/opt/gps-sdr-sim/brdc0010.22n
CN0_REF=${CN0_REF:-47}
ATTACK_T=${ATTACK_T:-75}; JAM_S=${JAM_S:-5}; JAM_JN_DB=${JAM_JN_DB:-25}
SPOOF_GAIN_DB=${SPOOF_GAIN_DB:-8}; SPOOF_DELAY=${SPOOF_DELAY:-10}
DRAG_ON=${DRAG_ON:-60}; DRAG_RAMP=${DRAG_RAMP:-10}; DRAG_HOLD=${DRAG_HOLD:-80}
SCENARIOS=${SCENARIOS:-clean overpower jamspoof dragoff}
KEEP_IQ=${KEEP_IQ:-0}
mkdir -p "$W" "$OUT"
: > "$OUT/timings.txt"; : > "$OUT/file_sizes.txt"

python3 /work/spoof_trajectory.py --lat "$LAT" --lon "$LON" --h "$H" --duration "$DUR" \
  --north-m 2000 --east-m 2000 --ve 20 -o "$OUT/spoof_offset_llh.csv"
python3 /work/spoof_trajectory.py --lat "$LAT" --lon "$LON" --h "$H" --duration "$DUR" \
  --north-m 0 --east-m 0 --hold-s "$DRAG_HOLD" --accel 0.5 --ve 20 -o "$OUT/spoof_drag_llh.csv"

sim_fifo() {  # $1 fifo, rest = gps-sdr-sim motion args
  local fifo=$1; shift
  rm -f "$fifo"; mkfifo "$fifo"
  gps-sdr-sim -e "$NAV" "$@" -d "$DUR" -s "$FS" -b 16 -o - > "$fifo" \
    2> >(tr '\r' '\n' | grep -v '^Time into run' >> "$OUT/gps-sdr-sim.log") &
}

for name in $SCENARIOS; do
  s=$SECONDS
  sim_fifo "$W/auth.fifo" -l "$LAT,$LON,$H"
  case $name in
    clean) extra=() ;;
    overpower)
      sim_fifo "$W/spoof.fifo" -x "$OUT/spoof_offset_llh.csv" -p 128
      extra=(--spoofer "$W/spoof.fifo" --spoof-on "$ATTACK_T" --spoof-gain-db "$SPOOF_GAIN_DB" --spoof-delay-samples "$SPOOF_DELAY") ;;
    jamspoof)
      sim_fifo "$W/spoof.fifo" -x "$OUT/spoof_offset_llh.csv" -p 128
      extra=(--spoofer "$W/spoof.fifo" --spoof-on "$ATTACK_T" --spoof-gain-db "$SPOOF_GAIN_DB" --spoof-delay-samples "$SPOOF_DELAY"
             --jam-on "$ATTACK_T" --jam-off "$((ATTACK_T + JAM_S))" --jam-jn-db "$JAM_JN_DB") ;;
    dragoff)
      sim_fifo "$W/spoof.fifo" -x "$OUT/spoof_drag_llh.csv" -p 128
      extra=(--spoofer "$W/spoof.fifo" --spoof-on "$DRAG_ON" --spoof-ramp-s "$DRAG_RAMP" --spoof-gain-db "$SPOOF_GAIN_DB") ;;
  esac
  python3 /work/mix_iq.py --authentic "$W/auth.fifo" --fs "$FS" --duration "$DUR" --cn0-ref "$CN0_REF" \
    -o "$W/$name.bin" --power-log "$OUT/$name.power.csv" "${extra[@]+"${extra[@]}"}" 2> "$OUT/$name.mix.log"
  wait
  echo "TIMING $name generate+mix $((SECONDS - s)) s" >> "$OUT/timings.txt"
  ls -l "$W/$name.bin" | awk '{print $5, $NF}' >> "$OUT/file_sizes.txt"

  rx="$W/rx_$name"; rm -rf "$rx"; mkdir -p "$rx"
  sed -e "s#@FS@#$FS#g" -e "s#@FILE@#$W/$name.bin#" -e "s#@OUT@#$rx#g" /work/gnss-sdr.conf.in > "$rx/gnss-sdr.conf"
  s=$SECONDS
  (cd "$rx" && gnss-sdr --config_file="$rx/gnss-sdr.conf" --log_dir="$rx" 2>&1 | sed 's/\x1b\[[0-9;]*m//g' > "$OUT/$name.gnss-sdr.log") || true
  echo "TIMING $name gnss-sdr $((SECONDS - s)) s" >> "$OUT/timings.txt"
  grep -ho "Sent reset to observables\|Sent clock offset correction to observables: [-0-9.e]*" "$rx/gnss-sdr.INFO" \
    | sed 's/\(: -*[0-9]*\.[0-9]\{3\}\)[0-9]*/\1/' | sort | uniq -c > "$OUT/$name.gnss-sdr.events.txt" || true
  python3 /work/extract_epochs.py "$rx" -o "$OUT/$name.epochs.jsonl"
  obs=$(ls "$rx"/*.[0-9][0-9]O 2>/dev/null | head -1); nav=$(ls "$rx"/*.[0-9][0-9]N 2>/dev/null | head -1)
  if [ -n "$obs" ] && [ -n "$nav" ]; then  # independent SPP of GNSS-SDR's RINEX with RTKLIB demo5
    rnx2rtkp -p 0 -sys G -m 10 -t -o "$OUT/$name.rtklib.pos" "$obs" "$nav" 2>/dev/null || echo "rnx2rtkp $name failed"
  fi
  [ "$KEEP_IQ" = 1 ] || rm -f "$W/$name.bin"
done
rm -f "$W"/*.fifo
