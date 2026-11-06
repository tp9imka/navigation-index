# OpenDroneID receiver-android - integration card
<!-- about: repo:opendroneid/receiver-android -->
One-line: Android app (Java) that receives ASTM F3411 / ASD-STAN Remote ID over Bluetooth legacy and long range, WiFi NAN and WiFi Beacon, shows drone and operator positions on a map and logs everything to CSV; the cheapest Remote ID detector for a C-UAS awareness demo.

| | |
|---|---|
| Install | Play Store (OSM build `org.opendroneid.android_osm`) or build: open the `Android/` folder in Android Studio, Build => Make Project. Default map is OpenStreetMap (no key); Google Maps needs `org.gradle.project.map=google_map` in `gradle.properties` and your key in `Android/app/src/main/res/values/google_maps_api.xml`. |
| Runs on | Android, `minSdkVersion 23` (Android 6), `targetSdk`/`compileSdk` 37 (`Android/app/build.gradle`). Reception per transport depends heavily on the handset (see `supported-smartphones.md`). |
| Inputs | Over-the-air Remote ID: BLE advertisements with 16-bit service UUID 0xFFFA (ASTM Remote ID, app code 0x0D), BT5 Coded PHY long range + extended advertising, WiFi NAN, WiFi Beacon. |
| Outputs | Map with drone (red) and operator/take-off (blue) markers and flight trail; detail views of Basic ID, Location, Self ID, System, Operator ID, Authentication messages; CSV log via `LogWriter` (header plus per-message CSV columns from `OpenDroneIdParser`). |
| Key API / entry points | Under `Android/app/src/main/java/org/opendroneid/android/`: `bluetooth/BluetoothScanner.java`, `bluetooth/WiFiNaNScanner.java`, `bluetooth/WiFiBeaconScanner.java` (scanners); `bluetooth/OpenDroneIdParser.java` (message decoding, `csvHeader()` / `toCsvString()` per message type); `bluetooth/OpenDroneIdDataManager.java`, `data/AircraftObject.java`; `log/LogWriter.java`. |
| Time to first result | Estimate: 10 min with the Play Store build next to a broadcasting drone or an [ArduRemoteID](./ardupilot__arduremoteid.md) dev board; 1-2 h to build from source in Android Studio. |
| License | Apache-2.0. |

## Minimal usage
Not run.

1. Install the OSM build or build `Android/` in Android Studio.
2. Grant location and nearby-devices permissions; check the settings screen, which lists the transports the handset claims to support.
3. Power an ArduRemoteID board fed with test OpenDroneID messages; the transmitter should appear in the list and on the map.
4. Pull the CSV log off the phone and feed it to your tracker.

## Wiring it into a nav stack
- Extend the app (or post-process its CSV) to emit CoT via [PyTAK](./snstac__pytak.md) to [OpenTAKServer](./brian7704__opentakserver.md) / [GoATAK](./kdudkov__goatak.md), so detections show next to own-ship and ADS-B traffic.
- Track and associate detections over time with [Stone Soup](./dstl__stone-soup.md); cross-check reported position against an RF bearing from [KrakenSDR DoA](./krakenrf__krakensdr_doa.md) to flag implausible broadcasts.
- Decoder library shared with transmitters: [opendroneid-core-c](../../catalog/repos/opendroneid__opendroneid-core-c.md); packet inspection with the [Wireshark dissector](../../catalog/repos/opendroneid__wireshark-dissector.md).
- Catalog: [receiver-android page](../../catalog/repos/opendroneid__receiver-android.md).

## Gotchas
- README warns the user must visually verify that a received signal matches a real drone; Remote ID is self-reported and spoofable.
- Handset lottery: BT5 long range only reliably received on a few tested phones (README names Galaxy S10, Mate 20 Pro); some Snapdragon phones listen in 5 s on / 15 s off cycles; some phones set the feature flags but never receive. WiFi NAN only verified on Galaxy S10. Test your phone on day one.
- Android 8+ throttles WiFi scans; WiFi Beacon reception needs Developer Options => disable WiFi scan throttling (README).
- Open issues: #99 crash on detecting a DJI Mavic 3 Enterprise; #88 BT5 long range documentation.
- DJI's proprietary DroneID is not ASTM Remote ID; this app does not decode it (see [dji_droneid](../../catalog/repos/proto17__dji_droneid.md) for that research line).

## Alternatives
- [DragonSync](../../catalog/repos/alphafox02__dragonsync.md) / [WarDragon](../../catalog/repos/alphafox02__wardragon.md): Linux-based Remote ID and DroneID sensing that can output to TAK.
- [drone-mesh-mapper](../../catalog/repos/colonelpanichacks__drone-mesh-mapper.md): ESP32 sniffers feeding a map.

Sources: `README.md`, `Android/app/build.gradle`, repo tree (Java sources), `BluetoothScanner.java` (UUID), `LogWriter.java`, `OpenDroneIdParser.java`, issue search (#99, #88).
