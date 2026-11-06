# LIO-SAM: Tightly-coupled Lidar Inertial Odometry via Smoothing and Mapping

`res:lio-sam-shan-2020` - paper - <https://arxiv.org/abs/2007.00258>

**By:** Tixiao Shan, Brendan Englot, Drew Meyers, Wei Wang, Carlo Ratti, Daniela Rus - **Year:** 2020 - **Level:** advanced - **Access:** open

Formulates LiDAR-inertial odometry as factor-graph smoothing with IMU preintegration, LiDAR odometry, GPS and loop-closure factors.

## Key takeaways

- Factor graphs make it straightforward to add or drop GNSS
- Keyframe-local scan matching keeps it real time

**Concepts:** [LiDAR odometry and SLAM](../../catalog/concepts/lidar-slam.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [GNSS/INS integration](../../catalog/concepts/gnss-ins.md)

**Tags:** `factor-graph`, `gtsam`

## Related

- has_code: [LIO-SAM](../../catalog/repos/tixiaoshan__lio-sam.md)

## Referenced by

- [4. Vision, LiDAR and radar odometry](../../docs/primer/04-vision-lidar-radar-odometry.md) (mentions)

_Indexed by lane(s): slam_
