# CFEAR Radarodometry - paper digest
<!-- about: res:cfear-radarodometry-adolfsson-2021, repo:dan11003/cfear_radarodometry -->
**CFEAR Radarodometry - Conservative Filtering for Efficient and Accurate Radar Odometry** - Adolfsson, Magnusson, Alhashimi, Lilienthal, Andreasson (Orebro Univ.), IROS 2021. [paper](https://arxiv.org/abs/2105.01457) | [code](https://github.com/dan11003/CFEAR_Radarodometry) | Read: full text, ar5iv HTML of arXiv (v3 is latest; Table II is flattened in the HTML, so column alignment for baselines is partly inferred)

## Problem
Odometry in large GNSS-denied areas where vision and LiDAR degrade (rain, fog, dust, smoke). Spinning FMCW radar sees through these, but its scans are noisy and learned radar odometry generalizes poorly to new places. Goal: learning-free, fast, accurate radar odometry.

## Method
- k-strongest filtering: per azimuth, keep only the k strongest returns above a noise floor z_min ("conservative" filtering) (Sec. III).
- Convert to Cartesian, grid-downsample, compute per-cell mean and covariance => oriented surface points with normals (smallest-eigenvalue eigenvector); reject cells with <6 points or condition number >1e5.
- Register the current scan jointly against the s most recent keyframes (scan-to-multi-keyframe), point-to-line residuals with radius r and normal angle limit theta_max.
- Huber loss for robustness; solved with Ceres (BFGS, auto-diff).
- Constant-velocity extrapolation for the initial guess; motion compensation of points to mid-sweep.
- New keyframe after 1.5 m or 5 deg of motion.
- Fixed parameters (Table I): k = 12, z_min = 55, r = 3.5, theta_max = 30, Huber delta = 0.1, s = 3, range 5-100 m; tuned on one Oxford sequence excluded from evaluation.

## Data and sensors
- 2D spinning FMCW radar without Doppler (Navtech CTS350-X on Oxford; Navtech CIR154XH on industrial sets).
- Quantitative: [Oxford Radar RobotCar](../dataset-cards/oxford-radar-robotcar.md), 8 sequences. Qualitative: Volvo CE test track (forest/gravel, 1605 m) and Kvarntorp underground mine (~1235 m loop), no ground truth.
- MulRan and Boreas are not in this IROS paper (the index record and README mention later work; see below).

## Headline results (as reported)
- Table II (Oxford, KITTI-style drift over 100-800 m, % / deg per 100 m): CFEAR mean 1.76 +- 0.12 / 0.50 +- 0.02; per-sequence 1.64 to 1.99 %. Baselines read from the flattened table: SuMa (LiDAR) 1.03 / 0.3; Hong et al. radar odometry 3.11 / 0.9; Barnes Dual Cart 2.784 / 0.85 (spatial cross-validation).
- Text: about 14% lower than Robust Keypoints (2.05%), lowest spatially cross-validated radar result in the table; learned methods only beat it when trained and tested on the same locations.
- Runtime (Table II / text): 18 +- 0.4 ms per scan, ~55 Hz, single thread on an i7-7700HQ 2.80 GHz laptop.
- Kvarntorp mine (text): ~15 m final error over 1235 m (1.2%) with Oxford parameters. Volvo CE: ~15 m max error (1.3%) with Oxford parameters, ~2.5 m (0.2%) after retuning (z_min = 85, f = 3, motion compensation off). Errors estimated from duplicated landmarks, not ground truth.
- Parameter sensitivity: accuracy stable for 12 <= k <= 35.

## Limitations
- Stated by authors: best accuracy needs sensor/environment-specific tuning; motion compensation hurt on uneven terrain; z_min = 55 too low in cluttered forest; normals struggle in clutter; feature-poor mine tunnels constrain the longitudinal direction poorly; more keyframes cost runtime. Future work: other loss functions, residual weighting by surface uncertainty.
- Our read: only one quantitatively evaluated dataset (urban Oxford); off-road and underground numbers are rough estimates. 2D radar gives planar odometry only (x, y, yaw); needs an IMU/baro for full 6-DOF. The index summary is accurate for this paper; the repo README now points to the later T-RO journal version, which is a different, larger paper not digested here.

## Code, weights, license
- [dan11003/CFEAR_Radarodometry](https://github.com/dan11003/CFEAR_Radarodometry), GPL-3.0 (GitHub API), last push 2024-10-17, not archived, ~64 stars.
- README links the T-RO paper, a public evaluation repo (CFEAR_Radarodometry_evaluation_public) and the authors' radar datasets on Google Drive. ROS distro not stated in the README lines we checked; index record says ROS 1.
- No learned weights.

## Reproduction effort (estimate)
Estimate:
- Hardware: any laptop CPU (single thread, ~55 Hz per paper).
- Data: Oxford Radar RobotCar requires registration and large downloads (radar scans per sequence are several GB).
- Time-to-first-result: ~1 day, mostly ROS 1 container setup and Oxford data conversion.
- Not reproducible: Volvo CE and Kvarntorp results (proprietary/qualitative); exact baseline columns of Table II.

## What a hackathon team can take from it
- The all-weather odometry option: if the scenario includes smoke, dust or fog, radar odometry at ~1.8% drift is the reference point.
- k-strongest-per-azimuth filtering is a 10-line preprocessing step reusable for any spinning radar or sonar scan before registration.
- Scan-to-multi-keyframe registration (s = 3) is a cheap drift reducer for any 2D scan matcher.
- Fuse its (x, y, yaw) increments with an IMU in a factor graph or EKF for 6-DOF; same pattern as LiDAR odometry from [KISS-ICP](kiss-icp-vizzo-2022.md).
- Evaluate with KITTI-style drift over 100-800 m segments to stay comparable with Oxford radar literature.
