# Micro XRCE-DDS Agent

`repo:eprosima/micro-xrce-dds-agent` - <https://github.com/eProsima/Micro-XRCE-DDS-Agent>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 213 | C++ | Apache-2.0 | 2026-09-03 | False | production | medium |

Agent that bridges DDS-XRCE clients on microcontrollers into a full DDS / ROS 2 graph; PX4 and ArduPilot use it for native ROS 2.

**Why it matters:** Core link in the PX4 and ArduPilot ROS 2 (DDS) paths.

**Build notes:** Install via snap or build from source; run MicroXRCEAgent udp4 -p 8888 for SITL.

## Deep dives

- [_index-round3](../../docs/integration-cards/_index-round3.md) (integration-cards)
- [eprosima__micro-xrce-dds-agent](../../docs/integration-cards/eprosima__micro-xrce-dds-agent.md) (integration-cards)

**Concepts:** [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `dds`, `xrce`, `ros2`, `bridge`

**Domains:** multi

## Related

- integrates_with: [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md)
- integrates_with: [ArduPilot](../../catalog/repos/ardupilot__ardupilot.md)
- integrates_with: [px4_msgs](../../catalog/repos/px4__px4_msgs.md)

## Referenced by

- [Integration cards](../../docs/integration-cards/README.md) (mentions)
- [Path to product: from a nav algorithm to something that flies](../../docs/path-to-product.md) (mentions)
- [ardupilot_ros](../../catalog/repos/ardupilot__ardupilot_ros.md) (depends_on)
- [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md) (integrates_with)
- [px4_msgs](../../catalog/repos/px4__px4_msgs.md) (integrates_with)
- [PX4 uXRCE-DDS (PX4-ROS 2/DDS Bridge)](../../catalog/resources/px4-uxrce-dds-docs.md) (uses)

_Indexed by lane(s): autopilots_

_GitHub metadata fetched 2026-11-23._
