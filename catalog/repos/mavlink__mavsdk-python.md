# MAVSDK-Python

`repo:mavlink/mavsdk-python` - <https://github.com/mavlink/MAVSDK-Python>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 458 | Python | BSD-3-Clause | 2026-10-15 | False | production | high |

Asyncio Python client for MAVSDK that wraps a bundled mavsdk_server.

**Why it matters:** Probably the fastest way to script missions or offboard control against PX4 SITL.

**Hackathon notes:** pip install mavsdk-grpc and import mavsdk_grpc (the PyPI name 'mavsdk' now means the native binding with a different API); examples cover takeoff, missions, offboard velocity.

## Deep dives

- [_index-flight-c2](../../docs/integration-cards/_index-flight-c2.md) (integration-cards)
- [mavlink__mavsdk-python](../../docs/integration-cards/mavlink__mavsdk-python.md) (integration-cards)

**Concepts:** [MAVLink, ground control and C2 links](../../catalog/concepts/mavlink-gcs.md), [Autopilots and flight control](../../catalog/concepts/autopilot.md)

**Tags:** `python`, `asyncio`, `offboard`

**Domains:** air

## Related

- depends_on: [MAVSDK](../../catalog/repos/mavlink__mavsdk.md)
- alternative_to: [DroneKit-Python](../../catalog/repos/dronekit__dronekit-python.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [6. Autopilots and C2](../../docs/primer/06-autopilots-and-c2.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [DroneKit-Python](../../catalog/repos/dronekit__dronekit-python.md) (alternative_to)
- [Полёт вслепую - GCS with terrain-referenced navigation](../../catalog/repos/drones-voronka__drones-backend.md) (depends_on)
- [MAVLinkMCP](../../catalog/repos/ion-g-ion__mavlinkmcp.md) (depends_on)
- [MAVSDK](../../catalog/repos/mavlink__mavsdk.md) (integrates_with)
- [LLM mission agent: a safety-gated MAVLink MCP server flying ArduPilot SITL](../../catalog/samples/llm-mission-agent.md) (explains)
- [PX4 SITL GPS denial: inject, measure drift, recover](../../catalog/samples/px4-sitl-gps-denial.md) (uses)
- [Headless SITL in Docker: ArduCopter and PX4 SIH with one compose file](../../catalog/samples/sitl-docker.md) (uses)

_Indexed by lane(s): autopilots_

_GitHub metadata fetched 2026-11-06._
