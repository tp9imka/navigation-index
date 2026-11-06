#!/usr/bin/env bash
# SPP vs RTK on the same rover data with RTKLIB demo5 rnx2rtkp, then score both against the CORS sheet.
# rnx2rtkp unpacks .gz itself and calls `crx2rnx` for Hatanaka .d files, so both must be on PATH.
set -euo pipefail
RNX2RTKP=${RNX2RTKP:-rnx2rtkp}
# $TS / $TE / $BASE_XYZ stay unquoted on purpose: rnx2rtkp takes "-ts y/m/d h:m:s" and "-r x y z" as separate args
TS="2024/04/09 12:00:00"; TE="2024/04/09 14:00:00"
EPOCH=2024.27                                           # decimal year of the data, for plate motion
mkdir -p out
BASE_XYZ=$(python3 compare_pos.py --truth data/p731_20.coord.txt --epoch $EPOCH --print-xyz)

# -p 0 single point; -e ECEF output; -sys G GPS only (the brdc file carries GPS ephemeris only)
$RNX2RTKP -k rtk.conf -p 0 -sys G -m 15 -e -ts $TS -te $TE \
  -o out/spp.pos data/p7301000.24d.gz data/brdc1000.24n.gz

# -p 2 kinematic RTK (per-epoch solution, nothing assumes the rover is static); -f 2 L1+L2;
# -r base ECEF from the NGS sheet (otherwise RTKLIB averages the base's own single solutions)
$RNX2RTKP -k rtk.conf -p 2 -f 2 -sys G -m 15 -e -r $BASE_XYZ -ts $TS -te $TE \
  -o out/rtk.pos data/p7301000.24d.gz data/p7311000.24d.gz data/brdc1000.24n.gz

python3 compare_pos.py --truth data/p730_20.coord.txt --epoch $EPOCH out/spp.pos out/rtk.pos
