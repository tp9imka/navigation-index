# COVINS / COVINS-G

`repo:v4rl-ucy/covins` - <https://github.com/v4rl-ucy/covins>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 465 | C++ | ? | 2023-12-01 | False | research-prototype | medium |

Centralized collaborative visual-inertial SLAM where agents run VIO and a server merges maps; COVINS-G is VIO-front-end agnostic.

**Why it matters:** Pattern for drones sharing maps through a ground station.

**Hackathon notes:** ROS 1 + Docker; COVINS-G can take poses from any VIO such as OpenVINS.

**Concepts:** [Swarms and multi-agent navigation](../../catalog/concepts/multi-agent.md), [Visual(-inertial) odometry](../../catalog/concepts/vio.md)

**Tags:** `centralized`, `map-merging`, `ros1`

**Domains:** air

## Related

- integrates_with: [OpenVINS](../../catalog/repos/rpng__open_vins.md)
- alternative_to: [Swarm-SLAM](../../catalog/repos/lajoiepy__cslam.md)

## Referenced by

- [Swarm-SLAM](../../catalog/repos/lajoiepy__cslam.md) (alternative_to)

_Indexed by lane(s): slam_

_GitHub metadata fetched 2026-11-06._
