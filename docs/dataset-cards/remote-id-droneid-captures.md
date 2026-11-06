# Remote ID and DJI DroneID sample captures

<!-- about: repo:rub-syssec/dronesecurity, repo:anarkiwi/samples2djidroneid, repo:proto17/dji_droneid, repo:opendroneid/wireshark-dissector, repo:opendroneid/receiver-android, repo:opendroneid/opendroneid-core-c, res:ndss-2023-dji-droneid -->

There is no large public Remote ID dataset. What exists are small sample captures shipped with decoders: raw SDR IQ of DJI DroneID (OcuSync 2.0) bursts, and pcaps of ASTM F3411 / ASD-STAN Open Drone ID over Wi-Fi and Bluetooth. Enough to build and test a passive "who is flying near us" receiver.

| Field | Value |
|---|---|
| Platform | DJI Mini 2 and Mavic Air 2 (DroneSecurity samples); Open Drone ID transmitter test captures (dissector repo) |
| Environment | Not stated |
| Sensors and rates | DroneSecurity: raw IQ from a USRP B205-mini, viewable at 50 MS/s (`inspectrum -r 50e6`); DroneID frame about 10 MHz wide, every ~600 ms in 2.4 GHz (proto17 README). ODID: Wi-Fi and Wi-Fi beacon pcaps plus a BT5 long-range pcapng (file names) |
| Ground truth | The decoded payload itself (drone and pilot/app GPS position, home point, serial, velocities); CRC check gives validity |
| Size | DroneSecurity `samples/mini2_sm` 5,820,000 B, `samples/mavic_air_2` 1,802,240 B. Wireshark dissector: `odid_wifi_sample.pcap` 7,164 B, `odid_wifi_bcn_sample.pcap` 4,707 B, `odid_bt5_lr_sample.pcapng` 83,616 B (git tree sizes, 2026-11-06). samples2djidroneid and proto17 ship no IQ (proto17 withholds it because it contains GPS positions) |
| License | DroneSecurity AGPL-3.0; samples2djidroneid Apache-2.0; proto17/dji_droneid MIT; opendroneid repos Apache-2.0 |
| Format | Raw complex IQ (DroneSecurity samples), pcap/pcapng |
| Index | [DroneSecurity](../../catalog/repos/rub-syssec__dronesecurity.md), [samples2djidroneid](../../catalog/repos/anarkiwi__samples2djidroneid.md), [dji_droneid](../../catalog/repos/proto17__dji_droneid.md), [ODID Wireshark dissector](../../catalog/repos/opendroneid__wireshark-dissector.md), [ODID Android receiver](../../catalog/repos/opendroneid__receiver-android.md), [opendroneid-core-c](../../catalog/repos/opendroneid__opendroneid-core-c.md), [NDSS 2023 paper](../../catalog/resources/ndss-2023-dji-droneid.md) |

## Download

```bash
git clone --depth 1 https://github.com/RUB-SysSec/DroneSecurity        # default branch public_squash, samples/ inside
git clone --depth 1 https://github.com/opendroneid/wireshark-dissector  # 3 pcaps in repo root
```

## Loading and tooling

```bash
cd DroneSecurity
python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
./src/droneid_receiver_offline.py -i samples/mini2_sm     # README: 10 candidates, 9 decoded, 7 CRC OK
```

- ODID pcaps: install the Lua dissector from the repo into Wireshark/tshark plugins, then `tshark -r odid_wifi_sample.pcap -V`.
- Live receivers: ODID Android app (Wi-Fi/BT on a phone), samples2djidroneid (Docker, needs float32 IQ at 15.36 or 30.72 MS/s).

## Hackathon fit

- C-UAS / airspace awareness: decode Remote ID or DroneID and push tracks with operator location to a TAK/C2 map (idea 1-style monitor, reference architecture 4.2).
- Cross-check reported drone position against an independent RF bearing or radar track as a plausibility test (spoofed Remote ID detection), analogous to idea 3 for AIS.

## Pitfalls

- Tiny samples: they validate a decoder, not a detector's false-alarm rate.
- `mini2_sm` has no drone GPS lock, so only the phone/app location decodes (README).
- DroneSecurity is a proof of concept "not optimized for bad RF conditions, performance, or range".
- DroneID payloads carry personal location data; do not publish decoded captures from real flights.
- Newer DJI firmware and OcuSync 3/4 may differ; samples cover OcuSync 2.0.

## Sources

- READMEs and git trees of RUB-SysSec/DroneSecurity, anarkiwi/samples2djidroneid, proto17/dji_droneid, opendroneid/wireshark-dissector (gh api, 2026-11-06)
