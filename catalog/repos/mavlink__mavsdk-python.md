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

**Concepts:** [MAVLink, ground control and C2 links](../concepts/mavlink-gcs.md), [Autopilots and flight control](../concepts/autopilot.md)

**Tags:** `python`, `asyncio`, `offboard`

**Domains:** air

## Related

- depends_on: [MAVSDK](../repos/mavlink__mavsdk.md)
- alternative_to: [DroneKit-Python](../repos/dronekit__dronekit-python.md)

## Referenced by

- [DroneKit-Python](../repos/dronekit__dronekit-python.md) (alternative_to)
- [MAVLinkMCP](../repos/ion-g-ion__mavlinkmcp.md) (depends_on)
- [MAVSDK](../repos/mavlink__mavsdk.md) (integrates_with)
- [PX4 SITL GPS denial: inject, measure drift, recover](../samples/px4-sitl-gps-denial.md) (uses)

_Indexed by lane(s): autopilots_

_GitHub metadata fetched 2026-11-06._
