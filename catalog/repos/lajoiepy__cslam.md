# Swarm-SLAM

`repo:lajoiepy/cslam` - <https://github.com/lajoiepy/cslam>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 50 | Python | MIT | 2025-04-10 | False | active-research | medium |

ROS 2 decentralized collaborative SLAM supporting LiDAR, stereo and RGB-D, with sparse inter-robot communication.

**Why it matters:** Designed for bandwidth-limited swarms, a realistic constraint under jamming.

**Hackathon notes:** This repo is only the core cslam ROS 2 package (loop closure detection front end and pose-graph back end); setup, launch files and docs live in the main MISTLab/Swarm-SLAM repo. Experiments run on recorded multi-robot datasets. Pick one sensor type to start.

**Concepts:** [Swarms and multi-agent navigation](../../catalog/concepts/multi-agent.md), [Visual SLAM](../../catalog/concepts/visual-slam.md), [LiDAR odometry and SLAM](../../catalog/concepts/lidar-slam.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `ros2`, `decentralized`, `swarm`

**Domains:** air, ground

## Related

- alternative_to: [Kimera-Multi](../../catalog/repos/mit-spark__kimera-multi.md)
- alternative_to: [COVINS / COVINS-G](../../catalog/repos/v4rl-ucy__covins.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [D2SLAM](../../catalog/repos/hkust-aerial-robotics__d2slam.md) (alternative_to)
- [COVINS / COVINS-G](../../catalog/repos/v4rl-ucy__covins.md) (alternative_to)
- [Swarm-SLAM: Sparse Decentralized Collaborative Simultaneous Localization and Mapping Framework for Multi-Robot Systems](../../catalog/resources/swarm-slam-paper.md) (has_code)

_Indexed by lane(s): slam_

_GitHub metadata fetched 2026-11-06._
