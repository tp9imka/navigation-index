# CFEAR Radarodometry

`repo:dan11003/cfear_radarodometry` - <https://github.com/dan11003/CFEAR_Radarodometry>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 64 | C++ | GPL-3.0 | 2024-10-17 | False | research-prototype | medium |

Learning-free spinning-radar odometry that filters returns to sparse oriented surface points and registers against keyframes.

**Why it matters:** Strong baseline for spinning (Navtech-style) radar odometry; robust in weather that defeats LiDAR.

**Hackathon notes:** ROS 1; benchmarked on Oxford Radar RobotCar and Boreas.

## Deep dives

- [boreas](../../docs/dataset-cards/boreas.md) (dataset-cards)
- [oxford-radar-robotcar](../../docs/dataset-cards/oxford-radar-robotcar.md) (dataset-cards)
- [cfear-radarodometry-adolfsson-2021](../../docs/paper-digests/cfear-radarodometry-adolfsson-2021.md) (paper-digests)

**Concepts:** [Radar navigation and odometry](../concepts/radar-nav.md)

**Tags:** `spinning-radar`, `oxford-radar`, `ros1`

**Domains:** ground

## Related

- alternative_to: [4DRadarSLAM](../repos/zhuge2333__4dradarslam.md)

## Referenced by

- [TBV Radar SLAM](../repos/dan11003__tbv_slam_public.md) (extends)
- [ORORA](../repos/url-kaist__outlier-robust-radar-odometry.md) (alternative_to)
- [4DRadarSLAM](../repos/zhuge2333__4dradarslam.md) (alternative_to)
- [CFEAR Radarodometry - Conservative Filtering for Efficient and Accurate Radar Odometry](../resources/cfear-radarodometry-adolfsson-2021.md) (has_code)

_Indexed by lane(s): slam_

_GitHub metadata fetched 2026-11-06._
