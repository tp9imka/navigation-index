#!/usr/bin/env bash
# Download the public sequences used here (no login). Usage: ./fetch_data.sh [lidar|vio|aerial|all]
# Sizes are HEAD Content-Length on 2026-11-06.
set -euo pipefail
DATA=${RELNAV_DATA:-$(cd "$(dirname "$0")" && pwd)/data}
PART=${1:-all}
K=https://s3.eu-central-1.amazonaws.com/avg-kitti
get() { mkdir -p "$(dirname "$2")"; [ -s "$2.done" ] || { curl -fSL -C - -o "$2" "$1" && echo ok > "$2.done"; }; }
if [[ $PART == lidar || $PART == all ]]; then
  get $K/raw_data/2011_09_30_calib.zip "$DATA/kitti/2011_09_30_calib.zip"                                       # 4 KB
  get $K/data_odometry_poses.zip "$DATA/kitti/data_odometry_poses.zip"                                           # 1.3 MB
  # odometry seq 04 = drive 0016 (1.13 GB), seq 07 = drive 0027 (4.42 GB); KITTI_SEQS="04 07"
  for s in ${KITTI_SEQS:-04}; do
    case $s in 04) d=2011_09_30_drive_0016;; 07) d=2011_09_30_drive_0027;; *) echo "seq $s not mapped"; exit 1;; esac
    get $K/raw_data/$d/${d}_sync.zip "$DATA/kitti/${d}_sync.zip"
    (cd "$DATA/kitti" && unzip -qn ${d}_sync.zip)
  done
  (cd "$DATA/kitti" && unzip -qn 2011_09_30_calib.zip && unzip -qn data_odometry_poses.zip)
fi
if [[ $PART == vio || $PART == all ]]; then
  get https://download.ifi.uzh.ch/rpg/web/datasets/uzh-fpv-newer-versions/v3/indoor_forward_3_snapdragon_with_gt.bag \
      "$DATA/uzhfpv/indoor_forward_3_snapdragon_with_gt.bag"                                                     # 1.61 GB
fi
if [[ $PART == aerial || $PART == all ]]; then
  get "https://zenodo.org/records/6473989/files/vpair_sample.zip?download=1" "$DATA/vpair/vpair_sample.zip"       # 0.86 GB
  (cd "$DATA/vpair" && unzip -qn vpair_sample.zip)
fi
du -sh "$DATA"/* 2>/dev/null
