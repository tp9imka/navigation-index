# DragonSync - integration card
<!-- about: repo:alphafox02/dragonsync -->
One-line: Python gateway that subscribes to ZMQ streams of decoded drone Remote ID / DJI DroneID frames (plus kit GPS status, optional readsb aircraft, FPV alerts, Kismet devices) and emits drone, pilot and home-point CoT to ATAK/TAK, MQTT/Home Assistant and Lattice; a ready-made passive drone-detection => common-operating-picture back end.

| | |
|---|---|
| Install | `git clone https://github.com/alphafox02/DragonSync && cd DragonSync && pip3 install -r requirements.txt` (`cffi`, `cryptography`, `gps`, `lxml`, `netifaces`, `psutil`, `pycparser`, `pyzmq`, `requests`). Off-kit also `sudo apt install lm-sensors gpsd gpsd-clients`. FAA RID lookup is a git submodule (`faa-rid-lookup`, MIT): clone with `--recurse-submodules`. No releases or tags; track `main`. systemd units in `services/`. |
| Runs on | Linux, Python 3.x. Designed for the WarDragon kit (all sensors and services preinstalled). DragonSync itself needs no radio; the sensors feeding it do (see Inputs). |
| Inputs | ZMQ SUB `tcp://<zmq_host>:4224`: JSON (`recv_json`) decoded RID/DJI frames, a list of dicts keyed `"Basic ID"`, `"Location/Vector Message"`, `"Self-ID Message"`, `"System Message"`, optional `"AUX_ADV_IND"` (`core/telemetry_parser.py`). ZMQ SUB 4225: kit status/GPS from `wardragon_monitor.py` (optional; `gps.ini` static position fallback). Optional ZMQ 4226 FPV alerts, readsb HTTP `/?all_with_pos`, Kismet REST (allow-listed MACs in `kismet_targets.txt`). Producers of 4224 on WarDragon: `droneid-go` (WiFi/BLE RID, Sniffle BLE) and `antsdr_dji_droneid` (DJI DroneID on an ANTSDR E200). |
| Outputs | CoT XML to multicast (default `239.2.3.1:6969`, TTL 1) and/or TAK server TCP/UDP with optional TLS (`.p12` or PEM). Drone type from RID UA type (`a-f-A-f` fixed wing, `a-u-A-M-H-R` rotorcraft/default), separate `pilot-<id>` and home markers, FAA make/model in remarks. MQTT per-drone JSON + HA discovery (`docs/mqtt-schema.md`), Lattice entities, read-only HTTP API (`/status`, `/drones`, `/signals`, `/config`, `/update/check`). |
| Key API / entry points | `python3 dragonsync.py -c config.ini [-d]` with CLI overrides `--zmq-host --zmq-port --zmq-status-port --tak-host --tak-port --tak-protocol {TCP,UDP} --tak-tls-p12 ... --enable-multicast --tak-multicast-addr --tak-multicast-port --rate-limit --inactivity-timeout --mqtt-*`. Core loop `zmq_to_cot(zmq_host, zmq_port, zmq_status_port, tak_host=None, tak_port=None, tak_tls_context=None, tak_protocol='TCP', multicast_address=None, multicast_port=None, enable_multicast=False, rate_limit=1.0, max_drones=100, inactivity_timeout=60.0, ...)`; parser `parse_drone_info(message, ua_type_mapping)`; CoT builders `utils/cot_builder.py` `build_drone_cot(drone, stale_offset)`, `build_pilot_cot`, `build_home_cot`. Test feeder `tests/test_drone_generator.py --scenario <json> --mode {replay,simulate} [--loop] [--dry-run]` (ZMQ PUB bind on 4224). |
| Time to first result | Estimate: 20-40 min to see simulated drones in ATAK with no RF hardware (simulator => DragonSync => multicast). Several hours off-kit to get real detections: you must supply and set up a sniffer that publishes the 4224 JSON. Assumes ATAK/WinTAK on the same LAN with multicast working. |
| License | Apache-2.0 (GitHub metadata and `LICENSE`, "Copyright 2025-2026 CEMAXECUTER LLC"). See Gotchas: the default sensor binaries are not Apache. |

## Minimal usage
No-hardware loop from the repo test tools. Not run.

```bash
git clone --recurse-submodules https://github.com/alphafox02/DragonSync && cd DragonSync
pip3 install -r requirements.txt
# terminal 1: publish an animated Boston-area scenario on ZMQ 4224
python3 tests/test_drone_generator.py -s tests/scenario_4236_-7106.json -m simulate --loop
# terminal 2: subscribe and send CoT to ATAK multicast (no status feed)
python3 dragonsync.py -c config.ini --zmq-status-port 0 --enable-multicast -d
```
`--zmq-status-port 0` skips the status socket (`if zmq_status_port:` in `zmq_to_cot`); without it there is no kit marker or kit GPS. To get one, also run `wardragon_monitor.py` with a `gps.ini` (`use_static_gps = true`) when no gpsd fix is available. For a TAK server: `--tak-host <ip> --tak-port 8087 --tak-protocol TCP` (port per your server).

## Wiring it into a nav stack
- Sensor side: WarDragon kit, or your own sniffer that publishes the same JSON on 4224. Open options in the index: [alphafox02/DroneID](https://github.com/alphafox02/DroneID) (GPL-3.0, `zmq_decoder.py`, the older open path; not indexed), [opendroneid-core-c](../../catalog/repos/opendroneid__opendroneid-core-c.md) for decoding, [RID ESP32 receiver](../../catalog/repos/peterjburke__rid.md), [drone-mesh-mapper](../../catalog/repos/colonelpanichacks__drone-mesh-mapper.md). DJI DroneID from SDR: [DroneSecurity](../../catalog/repos/rub-syssec__dronesecurity.md), [samples2djidroneid](../../catalog/repos/anarkiwi__samples2djidroneid.md).
- Picture side: CoT => [OpenTAKServer](./brian7704__opentakserver.md) / [GoATAK](./kdudkov__goatak.md) / ATAK multicast, next to [ADSBCOT](./snstac__adsbcot.md) aircraft and [KrakenSDR DoA](./krakenrf__krakensdr_doa.md) bearings. Add a DF bearing on a non-RID emitter and RID tracks side by side to show cooperative vs non-cooperative detection.
- Fusion: MQTT per-drone JSON is the easiest tap for a tracker ([Stone Soup](./dstl__stone-soup.md)) without parsing CoT.
- Catalog: [DragonSync page](../../catalog/repos/alphafox02__dragonsync.md).

## Gotchas
- Licensing trap: DragonSync is Apache-2.0, but the default 4224 producer `droneid-go` is a closed binary under the "CEMAXECUTER LLC SOFTWARE LICENSE" (personal/non-commercial, no redistribution, no reverse engineering; GitHub shows `NOASSERTION`), and `antsdr_dji_droneid` has no license file (all rights reserved by default). The README also notes WarDragon Pro/Elite capabilities that are not covered by this repo's license. For anything beyond a hackathon demo, plan your own open sniffer.
- Not standalone: no ZMQ producer => no drones. Off-kit you need a WiFi adapter in monitor mode and/or a BLE sniffer (Sniffle-capable dongle) or an ANTSDR E200 for DJI, plus the matching software.
- `test_drone_generator.py` defaults to `test_scenarios.json`, which is not in the repo; pass `-s tests/scenario_4236_-7106.json` (only `animated_tracks`, so use `-m simulate`). It binds PUB on 4224; `tests/run_test_scenario.sh` stops `zmq-decoder.service` first, so stop the real decoder on a kit before simulating.
- Shipped `config.ini` defaults: `api_enabled = true` on `0.0.0.0:8088` and `tak_tls_skip_verify = true`. Port 8088 is also a common TAK server TCP CoT port; move one of them if both run on one host. Turn verification on for real TLS.
- Multicast needs IGMP-friendly networks; README troubleshooting points at Wireshark `udp.port==6969`. Older RC2 `.p12` files fail under OpenSSL 3; convert to PEM.
- UA type comes from the drone's RID broadcast; a misconfigured transmitter shows the wrong icon (README).
- Remote ID carries operator/pilot location; treat logs and MQTT history as personal data.
- Open #40: GPS fix always false despite valid coordinates. Open #37 asks about range/coverage; not stated in the repo.

## Alternatives
- [OpenDroneID Android receiver](./opendroneid__receiver-android.md) for a phone-only RID receiver with its own map, no TAK output.
- [drone-mesh-mapper](../../catalog/repos/colonelpanichacks__drone-mesh-mapper.md) for cheap ESP32 WiFi RID sensors relayed over Meshtastic.
- Build your own: an open RID decoder plus [PyTAK](./snstac__pytak.md) `gen_cot` is about the same amount of code as wiring DragonSync to a non-WarDragon sensor.

Sources: `README.md`, `LICENSE`, `.gitmodules`, `requirements.txt`, `config.ini`, `dragonsync.py` (`zmq_to_cot`, argparse), `core/telemetry_parser.py`, `utils/cot_builder.py`, `tests/test_drone_generator.py`, `tests/run_test_scenario.sh`, `tests/scenario_4236_-7106.json`, `ingest/aircraft.py`; repo metadata for alphafox02/DragonSync, alphafox02/droneid-go (+ `LICENSE`), alphafox02/antsdr_dji_droneid, alphafox02/DroneID, jlrjr/faa-rid-lookup; issue search (#37, #40).
