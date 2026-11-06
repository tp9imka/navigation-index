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
Trimmed from `examples/failure_injection.py` (main). Not run.

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

## Alternatives
- [pymavlink](./ardupilot__pymavlink.md): lower level, every message, both autopilots, log parsing.
- [MAVROS](./mavlink__mavros.md): when the rest of the system is ROS 2.
- [DroneKit-Python](../../catalog/repos/dronekit__dronekit-python.md): older ArduPilot-oriented API.

Sources: `README.md`, `examples/` listing, `examples/failure_injection.py`, `examples/px4_ev_automation.py` header, `MAVSDK_SERVER_VERSION`, PyPI JSON for `mavsdk` and `mavsdk-grpc`, releases API.
