# tercom_nav (TERCOM + ESKF)

`repo:mzahana/tercom_nav` - <https://github.com/mzahana/tercom_nav>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 85 | Python | ? | 2026-04-26 | False | research-prototype | high |

ROS 2 package combining TERCOM-style terrain matching with an error-state Kalman filter for UAV navigation.

**Why it matters:** Bridges batch terrain matching into a recursive filter that a real autopilot stack could consume.

**Hackathon notes:** Good if your team runs ROS 2 with PX4/ArduPilot SITL; pair with a DEM and simulated altimeter.

**Concepts:** [Terrain-relative navigation](../concepts/terrain-nav.md), [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [ROS / ROS 2 robotics middleware](../concepts/ros.md)

**Tags:** `ros2`, `eskf`, `tercom`

**Domains:** air

## Related

- alternative_to: [python-tercom](../repos/alti3__python-tercom.md)

## Referenced by

- [python-tercom](../repos/alti3__python-tercom.md) (alternative_to)
- [TRN particle filter examples](../repos/rhymesg__particle_filter.md) (alternative_to)
- [Terrain-relative navigation with a particle filter](../samples/terrain-relative-nav-pf.md) (explains)

_Indexed by lane(s): alt-nav_

_GitHub metadata fetched 2026-11-06._
