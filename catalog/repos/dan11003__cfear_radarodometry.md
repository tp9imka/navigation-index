# CFEAR Radarodometry

`repo:dan11003/cfear_radarodometry` - <https://github.com/dan11003/CFEAR_Radarodometry>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 64 | C++ | GPL-3.0 | 2024-10-17 | False | research-prototype | low |

Landing page for CFEAR, learning-free spinning-radar odometry that filters returns to sparse oriented surface points and registers against keyframes. This repo holds only a README and LICENSE; the code is in dan11003/CFEAR_Radarodometry_code_public.

**Why it matters:** Strong baseline for spinning (Navtech-style) radar odometry; robust in weather that defeats LiDAR.

**Hackathon notes:** Clone CFEAR_Radarodometry_code_public for the ROS 1 code (Melodic or later; Oxford Radar RobotCar demo bag provided). Benchmarked on Oxford Radar RobotCar and Boreas. GPL-3.0.

## Deep dives

- [boreas](../../docs/dataset-cards/boreas.md) (dataset-cards)
- [oxford-radar-robotcar](../../docs/dataset-cards/oxford-radar-robotcar.md) (dataset-cards)
- [cfear-radarodometry-adolfsson-2021](../../docs/paper-digests/cfear-radarodometry-adolfsson-2021.md) (paper-digests)

**Concepts:** [Radar navigation and odometry](../../catalog/concepts/radar-nav.md)

**Tags:** `spinning-radar`, `oxford-radar`, `ros1`

**Domains:** ground

## Related

- alternative_to: [4DRadarSLAM](../../catalog/repos/zhuge2333__4dradarslam.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [TBV Radar SLAM](../../catalog/repos/dan11003__tbv_slam_public.md) (extends)
- [ORORA](../../catalog/repos/url-kaist__outlier-robust-radar-odometry.md) (alternative_to)
- [4DRadarSLAM](../../catalog/repos/zhuge2333__4dradarslam.md) (alternative_to)
- [CFEAR Radarodometry - Conservative Filtering for Efficient and Accurate Radar Odometry](../../catalog/resources/cfear-radarodometry-adolfsson-2021.md) (has_code)
- [USV own-ship navigation under GNSS spoofing: radar-to-chart fixes and an integrity monitor in the Oresund](../../catalog/samples/usv-gnss-denied-nav.md) (explains)

_Indexed by lane(s): slam_

_GitHub metadata fetched 2026-11-06._
