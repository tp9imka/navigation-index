# COEX Clover

`repo:copterexpress/clover` - <https://github.com/CopterExpress/clover>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 694 | C++ | MIT | 2026-04-14 | False | production | high |

ROS-based software stack and Raspberry Pi image for the Clover educational quadcopter (PX4 underneath). Ships ArUco marker detection, marker-map navigation published to PX4 as a vision position estimate, downward optical-flow position hold, and a Gazebo simulator. Documentation is written in Russian first, with English translations.

**Why it matters:** One of the most complete Russian-language open stacks for GNSS-free indoor/outdoor flight: optical flow plus marker maps fed into the autopilot EKF, with documented parameter sets.

**Hackathon notes:** Use the Docker/VM simulator image to fly ArUco-map navigation without hardware in hours. The marker-map => VPE path is a ready template for any external position source into PX4. ROS1 (Noetic) based; ROS2 only via community ports. Canonical repo is CopterExpress/clover; klever-coex/clover is a recent fork.

## Deep dives

- [_index-round5-c2-gis](../../docs/integration-cards/_index-round5-c2-gis.md) (integration-cards)
- [copterexpress__clover](../../docs/integration-cards/copterexpress__clover.md) (integration-cards)
- [ua-ru-sources-overview](../../docs/landscape/ua-ru-sources-overview.md) (landscape)

**Concepts:** [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Autopilots and flight control](../../catalog/concepts/autopilot.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md), [MAVLink, ground control and C2 links](../../catalog/concepts/mavlink-gcs.md)

**Tags:** `lang:ru`, `aruco`, `optical-flow`, `px4`, `raspberry-pi`, `education`, `coex`

**Domains:** air

## Related

- integrates_with: [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md)
- depends_on: [MAVROS](../../catalog/repos/mavlink__mavros.md)
- part_of: [Навигация по Optical Flow · Clover](../../catalog/resources/coex-clover-docs-optical-flow-ru.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Ukrainian- and Russian-language sources: what they add](../../docs/landscape/ua-ru-sources-overview.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Clover Rescue Project](../../catalog/repos/devmbs__crtclient.md) (depends_on)
- [CRTClover - Clover Rescue Team backend](../../catalog/repos/devmbs__crtclover.md) (integrates_with)
- [Swarm in Blocks](../../catalog/repos/grupo-semear-usp__swarm_in_blocks.md) (depends_on)
- [TPU_2 (CopterHack 2023) - flight through forest](../../catalog/repos/shamoleg__clover.md) (fork_of)
- [V-NAV (CopterHack 2022) - visual navigation for Clover](../../catalog/repos/v-nav__clover.md) (fork_of)
- [Навигация по карте маркеров · Clover](../../catalog/resources/coex-clover-docs-aruco-map-ru.md) (part_of)
- [Навигация по Optical Flow · Clover](../../catalog/resources/coex-clover-docs-optical-flow-ru.md) (part_of)
- [CopterHack 2023](../../catalog/resources/coex-copterhack-2023.md) (uses)

_Indexed by lane(s): ua-ru-sources_

_GitHub metadata fetched 2026-11-06._
