# Micro XRCE-DDS Agent

`repo:eprosima/micro-xrce-dds-agent` - <https://github.com/eProsima/Micro-XRCE-DDS-Agent>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 211 | C++ | Apache-2.0 | 2026-09-03 | False | production | medium |

Agent that bridges DDS-XRCE clients on microcontrollers into a full DDS / ROS 2 graph; PX4 and ArduPilot use it for native ROS 2.

**Why it matters:** Core link in the PX4 and ArduPilot ROS 2 (DDS) paths.

**Hackathon notes:** Install via snap or build from source; run MicroXRCEAgent udp4 -p 8888 for SITL.

## Deep dives

- [_index-round3](../../docs/integration-cards/_index-round3.md) (integration-cards)
- [eprosima__micro-xrce-dds-agent](../../docs/integration-cards/eprosima__micro-xrce-dds-agent.md) (integration-cards)

**Concepts:** [ROS / ROS 2 robotics middleware](../concepts/ros.md)

**Tags:** `dds`, `xrce`, `ros2`, `bridge`

**Domains:** multi

## Related

- integrates_with: [PX4 Autopilot](../repos/px4__px4-autopilot.md)
- integrates_with: [ArduPilot](../repos/ardupilot__ardupilot.md)
- integrates_with: [px4_msgs](../repos/px4__px4_msgs.md)

## Referenced by

- [ardupilot_ros](../repos/ardupilot__ardupilot_ros.md) (depends_on)
- [PX4 Autopilot](../repos/px4__px4-autopilot.md) (integrates_with)
- [px4_msgs](../repos/px4__px4_msgs.md) (integrates_with)

_Indexed by lane(s): autopilots_

_GitHub metadata fetched 2026-11-06._
