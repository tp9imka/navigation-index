# tercom_nav (TERCOM + ESKF)

`repo:mzahana/tercom_nav` - <https://github.com/mzahana/tercom_nav>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 85 | Python | ? | 2026-04-26 | False | research-prototype | high |

ROS 2 (Humble) package for GPS-denied fixed-wing UAV navigation: a TERCOM node correlates baro + rangefinder terrain profiles against a GeoTIFF DEM and feeds fixes into a 15-state error-state Kalman filter driven by IMU, baro and velocity updates.

**Why it matters:** Bridges batch terrain matching into a recursive filter that a real autopilot stack could consume.

**Hackathon notes:** Tested against PX4 SITL + Gazebo via MAVROS (no ArduPilot setup documented); colcon build, then launch with a GeoTIFF DEM path and world origin. GPS is used once to initialise the filter. Needs a rangefinder and barometer, real or simulated.

## Deep dives

- [_index-perception-altnav](../../docs/integration-cards/_index-perception-altnav.md) (integration-cards)
- [mzahana__tercom_nav](../../docs/integration-cards/mzahana__tercom_nav.md) (integration-cards)

**Concepts:** [Terrain-relative navigation](../concepts/terrain-nav.md), [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [ROS / ROS 2 robotics middleware](../concepts/ros.md)

**Tags:** `ros2`, `eskf`, `tercom`

**Domains:** air

## Related

- alternative_to: [python-tercom](../repos/alti3__python-tercom.md)

## Referenced by

- [python-tercom](../repos/alti3__python-tercom.md) (alternative_to)
- [TRN particle filter examples](../repos/rhymesg__particle_filter.md) (alternative_to)
- [FlyingBlind_Hakaton](../repos/solarwarlock__flyingblind_hakaton.md) (alternative_to)
- [Terrain-relative navigation with a particle filter](../samples/terrain-relative-nav-pf.md) (explains)

_Indexed by lane(s): alt-nav_

_GitHub metadata fetched 2026-11-06._
