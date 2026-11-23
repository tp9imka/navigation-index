# ROVIO

`repo:ethz-asl/rovio` - <https://github.com/ethz-asl/rovio>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 1,275 | C++ | NOASSERTION | 2026-09-03 | False | research-prototype | medium |

Robust visual-inertial odometry using an iterated EKF directly on image-patch photometric errors.

**Why it matters:** Long a go-to VIO on PX4/MAV research platforms because it is cheap to run.

**Build notes:** ROS 1 / catkin. Lightweight; tuning of patch and feature counts matters.

**Concepts:** [Visual(-inertial) odometry](../../catalog/concepts/vio.md)

**Tags:** `iekf`, `patch-based`, `ros1`

**Domains:** air

## Related

- extends: [ROVTIO](../../catalog/repos/ntnu-arl__rovtio.md)

## Referenced by

- [ethzasl_msf (Multi Sensor Fusion)](../../catalog/repos/ethz-asl__ethzasl_msf.md) (same_org)
- [ROVTIO](../../catalog/repos/ntnu-arl__rovtio.md) (extends)
- [SVO Pro](../../catalog/repos/uzh-rpg__rpg_svo_pro_open.md) (alternative_to)
- [A Benchmark Comparison of Monocular Visual-Inertial Odometry Algorithms for Flying Robots](../../catalog/resources/delmerico-scaramuzza-2018-vio-benchmark-flying-robots.md) (evaluates)
- [Run Your Visual-Inertial Odometry on NVIDIA Jetson: Benchmark Tests on a Micro Aerial Vehicle](../../catalog/resources/jeon-2021-vio-jetson-benchmark.md) (evaluates)

_Indexed by lane(s): slam_

_GitHub metadata fetched 2026-11-23._
