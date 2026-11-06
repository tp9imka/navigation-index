# LLM mission agent: a safety-gated MAVLink MCP server on ArduPilot SITL

<!-- about: repo:ion-g-ion/mavlinkmcp, repo:ardupilot/pymavlink, repo:ardupilot/ardupilot, repo:rmeadomavic/ardupilot-mcp, repo:deepakpopli/mavlink-mcp, repo:mavlink/mavsdk-python -->

An LLM agent that can both look up methods in this hub (`tools/mcp_server.py`) and fly a
simulated copter (`mav_mcp_server.py`), with the safety logic in the server, not in the
prompt. The flight server is ~900 lines of Python on pymavlink (server 540, safety 240,
nav_health 100); the geofence, altitude and
nav-health logic is stdlib and unit-tested.

| File | What |
|---|---|
| `mav_mcp_server.py` | MCP server, stdio JSON-RPC 2.0 (same framing as `tools/mcp_server.py`), pymavlink to ArduCopter |
| `safety.py` | polygon geofence (target + straight path + edge margin), altitude band, max leg, mission check, lawnmower survey planner |
| `nav_health.py` | EKF_STATUS_REPORT + GPS_RAW_INT => `nominal / degraded / lost / unknown` with reasons |
| `fence.example.json` | 5-vertex fence around the ArduPilot SITL default home (CMAC), 5-60 m above home, 10 m margin |
| `run_transcript.py` | scripted MCP client used to verify the server end to end against SITL (no LLM) |
| `agent_loop.py` | Claude tool-use loop over this server (+ optionally the index server) via the `anthropic` SDK. **Not run** |
| `test_safety.py` | 24 stdlib tests: fence, concave-path crossing, altitude, mission, survey, nav-health verdicts, dry-run server |
| `example_output/` | transcripts and command logs from the verified runs |

## Tools

All positions are WGS84 decimal degrees; altitudes are `rel_alt_m`, metres above the home
position (`MAV_FRAME_GLOBAL_RELATIVE_ALT_INT`), not MSL or AGL. Each tool description says
this so the model sees it.

| Tool | Does | Safety gate |
|---|---|---|
| `get_state` | position (lat/lon, alt MSL, rel alt, heading), local NED, mode, armed, groundspeed, EKF flags, GPS fix/sats/HDOP, battery, home, last commanded source set, last 5 STATUSTEXT, the fence | read only |
| `get_nav_health` | verdict + reasons, `gnss_ok`, `horizontal_position abs/rel/none`, EKF variances with warn/bad levels | read only |
| `arm_takeoff` | GUIDED, arm (retries while pre-arm fails, 60 s), NAV_TAKEOFF, optional wait for 90% alt | alt band, vehicle inside fence |
| `goto` | `SET_POSITION_TARGET_GLOBAL_INT` position-only, optional `wait_s` until within 3 m | alt band, target inside fence with margin, straight path from current position does not cross the fence, max leg |
| `set_mode` | `MAV_CMD_DO_SET_MODE` | allowlist GUIDED/AUTO/LOITER/BRAKE/RTL/LAND/SMART_RTL; AUTO only after a fence-checked upload |
| `plan_survey` | lawnmower over a polygon (default: the fence), inset from the edges; returns waypoints, sends nothing | output re-checked against the fence |
| `upload_mission` | MISSION_COUNT / MISSION_ITEM_INT handshake, optional RTL at end, optional start in AUTO | every waypoint and every leg (from the vehicle position) inside fence and band; 200 waypoint cap |
| `set_ekf_source_set` | `MAV_CMD_SET_EKF_SOURCE_SET` 1-3, reports what the set uses from `EK3_SRCn_*` params | none beyond the enum; the description warns that a set without live sensors loses position |

Cross-cutting:

- **Dry run** (`--dry-run` or `MAV_DRY_RUN=1`): actuating tools run every check, then return
  `would_send` instead of sending. Reads still work if a vehicle is connected. `--connect none`
  gives a validation-only server with no vehicle.
- **Command log** (`--log`, default `mav_mcp_commands.jsonl`): one JSON line per tool call with
  arguments, outcome `read / ok / dry_run / rejected / error`, reason and result.
- Safety rejections come back as tool results with `isError: true` and `{"rejected": true,
  "reason": ...}`, so the model sees why; unknown tools are JSON-RPC errors.
- The vehicle link opens on the first tool call, so `initialize` never blocks on a vehicle.
- What it does not do: no disarm/kill tool, no parameter writes, no rally points, no terrain
  following, no obstacle checks; the fence is the server's, not uploaded to the autopilot
  (ArduPilot's own `FENCE_*` is still worth enabling as a second layer); the fence math is a
  local tangent plane, fine for fences a few km across.

## Run it against SITL

```sh
# 1. ArduCopter SITL (image from samples/sitl-docker)
cd samples/sitl-docker && docker compose up -d ardupilot          # TCP 5760/5762/5763
# 2. host venv
python3 -m venv .venv && .venv/bin/pip install -r samples/llm-mission-agent/requirements.txt
# 3. once: EKF3 source set 2 = ExternalNav (SITL vicon), then wait ~20 s for the reboot
.venv/bin/python samples/ardupilot-ekf3-source-switch/source_switch.py --connect tcp:127.0.0.1:5763 --setup
# 4. tests (stdlib) and the scripted flight
cd samples/llm-mission-agent
python3 -m unittest test_safety
../../.venv/bin/python run_transcript.py --scenario flight --connect tcp:127.0.0.1:5762 --sim-connect tcp:127.0.0.1:5763
../../.venv/bin/python run_transcript.py --scenario dry --connect tcp:127.0.0.1:5762
```

The MCP server uses SERIAL1 (5762); the "jammer" in `run_transcript.py` uses SERIAL2 (5763)
to set `SIM_GPS_DISABLE` (ArduPilot 4.6; 4.7/master renamed it `SIM_GPS1_ENABLE`).

## What was verified (2026-11-06)

ArduCopter `Copter-4.6.3` SITL, `nav-sitl-ardupilot:copter-4.6.3` image from
`samples/sitl-docker`, Docker on Apple Silicon (linux/arm64), started as a plain
`docker run` with host ports 15760/15762/15763 (other containers were using the defaults).
pymavlink 2.4.50 in a uv venv on python 3.13; unit tests on python 3.14.7.

`python3 -m unittest test_safety`: 24 tests, OK. The first version of the survey planner
failed `test_survey_tool_returns_checked_waypoints`: an along-track inset does not keep a
pass end 10 m from a fence edge that meets it at a shallow angle, and rounding to 1e-7 deg
pushed a point that sat exactly on the margin back out. The planner now trims pass ends
until they clear the margin plus 0.5 m.

Scripted flight (`example_output/flight_stdout.txt`, full JSON-RPC in
`flight_transcript.jsonl`, server log in `flight_commands.jsonl`), 39 requests, 126 s:

```
get_nav_health   => nominal, gnss_ok true, horizontal_position abs
goto -35.37,149.1652          => rejected: target outside the geofence
arm_takeoff 120 m             => rejected: altitude 120.0 m outside [5.0, 60.0] m above home
arm_takeoff 20 m              => armed, takeoff ACCEPTED, reached_rel_alt_m 18.11
goto -35.363,149.1648 @20 m   => fence_check leg_m 48.6, arrived true
plan_survey (110 x 127 m box, 25 m spacing) => 10 waypoints
upload_mission start=true     => 12 items (home, 10 WP, RTL), path 580.9 m, AUTO ACCEPTED
get_state (25 s later)        => AUTO, rel_alt 20.0 m, inside_fence true
# jammer: SIM_GPS_DISABLE=1
get_nav_health   => nominal (first poll), then degraded: "GNSS weak: fix=NO_FIX sats=3 hdop=1.21"
set_ekf_source_set 2          => ACCEPTED, uses POSXY/VELXY/VELZ/YAW ExternalNav, POSZ Baro
get_nav_health x4 over 15 s   => degraded (GNSS only), horizontal_position abs, variances good
set_mode RTL                  => ACCEPTED; descended over home, "SIM Hit ground", "Disarming motors"
# GPS restored, set_ekf_source_set 1 => ACCEPTED, uses GPS/GPS/Baro/GPS/Compass
```

Observations from that run, not general claims:

- With GPS disabled, SITL's `GPS_RAW_INT` reported fix `NO_FIX` but kept `satellites_visible
  3` and `eph` 121 (HDOP 1.21). An agent that only watched HDOP would have missed the loss;
  the verdict keys off fix type and satellite count too.
- On source set 2 the EKF kept `POS_HORIZ_ABS` with all variances `good` and flew RTL to
  home on vicon alone. SITL vicon is a perfect pose source; a real VIO will not look this
  clean. The opposite case (GPS cut, no switch => EKF failsafe LAND) is shown in
  `samples/ardupilot-ekf3-source-switch`.
- The survey was interrupted at waypoint 6 of 10 by the RTL, as scripted.
- Rejections happen before anything is sent: the command log shows `outcome: rejected` and
  the vehicle state did not change.

Dry-run scenario (`example_output/dry_*`): `goto` inside the fence returned `would_send` with
`path_checked true, leg_m 90.4`; outside => rejected; `set_mode AUTO` without an uploaded
mission => rejected; `set_ekf_source_set 2` read the params and returned `would_send`.

Not verified: `agent_loop.py` against the Claude API (no `ANTHROPIC_API_KEY` was set in this
environment, so no real agent session was run and none is shown); the Claude Code
registration commands below (they follow the documented `claude mcp add` syntax but were
not executed); PX4 (the server is ArduPilot-specific: mode names, `SIM_*`, `EK3_SRC*`);
`agent_loop.py` was only checked to start both MCP servers, list their 12 tools and route
calls (done, with `--connect none --dry-run`).

## Register in Claude Code next to the index server

Use absolute paths. The flight server needs a Python that has pymavlink.

```sh
claude mcp add navigation-index -- python3 /abs/path/tools/mcp_server.py
claude mcp add mavlink-sitl \
  -e MAV_CONNECT=tcp:127.0.0.1:5762 \
  -e MAV_FENCE=/abs/path/samples/llm-mission-agent/fence.example.json \
  -e MAV_LOG=/abs/path/mav_mcp_commands.jsonl \
  -- /abs/path/.venv/bin/python /abs/path/samples/llm-mission-agent/mav_mcp_server.py
claude mcp list
```

Or as a project `.mcp.json` (Claude Code; Cursor and Claude Desktop take the same
`mcpServers` shape):

```json
{
  "mcpServers": {
    "navigation-index": {"command": "python3", "args": ["/abs/path/tools/mcp_server.py"]},
    "mavlink-sitl": {
      "command": "/abs/path/.venv/bin/python",
      "args": ["/abs/path/samples/llm-mission-agent/mav_mcp_server.py"],
      "env": {"MAV_CONNECT": "tcp:127.0.0.1:5762",
              "MAV_FENCE": "/abs/path/samples/llm-mission-agent/fence.example.json",
              "MAV_LOG": "/abs/path/mav_mcp_commands.jsonl",
              "MAV_DRY_RUN": "0"}
    }
  }
}
```

Start a second entry with `MAV_DRY_RUN=1` if you want the agent to rehearse first. Claude
Code asks for permission per tool by default; keep that on for the actuating tools
(`arm_takeoff`, `goto`, `set_mode`, `upload_mission`, `set_ekf_source_set`) and allow the
read tools.

Without Claude Code, `agent_loop.py` does the same over the Messages API:

```sh
export ANTHROPIC_API_KEY=...
python agent_loop.py --with-index --confirm --connect tcp:127.0.0.1:5762 \
  --prompt "Survey the fence at 20 m with 40 m spacing. If GNSS degrades, switch to the vision source set and RTL."
```

It defaults to `claude-sonnet-5-5` (`--model claude-opus-5-5` for the larger model), effort
`medium`, server-side refusal fallback (`fallbacks: "default"`), and writes
`agent_transcript.jsonl`. `--confirm` asks on the terminal before every actuating call.

## Prompt recipes

Each assumes both servers are registered. Tool names are what the model sees.

1. **Survey with a GNSS contingency**
   "Read get_state and get_nav_health. Take off to 20 m, plan a survey of polygon
   [[-35.3629,149.1648],[-35.3629,149.1662],[-35.3619,149.1662],[-35.3619,149.1648]] with
   25 m spacing, upload it with RTL at the end and start it. Poll get_nav_health every few
   seconds. If gnss_ok goes false or the verdict is degraded or lost, call
   set_ekf_source_set 2, confirm the EKF still has horizontal position, then set_mode RTL.
   Report what happened with timestamps."
2. **Look up before flying**: "Use navigation-index to find how ArduPilot EKF3 source sets
   work and which sample switches them under GPS denial (search 'ekf3 source set', then show
   the sample). Then check what source set 2 uses on this vehicle with set_ekf_source_set in
   dry-run, and explain whether switching would be safe right now from get_nav_health."
3. **Rehearse in dry run** (server with `MAV_DRY_RUN=1`): "Plan a survey of the whole fence at
   30 m, 40 m spacing, upload it, and list every waypoint the fence check rejected or
   trimmed. Do not retry rejected commands with modified numbers."
4. **Explain an alarm**: "get_nav_health says degraded. Using the EKF flags, variances and
   GPS fields it returns, explain the likely cause in two sentences and recommend one of:
   continue, switch source, RTL, LAND. Do not act."
5. **Methods scouting**: "Using navigation-index only, list three open-source options to
   provide ExternalNav (vision) position to ArduPilot when GNSS is jammed, with their
   hackathon_fit and the sample that shows the MAVLink side."

Guard rails worth keeping in the system prompt (see `agent_loop.py`): read state before and
after every command; an ACK is not arrival; never retry a rejected command with tweaked
numbers; end with what could not be verified.

## When to use this vs MAVLinkMCP (and the others)

[MAVLinkMCP](https://github.com/ion-g-ion/MAVLinkMCP) (`repo:ion-g-ion/mavlinkmcp`, MIT,
source read 2026-11-06 at the 2026-08-31 commit, not run): a much larger server
(`server.py` ~3000 lines plus ~27 helper modules) on MAVSDK and the official `mcp` FastMCP
package. 51 `@mcp.tool` functions: telemetry, arm/takeoff/land/RTL, offboard `move_to_relative`, a reviewable
plan pipeline (`create_survey_plan` with shapely/pyproj, `validate_plan`, `preflight_check`,
`upload_plan`, `verify_uploaded_plan`), map tiles, QGC `.plan` export, stdio or
streamable-http. PX4 SITL first. Its safety model is validation of inputs and plans
(`plan_check_helpers.py`: max leg 2000 m, altitude 0.5-500 m, home distance, speed,
waypoint count) and fail-closed status payloads. A grep of `server.py` found polygons only
as survey areas, no inclusion geofence on commands and no dry-run mode.

- **Dependency pin issue**: `pyproject.toml` depends on unpinned `mavsdk` and imports
  `from mavsdk import System` (the gRPC-wrapper API); `uv.lock` pins `mavsdk` 3.17.2. On PyPI
  today `mavsdk` 4.1.0 is "Python binding for MAVSDK" (the native binding, with a migration
  guide from MAVSDK-Python) while the gRPC wrapper continues as `mavsdk-grpc` 4.0.5. So
  `uv sync` gets the locked 3.17.2 and works as written, but `pip install -e .` resolves
  `mavsdk` 4.x. Whether 4.x keeps `mavsdk.System` / `mavsdk.mission` import-compatible was
  not tested here; pin `mavsdk<4` or use `uv sync`. (The `samples/sitl-docker` client image
  installs `mavsdk-grpc` 4.0.5 for the PX4 sample.)

| | this sample | MAVLinkMCP |
|---|---|---|
| Autopilot | ArduPilot (modes, `EK3_SRC*`, `SIM_*`) | PX4 first via MAVSDK; ArduPilot as far as MAVSDK supports it |
| Size / deps | ~900 lines, pymavlink only, stdlib JSON-RPC | large, MAVSDK + mcp + fast-agent + shapely + pyproj + pillow + httpx |
| Safety | polygon fence on target, path and every mission leg, alt band, mode allowlist, dry run, JSONL command log | input and plan validation, fail-closed results, preflight check, uploaded-plan verification |
| Nav integrity | EKF flags/variances + GNSS => verdict, EKF source-set switch | `get_health`, `get_gps_info` (MAVSDK health booleans) |
| Planning | simple lawnmower | survey patterns, map views, QGC export |
| Transports | stdio | stdio, streamable-http, sse |

Use **this** when the demo is ArduPilot, the story is GNSS loss and source switching, or you
want a server small enough to read and change during a hackathon and a hard fence in front
of the model. Use **MAVLinkMCP** for PX4, for richer planning and map context, or for an
HTTP-served operator assistant; add a fence in front of `upload_plan` and `move_to_relative`
before anything flies. From their index records only (source not read):
`repo:rmeadomavic/ardupilot-mcp` is ArduPilot SITL-first, read-only by default with explicit
`--enable-actuation` / `--allow-real-vehicle` flags, the closest in spirit to this sample;
`repo:deepakpopli/mavlink-mcp` covers ArduPilot missions and camera workflows.

Scope note: this is a navigation/autonomy sample for simulation. Do not point any LLM
agent at a real airframe without an independent autopilot fence, a human with a kill
switch, and the operator approval gate on.
