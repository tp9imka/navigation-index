#!/usr/bin/env bash
# Download the 7 VAARA (Jammertest 2024) u-blox logs used here (64 MB as .xz, 272 MB decompressed)
# and the IGS broadcast ephemerides for 2024-09-11/12 from the BKG mirror (no login for either).
# Usage: ./fetch_data.sh [data_dir]   (default ./data, git-ignored)
set -euo pipefail
cd "$(dirname "$0")"
D=${1:-data}
RAW=https://raw.githubusercontent.com/UniVaasaDigiEco/VAARA/main
FILES="2024-09-10/Test_1/ublox_2024-09-10T073207Z0000.ubx
2024-09-10/Test_2/ublox_2024-09-10T115512Z0000.ubx
2024-09-11/Morning_Motorcade/Test_1/ublox_2024-09-11T075704.ubx
2024-09-11/Afternoon/Test_1/ublox_2024-09-11T122113.ubx
2024-09-11/Afternoon/Test_2/ublox_2024-09-11T143312.ubx
2024-09-12/Test_1/ublox_2024-09-12T071744.ubx
2024-09-12/Test_2/ublox_2024-09-12T085023.ubx"
for f in $FILES; do
  mkdir -p "$D/vaara/$(dirname "$f")"
  [ -s "$D/vaara/$f" ] && continue
  curl -fsSL -o "$D/vaara/$f.xz" "$RAW/$f.xz"
  xz -d "$D/vaara/$f.xz"
done
curl -fsSL -o "$D/vaara/Jammertest_metadata.md" "$RAW/Jammertest_metadata.md"
mkdir -p "$D/brdc"
for doy in 255 256; do
  [ -s "$D/brdc/BRDC_$doy.rnx.gz" ] || curl -fsSL -o "$D/brdc/BRDC_$doy.rnx.gz" \
    "https://igs.bkg.bund.de/root_ftp/IGS/BRDC/2024/$doy/BRDC00WRD_S_2024${doy}0000_01D_MN.rnx.gz"
done
ls -lR "$D" | grep -E '\.ubx$|rnx.gz$'
