# VINS-Fusion

`repo:hkust-aerial-robotics/vins-fusion` - <https://github.com/HKUST-Aerial-Robotics/VINS-Fusion>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 4,776 | C++ | GPL-3.0 | 2024-05-23 | False | research-prototype | medium |

Extension of VINS-Mono supporting mono+IMU, stereo, and stereo+IMU, with optional loose fusion of global sensors such as GPS.

**Why it matters:** Shows how to plug intermittent GNSS into a VIO estimator, which is the core pattern for degraded-PNT navigation.

**Hackathon notes:** ROS 1; use a Docker image. The global-fusion node is a good template for injecting GNSS when it is trusted and dropping it when jammed.

**Concepts:** [Visual(-inertial) odometry](../concepts/vio.md), [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [GNSS/INS integration](../concepts/gnss-ins.md)

**Tags:** `stereo`, `gps-fusion`, `ceres`, `ros1`

**Domains:** air, ground

## Related

- extends: [VINS-Mono](../repos/hkust-aerial-robotics__vins-mono.md)

## Referenced by

- [Ceres Solver](../repos/ceres-solver__ceres-solver.md) (integrates_with)
- [VINS-Mono](../repos/hkust-aerial-robotics__vins-mono.md) (alternative_to)

_Indexed by lane(s): slam_

_GitHub metadata fetched 2026-11-06._
