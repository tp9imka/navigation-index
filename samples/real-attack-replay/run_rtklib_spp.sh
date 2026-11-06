#!/usr/bin/env bash
# UBX (RXM-RAWX + RXM-SFRBX) => RINEX 3.04 obs/nav with convbin => RTKLIB SPP with solution status,
# in the rtklib-demo5 image built by samples/gnss-rinex-processing.
# Usage: ./run_rtklib_spp.sh <file.ubx> <out_dir> [SYS (default G,E,R,C)] [external nav .rnx(.gz)]
# Without an external nav file SPP uses the ephemerides the receiver decoded, which during Jammertest
# include the spoofers' synthetic ones; pass an IGS BRDC file (see README) for a clean solution.
# Files move with docker cp (the host path need not be shared with the Docker VM).
set -euo pipefail
UBX=$1; OUT=$2; SYS=${3:-G,E,R,C}; EXTNAV=${4:-}
IMAGE=rtklib-demo5
NAME=rar-rtklib-$$
docker image inspect "$IMAGE" >/dev/null 2>&1 || docker build -t "$IMAGE" "$(dirname "$0")/../gnss-rinex-processing/docker/"
mkdir -p "$OUT"
BASE=$(basename "$UBX" .ubx)
NAV=/work/$BASE.nav; TAG=lognav
if [ -n "$EXTNAV" ]; then NAV=/work/$(basename "$EXTNAV"); TAG=brdc; fi
# -m 10 elevation mask; -y 1 writes <out>.stat with $POS/$CLK per epoch
docker create --name "$NAME" "$IMAGE" bash -c "
  set -e
  convbin -r ubx -v 3.04 -od -os -o /work/$BASE.obs -n /work/$BASE.nav /work/$BASE.ubx > /work/convbin.log 2>&1
  rnx2rtkp -p 0 -sys $SYS -m 10 -y 1 -o /work/$BASE.$TAG.spp.pos /work/$BASE.obs $NAV 2> /work/rnx2rtkp.log" >/dev/null
trap 'docker rm -f "$NAME" >/dev/null' EXIT
docker cp "$UBX" "$NAME":/work/$BASE.ubx
[ -n "$EXTNAV" ] && docker cp "$EXTNAV" "$NAME":$NAV
docker start -a "$NAME"
for f in $BASE.$TAG.spp.pos $BASE.$TAG.spp.pos.stat; do docker cp "$NAME":/work/$f "$OUT"/ ; done
