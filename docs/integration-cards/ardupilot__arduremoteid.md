# ArduRemoteID - integration card
<!-- about: repo:ardupilot/arduremoteid -->
One-line: ESP32-S3/C3 firmware that turns an autopilot's MAVLink or DroneCAN OpenDroneID messages into broadcast Remote ID (WiFi Beacon, WiFi NAN, BT4 legacy, BT5 long range); with a $10 dev board it gives you a known, cooperative emitter to test a Remote ID detection pipeline end to end.

| | |
|---|---|
| Install | Prebuilt binaries on the releases page (latest release tag seen v1.14, 2023-10), flashed with Espressif Flash Tool (hold BOOT on first flash) or OTA through the module's web UI. From source (`BUILDING.md`): `sudo apt install arduino; pip install pymavlink; git clone https://github.com/ardupilot/arduremoteid; cd arduremoteid; git submodule init; git submodule update --recursive; ./scripts/install_build_env.sh; ./scripts/regen_headers.sh; ./scripts/add_libraries.sh; cd RemoteIDModule; make setup; make; make upload` (arduino-cli based `Makefile`). |
| Runs on | ESP32-S3 and ESP32-C3 dev boards, plus vendor modules (BlueMark DB110/200/201/202mav/210pro, Holybro, others in `Makefile` targets). S3 dev board pins: UART TX 18 / RX 17, CAN TX 47 / RX 38; C3: UART TX 3 / RX 2, CAN TX 5 / RX 4. MAVLink also on the USB UART for bench tests. |
| Inputs | MAVLink OpenDroneID service messages (`OPEN_DRONE_ID_*`) or DroneCAN `dronecan.remoteid.*` from ArduPilot (or any sender, e.g. a pymavlink script). Parameters via DroneCAN (all) or MAVLink (non-string only): `UAS_TYPE`, `UAS_ID_TYPE`, `UAS_ID`, `LOCK_LEVEL`, `WEBSERVER_ENABLE`, `WIFI_SSID`, `WIFI_PASSWORD`, `PUBLIC_KEY1..5`. |
| Outputs | ASTM F3411 / ASD-STAN broadcast frames over the enabled transports; optional WiFi AP + web server (default SSID `RID_<mac>`, password `ArduRemoteID`, `http://192.168.4.1`) for status and signed firmware update. |
| Key API / entry points | `RemoteIDModule/` (Arduino sketch, `board_config.h`, `Makefile` targets such as `esp32s3dev`, `esp32c3dev`); `scripts/generate_keys.py`, `scripts/sign_fw.py <ota.bin> <private_key.dat> <board_id>`, `scripts/secure_command.py` (DroneCAN/MAVLink SecureCommand). |
| Time to first result | Estimate: 30-60 min to flash a prebuilt binary onto an ESP32-S3 dev board, feed it from ArduPilot SITL or a pymavlink script over USB, and see it in the OpenDroneID Android receiver. Assumes the board, a USB cable and a phone that receives BT legacy advertising. |
| License | GPL-2.0 (GitHub metadata). |

## Minimal usage
From README / `BUILDING.md`. Not run.

```bash
# flash the ESP32-S3 dev board (prebuilt ArduRemoteID_ESP32S3_DEV.bin) with Espressif Flash Tool, then:
# feed it OpenDroneID MAVLink from ArduPilot SITL over the USB UART, or from a pymavlink script sending
# OPEN_DRONE_ID_BASIC_ID / OPEN_DRONE_ID_LOCATION / OPEN_DRONE_ID_SYSTEM at 1 Hz
```
Bench check: open the OpenDroneID receiver app on a phone next to the board; a test/demo Remote ID should appear over Bluetooth (BUILDING.md: after flashing the board emits test/demo Remote ID).

## Wiring it into a nav stack
- Transmit side: [ArduPilot](./ardupilot__ardupilot.md) has OpenDroneID support in master and recent stable (README "ArduPilot Support"); [MAVProxy](./ardupilot__mavproxy.md) has an `OpenDroneID` module to send or display the messages; [pymavlink](./ardupilot__pymavlink.md) for a scripted emitter with scripted (including deliberately inconsistent) positions.
- Receive side: [OpenDroneID receiver-android](./opendroneid__receiver-android.md), [opendroneid-core-c](../../catalog/repos/opendroneid__opendroneid-core-c.md) decoders, Linux sniffers such as [DragonSync](../../catalog/repos/alphafox02__dragonsync.md); forward detections as CoT via [PyTAK](./snstac__pytak.md) and track them with [Stone Soup](./dstl__stone-soup.md).
- C-UAS angle: cooperative Remote ID is the baseline; a demo that cross-checks broadcast position against an RF bearing ([KrakenSDR DoA](./krakenrf__krakensdr_doa.md)) shows how to flag a spoofed or inconsistent Remote ID.
- Catalog: [ArduRemoteID page](../../catalog/repos/ardupilot__arduremoteid.md).

## Gotchas
- `LOCK_LEVEL=2` burns ESP32 eFuses: firmware updates are then only possible via the signed web interface, permanently, even if `LOCK_LEVEL` is later lowered (README). Never set it on a hackathon board. `LOCK_LEVEL=1` blocks normal parameter writes; only SecureCommand works.
- If no public keys are set, the web server accepts any firmware (README); fine for a bench, not for anything fielded.
- Regulatory: transmitting Remote ID with an ID you do not own, or near real air traffic, may be illegal; keep the bench test short-range and with test IDs.
- Open issues: #35 (MAV_ODID_ARM_STATUS enum out of sync with upstream MAVLink), #133 / #138 (ID and operator ID handling when params unset).
- Last release tag is from 2023, last push 2025-07; build from `master` for newer board targets.

## Alternatives
- [transmitter-linux](../../catalog/repos/opendroneid__transmitter-linux.md): Remote ID transmitter from a Linux box with BT/WiFi.
- Any commercial broadcast module (BlueMark, Holybro) running this same firmware.

Sources: `README.md`, `BUILDING.md`, `RemoteIDModule/Makefile`, repo root listing, releases API, issue search (#35, #133, #138).
