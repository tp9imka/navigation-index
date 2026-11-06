# px4_msgs

`repo:px4/px4_msgs` - <https://github.com/PX4/px4_msgs>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 163 | Shell | BSD-3-Clause | 2026-11-05 | False | production | high |

ROS 2 message definitions mirroring PX4 uORB topics, used with the uXRCE-DDS bridge.

**Why it matters:** Required to talk to PX4 natively from ROS 2 (e.g. VehicleOdometry for external vision).

**Hackathon notes:** Match the branch to your PX4 version or messages will mismatch.

**Concepts:** [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md), [Autopilots and flight control](../../catalog/concepts/autopilot.md)

**Tags:** `ros2`, `uorb`, `dds`

**Domains:** air

## Related

- depends_on: [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md)
- integrates_with: [px4_ros_com](../../catalog/repos/px4__px4_ros_com.md)
- integrates_with: [Micro XRCE-DDS Agent](../../catalog/repos/eprosima__micro-xrce-dds-agent.md)

## Referenced by

- [6. Autopilots and C2](../../docs/primer/06-autopilots-and-c2.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [ROS2 PX4 Offboard Example](../../catalog/repos/ark-electronics__ros2_px4_offboard_example.md) (depends_on)
- [PX4 ROS 2 Interface Library](../../catalog/repos/auterion__px4-ros2-interface-lib.md) (depends_on)
- [Micro XRCE-DDS Agent](../../catalog/repos/eprosima__micro-xrce-dds-agent.md) (integrates_with)
- [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md) (integrates_with)
- [px4_ros_com](../../catalog/repos/px4__px4_ros_com.md) (depends_on)

_Indexed by lane(s): autopilots_

_GitHub metadata fetched 2026-11-06._
