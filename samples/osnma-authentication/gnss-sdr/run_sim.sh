#!/usr/bin/env bash
# Inside the osnma-gnss-sdr image: simulate a Galileo E1 IQ FILE with OSNMA (no RF, usrp=1),
# then decode it with GNSS-SDR 0.0.20 in non-strict and strict OSNMA mode.
# Usage: run_sim.sh <duration_s> <out_dir> <merkle_tree_xml> [public_key_pem]
# GNSS-SDR 0.0.20 segfaults on the simulator's short-form public key XML, so the key is given as PEM.
set -euo pipefail
DUR=${1:-150}
OUT=${2:-/out}
MERKLE=${3:-/scripts/OSNMA_MerkleTree.xml}
PUBKEY=${4:-/scripts/OSNMA_PublicKey_PKID2.pem}
mkdir -p "$OUT"
cd /sim/build

cat > "$OUT/e1_only.ini" <<EOF
location=20,-51,100
start_time=2026/05/13,12:41:01
osnma_file=../auxiliary_osnma/13_MAY_2026_GST_12_11_01_keychain.csv
rinex_file=../rinex_files/2026_05_13.rnx
output_file=$OUT/osnma_sim_e1.bin
usrp=1
bit=0
duration=$DUR
enable_e5=false
cross_auth_neighbor_count=4
cross_auth_mode=${CROSS_AUTH_MODE:-3}
no_osnma_prns=[]
EOF
grep -qx 'usrp=1' "$OUT/e1_only.ini"  # usrp=1 means file output; usrp=0 would transmit

start=$(date +%s)
./osnma-sdr-sim -f "$OUT/e1_only.ini" > "$OUT/sim.log" 2>&1 || { tail -20 "$OUT/sim.log"; exit 1; }
echo "simulation wall time: $(( $(date +%s) - start )) s for ${DUR} s of signal"
[ "${SIM_ONLY:-0}" = 1 ] && exit 0
ls -l "$OUT/osnma_sim_e1.bin"

for mode in ${MODES:-nonstrict strict}; do
  d="$OUT/rx_$mode"; mkdir -p "$d"; cd "$d"
  sed -e "s|^SignalSource.filename=.*|SignalSource.filename=$OUT/osnma_sim_e1.bin|" \
      -e "s|^GNSS-SDR.osnma_public_key=.*|GNSS-SDR.osnma_public_key=$PUBKEY|" \
      -e "s|^GNSS-SDR.osnma_merkletree=.*|GNSS-SDR.osnma_merkletree=$MERKLE|" \
      -e "s|^Observables.dump=true|Observables.dump=false|" \
      -e "s|^PVT.dump=true|PVT.dump=false|" \
      -e "s|^NavDataMonitor.enable_monitor=true|NavDataMonitor.enable_monitor=false|" \
      /sim/E1_off_line.conf > receiver.conf
  [ "$mode" = strict ] && echo "GNSS-SDR.osnma_mode=strict" >> receiver.conf
  start=$(date +%s)
  gnss-sdr --config_file=receiver.conf > gnss-sdr.out 2> gnss-sdr.err || echo "gnss-sdr exit $? ($mode)"
  echo "gnss-sdr $mode wall time: $(( $(date +%s) - start )) s"
  cd /sim/build
done
