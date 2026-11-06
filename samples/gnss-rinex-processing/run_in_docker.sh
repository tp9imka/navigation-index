#!/usr/bin/env bash
# Build RTKLIB demo5 in Docker and run run_rtklib.sh (+ optional RINEX 3 conversion) inside it.
# Copies files in and out with `docker cp`, so it works when the host path is not shared with
# the Docker VM. Usage: ./run_in_docker.sh   (after ./fetch_data.sh)
set -euo pipefail
cd "$(dirname "$0")"
IMAGE=rtklib-demo5
docker image inspect "$IMAGE" >/dev/null 2>&1 || docker build -t "$IMAGE" docker/
CID=$(docker create "$IMAGE" bash -c '
  set -e
  ./run_rtklib.sh
  # RINEX 2.11 => 3.04 for gnss_lib_py (glp_spp.py): crx2rnx, then convbin
  gzip -dc data/p7301000.24d.gz | crx2rnx - > data/p7301000.24o
  convbin -r rinex -v 3.04 -os -o data/p730_r3.rnx data/p7301000.24o >/dev/null 2>&1
  ls -l out data/p730_r3.rnx')
trap 'docker rm -f "$CID" >/dev/null' EXIT
docker cp . "$CID":/work
docker start -a "$CID"
mkdir -p out
docker cp "$CID":/work/out/. out/
docker cp "$CID":/work/data/p730_r3.rnx data/p730_r3.rnx
