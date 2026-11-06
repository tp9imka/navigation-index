# mavp2p - integration card
<!-- about: repo:bluenviron/mavp2p -->
One-line: single static Go binary that links any number of serial, UDP and TCP MAVLink endpoints, so the autopilot, the GCS and your nav process share one link - no Python, no build.

| | |
|---|---|
| Install | Release tarball, e.g. `mavp2p_v1.3.4_linux_arm64v8.tar.gz` (also `linux_amd64`, `linux_armv6`, `linux_armv7`, `windows_amd64.zip`) from GitHub releases, latest v1.3.4. Docker: `docker run --rm -it --network=host bluenviron/mavp2p` (README; tag not checked). No macOS asset in v1.3.4: build with Go >= 1.27, `CGO_ENABLED=0 go build .` |
| Runs on | Linux amd64/armv6/armv7/arm64 (libc-independent, works on Alpine and OpenWrt), Windows amd64. No GPU. Pi Zero class hardware is fine. |
| Inputs | MAVLink 1 and 2, any dialect, on endpoints given as positional args: `serial:<dev>:<baud>`, `udps:<listen_ip>:<port>`, `udpc:<dest_ip>:<port>`, `udpb:<broadcast_ip>:<port>`, `tcps:<listen_ip>:<port>`, `tcpc:<dest_ip>:<port>`. Domain names accepted. |
| Outputs | Frames forwarded to every other endpoint, routed by target system/component when the message has those fields. Own HEARTBEAT (default sysid 125, compid 191, every 5 s). Optional `.tlog` dump segments. |
| Key API / entry points | CLI only (`main.go`, kong parser): `mavp2p [<endpoints> ...] [flags]`. Flags: `--print`, `--print-errors`, `-q`, `--read-timeout=10s`, `--write-timeout=10s`, `--idle-timeout=60s`, `--hb-disable`, `--hb-version=1`, `--hb-systemid=125`, `--hb-componentid=191`, `--hb-period=5`, `--streamreq-disable`, `--streamreq-frequency=4`, `--dump`, `--dump-path="dump/2006-01-02_15-04-05.tlog"`, `--dump-duration=1h`. Library underneath: [gomavlib](../../catalog/repos/bluenviron__gomavlib.md). |
| Time to first result | Estimate: 5 min from download to QGC seeing a SITL or USB autopilot through mavp2p. Assumes a Linux/Windows host and a known serial device and baud. |
| License | MIT (LICENSE, "Copyright (c) 2019 aler9"). |

## Minimal usage
Not run. Commands from the README, combined.

```sh
tar xzf mavp2p_v1.3.4_linux_arm64v8.tar.gz
# Autopilot on UART => GCS on UDP 14550 (server), nav process on UDP 14560 (client), log everything
./mavp2p serial:/dev/ttyAMA0:57600 udps:0.0.0.0:14550 udpc:127.0.0.1:14560 tcps:0.0.0.0:5760 \
  --dump --dump-path="dump/2006-01-02_15-04-05.tlog"
```

QGC: Application Settings => Comm Links => Add, type UDP, port 0, server `<mavp2p-ip>:14550` (README procedure, adapted to the port above). Mission Planner: TCP to the `tcps` port. PX4 SITL on another host needs `-p` added to `mavlink start` in `px4-rc.mavlink` (README).

## Wiring it into a nav stack
- Typical companion layout: FC UART => mavp2p => (a) GCS ([QGroundControl](./mavlink__qgroundcontrol.md)), (b) your estimator or GNSS-integrity monitor via [pymavlink](./ardupilot__pymavlink.md) or [MAVSDK-Python](./mavlink__mavsdk-python.md) on `udpin:0.0.0.0:14560`, (c) [MAVROS](./mavlink__mavros.md) if ROS is in the loop.
- External position back into ArduPilot (VISION_POSITION_ESTIMATE, GPS_INPUT, ODOMETRY) goes the same way in reverse: your process sends to its endpoint, mavp2p forwards to the FC.
- Telemetry `.tlog` dumps are readable with pymavlink (`mavlogdump.py`) for offline replay of GNSS-loss runs.
- [BlueOS](./bluerobotics__blueos.md) ships mavp2p as one of three selectable routers (`core/services/ardupilot_manager/mavlink_proxy/MAVP2P.py`), so the same CLI semantics apply there.
- Concept: [mavlink-gcs](../../catalog/concepts/mavlink-gcs.md). Catalog page: [catalog/repos/bluenviron__mavp2p.md](../../catalog/repos/bluenviron__mavp2p.md).

## Gotchas
- Stream requests are ON by default: mavp2p asks ArduPilot devices for streams at 4 Hz and blocks GCS stream requests. If your nav code needs e.g. 50 Hz ATTITUDE or RAW_IMU, raise `--streamreq-frequency`, or disable with `--streamreq-disable` and set SRx_ rates on the FC. Per-client rates are an open request (#195).
- Only messages with TargetSystem/TargetComponent fields plus HEARTBEAT are decoded (`generateDialect` in `main.go`); everything else is forwarded as raw frames. Good for dialect independence, but routing relies on clean MAVLink 2 framing: #59 (closed) traced lost PARAM_EXT replies to third-party libraries not truncating trailing zero bytes as the spec requires.
- Serial endpoint takes only device and baud (`EndpointSerial{Device, Baud}` in `main.go`); there is no CLI flag for hardware flow control. Pixhawk TELEM ports with RTS/CTS enabled may not connect (#50).
- Give each router on the network a different `--hb-systemid` (help text). Two mavp2p instances both at 125 confuse GCS node lists.
- Reconnect storms to a dead `udpc`/`tcpc` endpoint were reported in #72 (closed, fix added a pause between reconnects); use v1.3.x.
- No macOS binary in the latest release; build from source or use Docker on a Linux VM.

## Alternatives
- [mavlink-router](./mavlink-router__mavlink-router.md) - C++, config-file driven, message filtering and flight-stack log download; prefer when you need filtering or already use a mavlink-router config (Rpanion-server uses it).
- [MAVProxy](./ardupilot__mavproxy.md) - Python, interactive console and modules (map, NMEA out, DGPS); prefer for bench work where you want a CLI GCS too, not for a lightweight onboard daemon.
- [Rpanion-server](./stephendade__rpanion-server.md) - web UI wrapper around mavlink-router plus video and NTRIP; prefer when operators need a browser config page.

Sources: `gh api repos/bluenviron/mavp2p` (license MIT, release v1.3.4 2026-10-16 and its asset list), README.md, main.go (endpoint types, kong flags, generateDialect), go.mod (go 1.27.0, gomavlib v4.0.1), LICENSE, issues #50, #59, #72, #195; BlueOS core/services/ardupilot_manager/mavlink_proxy listing.
