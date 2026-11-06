# opendroneid-core-c - integration card
<!-- about: repo:opendroneid/opendroneid-core-c -->
One-line: the reference C codec for broadcast Remote ID (ASTM F3411 / ASD-STAN EN 4709-002) - feed it the 25-byte messages or message packs your BLE/Wi-Fi sniffer captured and get drone ID, position, speed, altitude and operator location as C structs for an airspace picture. This card covers the receive/decode side only.

| | |
|---|---|
| Install | Build from source (no package manager release; last tag v2.0 is 2022-04-06, fixes since are on `master` only): `sudo apt-get install libgps-dev libnl-genl-3-dev libgtest-dev cmake`, `git submodule update --init`, `mkdir build && cd build && cmake .. && make -j`. Options: `-DBUILD_WIFI=off` (drops the libgps/libnl NaN sender), `-DBUILD_MAVLINK=off`, `-DBUILD_CN=off`, `-DBUILD_TESTS=off`, `-DODID_AUTH_MAX_PAGES=1` for small MCUs. On ESP32/Arduino, copy `libopendroneid/opendroneid.c/.h` (and `wifi.c`/`odid_wifi.h` if you need Wi-Fi frame parsing) into the project. |
| Runs on | Any C99 target: Linux x86/ARM (Raspberry Pi), ESP32, other MCUs. The library itself does no radio I/O - you supply a BLE scanner (BlueZ, ESP-IDF NimBLE) or a monitor-mode Wi-Fi capture. |
| Inputs | Raw bytes: single 25-byte ODID messages (`ODID_MESSAGE_SIZE`) from BLE service data (16-bit UUID 0xFFFA, app code 0x0D, per receiver-android), message packs, or whole Wi-Fi NAN action frames / beacon vendor IEs. Protocol versions 0 (F3411-19), 1 (EN 4709-002 P1) and 2 (F3411-22a). China GB 46750-2025 (separate, incompatible wire format) in `libopendroneidcn/`. |
| Outputs | `ODID_UAS_Data` with `BasicID[]` (UAS ID, ID type, UA type), `Location` (Latitude/Longitude deg, AltitudeBaro and AltitudeGeo m WGS84 HAE, Height m with `HeightType`, Direction deg true, SpeedHorizontal/SpeedVertical m/s, accuracy enums, TimeStamp s after the hour), `System` (OperatorLatitude/Longitude, area, classification), `OperatorID`, `SelfID`, `Auth[]`, plus `*Valid` flags. Sentinels mark unknown values (lat/lon 0, altitude -1000 m, direction 361, speed 255). `drone_export_gps_data()` writes a JSON string. |
| Key API / entry points | `void odid_initUasData(ODID_UAS_Data *data)`; `ODID_messagetype_t decodeMessageType(uint8_t byte)`; `ODID_messagetype_t decodeOpenDroneID(ODID_UAS_Data *uas_data, const uint8_t *msg_data)` (one 25-byte message, any type); `int decodeMessagePack(ODID_UAS_Data *uasData, const ODID_MessagePack_encoded *pack)`; `int odid_message_process_pack(ODID_UAS_Data *UAS_Data, const uint8_t *pack, size_t buflen)`; `int odid_wifi_receive_message_pack_nan_action_frame(ODID_UAS_Data *UAS_Data, char *mac, const uint8_t *buf, size_t buf_size)`; `decodeHorizontalAccuracy()` / `decodeVerticalAccuracy()` / `decodeSpeedAccuracy()` (enum => metres); `void drone_export_gps_data(const ODID_UAS_Data*, char *buf, size_t buf_size)`. MAVLink bridge in `libmav2odid/mav2odid.c`. Test binary `test/odidtest`. |
| Time to first result | Estimate: 15 min to build and run `test/odidtest` (encode/decode self-test); 2-4 h to a working Linux BLE receiver that decodes live broadcasts, assuming BlueZ HCI scanning code of your own and a Remote ID transmitter in range. |
| License | Apache-2.0 (LICENSE file). |

## Minimal usage

Not run. Decode one BLE Remote ID advertisement whose service data you already extracted (layout `0x0D`, 1-byte counter, 25-byte message - per ASTM F3411 legacy advertising; check against your scanner's output). Signatures from `libopendroneid/opendroneid.h`.

```c
#include <stdio.h>
#include "opendroneid.h"

void on_ble_service_data(const uint8_t *sd, size_t len) {   /* sd starts after UUID 0xFFFA */
    if (len < 2 + ODID_MESSAGE_SIZE || sd[0] != 0x0D) return;
    static ODID_UAS_Data uas;                 /* keep one per transmitter MAC in a real receiver */
    ODID_messagetype_t t = decodeOpenDroneID(&uas, sd + 2);
    if (t == ODID_MESSAGETYPE_LOCATION && uas.LocationValid)
        printf("lat %.7f lon %.7f altGeo %.1f m spd %.1f m/s dir %.0f\n",
               uas.Location.Latitude, uas.Location.Longitude, uas.Location.AltitudeGeo,
               uas.Location.SpeedHorizontal, uas.Location.Direction);
    if (t == ODID_MESSAGETYPE_BASIC_ID && uas.BasicIDValid[0])
        printf("id %s\n", uas.BasicID[0].UASID);
}
```

Call `odid_initUasData(&uas)` once per new transmitter before the first decode.

## Wiring it into a nav stack

- Defensive airspace picture: sniffer (ESP32, Pi BLE + monitor-mode Wi-Fi) => this decoder => per-MAC track table => JSON/MQTT => map or TAK. Ready-made receivers built on it or the same spec: [peterjburke/RID](./peterjburke__rid.md) (ESP32 BLE => serial JSON), [drone-mesh-mapper](./colonelpanichacks__drone-mesh-mapper.md) (ESP32 + Meshtastic + Flask map), [opendroneid receiver-android](./opendroneid__receiver-android.md), [DragonSync](./alphafox02__dragonsync.md) (detections => CoT for TAK).
- To TAK: map `Location` to a CoT event (`point lat/lon/hae`, `track course/speed`) with [node-cot](./dfpc-coe__node-cot.md) or [PyTAK](./snstac__pytak.md); operator position from `System` as a second marker.
- Into a tracker: treat decoded positions as cooperative self-reports and fuse them with radar/RF/acoustic detections in [Stone Soup](./dstl__stone-soup.md); a mismatch between Remote ID claims and sensed position is itself a spoofing indicator.
- Own-ship side: [ArduRemoteID](./ardupilot__arduremoteid.md) transmits from MAVLink `OPEN_DRONE_ID_*` messages; `libmav2odid` converts those MAVLink messages to/from the same structs, so a GCS can log what its own aircraft broadcasts.
- Packet-level debugging: [wireshark-dissector](../../catalog/repos/opendroneid__wireshark-dissector.md).

Catalog page: [catalog/repos/opendroneid__opendroneid-core-c.md](../../catalog/repos/opendroneid__opendroneid-core-c.md). Concepts: [counter-uas](../../catalog/concepts/counter-uas.md), [situational-awareness](../../catalog/concepts/situational-awareness.md), [standards](../../catalog/concepts/standards.md).

## Gotchas

- Treat every received frame as hostile input (the decoder does no range checks, see Verified in this hub). Fixed on `master` in 2026: out-of-bounds read on a truncated Wi-Fi NAN frame that crashed receivers (#106) and a stack buffer overflow from an out-of-range message-pack count via MAVLink (#107). The v2.0 tag (2022) predates both; build from current `master`.
- `drone_export_gps_data()` produced invalid JSON (trailing commas, missing comma, #109); fixed by commit 2026-08-27 "Fix faulty json output from wifi.c". Older copies vendored into other projects may still have it.
- `install(TARGETS ...)` installs only `libopendroneid.so`; headers are not installed. Point your include path at `libopendroneid/`.
- Default build flags are `-O0` with fortify/stack protector (top-level CMakeLists.txt) - fine for a receiver, set your own for embedded.
- Remote ID is unauthenticated in practice (Auth messages optional, #113 discusses a post-quantum profile). Positions are claims by the transmitter, not measurements; spoofed Remote ID is trivial with the transmitter examples.
- Many drones transmit only some methods (BT4 legacy, BT5 long range, Wi-Fi NaN, Wi-Fi Beacon); iOS and many Android phones cannot receive BT5 LR or NaN (README). Plan receiver hardware for all four.
- China GB 46750-2025 drones use a different wire format (`libopendroneidcn`), not decodable by the ASTM functions.
- Message pack with multiple messages of one type is an open question (#101).

## Verified in this hub
Measured by hub samples that ran this code on 2026-11-06, unless a bullet says otherwise. The linked sample README holds the commands and raw output.

- A stdlib Python decoder was checked field by field against core-c (500 core-c-encoded vectors, 500 random raw messages, 81 payloads from the wireshark-dissector captures); five planted decoder bugs each failed the suite. Things found in core-c while mirroring it (not fixed upstream by the hub) - [remote-id-to-tak](../../samples/remote-id-to-tak/README.md):
  - `decodeHorizontalAccuracy(ODID_HOR_ACC_4NM)` returns 7808 m; 4 NM (and the enum comment) is 7408 m.
  - `decodeBasicIDMessage` copies 21 bytes (`sizeof(UASID)`) from a 20-byte UUID/session-ID field; the C string is not NUL-terminated if the reserved byte is nonzero.
  - `decodeOpenDroneID` on a pack trusts the buffer to hold `MsgPackSize` messages (only `odid_message_process_pack` checks length).
  - No range checks on decode: corrupted BT5 frames without the sniffer CRC check decoded to lat -89.8, lon -214.6.
  - `TimeStamp` must be decoded in float32 to match core-c bit for bit.

## Alternatives

- [opendroneid/receiver-android](./opendroneid__receiver-android.md) - full phone receiver app (Java decoding of the same spec); prefer when a phone is enough.
- [sxjack/uav_electronic_ids](../../catalog/repos/sxjack__uav_electronic_ids.md) - Arduino classes including ESP32 receive code; prefer for quick ESP32 prototypes.
- [opendroneid/wireshark-dissector](../../catalog/repos/opendroneid__wireshark-dissector.md) - decode captures on a laptop without writing C.

Sources: `gh api repos/opendroneid/opendroneid-core-c` (Apache-2.0, tags v1.0/v2.0), README.md, LICENSE, CMakeLists.txt and libopendroneid/CMakeLists.txt, libopendroneid/opendroneid.h (structs, sentinels, function signatures), repo listing of wifi/ and libopendroneidcn/, commits to 2026-10-07, opendroneid/receiver-android BluetoothScanner.java (UUID 0xFFFA, app code 0x0D), issues #106, #107, #109, #113, #101.
