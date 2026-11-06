# evo - integration card
<!-- about: repo:michaelgrupp/evo -->
One-line: the fastest way to put an honest number (APE/RPE, aligned, plotted) on any trajectory your nav stack produces, against GNSS, mocap or dataset ground truth.

| | |
|---|---|
| Install | `pip install evo` inside a venv / `uvx` / `pipx` (README warns against `--user`, `--break-system-packages`, `sudo pip`). Source: `pip install --editable .`. Pixi: `pixi add evo`. Latest tag v1.38.1 (no GitHub release objects, tags only). Optional: `PyQt6` (Qt plot backend), `contextily` (map tiles), `rerun-sdk` (`--rerun`). |
| Runs on | Pure Python, CPU only. Python 3.11+ (`requires-python = ">=3.11"` in `pyproject.toml`). CI on Linux / macOS / Windows / ROS / ROS 2. ROS not required: bags read through the bundled `rosbags` package, except `/tf` topics which need a ROS install (README). |
| Inputs | TUM (`timestamp tx ty tz qx qy qz qw`), KITTI (3x4 pose rows, no timestamps), EuRoC `state_groundtruth_estimate0/data.csv`, ROS 1 / ROS 2 bags with `geometry_msgs/PoseStamped`, `TransformStamped`, `PoseWithCovarianceStamped`, `PointStamped`, `nav_msgs/Odometry` or TF. Units: metres, seconds. Both trajectories must be in a metric Cartesian frame; no lat/lon input (convert first). |
| Outputs | Console stats (rmse, mean, median, std, min, max, sse), plots (matplotlib, optional map tiles / Rerun), `--save_results x.zip` result files, tables via `evo_res --save_table` (CSV), exported trajectories (TUM/KITTI/bag) from `evo_traj`. |
| Key API / entry points | CLIs: `evo_ape`, `evo_rpe`, `evo_traj`, `evo_res`, `evo_config`. Library (confirmed in source): `evo.tools.file_interface.read_tum_trajectory_file(path) -> PoseTrajectory3D`, `read_kitti_poses_file`, `read_euroc_csv_trajectory`, `read_bag_trajectory(reader, topic, ...)`; `evo.core.sync.associate_trajectories(traj_1, traj_2, *, sync_method=..., max_diff=0.01, offset_2=0.0)`; `PosePath3D.align(traj_ref, correct_scale=False, correct_only_scale=False, n=-1)` (Umeyama); `evo.core.metrics.APE(pose_relation=PoseRelation.translation_part)`, `RPE(pose_relation, delta=1.0, delta_unit=Unit.frames, ...)` with `.process_data((ref, est))`, `.get_all_statistics()`. |
| Time to first result | Estimate: 10 min to run on the bundled `test/data` KITTI files; 30-60 min on your own run, most of it converting GNSS to a local metric frame and fixing timestamps. Assumes a working Python 3.11+ venv. |
| License | GPL-3.0 (GitHub metadata; README says "GPL-3.0 or later"). Fine as an offline tool; do not import it into a closed-source product. |

## Minimal usage
From README "Example Workflow", run inside the repo's `test/data`. Not run.

```bash
pip install evo
cd evo/test/data
evo_traj kitti KITTI_00_ORB.txt KITTI_00_SPTAM.txt --ref=KITTI_00_gt.txt -p --plot_mode=xz
mkdir results
evo_ape kitti KITTI_00_gt.txt KITTI_00_ORB.txt -va --plot --plot_mode xz --save_results results/ORB.zip
evo_ape kitti KITTI_00_gt.txt KITTI_00_SPTAM.txt -va --plot --plot_mode xz --save_results results/SPTAM.zip
evo_res results/*.zip -p --save_table results/table.csv
```

For timestamped data (`-a` = SE(3) Umeyama align, `-s` = also scale, for monocular):

```bash
evo_ape tum gt.tum est.tum -va --t_max_diff 0.02 --plot
evo_rpe tum gt.tum est.tum -va --delta 1 --delta_unit m --pose_relation point_distance
```

## Wiring it into a nav stack
- Logging: write estimator output as TUM lines (`t x y z qx qy qz qw`) or record a ROS 2 bag of `nav_msgs/Odometry`; evo reads both directly. Same for ground truth from [EuRoC](../../catalog/resources/ethz-euroc-mav-dataset.md), [TUM-VI](../../catalog/resources/tum-vi-benchmark.md), [KITTI odometry](../../catalog/resources/kitti-odometry-benchmark.md) (KITTI via [pykitti](../../catalog/repos/utiasstars__pykitti.md) or the raw pose files).
- GNSS truth: convert lat/lon/alt to local ENU (e.g. with [pymap3d](./geospace-code__pymap3d.md)), then write `t e n u 0 0 0 1` per the author's advice in issue #129 (identity orientation).
- Typical demo: run [robot_localization](./cra-ros-pkg__robot_localization.md), [MINS](./rpng__mins.md), [OpenVINS](../../catalog/repos/rpng__open_vins.md) or the [gnss-ins-ekf-outage sample](../../samples/gnss-ins-ekf-outage) with and without GNSS, `--save_results` both, then `evo_res` for one table and plot.
- Results zip / CSV tables are a clean hand-off to slides; `--rerun` streams into a Rerun viewer for live judging.

## Gotchas
- RPE blows up when ground truth has no reliable orientation (GNSS): use `--pose_relation point_distance` (author answer, issue #751). APE with `translation_part` is unaffected.
- Time sync is on you: evo only offers `--t_offset` (known constant offset) and `--t_max_diff` (association tolerance), issue #740. Default `max_diff` in `associate_trajectories` is 0.01 s, which silently drops pairs if your clocks differ more.
- KITTI format has no timestamps, so both files must already be one-to-one pose aligned.
- Always state the alignment you used (`-a`, `-s`, `--n_to_align`). Full-trajectory SE(3) alignment hides heading and start-up errors; for a GNSS-denied drift claim, also report with `--align_origin` or no alignment.
- Python 3.11+ only on current releases; older Jetson images (Python 3.8) need an older evo or a container.
- Reading `/tf` from bags needs a real ROS install; plain pose topics do not.
- GPL-3.0.

## Alternatives
- [rpg_trajectory_evaluation](../../catalog/repos/uzh-rpg__rpg_trajectory_evaluation.md) - when you want the UZH protocol (sub-trajectory relative error by distance, multi-run boxplots) for a VIO paper-style table.
- [MINS](./rpng__mins.md) ships its own `mins_eval` (accuracy, consistency/NEES, timing) - prefer it when you need filter consistency, which evo does not compute.

Sources: README.md, pyproject.toml, evo/core/{metrics,sync,trajectory}.py, evo/tools/file_interface.py, evo/cli/rpe_parser.py (flag names and choices), tags list, issues #129, #740, #751 (all read 2026-11-06 via `gh api`).
