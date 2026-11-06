# evo

`repo:michaelgrupp/evo` - <https://github.com/MichaelGrupp/evo>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 4,360 | Python | GPL-3.0 | 2026-10-30 | False | production | high |

Python package and CLI for evaluating odometry and SLAM trajectories (ATE/RPE, alignment, plotting) in TUM, KITTI, EuRoC and ROS bag formats.

**Why it matters:** The default way to score a nav or SLAM result against ground truth; essential for any demo that claims accuracy.

**Hackathon notes:** pip install evo. Run evo_ape with alignment flags; it reads most dataset ground-truth formats directly.

**Concepts:** [Datasets and benchmarks](../concepts/datasets-benchmarks.md), [Visual SLAM](../concepts/visual-slam.md), [LiDAR odometry and SLAM](../concepts/lidar-slam.md)

**Tags:** `evaluation`, `ate`, `rpe`, `trajectory`, `pip`, `plotting`

**Domains:** multi

## Related

- alternative_to: [rpg_trajectory_evaluation](../repos/uzh-rpg__rpg_trajectory_evaluation.md)

## Referenced by

- [cnspy trajectory evaluation](../repos/aau-cns__cnspy_trajectory_evaluation.md) (alternative_to)
- [KISS-ICP](../repos/prbonn__kiss-icp.md) (evaluated_on)
- [OpenVINS](../repos/rpng__open_vins.md) (evaluated_on)
- [ORB-SLAM3](../repos/uz-slamlab__orb_slam3.md) (evaluated_on)
- [rpg_trajectory_evaluation](../repos/uzh-rpg__rpg_trajectory_evaluation.md) (alternative_to)
- [The EuRoC MAV Dataset](../resources/ethz-euroc-mav-dataset.md) (uses)
- [TUM RGB-D SLAM Dataset and Benchmark](../resources/tum-rgbd-benchmark.md) (uses)

_Indexed by lane(s): sim-data, slam_

_GitHub metadata fetched 2026-11-06._
