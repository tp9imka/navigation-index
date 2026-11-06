# DSO (Direct Sparse Odometry)

`repo:jakobengel/dso` - <https://github.com/JakobEngel/dso>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 2,462 | C++ | GPL-3.0 | 2024-02-23 | False | research-prototype | low |

Direct monocular visual odometry that optimizes photometric error over a sparse set of pixels with joint photometric calibration.

**Why it matters:** Works in low-texture scenes where feature-based methods fail; the basis for DM-VIO and many direct methods.

**Hackathon notes:** No IMU, no loop closure, scale-ambiguous; mostly useful as a building block or comparison.

**Concepts:** [Visual SLAM](../concepts/visual-slam.md)

**Tags:** `direct`, `photometric`, `monocular`

**Domains:** air, ground

## Related

- extends: [DM-VIO](../repos/lukasvst__dm-vio.md)

## Referenced by

- [DM-VIO](../repos/lukasvst__dm-vio.md) (extends)

_Indexed by lane(s): slam_

_GitHub metadata fetched 2026-11-06._
