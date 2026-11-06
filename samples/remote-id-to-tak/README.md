# Drone Remote ID => track table => TAK

<!-- about: repo:opendroneid/opendroneid-core-c, repo:opendroneid/wireshark-dissector, repo:opendroneid/receiver-android, repo:peterjburke/rid, repo:alphafox02/dragonsync, repo:colonelpanichacks/drone-mesh-mapper, repo:snstac/pytak -->

Goal: a passive "who is flying near us" picture from broadcast Remote ID (ASTM F3411 /
ASD-STAN EN 4709-002, "Open Drone ID"). Receiving these broadcasts is their intended
public use. The pipeline:

```
pcap / sniffer bytes => capture.py (Wi-Fi beacon, Wi-Fi NAN, BLE) => odid.py (decode)
  => tracker.py (per-UAS tracks, staleness, plausibility flags)
  => rid_to_cot.py (UAS track + operator point as CoT) => PyTAK => TAK server / Mesh SA
```

Everything except the PyTAK transport is Python stdlib. Remote ID is a self-report: the
flags below are consistency checks that raise suspicion, not proof of spoofing.

## Files

| File | What |
|---|---|
| `odid.py` | Decoder for Basic ID, Location/Vector, Authentication, Self-ID, System, Operator ID and message packs. Mirrors `opendroneid.c` decode semantics (float32 arithmetic, string copy rules, pack validation). `summarize()` turns sentinels (lat/lon 0, alt -1000, dir 361, speed 255) into `None`. |
| `capture.py` | pcap/pcapng reader. Wi-Fi (radiotap): 802.11 beacon vendor IE `FA:0B:BC` type `0x0D`, and NAN service discovery frames with the ODID service id `88:69:19:9D:92:09`. BLE: signature scan for service data UUID `0xFFFA` app code `0x0D`; drops nRF Sniffer packets with the CRC-OK flag clear. |
| `tracker.py` | Track table keyed by UAS ID (falls back to transmitter MAC until a Basic ID arrives), staleness, anomaly flags. Thresholds are named constants at the top. |
| `rid_to_cot.py` | CoT via `samples/mavlink-to-tak-cot/cot.py` (imported, not copied) and PyTAK. Modes: `--sim` / `--pcap`, `--offline` or `--cot-url`. |
| `sim.py` | Minimal encoder + a made-up 30 s scenario with one normal flight and one case per anomaly. |
| `corec/odid_vectors.c`, `corec/build.sh` | Reference harness linked against upstream `opendroneid.c`: encodes random inputs with core-c and prints core-c's own decode, or decodes hex from stdin. |
| `fixtures/core_c_*.jsonl` | Vectors produced by that harness (gen 500, fuzz 500, captures 81). |
| `test_odid.py`, `test_tracker.py` | 16 tests: bit-exact core-c comparison, public captures, scaling rules, tracker flags, CoT shape. |
| `fetch_captures.sh` | Downloads the three public sample captures (Apache-2.0) into `captures/` (git-ignored). |

## Run

```sh
cd samples/remote-id-to-tak
./fetch_captures.sh                      # optional: public pcaps for the capture tests/demos
./corec/build.sh                         # optional: clones opendroneid-core-c, builds the harness with cc
python3 -m unittest test_odid test_tracker
python3 capture.py captures/odid_wifi_bcn_sample.pcap | head -3
python3 rid_to_cot.py --sim --offline --quiet
python3 rid_to_cot.py --pcap captures/odid_wifi_bcn_sample.pcap --offline

pip install -r requirements.txt          # pytak, only for --cot-url
python3 ../mavlink-to-tak-cot/cot_sink.py --port 18087 --count 1000 &
python3 rid_to_cot.py --sim --cot-url tcp://127.0.0.1:18087 --speed 10
python3 rid_to_cot.py --pcap captures/odid_bt5_lr_sample.pcapng --cot-url udp+wo://239.2.3.1:6969   # Mesh SA
```

Without the harness or captures the corresponding tests skip; the committed fixtures
still check the decoder against core-c output.

## 1. Decoder validated against opendroneid-core-c (ran it)

How: `corec/odid_vectors.c` links upstream `libopendroneid/opendroneid.c` (master
`849c03a`, 2026-10-07; compiled directly with Apple clang 21 since cmake was not on the
machine). `gen` builds random `ODID_*_data` inputs with edge cases (direction 179.5/360/361,
speed 63.75 boundary and 254.25 clamp, altitude -1000/31767.5, timestamp 0xFFFF, 20-char
IDs without NUL, binary UUID/session IDs, multi-page auth), encodes them with core-c's
encoders and packs, then prints core-c's `decodeOpenDroneID` result with `%.17g`. `fuzz`
feeds random 25-byte messages (valid and invalid type nibbles). The Python side decodes the
same bytes and must reproduce every field exactly: floats as IEEE values, strings as the raw
C buffer bytes, return type, and which messages were accepted.

Observed (Python 3.14.7 and 3.12.14):

```
test_encoded_by_core_c ... ok      500 core-c-encoded vectors (125 of them packs)
test_random_raw_messages ... ok    500 random raw messages, 141 rejected by core-c and by odid.py alike
test_public_captures ... ok        81 unique payloads from the 3 public captures (13 rejected, incl. empty packs)
test_live_harness ... ok           fresh 300 gen + 300 fuzz from the built harness
...
Ran 16 tests in 0.086s
OK
```

Negative control: five planted decoder bugs (Baro/Speed accuracy nibble swap, timestamp
without float32 rounding, `rstrip` instead of first-NUL string copy, Basic ID slot rule
removed, 3-bit instead of 2-bit operator location type) each made the suite fail. The
float32 one matters: `TimeStamp` decoded in double differs from core-c in the last bits.

Things found in core-c while mirroring it (mirrored, not fixed):

- `decodeHorizontalAccuracy(ODID_HOR_ACC_4NM)` returns 7808 m; the enum comment and 4 NM
  are 7408 m. `odid.HORIZ_ACC_M` keeps 7808 so outputs match; use 7408 if you need truth.
- `decodeBasicIDMessage` copies `sizeof(outData->UASID)` = 21 bytes for UUID/session IDs
  from a 20-byte field, so the 21st byte is the first reserved byte. Stays inside the packed
  struct, but the C string is not NUL-terminated if that byte is nonzero.
- `decodeOpenDroneID` on a pack trusts the buffer to hold `MsgPackSize` messages;
  `odid_message_process_pack` checks the length, the bare decoder does not. `odid.py`
  rejects truncated packs.
- The C decoder does no range checks on decode: a corrupted frame gives lon -214 deg.

## 2. Public captures (ran it)

`opendroneid/wireshark-dissector` at `d12670f` ships three small captures (sizes in the
[dataset card](../../docs/dataset-cards/remote-id-droneid-captures.md)):

| Capture | Link type | Payloads found | Content |
|---|---|---|---|
| `odid_wifi_sample.pcap` | radiotap | 21 NAN + 21 beacon packs | each pack holds only an Operator ID `GBR-OP-123ABCD` |
| `odid_wifi_bcn_sample.pcap` | radiotap | 21 beacon packs | 5 messages each: Basic ID (type none), Location, System, Operator ID, Self-ID "Recreational"; drone near 45.5457, -122.968 moving at a claimed 20.5 m/s, operator ~400 m away |
| `odid_bt5_lr_sample.pcapng` | 272 (nRF Sniffer) | 273 raw, 244 after CRC filter | serial `SSEVTFG93700070`, multirotor, airborne, no position (lat/lon 0); packs of 0-5 messages, 19 empty packs |

```
$ python3 capture.py captures/odid_wifi_bcn_sample.pcap | head -1
{"t": 1621633931.161999, "transport": "wifi-beacon", "mac": "84:cc:a8:60:43:24", "counter": 208, "type": 15, "ids": {"none": "4d46473141303132333435363738390000000000"}, "ua_type": "none", "status": "undeclared", "lat": 45.5457468, "lon": -122.9681496, "alt_geo_m": 237.0, "alt_baro_m": null, "height_m": 100.0, "height_ref": "takeoff", "course_deg": 92.0, "speed_h_ms": 20.5, "speed_v_ms": null, "h_acc_m": 30.0, "v_acc_m": 25.0, "ts_after_hour_s": 0.0, "operator_lat": 45.5443876, "operator_lon": -122.9726866, "operator_alt_geo_m": null, "operator_location_type": "takeoff", "system_timestamp": 0, "operator_id": "GBR-OP-123ABCD", "self_id": "Recreational"}
```

Two lessons from real bytes. First, without the nRF Sniffer CRC flag 29 BT5 frames decode
to garbage (lat -89.8, lon -214.6, mangled serials); a receiver must check CRC and range.
Second, the beacon sample's Basic ID has ID type "none", so the track is keyed by MAC, and
its Location timestamp is constantly 0, which the tracker flags as `timestamp_skew`
(469 s from the capture clock). That flag is noise here: test transmitters often leave the
timestamp unset. These captures validate a decoder, not detection rates.

## 3. Track management and anomaly flags (ran it, synthetic data)

| Flag | Rule (constants in `tracker.py`) | Why it matters |
|---|---|---|
| `impossible_speed` | implied speed between fixes from the same transmitter > 100 m/s | teleporting track, replay or fabricated position |
| `location_jump` | distance > claimed speed x dt + both accuracy radii + 50 m | position inconsistent with its own velocity |
| `speed_mismatch` | claimed vs implied speed differ by > 20 m/s (0.5-10 s window) | velocity field not tied to motion |
| `operator_far` | operator > 2000 m from UAS | VLOS-type operations keep the operator far closer; fake operator point |
| `id_change` | one transmitter address switches its claimed UAS ID | ID rotation to dodge tracking |
| `duplicate_id` | same UAS ID from two transmitters > 500 m apart within 3 s | cloned serial |
| `timestamp_skew` | Location timestamp (s after the hour) > 30 s from receiver clock | replayed frames; also unset timestamps |

Tracks go stale after 5 s without a message (F3411 Location is broadcast at >= 1 Hz) and
are dropped after 60 s. Tracks start keyed by MAC and are re-keyed when a Basic ID arrives
(BT4 legacy sends one message per advertisement, so ID and position arrive separately).

Observed on the synthetic scenario (`python3 rid_to_cot.py --sim --offline --quiet`):

```
# 148 payloads => 256 CoT events
# tracks at end: 4 live, 2 stale
#  serial_number:SIMA-0001              msgs= 50 fixes= 50 live  flags=['duplicate_id']
#  serial_number:SIMC-0003              msgs= 30 fixes= 30 live  flags=['impossible_speed', 'location_jump']
#  serial_number:SIMD-0004              msgs= 30 fixes=  1 live  flags=['operator_far']
#  serial_number:SIME-0005              msgs= 12 fixes=  1 STALE flags=-
#  serial_number:SIME-9999              msgs= 18 fixes=  1 live  flags=['id_change']
#  serial_number:SIMF-0006              msgs=  8 fixes=  1 STALE flags=-
# anomaly events (first occurrence per track):
#  t+   0.2s serial_number:SIMD-0004: operator_far - operator 7991 m from UAS
#  t+  10.3s serial_number:SIMA-0001: duplicate_id - serial_number:SIMA-0001 heard from a0:00:00:00:00:0a and b0:00:00:00:00:0b 2999 m apart within 3 s
#  t+  12.4s serial_number:SIME-9999: id_change - transmitter e0:00:00:00:00:0e switched from serial_number:SIME-0005 to serial_number:SIME-9999
#  t+  15.1s serial_number:SIMC-0003: impossible_speed - 2010 m/s implied over 1.0 s
#  t+  15.1s serial_number:SIMC-0003: location_jump - moved 2010 m in 1.0 s, claimed 12.0 m/s
```

The scenario was built to trigger each flag, so this shows the rules fire, not that the
thresholds are right. A careful spoofer that keeps position, velocity, operator and
timestamp consistent passes every check here. The real defence is an independent sensor:
an RF bearing (e.g. [interference-geolocation-to-tak](../interference-geolocation-to-tak/))
or radar track that disagrees with the claimed position. MAC addresses are also weak keys:
transmitters can randomise them.

## 4. CoT output (ran it)

Per track, at most 1 Hz: a UAS event and, if the System message has an operator location,
an operator event. Affiliation stays unknown (`u`): a broadcast says nothing about intent.

- UAS type: `a-u-A-M-H-Q` (rotor drone) for multirotor/gyroplane, `a-u-A-M-F-Q` for
  aeroplane/hybrid lift, `a-u-A` otherwise. Operator: `a-u-G`.
- `hae` = F3411 geodetic altitude, which is already WGS84 HAE (no geoid correction, unlike
  MAVLink AMSL). Unknown => 9999999. `ce`/`le` from the horizontal/vertical accuracy enums.
- `stale` = 5 s, matching the tracker. Flags go into `<remarks>`.

```xml
<event version="2.0" type="a-u-A-M-H-Q" uid="rid-SIMA-0001" how="m-g" time="2025-11-06T12:00:00.000Z" start="2025-11-06T12:00:00.000Z" stale="2025-11-06T12:00:05.000Z"><point lat="51.4710780" lon="-0.4543000" hae="150.00" ce="10.0" le="10.0" /><detail><contact callsign="RID SIMA-0001" /><track course="90.0" speed="9.50" /><remarks>RID serial_number:SIMA-0001 via a0:00:00:00:00:0a; operator GBR-OP-DEMO0001; self-id 'survey'; status airborne</remarks></detail></event>
```

PyTAK runs (pytak 7.6.1, Python 3.12.14): `--sim --cot-url tcp://127.0.0.1:18087 --speed 10`
delivered 256 events to `cot_sink.py` (128 UAS tracks + 128 operator points, plus PyTAK's
`takPing`), same count as offline. `--pcap captures/odid_wifi_bcn_sample.pcap --cot-url
udp+wo://127.0.0.1:16969 --speed 1` delivered the real capture's track:

```
cot 1: uid=rid-84:cc:a8:60:43:24 type=a-u-A lat=45.5457468 lon=-122.9681496 hae=237.00 course=92.0 speed=20.50 time=2026-11-06T09:22:03.792Z stale=2026-11-06T09:22:08.792Z
sink: received 10 track CoT events over udp
```

Not run: a real TAK server, ATAK/WinTAK rendering, multicast, TLS.

## 5. Receiver hardware (from sources, not tested here)

Drones may use any of four transports: BT4 legacy advertising, BT5 long range (Coded PHY +
extended advertising), Wi-Fi NAN, Wi-Fi beacon. A receiver that covers one transport misses
drones that only use another, so plan for at least BLE + 2.4 GHz Wi-Fi.

| Option | Transports | Limits | Source |
|---|---|---|---|
| Android phone + [receiver-android](../../docs/integration-cards/opendroneid__receiver-android.md) | All four, handset permitting | BT5 LR reliable only on tested Galaxy S10 / Mate 20 Pro; OnePlus 6T and Mi 9 listen 5 s on / 15 s off; some phones set the feature flags but never receive. NAN verified on Galaxy S10 only. Beacon scans throttled on Android 8+ unless disabled in Developer Options. | receiver-android README |
| iPhone | BT4 legacy only | iOS (to 15 per README) cannot receive BT5 LR, NAN or beacon | opendroneid-core-c README |
| ESP32 classic, e.g. [peterjburke/RID](../../docs/integration-cards/peterjburke__rid.md) | BT4 legacy (Wi-Fi code present but off) | No Coded PHY, so no BT5 LR; Wi-Fi path does not link without `wifi.c`; unmaintained since 2024 | RID card, core-c README ("ESP32-S3 or ESP32-C3 HW is needed" for long range) |
| ESP32-S3 / C3 / C5, e.g. [drone-mesh-mapper](../../docs/integration-cards/colonelpanichacks__drone-mesh-mapper.md) | S3: BLE + 2.4 GHz Wi-Fi; C3: Wi-Fi; C5: 5 GHz ch 149-165 | Wi-Fi listens on one fixed channel (6 by default); cheap, meshable over Meshtastic | drone-mesh-mapper card |
| Linux + monitor-mode Wi-Fi adapter, e.g. `sxjack/unix_rid_capture` | NAN, beacon (+ BLE via BlueZ or nRF52840 sniffer) | Needs a monitor-mode chipset (author tested rtl8812au); README: "Probably won't receive Bluetooth 5 advertising without external hardware" | unix_rid_capture README |
| BLE 5 sniffer: nRF52840 dongle (nRF Sniffer) or TI CC1352/CC26x2 with Sniffle | BT4 + BT5 incl. Coded PHY and extended advertising | Extra dongle and host software; check the per-packet CRC flag (see section 2). DragonSync/WarDragon feeds from Sniffle | Sniffle README, dragonsync card, this sample's BT5 capture (linktype 272) |

Range: none of the sources state a measured detection range; do not quote one without a
field test. DJI DroneID (OcuSync) is a different, proprietary signal and needs an SDR
(see the dataset card); China GB 46750-2025 uses its own format (`libopendroneidcn`).

## Gotchas

- Decoded values are claims. Location, operator position and ID can all be fabricated with
  the public transmitter examples.
- Real-world privacy: decoded operator positions are personal data. Do not publish logs
  from real flights.
- `capture.py`'s BLE path is a signature scan; it works on the nRF Sniffer capture here,
  other BLE link types (HCI, btle) are untested.
- The beacon sample carries one byte after the pack; decoders ignore it.
- `odid.py` decodes Authentication pages but does not verify signatures.

## Related

- [opendroneid-core-c card](../../docs/integration-cards/opendroneid__opendroneid-core-c.md),
  [DragonSync card](../../docs/integration-cards/alphafox02__dragonsync.md) (production-grade
  sniffer => CoT gateway), [PyTAK card](../../docs/integration-cards/snstac__pytak.md).
- [mavlink-to-tak-cot](../mavlink-to-tak-cot/) for the shared CoT builder and sink.
