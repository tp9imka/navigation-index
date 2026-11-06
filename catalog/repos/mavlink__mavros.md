# MAVROS

`repo:mavlink/mavros` - <https://github.com/mavlink/mavros>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,249 | C++ | NOASSERTION | 2026-11-06 | False | production | high |

ROS/ROS 2 node bridging MAVLink to ROS topics and services, with GCS proxy; widely used to push vision/SLAM poses into PX4 or ArduPilot.

**Why it matters:** Standard glue between ROS-based VIO/SLAM and a flight controller for GPS-denied navigation.

**Hackathon notes:** Publish to /mavros/vision_pose/pose or odometry topics; mind ENU/NED frame conversions.

## Deep dives

- [mavlink__mavros](../../docs/integration-cards/mavlink__mavros.md) (integration-cards)

**Concepts:** [MAVLink, ground control and C2 links](../concepts/mavlink-gcs.md), [ROS / ROS 2 robotics middleware](../concepts/ros.md), [Visual(-inertial) odometry](../concepts/vio.md)

**Tags:** `ros`, `ros2`, `bridge`, `vision_pose`, `mavlink`, `gateway`

**Domains:** air, ground, maritime, underwater

## Related

- integrates_with: [PX4 Autopilot](../repos/px4__px4-autopilot.md)
- integrates_with: [ArduPilot](../repos/ardupilot__ardupilot.md)
- integrates_with: [vision_to_mavros](../repos/thien94__vision_to_mavros.md)
- alternative_to: [px4_ros_com](../repos/px4__px4_ros_com.md)
- integrates_with: [OpenVINS](../repos/rpng__open_vins.md)

## Referenced by

- [ArduPilot](../repos/ardupilot__ardupilot.md) (integrates_with)
- [COEX Clover](../repos/copterexpress__clover.md) (depends_on)
- [MAVSDK](../repos/mavlink__mavsdk.md) (alternative_to)
- [px4_ros_com](../repos/px4__px4_ros_com.md) (alternative_to)
- [vision_to_mavros](../repos/thien94__vision_to_mavros.md) (depends_on)
- [ROS and VIO tracking camera for non-GPS navigation](../resources/ardupilot-ros-vio-tracking-camera.md) (uses)
- [Using Vision or Motion Capture Systems for Position Estimation](../resources/px4-external-position-estimation.md) (uses)
- [VIO to MAVLink bridge with ENU/FLU to NED/FRD conversion](../samples/vio-to-mavlink-bridge.md) (explains)

_Indexed by lane(s): autopilots, domains-swarm_

_GitHub metadata fetched 2026-11-06._
