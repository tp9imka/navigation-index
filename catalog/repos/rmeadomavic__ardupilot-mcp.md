# ardupilot-mcp (safety-gated)

`repo:rmeadomavic/ardupilot-mcp` - <https://github.com/rmeadomavic/ardupilot-mcp>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 4 | Python | MIT | 2026-08-03 | False | research-prototype | medium |

SITL-first MCP server for talking to ArduPilot vehicles over MAVLink, with explicit safety gating of commands.

**Why it matters:** Its safety-gate design is a useful pattern for keeping an LLM from issuing unsafe flight commands.

**Hackathon notes:** `pipx install ardupilot-mavlink-mcp`, point it at SITL (tcp:127.0.0.1:5760). Read-only by default; arming needs `--enable-actuation`, and real (non-loopback) links also need `--allow-real-vehicle`. Its prearm-diagnosis and single-reader-thread design are worth copying.

**Concepts:** [LLM agents for robotics and navigation](../../catalog/concepts/llm-agents-robotics.md), [MAVLink, ground control and C2 links](../../catalog/concepts/mavlink-gcs.md)

**Tags:** `mcp`, `ardupilot`, `safety`, `sitl`

**Domains:** air

## Related

- alternative_to: [MAVLinkMCP](../../catalog/repos/ion-g-ion__mavlinkmcp.md)

## Referenced by

- [MAVLinkMCP](../../catalog/repos/ion-g-ion__mavlinkmcp.md) (alternative_to)
- [LLM mission agent: a safety-gated MAVLink MCP server flying ArduPilot SITL](../../catalog/samples/llm-mission-agent.md) (explains)

_Indexed by lane(s): gap-fill_

_GitHub metadata fetched 2026-11-06._
