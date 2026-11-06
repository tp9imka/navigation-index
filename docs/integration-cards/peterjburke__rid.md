# RID (PeterJBurke) - integration card
<!-- about: repo:peterjburke/rid -->
One-line: minimal PlatformIO firmware that turns a TTGO ESP32 board into a passive Remote ID receiver - BLE scan for ASTM F3411 broadcasts, decode with opendroneid-core-c, print one JSON line per drone over USB serial. A starting point to fork, not a finished product. Receive/decode only.

| | |
|---|---|
| Install | No release. Clone, open in VS Code + PlatformIO, build and flash env `ttgo-lora32-v1` (`platform = espressif32`, `framework = arduino`, `lib_deps = bodmer/TFT_eSPI@^2.4.79`, TFT setup `Setup25_TTGO_T_Display.h` via `build_flags`). `pio run -e ttgo-lora32-v1 -t upload` then `pio device monitor -b 115200`. |
| Runs on | Classic ESP32 (README hardware: HiLetgo ESP32 1.14 in LCD WiFi Kit, TTGO T-Display style). Code has `#error` unless `ARDUINO_ARCH_ESP32`. BLE 4 legacy advertising only (ESP32 classic has no BT5 Coded PHY). |
| Inputs | Over the air: BLE advertisements with service data UUID 0xFFFA and app code 0x0D (byte check in `MyAdvertisedDeviceCallbacks::onResult`). Wi-Fi NAN/Beacon and French ID parsing exist in code behind `#define WIFI_SCAN 0` (off). |
| Outputs | Serial at 115200: JSON lines `{ "index", "runtime", "mac", "id", "uav latitude", "uav longitude", "alitude msl", "height agl", "base latitude", "base longitude", "speed", "heading" }` (keys verbatim from `print_json`); optional TFT display of tracks (`TFT_DISPLAY 1`), optional SD log (`SD_LOGGER 0`). Up to `MAX_UAVS` 8 tracked by MAC. |
| Key API / entry points | `src/main.cpp`: compile-time switches `WIFI_SCAN`, `BLE_SCAN`, `TFT_DISPLAY`, `SD_LOGGER`, `DUMP_ODID_FRAME`, `MAX_UAVS`; `MyAdvertisedDeviceCallbacks::onResult(BLEAdvertisedDevice)` (BLE decode via `decodeBasicIDMessage`, `decodeLocationMessage`, `decodeSystemMessage`, `decodeOperatorIDMessage`); `callback(void*, wifi_promiscuous_pkt_type_t)` (Wi-Fi path); `print_json(int index, int secs, struct id_data*)`. Vendored `src/opendroneid.c/.h`, `src/odid_wifi.h`. |
| Time to first result | Estimate: 30-60 min to JSON on the serial monitor, assuming the exact TTGO board, PlatformIO installed, and a BT4-legacy Remote ID transmitter nearby (e.g. an [ArduRemoteID](./ardupilot__arduremoteid.md) board or a compliant consumer drone). |
| License | MIT (LICENSE, Peter Burke 2022; `main.cpp` header MIT, Steve Jack 2020-2021; vendored opendroneid files Apache-2.0). |

## Minimal usage

Not run. Flash and read detections from a laptop:

```bash
git clone https://github.com/PeterJBurke/RID && cd RID
pio run -e ttgo-lora32-v1 -t upload
pio device monitor -b 115200
```

Pipe detections onward (Python, needs `pyserial`):

```python
import json, serial
for line in serial.Serial("/dev/ttyUSB0", 115200, timeout=2):
    line = line.decode(errors="ignore").strip()
    if line.startswith('{ "index"'):
        d = json.loads(line)
        print(d["mac"], d["uav latitude"], d["uav longitude"], d["alitude msl"])
```

## Wiring it into a nav stack

- Defensive sensor node: ESP32 => USB serial JSON => small bridge => map/TAK. Convert each line to CoT with [PyTAK](./snstac__pytak.md) or [node-cot](./dfpc-coe__node-cot.md), or feed GeoJSON to a [MapLibre](./maplibre__maplibre-gl-js.md) view.
- Multiple nodes for coverage: tag each line with the receiving node position and a host timestamp (RSSI is tracked in `id_data` but not printed); drone-mesh-mapper ([card](./colonelpanichacks__drone-mesh-mapper.md)) already solves the multi-node relay over Meshtastic.
- Cooperative tracks into a tracker such as [Stone Soup](./dstl__stone-soup.md) alongside non-cooperative detections; see [counter-uas](../../catalog/concepts/counter-uas.md).
- The decode logic is the [opendroneid-core-c](./opendroneid__opendroneid-core-c.md) library; for a Linux receiver use that directly.

Catalog page: [catalog/repos/peterjburke__rid.md](../../catalog/repos/peterjburke__rid.md). Concepts: [counter-uas](../../catalog/concepts/counter-uas.md), [situational-awareness](../../catalog/concepts/situational-awareness.md).

## Gotchas

- Unmaintained since 2024-03-31; last commits say "tft still buggy" and "should work on tft display (need to test still)". Open #4 (2026-05): display shows only the banner, serial prints nothing, no DJI Air 3 Remote ID received.
- BLE 4 legacy only. Many drones (DJI included) broadcast Remote ID over Wi-Fi Beacon/NAN or BT5 long range; an ESP32 classic on BLE will miss them. The original sxjack header notes "Added BLE scan. Doesn't work very well."
- Turning `WIFI_SCAN` on fails to link: `wifi.c` from opendroneid-core-c is not vendored, so `odid_message_process_pack` and `odid_wifi_receive_message_pack_nan_action_frame` are undefined (#2, closed without a code fix in the tree). Copy `wifi.c` from upstream.
- Vendored `opendroneid.c` predates the 2026 upstream hardening (truncated NAN frame OOB read #106, pack-count overflow #107 in opendroneid-core-c). Update it before exposing the receiver to arbitrary traffic.
- The JSON `"id"` field is the Operator ID (`op_id`), not the UAS serial; the Basic ID is decoded but not printed. Key `"alitude msl"` is misspelled; altitude, speed and heading are truncated to `int`.
- `esp_event_loop.h` / `tcpip_adapter_init()` are deprecated ESP-IDF APIs; newer `espressif32` platform versions may not compile without pinning an older platform (not verified).

## Alternatives

- [colonelpanichacks/drone-mesh-mapper](./colonelpanichacks__drone-mesh-mapper.md) - BLE + Wi-Fi on ESP32-S3/C3/C5, mesh relay and a web map; prefer for anything beyond a bench demo.
- [opendroneid/receiver-android](./opendroneid__receiver-android.md) - phone receiver with all four transports (hardware permitting).
- [sxjack/uav_electronic_ids](../../catalog/repos/sxjack__uav_electronic_ids.md) - the upstream this is forked from; more complete receive code and transmit examples.

Sources: `gh api repos/PeterJBurke/RID` (MIT, last push 2024-03-31), README.md, LICENSE, platformio.ini, src/main.cpp (switches, BLE callback, `print_json`, setup), src/ listing, commits 2024-03-31, issues #2, #3, #4; upstream opendroneid-core-c issues #106, #107.
