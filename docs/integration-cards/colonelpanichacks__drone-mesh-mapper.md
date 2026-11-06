# Drone Mesh Mapper - integration card
<!-- about: repo:colonelpanichacks/drone-mesh-mapper -->
One-line: cheapest end-to-end passive Remote ID picture - ESP32 sniffers decode BLE + Wi-Fi broadcasts, relay over a Meshtastic LoRa mesh or USB, and a single-file Flask app plots drones, pilots, tracks and optional ADS-B on an offline-capable web map with CSV/KML/GeoJSON export. Receive/decode only.

| | |
|---|---|
| Install | Mapper: `git clone https://github.com/colonelpanichacks/drone-mesh-mapper && cd drone-mesh-mapper && pip3 install -r requirements.txt && python3 mesh-mapper.py` (deps: flask>=2.0.0, flask-socketio>=5.0.0, requests, urllib3, pyserial>=3.5; optional `pyModeS` for Beast ADS-B). Firmware: browser web flasher at `colonelpanichacks.github.io/drone-mesh-mapper/flasher/` (Chrome/Edge, three builds), prebuilt `.bin` files in `firmware/`, or PlatformIO: `cd remoteid-mesh-dualcore && pio run -t upload` (envs `seeed_xiao_esp32s3`, `seeed_xiao_esp32c6`, pioarduino platform); `node-mode-dualcore` has `-e remote` / `-e home`; `remoteid-c5-5g` for ESP32-C5. Pi helper: `RPI/install_rpi.py --branch main`. |
| Runs on | Mapper: any OS with Python 3 (README badge says 3.7+), tested target Raspberry Pi; no GPU. Detectors: Xiao ESP32-S3 (BLE + 2.4 GHz Wi-Fi, recommended), ESP32-C3 (Wi-Fi only), ESP32-C5 (5 GHz UNII-3 channels 149-165). Mesh relay: Heltec WiFi LoRa 32 V3 running Meshtastic. |
| Inputs | Over the air: ASTM F3411 BLE advertisements (UUID 0xFFFA check in firmware) and Wi-Fi NAN/Beacon on a fixed channel (6 by default). Into the mapper: newline JSON over USB serial from detectors, Meshtastic text messages via the home node, or HTTP `POST /api/detections` with keys `mac`, `rssi`, `drone_lat`, `drone_long`, `drone_altitude`, `pilot_lat`, `pilot_long`, `basic_id`. Optional ADS-B from adsb.lol / adsb.fi / airplanes.live / OpenSky / ADSBexchange or local dump1090/readsb JSON or Beast TCP 30005. Basemaps: MBTiles in `tiles/`. |
| Outputs | Web UI (Leaflet 1.9.4 + MapLibre GL 4.7.1 vendored, default port 5000) with Socket.IO events `detections`, `paths`, `serial_status`, `aliases`, `cumulative_log`, `faa_cache`, `adsb`. REST: `GET /api/detections` (current tracks), `GET /api/detections_history` (GeoJSON FeatureCollection, coordinates `[lon, lat]`), `GET /api/paths`; downloads `/download/csv`, `/download/kml`, `/download/cumulative_detections.csv`, `/download/cumulative.kml`; webhooks on detection transitions; optional FAA registry lookup. |
| Key API / entry points | `python3 mesh-mapper.py [--web-port 5000] [--headless] [--debug] [--port-interval 10] [--no-auto-start]`; `update_detection(detection)` in `mesh-mapper.py` (single ingest path for serial and HTTP); firmware JSON line format in `remoteid-mesh-dualcore/src/main.cpp`; `/tiles/<name>/<z>/<x>/<y>.<ext>` MBTiles server; `tools/cache_tiles.py` (only on branch `dev-adsb-offline-maps`, see Gotchas). |
| Time to first result | Estimate: 30 min to drones on the map with a pre-flashed Xiao ESP32-S3 on USB and a broadcasting drone nearby; half a day for the full Meshtastic multi-node setup. Offline basemap needs a pre-built or pre-cached MBTiles file. |
| License | MIT (LICENSE, 2025-2026 colonelpanichacks) for this project's code. README: started as a fork of JimZGChow/wifi-rid-to-mesh, "which publishes no license; code from it stays under its author's terms" - unclear provenance for redistribution. Vendored opendroneid files are Apache-2.0 (Intel). Basemap tiles carry their providers' terms (OSM tile policy forbids bulk download). |

## Minimal usage

Not run. Single detector on USB, no mesh:

```bash
git clone https://github.com/colonelpanichacks/drone-mesh-mapper && cd drone-mesh-mapper
python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
python3 mesh-mapper.py --web-port 5000 --debug
# flash a Xiao ESP32-S3 via the web flasher ("Standard Dualcore"), plug it in, select the port in the UI
```

Inject a detection from another sensor (any tool that can POST JSON), e.g. a Linux receiver built on [opendroneid-core-c](./opendroneid__opendroneid-core-c.md):

```bash
curl -X POST localhost:5000/api/detections -H 'Content-Type: application/json' \
  -d '{"mac":"aa:bb:cc:dd:ee:ff","rssi":-70,"drone_lat":47.3712,"drone_long":8.5421,"drone_altitude":120,"pilot_lat":47.3701,"pilot_long":8.5402,"basic_id":"TEST-SERIAL"}'
curl -s localhost:5000/api/detections_history | head -c 400
```

## Wiring it into a nav stack

- As a fusion front-end: `/api/detections_history` GeoJSON and webhooks give cooperative drone tracks to a tracker ([Stone Soup](./dstl__stone-soup.md)) or a C-UAS dashboard; compare claimed Remote ID positions with RF/radar/acoustic detections from [counter-uas](../../catalog/concepts/counter-uas.md) sensors.
- To TAK: poll `/api/detections` or take the webhook and emit CoT with [PyTAK](./snstac__pytak.md) or [node-cot](./dfpc-coe__node-cot.md); [DragonSync](./alphafox02__dragonsync.md) is an existing Remote ID => CoT gateway for WarDragon-class kits.
- ADS-B layer: point it at a local [readsb](./wiedehopf__readsb.md) (JSON or Beast 30005) for a manned-traffic overlay that works without internet.
- Offline basemaps: any raster/vector MBTiles works; [PMTiles](./protomaps__pmtiles.md) users must convert to MBTiles first (the server reads SQLite MBTiles). For a cleaner custom map UI see [MapLibre GL JS](./maplibre__maplibre-gl-js.md).
- Simpler single-board alternative: [peterjburke/RID](./peterjburke__rid.md).

Catalog page: [catalog/repos/colonelpanichacks__drone-mesh-mapper.md](../../catalog/repos/colonelpanichacks__drone-mesh-mapper.md). Concepts: [counter-uas](../../catalog/concepts/counter-uas.md), [situational-awareness](../../catalog/concepts/situational-awareness.md), [multi-agent](../../catalog/concepts/multi-agent.md).

## Gotchas

- No auth anywhere: Flask-SocketIO runs on `0.0.0.0` with `cors_allowed_origins="*"`, and `POST /api/detections`, `/api/send_command` (commands to ESP32s) and `/api/set_webhook_url` are open. Anyone on the network can inject fake drones or reconfigure nodes. Bind behind a firewall or reverse proxy on any shared network.
- README on `main` documents `tools/cache_tiles.py`, but `tools/` only exists on branch `dev-adsb-offline-maps`. The in-UI "Cache This Area" path is in `mesh-mapper.py` on `main`.
- `tiles/` is empty on a fresh clone and the eight built-in basemaps are online sources; "offline-capable" means the UI assets, not the map. Cache or import MBTiles before going offline (README calls this out).
- `RPI/install_rpi.py` downloads only `mesh-mapper.py` (`TARGET_FILE`) from raw.githubusercontent, not `static/`, so the vendored offline UI assets are not installed by that path (from reading the script, not tested). README also suggests `--branch Dev`, which does not exist (branches are `main` and `dev-adsb-offline-maps`). Prefer `git clone`.
- Wi-Fi detection listens on one fixed channel (`esp_wifi_set_channel(6, ...)`); Remote ID on other 2.4 GHz channels or 5 GHz needs the C5 build or a firmware change.
- Vendored `opendroneid.c` / `wifi.c` differ from upstream `master`; upstream fixed a truncated-NAN-frame OOB read (#106) and a pack-count overflow (#107) in 2026. Check before deploying where hostile transmitters are plausible.
- Performance table in README (latency < 500 ms, 50+ drones, 1000+ detections/min) is the author's claim; no test method given.
- Remote ID content is self-reported and unauthenticated; a drone position on this map is a claim, not a measurement.

## Alternatives

- [alphafox02/DragonSync](./alphafox02__dragonsync.md) - gateway from WarDragon-style sensors to TAK CoT; prefer when the consumer is ATAK/WinTAK rather than a browser.
- [opendroneid/receiver-android](./opendroneid__receiver-android.md) - single phone, no hardware build; prefer for a quick look.
- [peterjburke/RID](./peterjburke__rid.md) - minimal ESP32 BLE receiver with serial JSON; prefer as a small codebase to fork.

Sources: `gh api repos/colonelpanichacks/drone-mesh-mapper` (MIT, branches `main`, `dev-adsb-offline-maps`), README.md, LICENSE, requirements.txt, repo trees of `main` and `dev-adsb-offline-maps`, mesh-mapper.py on `main` (argparse flags, `update_detection`, `/api/detections` routes, `socketio.run` host, CORS, ADS-B fetchers), remoteid-mesh-dualcore/src/main.cpp and platformio.ini, RPI/install_rpi.py, wifi.c compared with opendroneid-core-c `master`, commits to 2026-11-03, PRs #1, #2, #3, #6 (no issues filed).
