#!/bin/sh
# Public Open Drone ID sample captures from opendroneid/wireshark-dissector (Apache-2.0).
set -eu
cd "$(dirname "$0")"
mkdir -p captures
BASE=https://raw.githubusercontent.com/opendroneid/wireshark-dissector/d12670fede3aa4e336cfa326528782abfc864a10
for f in odid_wifi_sample.pcap odid_wifi_bcn_sample.pcap odid_bt5_lr_sample.pcapng; do
  curl -fsSL -o "captures/$f" "$BASE/$f"
done
ls -l captures
