# MAVSDK - integration card
<!-- about: repo:mavlink/mavsdk -->
C++ high-level MAVLink API (action, mission, offboard, telemetry, param, failure injection, mavlink_direct) plus the `mavsdk_server` gRPC binary and, since v4, native C / Python / Kotlin bindings in the same repo. Use it to script a PX4 or ArduPilot vehicle from a companion computer without touching raw messages.

| | |
|---|---|
| Install | Latest release v4.1.0 (2026-10-27); v3 line still patched (v3.17.5, 2026-10-28). Ubuntu/Debian: download `libmavsdk-dev_4.1.0_<distro>_<arch>.deb` from the v4.1.0 release (assets exist for `ubuntu22.04_amd64`, `ubuntu24.04_amd64`, `ubuntu26.04_amd64`, `debian12_{amd64,arm64,armv6,armv7}`, `debian13_amd64`) then `sudo dpkg -i libmavsdk-dev_4.1.0_ubuntu24.04_amd64.deb`. Windows: `mavsdk-windows-x64.zip`. Standalone gRPC server binaries: `mavsdk_server_musl_x86_64`, `mavsdk_server_linux-arm64-musl`, `mavsdk_server_macos_arm64`, etc. Python native binding: `pip install mavsdk` (PyPI 4.1.0, abi3 wheels for macOS arm64/x86_64, manylinux_2_28 x86_64/aarch64, Windows; `requires_python >=3.8`). Build from source: mavsdk.mavlink.io "Building the Library" (not read in this pass). |
| Runs on | Linux, macOS, Windows, iOS, Android (README). Pure CPU. Raspberry Pi 32-bit: Debian 12 armv6/armv7 debs and musl armv6/armv7l server binaries. |
| Inputs | A connection URL (from `mavsdk_server` usage text): `serial:///dev/ttyUSB0[:baud]`, `udpin://[host][:port]`, `udpout://host:port`, `tcpin://...`, `tcpout://...`. SITL default `udpin://0.0.0.0:14540`. |
| Outputs | Typed telemetry callbacks/streams (position, attitude, health, odometry, GPS info, battery), command results (`Action::Result`...), mission progress, logs/FTP files, raw messages via `MavlinkDirect`. `mavsdk_server` exposes the same as gRPC on port 50051 by default (`-p 0` picks a free port). |
| Key API / entry points | C++: `Mavsdk mavsdk{Mavsdk::Configuration{ComponentType::GroundStation}}`; `mavsdk.add_any_connection(url)`; `mavsdk.first_autopilot(timeout_s)` => `std::optional<std::shared_ptr<System>>`; plugins `Action{system}` (`arm()`, `takeoff()`, `land()`, `hold()`), `Telemetry{system}` (`subscribe_position()`, `set_rate_position()`), `Offboard`, `Mission`, `Param`, `Failure`, `MavlinkDirect`. Python v4: `from mavsdk.asyncio import Mavsdk, Configuration, ComponentType`; `Configuration.create_with_component_type(ComponentType.GROUND_STATION)`; `await mavsdk.add_any_connection(url)`; `mavsdk.on_new_system()`; `from mavsdk.asyncio.plugins.action import ActionAsync`. Server CLI: `mavsdk_server [-p port] [--sysid N] [--compid N] [--heartbeat-watchdog-timeout s] <url>`. ~60 C++ examples in `cpp/examples/` (`takeoff_and_land`, `offboard`, `fly_mission`, `set_gps_origin`, `goto_location_with_terrain`, `mavlink_direct_sender_custom`, `sniffer`, `write_tlog`...). |
| Time to first result | Estimate: 15 min with the .deb or `pip install mavsdk` against an already running PX4 SITL; 45-90 min if you build from source. |
| License | `LICENSE.md`: BSD-3-Clause. |

## Minimal usage
Not run. Python, condensed from `py/mavsdk/examples/asyncio/takeoff_and_land.py`.

```python
import asyncio
from mavsdk.asyncio import Mavsdk, Configuration, ComponentType
from mavsdk.asyncio.plugins.action import ActionAsync

async def main():
    mavsdk = Mavsdk(Configuration.create_with_component_type(ComponentType.GROUND_STATION))
    await mavsdk.add_any_connection("udpin://0.0.0.0:14540")
    async for _ in mavsdk.on_new_system():
        for s in await mavsdk.get_systems():
            if await s.has_autopilot() and await s.is_connected():
                action = ActionAsync(s)
                await action.arm(); await action.takeoff()
                await asyncio.sleep(10); await action.land()
                return

asyncio.run(main())
```

C++ (from `cpp/examples/takeoff_and_land`): `./takeoff_and_land udpin://0.0.0.0:14540`.

gRPC route for other languages: `./mavsdk_server_musl_x86_64 -p 50051 udpin://0.0.0.0:14540`, then point a MAVSDK-Swift/Java/Go client at it.

## Wiring it into a nav stack
- GNSS-denied scenarios: `Failure` plugin to inject GPS loss in PX4 SITL; `set_gps_origin` example to set the EKF origin when there is no GNSS (issues #1531, #2263 discuss origin setting); `Offboard` for velocity control from an alt-nav loop.
- Feeding external estimates: `MavlinkDirect` (replaces the deprecated `MavlinkPassthrough`) to send `ODOMETRY` / `VISION_POSITION_ESTIMATE` / `GPS_INPUT` from your estimator. Message definitions: [MAVLink](./mavlink__mavlink.md).
- Python users with older code: [MAVSDK-Python card](./mavlink__mavsdk-python.md) (gRPC wrapper, now `mavsdk-grpc` on PyPI).
- Same vehicle from ROS 2: [MAVROS](./mavlink__mavros.md) or [px4_ros_com](./px4__px4_ros_com.md); share one link with [mavlink-router](./mavlink-router__mavlink-router.md).

## Gotchas
- PyPI name collision: since v4, `pip install mavsdk` is the native binding (`mavsdk.asyncio`, `ActionAsync`, no gRPC). Old tutorials using `from mavsdk import System` and `drone.action.arm()` need `pip install mavsdk-grpc` (4.0.5) or `mavsdk<4`. Its README calls the asyncio binding "still new ... hasn't been tested as much".
- Two supported majors: v3.17.x and v4.x both get releases; pin one.
- `first_autopilot()` returns empty if no heartbeat arrives within the timeout: check the URL direction (`udpin` listens, `udpout` sends) before debugging anything else.
- Command support depends on the autopilot: closed issue #1846 shows `Command unsupported (511)`; many plugins are PX4-first, ArduPilot coverage varies per plugin.
- Volunteer-maintained (README: not sponsored by any company).

## Verified in this hub
Measured by hub samples that ran this code on 2026-11-06, unless a bullet says otherwise. The linked sample README holds the commands and raw output.

- The Python gRPC path (`mavsdk-grpc` 4.0.5 with its bundled `mavsdk_server`, linux/aarch64) flew a PX4 v1.17.0 SIH mission end to end; the native v4 binding and the C++ API were not run. Failure plugin GPS injection timed out against v1.17.0 SIH (PX4 limitation) - [px4-sitl-gps-denial](../../samples/px4-sitl-gps-denial/README.md).

## Alternatives
- [pymavlink](./ardupilot__pymavlink.md) - raw messages, any dialect, log parsing; more code per action.
- [MAVROS](./mavlink__mavros.md) - when the companion stack is ROS.
- [px4-ros2-interface-lib](./auterion__px4-ros2-interface-lib.md) - PX4-only, DDS-native custom flight modes.

Sources: `README.md`, `LICENSE.md`, `py/README.md`, `py/mavsdk/` listing, `py/mavsdk/examples/asyncio/takeoff_and_land.py`, `cpp/examples/` listing, `cpp/examples/takeoff_and_land/takeoff_and_land.cpp`, `cpp/src/mavsdk_server/src/mavsdk_server_bin.cpp`, releases v4.1.0 (asset list) and v3.17.5, issues #1531 #1846 #2263, PyPI JSON for `mavsdk` and `mavsdk-grpc` (github.com/mavlink/MAVSDK).
