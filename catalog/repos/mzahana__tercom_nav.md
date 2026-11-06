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
- [blind-flight-teardown](../../docs/landscape/blind-flight-teardown.md) (landscape)

**Concepts:** [Terrain-relative navigation](../../catalog/concepts/terrain-nav.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `ros2`, `eskf`, `tercom`

**Domains:** air

## Related

- alternative_to: [python-tercom](../../catalog/repos/alti3__python-tercom.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- ["Polyot vslepuyu" (Blind flight) 2026: problem teardown and seven public solutions](../../docs/landscape/blind-flight-teardown.md) (mentions)
- [5. Absolute alternative PNT](../../docs/primer/05-absolute-alt-pnt.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Docs map](../../docs/README.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [python-tercom](../../catalog/repos/alti3__python-tercom.md) (alternative_to)
- [Gagarin - TERCOM for UAVs without GNSS](../../catalog/repos/danilka88__gag27062026.md) (alternative_to)
- [TRN particle filter examples](../../catalog/repos/rhymesg__particle_filter.md) (alternative_to)
- [FlyingBlind_Hakaton](../../catalog/repos/solarwarlock__flyingblind_hakaton.md) (alternative_to)
- [Terrain Contour Matching (TERCOM): A Cruise Missile Guidance Aid](../../catalog/resources/golden-1980-tercom.md) (explains)
- [Terrain-relative navigation with a particle filter](../../catalog/samples/terrain-relative-nav-pf.md) (explains)

_Indexed by lane(s): alt-nav_

_GitHub metadata fetched 2026-11-06._
