#!/usr/bin/env bash
# One command per part: ./run.sh lidar | vio | aerial | integrate | all
# Needs: python3.12 venv with requirements.txt (PY=...), Docker for the OpenVINS part.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
DATA=${RELNAV_DATA:-$HERE/data}
PY=${PY:-python3}
R=$HERE/results
part=${1:-all}
cd "$HERE"
if [[ $part == lidar || $part == all ]]; then
  ./fetch_data.sh lidar
  for s in ${KITTI_SEQS:-04}; do
    $PY lidar/run_kiss_icp_kitti.py --data "$DATA/kitti" --poses "$DATA/kitti/dataset/poses" --seq $s
  done
fi
if [[ $part == vio || $part == all ]]; then
  ./fetch_data.sh vio
  BAG=$DATA/uzhfpv/indoor_forward_3_snapdragon_with_gt.bag
  OV=$R/vio/openvins_raw
  vio/run_openvins.sh "$BAG" "$OV" uzhfpv_indoor 2
  $PY vio/eval_uzhfpv.py --bag "$BAG" --openvins "$OV"
fi
if [[ $part == aerial || $part == all ]]; then
  ./fetch_data.sh aerial
  $PY aerial/run_nadir_vo.py --data "$DATA/vpair"
fi
if [[ $part == integrate || $part == all ]]; then
  $PY integrate/vo_to_altpnt.py \
    kiss-icp-kitti04=$R/lidar/kitti04_gt.tum,$R/lidar/kitti04_kiss_icp.tum \
    openvins-uzhfpv=$R/vio/uzhfpv_indoor_forward_3_gt.tum,$R/vio/uzhfpv_indoor_forward_3_openvins.tum \
    nadir-vo-vpair=$R/aerial/vpair_gt.tum,$R/aerial/vpair_nadir_vo.tum
fi
