# FAST-LIO2 - paper digest
<!-- about: res:fast-lio2-xu-2021, repo:hku-mars/fast_lio -->
**FAST-LIO2: Fast Direct LiDAR-inertial Odometry** - Xu, Cai, He, Lin, Zhang (HKU MaRS), arXiv 2107.06829, 2021 (arXiv lists no journal-ref; venue not verified here). [paper](https://arxiv.org/abs/2107.06829) | [code](https://github.com/hku-mars/FAST_LIO) | Read: full text, ar5iv HTML of arXiv v1 (appendix Table VIII not read)

## Problem
LiDAR-inertial odometry has to run on small onboard computers, cope with motion distortion, and work with both spinning and small-FoV solid-state LiDARs where hand-crafted edge/plane features break down. Maintaining a dense, updatable map in realtime is the main compute cost.

## Method
- Tightly coupled iterated Kalman filter on manifold (from FAST-LIO), 24-dim state, online LiDAR-IMU extrinsic calibration. Kalman gain computed with a state-dimension inverse, not measurement-dimension.
- Direct registration: raw (downsampled) points matched to the map; plane fitted to 5 nearest map neighbours per point; no feature extraction.
- Motion compensation by IMU back-propagation of every point to scan-end time.
- ikd-Tree: incremental k-d tree with point insertion + on-tree downsampling, box-wise deletion via lazy labels, and parallel re-balancing; O(log n) insert and k-NN.
- Map kept as a local cube moving with the sensor (default L = 1000 m); 0.5 m spatial downsampling; 1:4 temporal point downsampling.
- Pure odometry: no loop closure.

## Data and sensors
- LiDAR + IMU. Evaluated with Livox Horizon (solid-state, 81.7 x 25.1 deg FoV), VLP-16, Velodyne HDL-32E; IMUs from 50 Hz to 1000 Hz.
- Datasets: lili (LILI-OM), liosam (LIO-SAM), utbm, ulhk (UrbanLoco, see [UrbanLoco](../dataset-cards/urbanloco.md)), [NCLT](../dataset-cards/nclt.md); 19 sequences for accuracy, 18 for data-structure study; plus own flip and handheld experiments.

## Headline results (as reported)
- Table IV (absolute translational RMSE, m), selected: utbm_8 FAST-LIO2 (1000 m map) 27.29 vs LILI-OM 59.48, LINS 48.17, LIO-SAM failed; nclt_4 8.71 vs LILI-OM 317.77, LIO-SAM 9461, LINS 65.95; liosam_1 4.58 vs LIO-SAM 4.75, LINS 880.92; ulhk_4 2.57 vs LILI-OM 2.29. Text: best in 18 of 19 sequences (exception ulhk_4).
- Table VI (avg time per scan, ms), selected: ulhk_4 FAST-LIO2 total 20.14 vs LILI-OM 52.40 odo + 74.80 map, LIO-SAM 39.50 + 95.29, LINS 34.72 + 93.70. Text: ~8x faster than LILI-OM, 10x than LIO-SAM, 6x than LINS.
- ARM (Khadas VIM3, Cortex-A73 2.2 GHz): Table VI 60.60 to 100.00 ms per scan on selected sequences; text says ~10 Hz on ARM.
- Table III (ikd-Tree vs nanoflann/Octree/R*-tree, total ms per scan): e.g. nclt_1 15.64 vs 20.41 / 42.57 / 30.14.
- Flip test (text): average 912 deg/s, max 1198 deg/s angular rate, 2.01 ms per scan. Handheld: up to 7 m/s, <0.06 m end-to-end error over 81 m.
- Main platform: DJI Manifold 2-C (i7-8550U 1.8 GHz, 8 GB).

## Limitations
- Stated by authors: odometry only, no loop detection; enlarging the map can cause false matches to old points once drift accumulates (gains stop beyond 2000 m map); map efficiency dips during parallel re-building.
- Our read: needs per-point timestamps in the LiDAR message (README warns "Failed to find match for field 'time'"). Geometrically degenerate scenes (long corridors, open fields, tunnels) are not addressed. Absolute errors of 25+ m on utbm show it still drifts at km scale.

## Code, weights, license
- [hku-mars/FAST_LIO](https://github.com/hku-mars/FAST_LIO), **GPL-2.0** (GitHub API; note: not GPL-3.0 like most of this lane), last push 2026-10-25, not archived, ~5.3k stars.
- README: ROS (Melodic or newer) via roslaunch; livox_ros_driver must be built and sourced even for Velodyne/Ouster; Docker instructions; configs for Velodyne, Ouster, Livox Avia/Horizon/MID-70.
- No learned weights.

## Reproduction effort (estimate)
Estimate:
- Hardware: x86 laptop; ARM boards work at ~10 Hz per paper.
- Data: example rosbags linked in README; NCLT/UrbanLoco sequences are multi-GB.
- Time-to-first-result: ~2-4 h including the livox driver dependency.
- Not reproducible quickly: full Table IV across 19 sequences and the baselines' configs; own flip/handheld data.

## What a hackathon team can take from it
- Default LIO for any LiDAR-carrying platform: one config file per sensor, no feature tuning. See [integration card](../integration-cards/hku-mars__fast_lio.md).
- ikd-Tree is reusable on its own for any incremental nearest-neighbour map (terrain matching, local occupancy).
- Pair with a loop-closure or global-correction layer (pose graph in [GTSAM](../integration-cards/borglab__gtsam.md)) since drift is unbounded.
- Before using FAST-LIO2 as the backbone on a ground vehicle in highway-like scenes, read MINS Table 6 ([digest](mins-2023.md)): FAST-LIO2 mostly failed on KAIST highways there.
- Compare against the simpler [KISS-ICP](kiss-icp-vizzo-2022.md) (no IMU) to show what the IMU buys.
