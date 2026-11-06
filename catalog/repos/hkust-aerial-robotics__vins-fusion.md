# VINS-Fusion

`repo:hkust-aerial-robotics/vins-fusion` - <https://github.com/HKUST-Aerial-Robotics/VINS-Fusion>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 4,776 | C++ | GPL-3.0 | 2024-05-23 | False | research-prototype | medium |

Extension of VINS-Mono supporting mono+IMU, stereo, and stereo+IMU, with optional loose fusion of global sensors such as GPS.

**Why it matters:** Shows how to plug intermittent GNSS into a VIO estimator, which is the core pattern for degraded-PNT navigation.

**Hackathon notes:** ROS 1; use a Docker image. The global-fusion node is a good template for injecting GNSS when it is trusted and dropping it when jammed.

**Concepts:** [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [GNSS/INS integration](../../catalog/concepts/gnss-ins.md)

**Tags:** `stereo`, `gps-fusion`, `ceres`, `ros1`

**Domains:** air, ground

## Related

- extends: [VINS-Mono](../../catalog/repos/hkust-aerial-robotics__vins-mono.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [4. Vision, LiDAR and radar odometry](../../docs/primer/04-vision-lidar-radar-odometry.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [Ceres Solver](../../catalog/repos/ceres-solver__ceres-solver.md) (integrates_with)
- [GVINS](../../catalog/repos/hkust-aerial-robotics__gvins.md) (extends)
- [VINS-Mono](../../catalog/repos/hkust-aerial-robotics__vins-mono.md) (alternative_to)
- [VIO to MAVLink bridge with ENU/FLU to NED/FRD conversion](../../catalog/samples/vio-to-mavlink-bridge.md) (explains)

_Indexed by lane(s): slam_

_GitHub metadata fetched 2026-11-06._
