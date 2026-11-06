# MAVLinkMCP

`repo:ion-g-ion/mavlinkmcp` - <https://github.com/ion-g-ion/MAVLinkMCP>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 25 | Python | MIT | 2026-08-31 | False | research-prototype | high |

MCP server bridging an LLM to a drone over MAVLink, exposing arming, takeoff, waypoint and telemetry tools via MAVSDK.

**Why it matters:** Direct template for a natural-language drone mission interface on PX4/ArduPilot SITL.

**Hackathon notes:** Pair with PX4 or ArduPilot SITL; never point at a real vehicle without geofence and human confirm.

## Deep dives

- [_index-flight-c2](../../docs/integration-cards/_index-flight-c2.md) (integration-cards)
- [ion-g-ion__mavlinkmcp](../../docs/integration-cards/ion-g-ion__mavlinkmcp.md) (integration-cards)

**Concepts:** [LLM agents for robotics and navigation](../../catalog/concepts/llm-agents-robotics.md), [MAVLink, ground control and C2 links](../../catalog/concepts/mavlink-gcs.md), [Mission planning and routing](../../catalog/concepts/mission-planning.md)

**Tags:** `mcp`, `mavlink`, `mavsdk`, `llm`, `drone`

**Domains:** air

## Related

- depends_on: [MAVSDK-Python](../../catalog/repos/mavlink__mavsdk-python.md)
- alternative_to: [mavlink-mcp (ArduPilot)](../../catalog/repos/deepakpopli__mavlink-mcp.md)
- alternative_to: [ardupilot-mcp (safety-gated)](../../catalog/repos/rmeadomavic__ardupilot-mcp.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [mavlink-mcp (ArduPilot)](../../catalog/repos/deepakpopli__mavlink-mcp.md) (alternative_to)
- [ardupilot-mcp (safety-gated)](../../catalog/repos/rmeadomavic__ardupilot-mcp.md) (alternative_to)
- [Model Context Protocol specification](../../catalog/resources/mcp-specification.md) (explains)
- [LLM mission agent: a safety-gated MAVLink MCP server flying ArduPilot SITL](../../catalog/samples/llm-mission-agent.md) (explains)

_Indexed by lane(s): gap-fill_

_GitHub metadata fetched 2026-11-06._
