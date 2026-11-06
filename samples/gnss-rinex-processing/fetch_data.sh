#!/usr/bin/env bash
# Download one day of public NOAA NGS CORS data: rover P730, base P731 (~30 km apart, N. California),
# the GPS broadcast ephemeris, and both stations' ITRF2020 coordinate sheets (ground truth).
set -euo pipefail
YEAR=2024; DOY=100; YY=24          # 2024-04-09
BASE_URL=https://geodesy.noaa.gov/corsdata
mkdir -p data
cd data
for s in p730 p731; do
  curl -fsSLO "$BASE_URL/rinex/$YEAR/$DOY/$s/${s}${DOY}0.${YY}d.gz"   # Hatanaka-compressed RINEX 2.11 OBS
  curl -fsSLO "$BASE_URL/coord/coord_20/${s}_20.coord.txt"
done
curl -fsSLO "$BASE_URL/rinex/$YEAR/$DOY/brdc${DOY}0.${YY}n.gz"
ls -l
