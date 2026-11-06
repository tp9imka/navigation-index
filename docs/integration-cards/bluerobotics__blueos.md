# BlueOS - integration card
<!-- about: repo:bluerobotics/blueos -->
One-line: Docker-based onboard OS for ArduPilot vehicles (BlueROV2, BlueBoat, generic) with a web UI, selectable MAVLink router, mavlink2rest, NMEA-to-GPS_INPUT injection and an extension store - a fast way to drop a nav add-on onto a marine vehicle.

| | |
|---|---|
| Install | Pi image from release 1.4.7: `BlueOS-raspberry-linux-arm-v7-bookworm.zip`, `BlueOS-raspberry-linux-arm-v7-bullseye-pi4.zip`, `BlueOS-raspberry-linux-arm64-v8-bookworm-pi5.zip`. On an existing Pi OS (as root): `sudo su -c 'curl -fsSL https://raw.githubusercontent.com/bluerobotics/BlueOS/master/install/install.sh \| bash'` (install/README.md). Other Linux: `docker compose -f core/compose/compose.yml up` or the long `docker run --privileged --network=host --pid=host ... bluerobotics/blueos-core:master` from README. |
| Runs on | Officially Raspberry Pi 3, 4, 5 (README). Images built for armv7, arm64, amd64; amd64 "not fully supported". `install.sh` accepts only `armhf`, `armv7`, `armv7l`, `aarch64` and exits on x86_64. Board config (`install/boards/configure_board.sh`) recognises Pi 0-3 (`bcm_28xx`), Pi 4 / CM4 (`bcm_27xx`), Pi 5 (`bcm_2712`) via `/proc/device-tree/model`; anything else prints "Hardware not identified". |
| Inputs | Autopilot over USB/serial or Linux-hosted ArduPilot (Navigator HAT; `--skip-board-config` skips it). NMEA 0183 GGA/RMC/GLL/GNS sentences over UDP/TCP into `nmea_injector`. Cameras (mavlink-camera-manager). Extensions as Docker images. |
| Outputs | Web UI on port 80. MAVLink endpoints managed by `ardupilot_manager` (router choice: MAVLinkRouter, MAVP2P or MAVProxy). mavlink2rest REST/WebSocket on `:6040`. NMEA positions converted to MAVLink `GPS_INPUT` (component id set per socket; 220 / 221 are the usual GPS ids). Video via RTSP/WebRTC. |
| Key API / entry points | `install/install.sh` (env `VERSION`, `REMOTE`, `GITHUB_REPOSITORY`; flags `--skip-board-config`, `--ci-run`). Images `bluerobotics/blueos-bootstrap:$VERSION`, `bluerobotics/blueos-core:$VERSION`. Services under `core/services/`: `ardupilot_manager` (`mavlink_proxy/Manager.py`, `set_preferred_router`), `nmea_injector` (REST on 2748: `GET/POST/DELETE /v1.0/socks` with `{kind, port, component_id}`; CLI `-u`/`-t` ports), `beacon` (mDNS), `cable_guy` (network), `kraken` (extensions), `versionchooser`. Service table in `core/start-blueos-core`. |
| Time to first result | Estimate: 30-45 min from flashing an image to the dashboard showing a connected autopilot. Assumes a Pi 4/5, an SD card and an ArduPilot board on USB. Several hours if you go the generic Docker route on non-Pi hardware. |
| License | Dual: `SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-BlueOS-Custom` (LICENSE.md; repo also has LICENSE-agplv3.md). The prose line in LICENSE.md says "GPLv3" while the SPDX tag says AGPL-3.0-only; GitHub metadata reports NOASSERTION. Treat as AGPL unless you hold the custom licence. |

## Minimal usage
Not run. Inject your own nav solution as a GNSS fix into ArduPilot through BlueOS.

```sh
# on the vehicle, after flashing the image; open http://blueos.local (or the Pi IP)
# nmea_injector: open a UDP listener (port 1024-65535, component id 26-249; 220/221 usual for GPS)
curl -X POST http://blueos.local:2748/v1.0/socks -H 'Content-Type: application/json' \
  -d '{"kind": "UDP", "port": 27000, "component_id": 220}'
# from the nav computer, send a GGA sentence at the fix rate:
python3 - <<'EOF'
import socket, functools, operator, time
def nmea(body): return f"${body}*{functools.reduce(operator.xor, map(ord, body)):02X}\r\n"
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
while True:
    s.sendto(nmea("GPGGA,120000.00,5925.000,N,01045.000,E,1,10,0.9,5.0,M,0.0,M,,").encode(), ("blueos.local", 27000))
    time.sleep(0.2)
EOF
```

ArduPilot must have a GPS type that accepts MAVLink input (GPS_TYPE = MAV) for `GPS_INPUT` to be used; check the ArduPilot docs for your firmware.

## Wiring it into a nav stack
- Estimator => GNSS substitute: a visual / terrain / dead-reckoning solution emitted as NMEA into `nmea_injector`, which becomes `GPS_INPUT` via mavlink2rest. Cheapest path when the nav code is not MAVLink-aware; for richer inputs (`VISION_POSITION_ESTIMATE`, `ODOMETRY`) talk MAVLink directly through a router endpoint or mavlink2rest on `:6040`.
- Router: pick [mavp2p](./bluenviron__mavp2p.md), mavlink-router or [MAVProxy](./ardupilot__mavproxy.md) in the UI; add a UDP endpoint for your process.
- Package the nav add-on as a BlueOS extension (a Docker image with BlueOS labels) so it installs from the UI on every vehicle.
- Vehicles: ArduSub (BlueROV2), ArduRover boats (BlueBoat), generic [ArduPilot](./ardupilot__ardupilot.md) / [PX4](./px4__px4-autopilot.md). Chart view on the boat side: [OpenCPN](./opencpn__opencpn.md) fed with NMEA.
- Concepts: [mavlink-gcs](../../catalog/concepts/mavlink-gcs.md), [underwater-nav](../../catalog/concepts/underwater-nav.md), [maritime-nav](../../catalog/concepts/maritime-nav.md), [autopilot](../../catalog/concepts/autopilot.md). Catalog page: [catalog/repos/bluerobotics__blueos.md](../../catalog/repos/bluerobotics__blueos.md).

## Gotchas
- `install.sh` defaults `VERSION=master`: the same value selects the raw GitHub files and the Docker tags (`blueos-core:$VERSION`), so a plain run installs the bleeding-edge master build. Set `VERSION` to a release tag to pin (not checked that every tag has matching images). Prefer the release Pi image for a demo.
- The container is `--privileged`, host network, host PID, with `/dev`, `/sys` and `docker.sock` mounted. It reconfigures Wi-Fi and Ethernet unless `BLUEOS_DISABLE_SERVICES` is set. Do not run it on your laptop's main OS; use a dedicated Pi or VM.
- Docker compose mode is not equal to a standard install: MDNS may not work, `cable_guy`, `wifi`, `commander` disabled (README known issues).
- Non-Pi hardware: Ubuntu 64-bit support is open (#1072); x86_64 (#2179, closed) and running as a virtual Pi (#1629) are community notes. Compute Modules skip host setup (#4234, open). Bullseye images do not boot on CM4 (#4490, open).
- Installer fetches many files from GitHub at install time; 503s break it (#3688, open). It also fails if `/etc/resolv.conf.host` already exists (#2665, open). Offline field installs: use the image.
- Bookworm networking oddities tracked in #2924 / #3019 / #3135 (open).
- Extension store can come up empty without internet (#1695, #3429, #4599 open).
- Licensing: AGPL-3.0 covers network use; a modified BlueOS reachable over the network implies a source offer.

## Alternatives
- [Rpanion-server](./stephendade__rpanion-server.md) - lighter Node.js companion manager, GPL-3.0, good for air vehicles and Jetson; no extension store.
- [mavp2p](./bluenviron__mavp2p.md) / [mavlink-router](./mavlink-router__mavlink-router.md) on a plain Linux image - when you only need routing and want full control of the OS.
- [MOOS-IvP](./moos-ivp__moos-ivp.md) - not a companion manager, but the usual autonomy layer on marine vehicles if you need behaviours rather than plumbing.

Sources: `gh api repos/bluerobotics/BlueOS` (NOASSERTION, release 1.4.7 2026-10-16 and its assets), README.md, LICENSE.md, install/README.md, install/install.sh (VERSION default, arch list, image names), install/boards/configure_board.sh, core/start-blueos-core (mavlink2rest :6040, service list), core/services/nmea_injector/{README.md,main.py,nmea_injector/TrafficController.py}, core/services/ardupilot_manager/mavlink_proxy/Manager.py, issues #1072, #1629, #1695, #2179, #2665, #2924, #3019, #3135, #3429, #3688, #4234, #4490, #4492, #4599.
