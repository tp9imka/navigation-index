# Sample: LLM mission agent: a safety-gated MAVLink MCP server flying ArduPilot SITL

`sample:llm-mission-agent` - code and walkthrough in [samples/llm-mission-agent](../../samples/llm-mission-agent/)

A small MCP server (stdio JSON-RPC 2.0, pymavlink) that lets Claude Code or any MCP client read and fly an ArduCopter: get_state, get_nav_health (EKF flags, variances, GNSS fix/sats/HDOP => nominal/degraded/lost), arm_takeoff, goto, set_mode, plan_survey, upload_mission and set_ekf_source_set. Every command passes a configurable polygon geofence (target and straight path, with margin), an altitude band and a mode allowlist, can run in dry-run mode and is appended to a JSONL command log. A scripted client flew it against ArduPilot SITL in Docker: geofence and altitude rejections, takeoff, goto, a lawnmower survey in AUTO, simulated GPS loss, switch to the vision (ExternalNav) source set and RTL to landing. Includes registration next to the navigation-index MCP server, prompt recipes, a Claude tool-use loop and a comparison with MAVLinkMCP.

**Verification:** Ran on 2026-11-06 against ArduCopter Copter-4.6.3 SITL in Docker (samples/sitl-docker image, linux/arm64) with pymavlink 2.4.50 on python3.13 (uv venv): scripted MCP client drove the server through fence and altitude rejections, arm_takeoff to 20 m, goto (arrived), plan_survey + upload_mission (12 items, AUTO), SIM_GPS_DISABLE=1 => get_nav_health degraded (gnss_ok false), set_ekf_source_set 2 (ExternalNav) accepted, RTL to landing and disarm; dry-run scenario also run. Transcripts in example_output/. 24 stdlib unit tests pass on python3.14.7. agent_loop.py was not run against the API (no ANTHROPIC_API_KEY in the environment); the Claude Code registration commands were not executed.

**Concepts:** [LLM agents for robotics and navigation](../../catalog/concepts/llm-agents-robotics.md), [MAVLink, ground control and C2 links](../../catalog/concepts/mavlink-gcs.md), [Mission planning and routing](../../catalog/concepts/mission-planning.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md)

**Tags:** `mcp`, `json-rpc`, `claude-code`, `pymavlink`, `ardupilot`, `sitl`, `geofence`, `dry-run`, `audit-log`, `ekf3`, `source-sets`, `gps-denied`, `survey`

## Related

- uses: [pymavlink](../../catalog/repos/ardupilot__pymavlink.md)
- uses: [ArduPilot](../../catalog/repos/ardupilot__ardupilot.md)
- explains: [MAVLinkMCP](../../catalog/repos/ion-g-ion__mavlinkmcp.md)
- explains: [ardupilot-mcp (safety-gated)](../../catalog/repos/rmeadomavic__ardupilot-mcp.md)
- explains: [mavlink-mcp (ArduPilot)](../../catalog/repos/deepakpopli__mavlink-mcp.md)
- explains: [MAVSDK-Python](../../catalog/repos/mavlink__mavsdk-python.md)

## Referenced by

- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)

_Indexed by lane(s): samples_
