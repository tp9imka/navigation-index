# COEX Clover

`repo:copterexpress/clover` - <https://github.com/CopterExpress/clover>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 694 | C++ | MIT | 2026-04-14 | False | production | high |

ROS-based software stack and Raspberry Pi image for the Clover educational quadcopter (PX4 underneath). Ships ArUco marker detection, marker-map navigation published to PX4 as a vision position estimate, downward optical-flow position hold, and a Gazebo simulator. Documentation is written in Russian first, with English translations.

**Why it matters:** One of the most complete Russian-language open stacks for GNSS-free indoor/outdoor flight: optical flow plus marker maps fed into the autopilot EKF, with documented parameter sets.

**Hackathon notes:** Use the Docker/VM simulator image to fly ArUco-map navigation without hardware in hours. The marker-map => VPE path is a ready template for any external position source into PX4. ROS1 (Noetic) based; ROS2 only via community ports. Canonical repo is CopterExpress/clover; klever-coex/clover is a recent fork.

## Deep dives

- [ua-ru-sources-overview](../../docs/landscape/ua-ru-sources-overview.md) (landscape)

**Concepts:** [Visual(-inertial) odometry](../concepts/vio.md), [Autopilots and flight control](../concepts/autopilot.md), [ROS / ROS 2 robotics middleware](../concepts/ros.md), [Simulation and HIL/SITL](../concepts/simulation.md), [MAVLink, ground control and C2 links](../concepts/mavlink-gcs.md)

**Tags:** `lang:ru`, `aruco`, `optical-flow`, `px4`, `raspberry-pi`, `education`, `coex`

**Domains:** air

## Related

- integrates_with: [PX4 Autopilot](../repos/px4__px4-autopilot.md)
- depends_on: [MAVROS](../repos/mavlink__mavros.md)
- part_of: [Навигация по Optical Flow · Clover](../resources/coex-clover-docs-optical-flow-ru.md)

## Referenced by

- [Clover Rescue Project](../repos/devmbs__crtclient.md) (depends_on)
- [Swarm in Blocks](../repos/grupo-semear-usp__swarm_in_blocks.md) (depends_on)
- [Навигация по карте маркеров · Clover](../resources/coex-clover-docs-aruco-map-ru.md) (part_of)
- [Навигация по Optical Flow · Clover](../resources/coex-clover-docs-optical-flow-ru.md) (part_of)
- [CopterHack 2023](../resources/coex-copterhack-2023.md) (uses)

_Indexed by lane(s): ua-ru-sources_

_GitHub metadata fetched 2026-11-06._
