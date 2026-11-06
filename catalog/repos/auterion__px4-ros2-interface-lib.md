# PX4 ROS 2 Interface Library

`repo:auterion/px4-ros2-interface-lib` - <https://github.com/Auterion/px4-ros2-interface-lib>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 187 | C++ | BSD-3-Clause | 2026-11-04 | False | production | high |

C++ library for writing PX4 flight modes and navigation-data sources in ROS 2 on a companion computer, registered with PX4 as first-class modes.

**Why it matters:** Lets a team ship a custom autonomy mode or inject a local/global position estimate (e.g. a visual geolocalisation fix) cleanly into PX4.

**Hackathon notes:** Needs recent PX4 (1.15+) and matching px4_msgs; examples include custom modes and external navigation interfaces.

## Deep dives

- [_index-flight-c2](../../docs/integration-cards/_index-flight-c2.md) (integration-cards)
- [auterion__px4-ros2-interface-lib](../../docs/integration-cards/auterion__px4-ros2-interface-lib.md) (integration-cards)

**Concepts:** [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md), [Autopilots and flight control](../../catalog/concepts/autopilot.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `ros2`, `flight-modes`, `companion`, `auterion`

**Domains:** air

## Related

- integrates_with: [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md)
- depends_on: [px4_msgs](../../catalog/repos/px4__px4_msgs.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [px4_ros_com](../../catalog/repos/px4__px4_ros_com.md) (alternative_to)

_Indexed by lane(s): autopilots_

_GitHub metadata fetched 2026-11-06._
