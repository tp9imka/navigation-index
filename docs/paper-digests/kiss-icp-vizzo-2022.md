# KISS-ICP - paper digest
<!-- about: res:kiss-icp-vizzo-2022, repo:prbonn/kiss-icp -->
**KISS-ICP: In Defense of Point-to-Point ICP - Simple, Accurate, and Robust Registration If Done the Right Way** - Vizzo, Guadagnino, Mersch et al. (Univ. Bonn), IEEE RA-L 2023 (DOI 10.1109/LRA.2023.3236571; arXiv 2022). [paper](https://arxiv.org/abs/2209.15397) | [code](https://github.com/PRBonn/kiss-icp) | Read: full text, ar5iv HTML

## Problem
LiDAR odometry pipelines usually depend on hand-tuned features, IMU/wheel input, or per-environment parameters. The authors ask whether plain point-to-point ICP, engineered carefully, can match them with one parameter set across sensors and platforms.

## Method
- Constant-velocity motion prediction from the last two poses; per-point deskewing using the point's relative timestamp in the sweep.
- Two voxel-grid subsampling passes (alpha*v for the map, beta*v for registration), keeping original points rather than voxel centres.
- Local map: hash-table voxel grid, max N points per voxel, voxels beyond max range dropped (bounded size).
- Adaptive correspondence threshold: tau = 3 sigma, where sigma is computed from deviations between the ICP result and the constant-velocity prediction.
- Geman-McClure robust kernel scaled by sigma; ICP iterates until the correction is below gamma.
- No features, normals, IMU, loop closure or pose graph.
- Seven parameters, one set for all experiments (Table I): tau0 = 2 m, delta_min = 0.1 m, N_max = 20, v = 0.01 * r_max, alpha = 0.5, beta = 1.5, gamma = 1e-4.

## Data and sensors
- 3D LiDAR only (Velodyne, Ouster, Livox non-repetitive). Platforms: car, drone, Segway, handheld.
- [KITTI](../dataset-cards/kitti.md) odometry + raw, [MulRan](../dataset-cards/mulran-helipr.md) (KAIST, DCC, Riverside, Sejong), [Newer College](../dataset-cards/newer-college.md), [NCLT](../dataset-cards/nclt.md) 2012-01-08.

## Headline results (as reported)
- Table II (KITTI benchmark, avg relative translational error %): KISS-ICP 0.50 (seq 00-10) / 0.61 (seq 11-21 test) vs CT-ICP 0.53 / 0.59, SuMa 0.80 / 1.39, F-LOAM 0.84 / 1.87. Text: 2nd among open-source methods (behind CT-ICP, which is a full SLAM system), 9th overall at time of writing.
- Table III (MulRan, KITTI-style tra % / rot deg per 100 m; ATE m): KAIST 2.28 / 0.68, ATE 17.40 (MULLS 37.24); Riverside 2.89 / 0.64, ATE 49.02 (MULLS 91.16); Sejong 4.69 / 0.70, ATE 1369.54 m (still best in table).
- Table IV (rel. trans. error %): Newer College 01-short 0.51, 02-long 0.96 (CT-ICP 0.48 / 0.58); NCLT 1.27 (CT-ICP 1.17).
- Table V (KITTI raw, no pre-deskewed input): with constant-velocity deskew 0.49% at 38 Hz; without deskew 0.91% at 51 Hz; CT-ICP 0.55% at 15 Hz; IMLS-SLAM 1 Hz. Hardware not stated in the paper.
- Table VI: adaptive threshold 0.50% vs best fixed threshold 0.51% (KITTI 00-10); text: removing the robust kernel raises error to 0.67%.

## Limitations
- Stated by authors: relies on a constant-velocity model, so deskewing assumes small intra-sweep motion change; open-loop, no loop closure; max range is sensor/environment dependent; they discourage NCLT for odometry evaluation (ground-truth issues).
- Our read: no IMU means aggressive rotation (drones, handheld) is the risk case; Sejong ATE of 1.37 km shows km-scale drift is real on long runs. Geometric degeneracy (tunnels, open fields) is not handled.

## Code, weights, license
- [PRBonn/kiss-icp](https://github.com/PRBonn/kiss-icp), **MIT** (GitHub API), last push 2026-06-09, not archived, ~2.4k stars.
- README: `pip install kiss-icp`, then `kiss_icp_pipeline` on a folder or rosbag; ROS 2 wrapper; ROS 1 dropped after v0.3.0.
- No learned weights.

## Reproduction effort (estimate)
Estimate:
- Hardware: any laptop.
- Data: KITTI odometry velodyne (~80 GB) or a single MulRan / own bag.
- Time-to-first-result: under 1 h with pip.
- Not reproducible: the 38 Hz figure (hardware unstated); KITTI test-set numbers need a benchmark submission.

## What a hackathon team can take from it
- Permissive MIT LiDAR odometry that installs with pip: the safest dependency in this lane for anything that might ship. See [integration card](../integration-cards/prbonn__kiss-icp.md).
- Adaptive threshold trick (tau = 3 sigma of deviation from motion prediction) transfers to any scan matcher, including radar or terrain-profile matching.
- Strong "first baseline" before trying [FAST-LIO2](fast-lio2-xu-2021.md); if KISS-ICP already meets the requirement, skip the IMU integration work.
- Feed its relative poses as odometry factors into a GTSAM/robot_localization layer with an IMU and a global correction.
- Deskewing ablation (Table V) is a quick way to show how much timestamping matters on your own sensor.
