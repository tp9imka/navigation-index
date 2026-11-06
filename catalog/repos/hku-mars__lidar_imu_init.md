# LiDAR_IMU_Init

`repo:hku-mars/lidar_imu_init` - <https://github.com/hku-mars/LiDAR_IMU_Init>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,539 | C++ | GPL-2.0 | 2026-04-30 | False | active-research | medium |

Real-time LiDAR-inertial initialization estimating extrinsics, time offset, gravity and IMU bias online (IROS 2022).

**Why it matters:** Removes the extrinsic-calibration blocker when bolting a LiDAR and IMU onto a new platform.

**Hackathon notes:** Builds like FAST_LIO; feed a bag with aggressive motion at start.

**Concepts:** [Sensor calibration](../../catalog/concepts/calibration.md), [LiDAR odometry and SLAM](../../catalog/concepts/lidar-slam.md), [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md)

**Tags:** `lidar-imu`, `online-init`, `fast-lio`, `extrinsics`, `time-offset`, `ros1`

**Domains:** ground, air

## Related

- integrates_with: [FAST-LIO / FAST-LIO2](../../catalog/repos/hku-mars__fast_lio.md)
- alternative_to: [LI-Calib](../../catalog/repos/april-zju__lidar_imu_calib.md)

## Referenced by

- [lidar_imu_calib](../../catalog/repos/chennuo0125-hit__lidar_imu_calib.md) (alternative_to)

_Indexed by lane(s): ins-fusion, slam_

_GitHub metadata fetched 2026-11-06._
