# RINO

`repo:yangsc4063/rino` - <https://github.com/yangsc4063/rino>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 72 | C++ | ? | 2025-09-18 | False | research-prototype | low |

Non-iterative, adaptively loosely coupled radar-inertial odometry for spinning (scanning) radar, built on the ORORA radar odometry baseline; the radar pose uncertainty from its voting step feeds a Kalman filter (T-ASE 2025).

**Why it matters:** Recent scanning-radar inertial method to benchmark against.

**Hackathon notes:** ROS Noetic / Ubuntu 20.04, catkin build, Sophus built manually. Replay MulRan with its file player (radar + IMU); a Boreas demo is shown.

**Concepts:** [Radar navigation and odometry](../../catalog/concepts/radar-nav.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `radar-inertial`, `scanning-radar`, `2025`

**Domains:** ground

## Related

- alternative_to: [STEAM-ICP](../../catalog/repos/utiasasrl__steam_icp.md)

_Indexed by lane(s): gap-fill_

_GitHub metadata fetched 2026-11-06._
