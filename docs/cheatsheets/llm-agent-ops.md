# Cheat sheet: LLM and agent-assisted operations

Briefs like "AI assistant for operators of unmanned systems under EW", "analyse GNSS incidents
across a fleet", "agentic mission planning". Decoder rows 21, 22. Pair it with a navigation
core from another sheet: the LLM narrates and proposes, deterministic tools decide.

## 1. What judges likely want (30 s)

"The agent can explain and propose; only a human can make the vehicle move." Judges ask how an
AI component is disengaged, logged and bounded. They reward deterministic extractors with the
LLM on top, every claim traceable to a log line, and hard guards on any command.

## 2. The demo in 24-48 h

A safety-gated MAVLink MCP server (geofence, altitude band, mode allowlist, dry run) on ArduCopter
SITL: takeoff, survey, GPS loss => degraded nav health => ExternalNav switch => RTL, with fence
and altitude rejections firing. The LLM explains the health change and proposes the switch; the
human approves.

| Sample | Status | Deps | Setup / download | First commands |
|---|---|---|---|---|
| [llm-mission-agent](../../samples/llm-mission-agent/) | partial (Claude tool-use loop `agent_loop.py` never run against the API) | docker + venv | ArduPilot SITL image ~8.5 min; scripted flight 126 s | `docker compose up -d ardupilot` in `samples/sitl-docker`, venv from the sample's `requirements.txt`, `source_switch.py --setup` once, then `run_transcript.py --scenario flight --connect tcp:127.0.0.1:5762 --sim-connect tcp:127.0.0.1:5763` (exact block: README "Run it against SITL") |
| [llm-agent-usage](../../samples/llm-agent-usage/) | ran | stdlib | under 1 s | `python3 ../../tools/mcp_server.py < demo_requests.jsonl` (from `samples/llm-agent-usage/`) |

Incident reporter (row 21): fault logs from [px4-sitl-gps-denial](../../samples/px4-sitl-gps-denial/)
or [golden-demo](../../samples/golden-demo/) flights, `nav_health.py` in llm-mission-agent as the
extractor.

## 3. First 2 hours (3-5 people)

| Who | 0:00-1:00 | 1:00-2:00 |
|---|---|---|
| Lead | Read-only or command authority? Which autopilot? API keys allowed on site? | ADR-001: metric = % of cited events that exist in the log; unsafe commands blocked |
| Nav | Pick the nav-health signals the agent may read | Deterministic extractor: GPS status, EKF innovations, source changes |
| Platform | SITL up, scripted flight green | Run `agent_loop.py` with a key: the first real LLM run of this sample |
| Viz (4-5) | Transcript + map side by side | Approval button; rejected commands shown in red |
| Pitch (5) | Governance slide: log, confidence, off switch | Threat model: prompt injection via telemetry text |

## 4. Numbers you can cite

There is no accuracy number for this family in the hub; only functional checks. Measure your
own (for example, share of LLM-cited timestamps found in the log) and quote it as yours.

- MCP tools flew takeoff, survey, GPS loss => degraded health => ExternalNav => RTL; fence and
  altitude rejections fired. **SITL**, scripted client, no LLM in the loop.
- The event the agent has to explain: GPS cut without a source switch => EKF coasts ~6 s, then
  failsafe LAND. **SITL** (Copter 4.6.3), 1 flight.
- The hub's MCP server answered 7 JSON-RPC requests in a demo session (0.32 s). Functional check.

## 5. Top traps

1. The LLM loop was never run against the API: budget time for the first real run, tool-call
   errors and rate limits.
2. Unsafe write access: ros-mcp-server and ROSA keep it by default; MAVLinkMCP depends on an
   unpinned `mavsdk` ([upstream finding 15](../upstream-findings.md#15-mavlinkmcp-unpinned-mavsdk)).
   Use mavlink-router msg-id filters for a read-only link.
3. LLM inventing events: check every cited timestamp exists. ArduPilot 4.6 `SIM_GPS_DISABLE`
   vs 4.7 / master `SIM_GPS1_ENABLE` when scripting the "jammer".

## 6. Stretch goal

Incident report where every sentence links to a log line and a checker rejects any sentence
whose timestamp is missing, with the rejection rate measured over several faulted flights. Or a
route planner tool that scores GNSS-denied routes by navigability (texture, terrain, interference
cells), proposal only.

## 7. Links

- Decoder: [rows 21, 22](../problem-statement-decoder.md#the-table); evidence:
  [section 13](../evidence-matrix.md#13-functional-checks-no-accuracy-metric).
- Cards: [MAVLinkMCP](../integration-cards/ion-g-ion__mavlinkmcp.md),
  [mavlink-router](../integration-cards/mavlink-router__mavlink-router.md),
  [ros-mcp-server](../integration-cards/robotmcp__ros-mcp-server.md),
  [ROSA](../integration-cards/nasa-jpl__rosa.md),
  [pymavlink](../integration-cards/ardupilot__pymavlink.md),
  [PX4](../integration-cards/px4__px4-autopilot.md).
- Datasets: none needed; SITL logs with injected GPS faults.
- Scope: [export-control-and-ethics](../export-control-and-ethics.md).
