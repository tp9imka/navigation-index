#!/usr/bin/env bash
# Part 2: OpenVINS v2.7 (ROS 1 serial bag reader) on a UZH-FPV Snapdragon bag, in Docker.
# Usage: vio/run_openvins.sh <bag> <out_dir> [config=uzhfpv_indoor] [max_cameras=2]
# Uses docker cp instead of bind mounts: colima / Docker Desktop only share some host paths.
set -euo pipefail
BAG=$1
OUT=$(mkdir -p "$2" && cd "$2" && pwd)
CFG=${3:-uzhfpv_indoor}
NCAM=${4:-2}
IMG=relnav-openvins:v2.7
HERE=$(cd "$(dirname "$0")" && pwd)
docker image inspect $IMG >/dev/null 2>&1 || docker build -f "$HERE/Dockerfile.openvins" -t $IMG "$HERE"
STEREO=true; [ "$NCAM" = 1 ] && STEREO=false
CID=$(docker create $IMG bash -c "
  source /catkin_ws/devel/setup.bash
  roscore >/dev/null 2>&1 &
  sleep 4
  mkdir -p /out
  time rosrun ov_msckf ros1_serial_msckf \
    _config_path:=/catkin_ws/src/open_vins/config/$CFG/estimator_config.yaml \
    _path_bag:=/input.bag _bag_start:=0 _bag_durr:=-1 \
    _max_cameras:=$NCAM _use_stereo:=$STEREO _verbosity:=WARNING \
    _save_total_state:=true _filepath_est:=/out/ov_state_est.txt _filepath_std:=/out/ov_state_std.txt \
    _record_timing_information:=true _record_timing_filepath:=/out/ov_timing.txt
")
trap 'docker rm -f $CID >/dev/null' EXIT
docker cp "$BAG" "$CID:/input.bag"
T0=$(date +%s)
docker start -a $CID > "$OUT/openvins.log" 2>&1 || true   # ROS 1 serial node aborts on exit, after writing
T1=$(date +%s)
docker cp "$CID:/out/." "$OUT/"
sec() { grep -E "^$1" "$OUT/openvins.log" | tail -1 | sed -E 's/.*\t([0-9]+)m([0-9.]+)s/\1 \2/' | awk '{print $1*60+$2}'; }
echo "{\"wall_s_rosrun\": $(sec real), \"user_s\": $(sec user), \"sys_s\": $(sec sys), \"wall_s_container\": $((T1 - T0)), \"where\": \"$(docker info --format '{{.Name}} {{.NCPU}} vCPU {{.Architecture}}')\"}" > "$OUT/run_time.json"
cat "$OUT/run_time.json"
tail -n 5 "$OUT/openvins.log"
