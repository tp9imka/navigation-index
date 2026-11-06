# Rpanion-server - integration card
<!-- about: repo:stephendade/rpanion-server -->
One-line: browser-configured companion computer for ArduPilot/PX4 - MAVLink routing (mavlink-router), RTSP video, NTRIP-to-autopilot RTK injection, logging and Wi-Fi AP - so a Pi or Jetson is useful in an hour.

| | |
|---|---|
| Install | Easiest: flash `rpanion-Server-1.0.0-Rpi5-RasPiOS.img.xz` from GitHub release v1.0.0 (Wi-Fi hotspot preconfigured). Existing OS: apt prerequisites from README (gstreamer, network-manager, dnsmasq, python3-venv, gpsbabel, ppp, ...), Node.js 24 from nodesource, then `wget https://github.com/stephendade/Rpanion-server/releases/download/v1.0.0/rpanion-server_1.0.0_arm64.deb && sudo dpkg -i rpanion-server_1.0.0_arm64.deb` (an `_amd64.deb` is also in the release). Master is `1.1.0-dev` (package.json). |
| Runs on | README table: Raspberry Pi 3B or later (RasPiOS, Ubuntu 22.04), Nvidia Jetson Orin (Ubuntu 22.04), Orange Pi Zero 3 (Ubuntu 24.04), Libre Computer Le Potato (RasPiOS). x86 deploy script in `deploy/`. Pi Zero W and Pi 2 dropped since 0.10.0. |
| Inputs | Flight controller over UART (choice of baud, MAVLink 1/2) or UDP input; NTRIP caster (RTCM3); USB/CSI cameras; network config from the UI. |
| Outputs | Web UI on port 3001. mavlink-router endpoints: UDP server `0.0.0.0:14550` (on by default, setting `flightcontroller.UDPBPort`), optional TCP server 5760, any number of user-added UDP client outputs. RTCM forwarded to the FC as `GPS_RTCM_DATA`. RTSP video. tlog/bin logs, KMZ conversion (`python/tlog2kmz.py`). |
| Key API / entry points | systemd service from the .deb; web UI pages (Flight Controller, Video, NTRIP, Network, Logging, User Management). Code: `server/flightController.js` (builds the `mavlink-routerd` command line), `server/ntrip.js` (NTRIP client, emits `rtcmpacket`), `mavlink/mavManager.js` (wraps RTCM in `GpsRtcmData`), `python/dflogger.py --connection <conn> --logdir <dir>`. Dev: `npm run dev` (ports 3000/3001). Packaging: `npm run build && npm run package`. |
| Time to first result | Estimate: 30-60 min from flashing the image to QGC receiving telemetry over the Pi's Wi-Fi AP. Assumes a Pi 5 (only Pi image in v1.0.0), an FC on a Pi UART or USB, and the default UDP 14550 output. |
| License | GPL-3.0 (LICENSE is the GPLv3 text). |

## Minimal usage
Not run. From the README; device names depend on board.

```sh
# on the companion, after dpkg -i
sudo apt remove modemmanager          # Rpanion refuses to start the FC link while it is installed
# browse to http://<device_ip>:3001, log in admin / admin, change the password
# Flight Controller page: pick /dev/serial0 (or /dev/ttyACM0), baud matching the FC port (UI offers 9600-1500000), MAVLink 2, Start
# Add UDP output 192.168.1.50:14560 for your nav process; GCS connects to UDP 14550
```

NTRIP page: host, port (default 2101), mountpoint, username/password, optional TLS (`server/ntrip.js`); corrections are then pushed to the autopilot without a GCS in the loop.

## Wiring it into a nav stack
- Routing core is [mavlink-router](./mavlink-router__mavlink-router.md): `-e 127.0.0.1:14540` (Rpanion's own MAVLink manager, rejected as a user output) and `-e 127.0.0.1:14541` are always added, then user outputs, then the serial device (`server/flightController.js`). Point an onboard estimator ([pymavlink](./ardupilot__pymavlink.md), [MAVSDK-Python](./mavlink__mavsdk-python.md), [MAVROS](./mavlink__mavros.md)) at a UDP output you add in the UI.
- RTK for the autopilot GNSS: NTRIP => Rpanion => `GPS_RTCM_DATA` => ArduPilot/PX4. For a base station you run yourself, see [pygnssutils](./semuconsulting__pygnssutils.md) `gnssserver` or the casters in the catalog ([node-ntrip/caster](../../catalog/repos/node-ntrip__caster.md)).
- Vision-based or GNSS-denied nav on the companion: the video pipeline and [vision_to_mavros](./thien94__vision_to_mavros.md)-style pose senders coexist; budget CPU on a Pi.
- Concept: [mavlink-gcs](../../catalog/concepts/mavlink-gcs.md). Catalog page: [catalog/repos/stephendade__rpanion-server.md](../../catalog/repos/stephendade__rpanion-server.md).

## Gotchas
- Default web login `admin`/`admin`; access control does not cover MAVLink or video streams (README). `npm run dev` skips authentication entirely; never field a dev build.
- ModemManager grabs serial ports; `flightController.js` returns an error until it is removed.
- Pi UART quirks: Bluetooth must be disabled on Pi 3 for the UART (#128); Pi 3B+ UART config fixes in #215; GPIO UARTs not working on Ubuntu 24.04 and CSI cameras not working on Ubuntu 22.04/24.04 (README).
- NTRIP: before the fix in #440 (closed), GGA was never sent to NTRIP 2.0 casters, so VRS / nearest-base mountpoints returned nothing. Use a release that includes the fix, or a single-base mountpoint.
- Dev installs need the `mavlink-routerd` binary (`devExtras.sh`); #360 (closed) was a missing binary.
- Ubuntu 24 needs a pinned zlib1g downgrade to install `python3-dev` (README); "externally-managed-environment" error in #252 (closed).
- Only a Pi 5 image is attached to v1.0.0; older Pis use the deb route.
- GPL-3.0: shipping a modified build on delivered hardware carries source-offer obligations.

## Alternatives
- [BlueOS](./bluerobotics__blueos.md) - Docker-based, extension store, stronger for ArduSub/ArduRover boats; heavier and AGPL/custom licensed.
- [mavp2p](./bluenviron__mavp2p.md) or [mavlink-router](./mavlink-router__mavlink-router.md) alone - when you only need routing and want no web stack.
- [MAVProxy](./ardupilot__mavproxy.md) - scripting-friendly bench router and console.

Sources: `gh api repos/stephendade/Rpanion-server` (GPL-3.0), release v1.0.0 asset list, README.md, LICENSE, package.json, server/flightController.js (router command line, defaults, ModemManager check), server/ntrip.js, server/index.js (`rtcmpacket` handler), mavlink/mavManager.js (`GpsRtcmData`), python/dflogger.py, issues #128, #215, #252, #360, #440.
