# DM-VIO

`repo:lukasvst/dm-vio` - <https://github.com/lukasvst/dm-vio>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,237 | C++ | GPL-3.0 | 2024-10-27 | False | research-prototype | medium |

Monocular visual-inertial odometry built on DSO using delayed marginalization and pose-graph bundle adjustment for IMU initialization.

**Why it matters:** Strong monocular VIO accuracy; good for single-camera drones.

**Hackathon notes:** Standalone build with an optional ROS wrapper repo. Expects photometrically calibrated input for best results.

**Concepts:** [Visual(-inertial) odometry](../../catalog/concepts/vio.md)

**Tags:** `direct`, `delayed-marginalization`, `monocular`

**Domains:** air

## Related

- extends: [DSO (Direct Sparse Odometry)](../../catalog/repos/jakobengel__dso.md)

## Referenced by

- [DSO (Direct Sparse Odometry)](../../catalog/repos/jakobengel__dso.md) (extends)

_Indexed by lane(s): slam_

_GitHub metadata fetched 2026-11-06._
