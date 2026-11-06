# MIMOSA

`repo:ntnu-arl/mimosa` - <https://github.com/ntnu-arl/mimosa>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 131 | C++ | BSD-3-Clause | 2026-10-01 | False | active-research | medium |

Tightly coupled sliding-window factor-graph fusion of IMU with LiDAR (geometric and photometric), radar radial-speed factors and external odometry such as VIO.

**Why it matters:** From the group behind DARPA SubT field robots; relevant to smoke/dark/dust scenarios.

**Hackathon notes:** ROS Noetic; publishes nav_msgs/Odometry. Radar factor lets you keep velocity constraints when LiDAR is blinded by dust or smoke.

**Concepts:** [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [LiDAR odometry and SLAM](../concepts/lidar-slam.md), [Radar navigation and odometry](../concepts/radar-nav.md)

**Tags:** `multi-modal`, `subterranean`, `2025`

**Domains:** air, ground

## Related

- same_org: [ROVTIO](../repos/ntnu-arl__rovtio.md)

_Indexed by lane(s): slam_

_GitHub metadata fetched 2026-11-06._
