# vision_to_mavros

`repo:thien94/vision_to_mavros` - <https://github.com/thien94/vision_to_mavros>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 295 | Python | GPL-3.0 | 2022-10-28 | False | research-prototype | high |

ROS and Python scripts that convert external localisation (fiducials, T265 VIO, SLAM, depth) into MAVROS/MAVLink pose messages, tested on ArduPilot.

**Why it matters:** Proven recipe for feeding vision-based localisation into ArduPilot EKF3 for GPS-denied flight; came out of GSoC work.

**Hackathon notes:** Old (2022) but simple; adapt the non-ROS T265 script to any VIO source.

## Deep dives

- [_index-flight-c2](../../docs/integration-cards/_index-flight-c2.md) (integration-cards)
- [thien94__vision_to_mavros](../../docs/integration-cards/thien94__vision_to_mavros.md) (integration-cards)

**Concepts:** [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [MAVLink, ground control and C2 links](../../catalog/concepts/mavlink-gcs.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `t265`, `vision_position_estimate`, `apriltag`, `gsoc`

**Domains:** air

## Related

- depends_on: [MAVROS](../../catalog/repos/mavlink__mavros.md)
- integrates_with: [ArduPilot](../../catalog/repos/ardupilot__ardupilot.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [6. Autopilots and C2](../../docs/primer/06-autopilots-and-c2.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [MAVROS](../../catalog/repos/mavlink__mavros.md) (integrates_with)
- [ROS and VIO tracking camera for non-GPS Navigation](../../catalog/resources/ardupilot-ros-vio-tracking-camera.md) (has_code)
- [Intel RealSense T265](../../catalog/resources/ardupilot-vio-tracking-camera.md) (has_code)
- [Spleenlab VISIONAIRY perception and GNSS-free navigation software](../../catalog/resources/spleenlab-visionairy.md) (alternative_to)
- [VIO to MAVLink bridge with ENU/FLU to NED/FRD conversion](../../catalog/samples/vio-to-mavlink-bridge.md) (explains)

_Indexed by lane(s): autopilots_

_GitHub metadata fetched 2026-11-06._
