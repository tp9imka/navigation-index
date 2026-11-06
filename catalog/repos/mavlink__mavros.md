# MAVROS

`repo:mavlink/mavros` - <https://github.com/mavlink/mavros>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,249 | C++ | NOASSERTION | 2026-11-06 | False | production | high |

ROS/ROS 2 node bridging MAVLink to ROS topics and services, with GCS proxy; widely used to push vision/SLAM poses into PX4 or ArduPilot.

**Why it matters:** Standard glue between ROS-based VIO/SLAM and a flight controller for GPS-denied navigation.

**Hackathon notes:** apt install ros-<distro>-mavros, then run install_geographiclib_datasets.sh; current MAVROS targets ROS 2 (Humble and newer). Feed your odometry into /mavros/vision_pose/pose.

## Deep dives

- [_index-flight-c2](../../docs/integration-cards/_index-flight-c2.md) (integration-cards)
- [mavlink__mavros](../../docs/integration-cards/mavlink__mavros.md) (integration-cards)

**Concepts:** [MAVLink, ground control and C2 links](../../catalog/concepts/mavlink-gcs.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md), [Visual(-inertial) odometry](../../catalog/concepts/vio.md)

**Tags:** `ros`, `ros2`, `bridge`, `vision_pose`, `mavlink`, `gateway`

**Domains:** air, ground, maritime, underwater

## Related

- integrates_with: [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md)
- integrates_with: [ArduPilot](../../catalog/repos/ardupilot__ardupilot.md)
- integrates_with: [vision_to_mavros](../../catalog/repos/thien94__vision_to_mavros.md)
- alternative_to: [px4_ros_com](../../catalog/repos/px4__px4_ros_com.md)
- integrates_with: [OpenVINS](../../catalog/repos/rpng__open_vins.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [ArduPilot](../../catalog/repos/ardupilot__ardupilot.md) (integrates_with)
- [COEX Clover](../../catalog/repos/copterexpress__clover.md) (depends_on)
- [MAVSDK](../../catalog/repos/mavlink__mavsdk.md) (alternative_to)
- [px4_ros_com](../../catalog/repos/px4__px4_ros_com.md) (alternative_to)
- [vision_to_mavros](../../catalog/repos/thien94__vision_to_mavros.md) (depends_on)
- [ROS and VIO tracking camera for non-GPS Navigation](../../catalog/resources/ardupilot-ros-vio-tracking-camera.md) (uses)
- [Using Vision or Motion Capture Systems for Position Estimation](../../catalog/resources/px4-external-position-estimation.md) (uses)
- [VIO to MAVLink bridge with ENU/FLU to NED/FRD conversion](../../catalog/samples/vio-to-mavlink-bridge.md) (explains)

_Indexed by lane(s): autopilots, domains-swarm_

_GitHub metadata fetched 2026-11-06._
