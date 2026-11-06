# mavlink-router - integration card
<!-- about: repo:mavlink-router/mavlink-router -->
One-line: small C++ daemon that fans one autopilot link out to many MAVLink clients (GCS, companion scripts, loggers) with sysid-aware routing, per-endpoint message filters, dedup for redundant links, and built-in `.ulg`/`.bin`/`.tlog` logging.

| | |
|---|---|
| Install | `git clone https://github.com/mavlink-router/mavlink-router && cd mavlink-router && git submodule update --init --recursive && sudo apt install git meson ninja-build pkg-config gcc g++ systemd && meson setup build . && ninja -C build && sudo ninja -C build install`. Latest release tag seen: `v4` (2024-02). |
| Runs on | Linux (systemd unit installed by default; `-Dsystemdsystemunitdir=` for non-systemd). Works on companion boards (RPi, Jetson). Needs meson >= 0.57 per README. |
| Inputs | UART (`/dev/ttyS1:1500000`), UDP server/client endpoints, TCP clients, TCP server on 5760 for dynamic clients. Config: `/etc/mavlink-router/main.conf` (or `-c`, `MAVLINK_ROUTERD_CONF_FILE`) plus `config.d/` overrides. |
| Outputs | Routed MAVLink to every endpoint that has seen the target sysid/compid; logs to `Log=` dir as `.ulg` (PX4) or `.bin` (ArduPilot), raw `.tlog` with `LogTelemetry` / `-T`. |
| Key API / entry points | `mavlink-routerd [-e host:port ...] [-c conf] [-d confdir] [-l logdir] [-T] <uart-or-udp>`; config sections and keys per `examples/config.sample`: `[General]` `Log`, `MavlinkDialect`, `TcpServerPort`; `[UartEndpoint x]`, `[UdpEndpoint x]` `Mode=Server|Normal`, `Address`, `Port`; filters `{Allow,Block}{MsgId,SrcSys,SrcComp}{In,Out}` (e.g. `AllowMsgIdOut`, `BlockMsgIdIn`); `Group=` for parallel links; `DeDuplicationPeriod`; `SnifferSysid`; `LogTelemetry`, `MaxLogFiles`, `MinFreeSpace` (key spellings from `examples/config.sample`). Test scripts `examples/sender.py`, `examples/receiver.py` (need pymavlink). |
| Time to first result | Estimate: 15-20 min to build and route SITL to two UDP clients. Assumes Debian/Ubuntu with build tools. |
| License | Apache-2.0. |

## Minimal usage
From README. Not run.

```bash
# serial autopilot => QGC on a laptop + local companion script
mavlink-routerd -e 192.168.7.1:14550 -e 127.0.0.1:14550 /dev/ttyS1:1500000

# SITL already sending to UDP 24550 => two clients
mavlink-routerd -e 127.0.0.1:14550 -e 127.0.0.1:14560 0.0.0.0:24550
```
Any client can also connect to TCP 5760 (server on by default).

## Wiring it into a nav stack
- Sits between the autopilot ([ArduPilot](./ardupilot__ardupilot.md) or [PX4](./px4__px4-autopilot.md)) and everything else: [QGroundControl](./mavlink__qgroundcontrol.md), [MAVROS](./mavlink__mavros.md), a VIO bridge such as [vision_to_mavros](./thien94__vision_to_mavros.md), [MAVLinkMCP](./ion-g-ion__mavlinkmcp.md).
- Use an `AllowMsgIdOut` filter on the endpoint that faces an LLM agent or an untrusted laptop so it only receives telemetry, and `BlockMsgIdIn` for `COMMAND_LONG`/`SET_POSITION_TARGET_*` if it must be read-only. This is a simple guard layer for agent demos.
- Flight logs land on the companion even without SD-card download, useful for post-run EKF analysis with [pymavlink](./ardupilot__pymavlink.md) tools or [flight_review](../../catalog/repos/px4__flight_review.md).
- Catalog: [mavlink-router page](../../catalog/repos/mavlink-router__mavlink-router.md).

## Gotchas
- Two parallel links (radio + LTE) must be in the same `Group` on both ends, otherwise routing rule 1 (reject messages from sysids already seen on this endpoint) stops one link (README).
- UDP client mode only receives after the remote side has sent; server mode only sends after first receipt. Mixing these up looks like "one direction works".
- Open issues: #506 idle TCP clients can exhaust file descriptors; #273 high routing latency with FC on USB; #244 UART stability on Jetson Xavier NX.
- `.tlog` logging only works when flight-stack logging (`Log=`) is also set.
- Last release tag is from 2024; build from `master` for fixes.

## Alternatives
- [mavp2p](../../catalog/repos/bluenviron__mavp2p.md): single Go binary, simpler, cross-platform.
- [MAVProxy](./ardupilot__mavproxy.md) `--out`: fine for SITL on a laptop, heavier on a companion.

Sources: `README.md`, `examples/config.sample` (key names), issue search (#506, #273, #244), releases API.
