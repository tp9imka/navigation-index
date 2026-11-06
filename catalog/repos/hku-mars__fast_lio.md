# FAST-LIO / FAST-LIO2

`repo:hku-mars/fast_lio` - <https://github.com/hku-mars/FAST_LIO>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 5,348 | C++ | GPL-2.0 | 2026-10-25 | False | production | high |

Computationally efficient LiDAR-inertial odometry using an iterated error-state Kalman filter and incremental k-d tree map, mapping raw points directly.

**Why it matters:** The default LIO in many field robots; runs on ARM boards and supports solid-state and spinning LiDARs.

**Hackathon notes:** Easiest LIO to get running; Livox drivers supported. No loop closure; pair with a localization or loop-closure add-on.

**Concepts:** [LiDAR odometry and SLAM](../concepts/lidar-slam.md), [Inertial navigation (INS/IMU)](../concepts/ins.md)

**Tags:** `iekf`, `ikd-tree`, `livox`, `ros1`

**Domains:** air, ground

## Related

- alternative_to: [Point-LIO](../repos/hku-mars__point-lio.md)
- extends: [FAST_LIO_LOCALIZATION](../repos/hviktortsoi__fast_lio_localization.md)
- integrates_with: [livox_ros_driver2](../repos/livox-sdk__livox_ros_driver2.md)
- alternative_to: [Faster-LIO](../repos/gaoxiang12__faster-lio.md)

## Referenced by

- [Faster-LIO](../repos/gaoxiang12__faster-lio.md) (alternative_to)
- [FAST-LIVO2](../repos/hku-mars__fast-livo2.md) (extends)
- [LiDAR_IMU_Init](../repos/hku-mars__lidar_imu_init.md) (integrates_with)
- [Point-LIO](../repos/hku-mars__point-lio.md) (alternative_to)
- [STD](../repos/hku-mars__std.md) (integrates_with)
- [FAST_LIO_LOCALIZATION](../repos/hviktortsoi__fast_lio_localization.md) (extends)
- [livox_ros_driver2](../repos/livox-sdk__livox_ros_driver2.md) (integrates_with)
- [RKO-LIO](../repos/prbonn__rko_lio.md) (alternative_to)
- [LIO-SAM](../repos/tixiaoshan__lio-sam.md) (alternative_to)
- [DLIO](../repos/vectr-ucla__direct_lidar_inertial_odometry.md) (alternative_to)
- [FAST-LIO2: Fast Direct LiDAR-inertial Odometry](../resources/fast-lio2-xu-2021.md) (has_code)
- [LiDAR Odometry Survey: Recent Advancements and Remaining Challenges](../resources/lee-lidar-odometry-survey-2023.md) (cites)

_Indexed by lane(s): slam_

_GitHub metadata fetched 2026-11-06._
