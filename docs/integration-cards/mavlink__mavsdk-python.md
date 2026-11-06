# MAVSDK-Python - integration card
<!-- about: repo:mavlink/mavsdk-python -->
One-line: asyncio Python API (takeoff, offboard, missions, telemetry streams, failure injection) over an embedded gRPC `mavsdk_server`, the fastest way to script a PX4 SITL scenario such as "take off, kill GPS, watch the estimator".

| | |
|---|---|
| Install | `pip install mavsdk-grpc` and `import mavsdk_grpc` (current, tracks MAVSDK v4; latest seen 4.0.5, `MAVSDK_SERVER_VERSION` = v4.0.5). The PyPI name `mavsdk` now means the separate native binding with a different API (latest 4.1.0). Pin `mavsdk<4` only to keep old code on the frozen gRPC wrapper. |
| Runs on | Python 3.7+ per README (asyncio). Wheels bundle `mavsdk_server` for Windows, Linux, macOS. On Raspberry Pi 1/2/Zero (armv6) `grpcio` has no wheel: `apt install python3-grpcio`, and you may have to run `mavsdk_server` yourself. |
| Inputs | A MAVLink endpoint URL: `udpin://0.0.0.0:14540` (PX4 SITL default), `tcpout://host:5760`, `serial:///dev/ttyACM0:57600`. |
| Outputs | Async generators of telemetry (`drone.telemetry.position()`, `health()`, `odometry()`...), action/mission results, exceptions on command failure. |
| Key API / entry points | `System(mavsdk_server_address=None, port=50051)`; `await drone.connect(system_address=...)`; `drone.core.connection_state()`; `drone.telemetry.health()` (`is_global_position_ok`, `is_home_position_ok`); `drone.action.arm()/takeoff()/goto_location(lat, lon, alt_amsl, yaw)`; `drone.offboard.set_velocity_ned(...)`; `drone.failure.inject(FailureUnit, FailureType, instance)`; `drone.param.set_param_int(name, v)`. |
| Time to first result | Estimate: 10-15 min to run `examples/takeoff_and_land.py` against a running PX4 SITL. Assumes SITL already up and an x86-64 or Apple Silicon host with wheels available. |
| License | BSD-3-Clause. |

## Minimal usage
Trimmed from `examples/failure_injection.py` (main). Not run as written; the hub's PX4 sample ran the same pattern with `mavsdk-grpc` 4.0.5 and found the GPS `inject` call times out on PX4 v1.17.0 SIH (see Verified in this hub).

```python
import asyncio
from mavsdk_grpc import System
from mavsdk_grpc.failure import FailureType, FailureUnit

async def run():
    drone = System()
    await drone.connect(system_address="udpin://0.0.0.0:14540")
    async for s in drone.core.connection_state():
        if s.is_connected: break
    async for h in drone.telemetry.health():
        if h.is_global_position_ok and h.is_home_position_ok: break
    await drone.param.set_param_int("SYS_FAILURE_EN", 1)
    await drone.action.arm()
    await drone.action.takeoff()
    await asyncio.sleep(10)
    await drone.failure.inject(FailureUnit.SENSOR_GPS, FailureType.OFF, instance=0)
    async for h in drone.telemetry.health():
        print(h)            # watch is_global_position_ok drop
        await asyncio.sleep(1)

asyncio.run(run())
```

## Wiring it into a nav stack
- Pair with [PX4](./px4__px4-autopilot.md) SITL/SIH (listens on 14540 by default). Other examples worth copying: `px4_ev_automation.py` (MOCAP/EV plus GNSS fusion, PX4 v1.14+), `offboard_velocity_ned.py`, `mission_import.py` (QGC `.plan`), `rtcm.py` (RTK corrections), `mavlink_direct_send.py` / `mavlink_direct_receive.py` for raw messages.
- ArduPilot works for basic actions and telemetry; failure injection and offboard are PX4-centric. For ArduPilot-specific params and SITL faults use [pymavlink](./ardupilot__pymavlink.md).
- When a GCS and the script share one link, put [mavlink-router](./mavlink-router__mavlink-router.md) in front.
- LLM front end: [MAVLinkMCP](./ion-g-ion__mavlinkmcp.md) builds its tools on MAVSDK.
- Catalog: [MAVSDK-Python page](../../catalog/repos/mavlink__mavsdk-python.md), C++ core [MAVSDK](../../catalog/repos/mavlink__mavsdk.md).

## Gotchas
- The rename is a trap for copied code: tutorials say `pip install mavsdk` / `from mavsdk import System`. Today that pulls the native binding (different API). Either `pip install mavsdk-grpc` + `import mavsdk_grpc as mavsdk`, or pin `mavsdk<4`.
- `drone.connect()` silently spawns the bundled `mavsdk_server` on port 50051; a second script on the same host will collide unless you set `port=` or point at a separately running server with `mavsdk_server_address`.
- Health `is_global_position_ok` waits for GNSS by default; GNSS-denied starts with EV only need a different readiness check.

## Verified in this hub
Measured by hub samples that ran this code on 2026-11-06, unless a bullet says otherwise. The linked sample README holds the commands and raw output.

- `mavsdk-grpc` 4.0.5 (`import mavsdk_grpc`) flew a full PX4 v1.17.0 SIH mission from a linux/aarch64 container; `mavsdk_server` ships in the wheel. The macOS arm64 wheel's server starts (`--help`) but was not flown. Python 3.12 - [px4-sitl-gps-denial](../../samples/px4-sitl-gps-denial/README.md).
- `drone.failure.inject(SENSOR_GPS, OFF)` times out against PX4 v1.17.0 SIH (PX4 side, see the PX4 card); the sample falls back to `param.set_param_int('SIM_GPS_USED', 0)`. Set `SYS_FAILURE_EN 1` first in any case - [px4-sitl-gps-denial](../../samples/px4-sitl-gps-denial/README.md).
- `telemetry.ground_truth()` is filled by SIH, so drift vs truth can be measured live; position telemetry alone is the EKF estimate - [px4-sitl-gps-denial](../../samples/px4-sitl-gps-denial/README.md).
- Harmless log noise: `Received ack for not-existing command: 176! Ignoring...` during mode changes. `MissionItem` takes 14 positional arguments in the version used - [px4-sitl-gps-denial](../../samples/px4-sitl-gps-denial/README.md).
- Rename trap seen in the wild: MAVLinkMCP's `pyproject.toml` depends on unpinned `mavsdk` and imports `from mavsdk import System`; `uv sync` gets the locked 3.17.2, `pip install -e .` would resolve 4.x (source read, not run) - [llm-mission-agent](../../samples/llm-mission-agent/README.md).

## Alternatives
- [pymavlink](./ardupilot__pymavlink.md): lower level, every message, both autopilots, log parsing.
- [MAVROS](./mavlink__mavros.md): when the rest of the system is ROS 2.
- [DroneKit-Python](../../catalog/repos/dronekit__dronekit-python.md): older ArduPilot-oriented API.

Sources: `README.md`, `examples/` listing, `examples/failure_injection.py`, `examples/px4_ev_automation.py` header, `MAVSDK_SERVER_VERSION`, PyPI JSON for `mavsdk` and `mavsdk-grpc`, releases API.
