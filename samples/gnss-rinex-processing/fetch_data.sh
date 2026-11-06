#!/usr/bin/env bash
# Download one day of public NOAA NGS CORS data: rover P730, base P731 (~30 km apart, N. California),
# the GPS broadcast ephemeris, and both stations' ITRF2020 coordinate sheets (ground truth).
# About 3.6 MB total; files already present are skipped. data/ is git-ignored.
set -euo pipefail
YEAR=2024; DOY=100; YY=24          # 2024-04-09
BASE_URL=https://geodesy.noaa.gov/corsdata
cd "$(dirname "$0")"
mkdir -p data
cd data
get() {  # NGS answers 408 now and then; retry instead of failing the whole fetch
  local url=$1 name=${1##*/}
  [ -s "$name" ] || curl -fsSL --retry 5 --retry-all-errors --retry-delay 3 -o "$name" "$url"
}
for s in p730 p731; do
  get "$BASE_URL/rinex/$YEAR/$DOY/$s/${s}${DOY}0.${YY}d.gz"   # Hatanaka-compressed RINEX 2.11 OBS
  get "$BASE_URL/coord/coord_20/${s}_20.coord.txt"
done
get "$BASE_URL/rinex/$YEAR/$DOY/brdc${DOY}0.${YY}n.gz"
ls -l
