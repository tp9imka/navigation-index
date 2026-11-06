# evo

`repo:michaelgrupp/evo` - <https://github.com/MichaelGrupp/evo>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 4,360 | Python | GPL-3.0 | 2026-10-30 | False | production | high |

Python package and CLI for evaluating odometry and SLAM trajectories (ATE/RPE, alignment, plotting) in TUM, KITTI, EuRoC and ROS bag formats.

**Why it matters:** The default way to score a nav or SLAM result against ground truth; essential for any demo that claims accuracy.

**Hackathon notes:** pip install evo. Run evo_ape with alignment flags; it reads most dataset ground-truth formats directly.

## Deep dives

- [_index-perception-altnav](../../docs/integration-cards/_index-perception-altnav.md) (integration-cards)
- [michaelgrupp__evo](../../docs/integration-cards/michaelgrupp__evo.md) (integration-cards)

**Concepts:** [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md), [Visual SLAM](../../catalog/concepts/visual-slam.md), [LiDAR odometry and SLAM](../../catalog/concepts/lidar-slam.md)

**Tags:** `evaluation`, `ate`, `rpe`, `trajectory`, `pip`, `plotting`

**Domains:** multi

## Related

- alternative_to: [rpg_trajectory_evaluation](../../catalog/repos/uzh-rpg__rpg_trajectory_evaluation.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Learning paths](../../docs/learning-paths.md) (mentions)
- [4. Vision, LiDAR and radar odometry](../../docs/primer/04-vision-lidar-radar-odometry.md) (mentions)
- [9. Evaluation and datasets](../../docs/primer/09-evaluation-and-datasets.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [cnspy trajectory evaluation](../../catalog/repos/aau-cns__cnspy_trajectory_evaluation.md) (alternative_to)
- [KISS-ICP](../../catalog/repos/prbonn__kiss-icp.md) (evaluated_on)
- [OpenVINS](../../catalog/repos/rpng__open_vins.md) (evaluated_on)
- [ORB-SLAM3](../../catalog/repos/uz-slamlab__orb_slam3.md) (evaluated_on)
- [rpg_trajectory_evaluation](../../catalog/repos/uzh-rpg__rpg_trajectory_evaluation.md) (alternative_to)
- [EuRoC MAV Dataset](../../catalog/resources/ethz-euroc-mav-dataset.md) (uses)
- [TUM RGB-D SLAM Dataset and Benchmark](../../catalog/resources/tum-rgbd-benchmark.md) (uses)
- [Relative navigation benchmark on real data: KISS-ICP lidar odometry, OpenVINS VIO, mono and nadir VO, scored with evo](../../catalog/samples/relative-nav-benchmark.md) (uses)

_Indexed by lane(s): sim-data, slam_

_GitHub metadata fetched 2026-11-06._
