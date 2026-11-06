# MAVLinkMCP - integration card
<!-- about: repo:ion-g-ion/mavlinkmcp -->
One-line: Python MCP server (built on MAVSDK) that lets an LLM agent read telemetry and fly a PX4-class vehicle, with a reviewable survey-plan pipeline (map view => plan => validate => preflight => upload => verify => start); good for an "operator assistant" demo in SITL.

| | |
|---|---|
| Install | `git clone https://github.com/ion-g-ion/MAVLinkMCP && cd MAVLinkMCP && uv sync` (uses the committed `uv.lock`), or `pip install -e .` (pulls `mavsdk` 4.x, a different API; see Verified in this hub). Python 3.10+. |
| Runs on | Any OS with Python 3.10+ and MAVSDK wheels; target is PX4 SITL first (README). |
| Inputs | MAVLink over UDP: `MAVLINK_ADDRESS` empty => `udpin://0.0.0.0:$MAVLINK_PORT` (default 14540, what PX4 SITL sends to); set => `udpout://host:port`. `MAVLINK_CONNECT_TIMEOUT` default 60 s. Map tiles: `MAVLINKMCP_MAP_PROVIDER` (`esri` default, `osm`, `mapbox`, `maptiler`, `custom`, `none`), `MAVLINKMCP_MAP_API_KEY`, `MAVLINKMCP_MAP_TILE_URL`. |
| Outputs | MCP tools/prompts/resources over stdio (default), `streamable-http` or `sse`; georeferenced map images; stored plans; QGC `.plan` export (`download_mission_as_plan`). |
| Key API / entry points | CLI `mavlinkmcp [--transport stdio|streamable-http|sse] [--host] [--port] [--path] [--allowed-host] [--allow-any-host]`. Tools (from `server.py`): telemetry `get_position`, `get_gps_info`, `get_health`, `get_odometry`, `get_attitude_euler`, `get_velocity_ned`, `get_heading`, `get_flight_mode`, `get_wind`, `get_distance_sensor`; control `arm_drone`, `takeoff`, `land`, `move_to_relative`, `return_to_launch`, `disarm_drone`; planning `get_map_view`, `map_transform`, `create_survey_plan`, `create_plan_from_waypoints`, `validate_plan`, `preflight_check`, `upload_plan`, `verify_uploaded_plan`, `start_mission`, `pause_mission`, `clear_mission`. |
| Time to first result | Estimate: 20-30 min to connect Claude Code / another MCP client to the server and read `get_position` from PX4 SITL. Assumes PX4 SITL already running. |
| License | MIT. |

## Minimal usage
From README. Not run.

```bash
git clone https://github.com/ion-g-ion/MAVLinkMCP && cd MAVLinkMCP && uv sync
export MAVLINK_PORT=14540                       # PX4 SITL; leave MAVLINK_ADDRESS empty to listen
claude mcp add mavlink -- /abs/path/to/MAVLinkMCP/.venv/bin/mavlinkmcp
# in the client: "what is the vehicle's GPS fix and health?" => get_gps_info / get_health
```
For a GNSS-loss demo: inject `failure gps off` in the PX4 shell ([PX4](./px4__px4-autopilot.md)) and ask the agent to explain `get_health` / `get_gps_info` and recommend an action; keep the action human-approved.

## Wiring it into a nav stack
- Vehicle: [PX4](./px4__px4-autopilot.md) SITL/SIH on 14540. ArduPilot works only as far as MAVSDK supports it; for ArduPilot-first agents see the alternatives.
- Put [mavlink-router](./mavlink-router__mavlink-router.md) between the vehicle and the MCP server, with an endpoint filter if you want a read-only agent.
- Show results on [QGroundControl](./mavlink__qgroundcontrol.md) (export `.plan`) or a TAK map via [PyTAK](./snstac__pytak.md).
- Same pattern for ROS robots: [ros-mcp-server](./robotmcp__ros-mcp-server.md).
- Catalog: [MAVLinkMCP page](../../catalog/repos/ion-g-ion__mavlinkmcp.md).

## Gotchas
- Dependency trap: `pyproject.toml` depends on unpinned `mavsdk` and imports `from mavsdk import System`; `uv.lock` pins `mavsdk` 3.17.2 (the gRPC wrapper). PyPI `mavsdk` 4.x is now the native binding with a different API (see the [MAVSDK-Python](./mavlink__mavsdk-python.md) card), so `pip install -e .` may pull an incompatible version. Use `uv sync`, or pin `mavsdk<4` (inferred from the files, not tested).
- No authentication on the HTTP transports; an open port can arm and fly the vehicle (README). Keep stdio or localhost, or add your own auth layer.
- One MAVSDK connection per MCP session; two HTTP clients means two independent command sources to one airframe (README).
- Map imagery is the only outbound network use; set `MAVLINKMCP_MAP_PROVIDER=none` on an air-gapped or opsec-sensitive setup, `prefetch_map_area` to cache before going offline. Provider attribution is required.
- Safety: README says prefer SITL and keep a human ready to land; treat tool failures as fail-closed.
- Small project (index metadata: 25 stars); GitHub issues search returned nothing.

## Verified in this hub
Measured by hub samples that ran this code on 2026-11-06, unless a bullet says otherwise. The linked sample README holds the commands and raw output.

- Not run. Source read at the 2026-08-31 commit: `pyproject.toml` depends on unpinned `mavsdk` and imports `from mavsdk import System` (gRPC API); `uv.lock` pins 3.17.2, so `uv sync` works as written, but `pip install -e .` resolves `mavsdk` 4.x (the native binding). Use `uv sync` or pin `mavsdk<4`. 51 `@mcp.tool` functions; no inclusion geofence on commands and no dry-run mode found by grep - [llm-mission-agent](../../samples/llm-mission-agent/README.md).

## Alternatives
- [ardupilot-mcp](../../catalog/repos/rmeadomavic__ardupilot-mcp.md): SITL-first, ArduPilot, explicit safety gating.
- [mavlink-mcp](../../catalog/repos/deepakpopli__mavlink-mcp.md): ArduPilot over MAVLink, missions and commands.
- Script directly with [MAVSDK-Python](./mavlink__mavsdk-python.md) when no LLM is needed.

Sources: `README.md`, `pyproject.toml`, `uv.lock` (mavsdk version), `src/mavlinkmcp/` listing, `src/mavlinkmcp/server.py` (tool function names, imports), PyPI JSON for `mavsdk`, issue search.
