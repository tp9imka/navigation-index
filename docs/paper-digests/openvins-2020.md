# OpenVINS - paper digest
<!-- about: repo:rpng/open_vins -->
**OpenVINS: A Research Platform for Visual-Inertial Estimation** - Geneva, Eckenhoff, Lee, Yang, Huang (Univ. of Delaware RPNG), ICRA 2020. [paper](https://pgeneva.com/downloads/papers/Geneva2020ICRA.pdf) | [code](https://github.com/rpng/open_vins) | Read: full text, author PDF (7 pages)

## Problem
Building a working visual-inertial estimator from scratch is hard, and the open VIO codebases of 2019 had hard-coded assumptions, thin documentation and no evaluation tooling. The paper presents a codebase meant to be extended, not just run.

## Method
- On-manifold sliding-window EKF (MSCKF family). State = current IMU state (quaternion, position, velocity, gyro and accel biases; 15 DOF) + c historical pose clones + m SLAM landmarks + per-camera intrinsics/extrinsics + one camera-IMU time offset (Eq. 1-5).
- First-Estimates Jacobian (FEJ) treatment for consistency; standard MSCKF update with nullspace projection for short tracks, plus long-lived "SLAM landmarks" kept in the state (Sec. III-B, V-A).
- Landmark representations: global 3D, inverse MSCKF, full inverse depth, anchored 3D (Sec. II).
- New state variables (e.g. landmarks) are initialized via QR/Givens split of the linear system so covariance and cross-correlations come out correct (Eq. 18-22).
- Online calibration of camera intrinsics, camera-IMU extrinsics and camera-IMU time offset, residuals computed on raw pixels (Sec. III-D).
- "Type" system manages state ordering and covariance blocks so a new measurement only needs a sparse Jacobian over the states it touches (Sec. III-A).
- Simulator: SE(3) cubic B-spline through a user pose trajectory; IMU readings from spline derivatives, synthetic landmarks projected into any number of cameras (Sec. IV).
- Packages: ov_core (tracking, triangulation, simulator), ov_eval (alignment, ATE/RPE/NEES, Monte-Carlo), ov_msckf (estimator).

## Data and sensors
- Monocular or stereo camera + MEMS IMU. Simulation uses ADIS16448 IMU noise, camera 10 Hz, IMU 400 Hz, 1 px noise (Sec. V-A).
- Real data: [EuRoC MAV](../dataset-cards/euroc-mav.md) Vicon room sequences V1_01 to V2_02 (V2_03 excluded because some baselines could not run it). Authors recomputed V1_01_easy ground truth because the original had wrong orientations (Sec. V-B).

## Headline results (as reported)
- Table I (simulation, 20 runs): with bad initial calibration and online calibration ON, ATE 0.218 deg / 0.139 m, position NEES 2.007; with calibration OFF, ATE 5.432 deg / 508.719 m, position NEES 1045.174 (diverges).
- Table II (EuRoC, mean ATE deg/m over 5 sequences, 10 runs each): mono_ov_slam 1.445 / 0.079; mono_okvis 1.911 / 0.154; mono_vinsfusion_vio 2.926 / 0.104; stereo_ov_slam 1.552 / 0.054; stereo_ov_vio 1.454 / 0.055; stereo_basalt 1.321 / 0.057.
- Table III (RPE): monocular ov_slam best at most segment lengths (8 m: 0.661 / 0.074); stereo second to Basalt per text.
- Runtime (Sec. V-B, text): on V1_01, 2.7x / 4.3x realtime for mono SLAM / VIO and 1.2x / 1.9x for stereo SLAM / VIO, single thread on Intel Xeon E3-1505M v6 @ 3.00 GHz. Per-frame timing "not evaluated rigorously"; Basalt was faster.
- Only VIO output compared (no loop closure / pose graph for any method).

## Limitations
- Stated by authors: frontend (OpenCV tracking) and SLAM feature update are the runtime bottleneck; no rigorous per-frame timing; future work = optimization-based estimator and visual-inertial mapping.
- Our read: EuRoC is short indoor flight; no outdoor, long-range, or GNSS-denied large-area evaluation in the paper. Stereo SLAM landmarks bring little gain over plain VIO (Table II). No loop closure in the evaluated system, so drift is unbounded over long runs.

## Code, weights, license
- [rpng/open_vins](https://github.com/rpng/open_vins), GPL-3.0 (GitHub API), last push 2025-11-30, not archived, ~3.2k stars.
- README: ROS 1, ROS 2 and ROS-free builds have CI workflows; Docker images since Dec 2021 per changelog. Docs site https://docs.openvins.com carries the derivations.
- No learned weights (classical estimator).
- GPL-3.0 means derivative work must ship source under the same license.

## Reproduction effort (estimate)
Estimate:
- Hardware: any x86 laptop; single-threaded runs faster than realtime per the paper.
- Data: EuRoC bags (a few GB) or zero download using the built-in simulator.
- Time-to-first-result: ~2-4 h for a ROS 2 or Docker build and a first EuRoC run with ov_eval plots.
- Not reproducible out of the box: the exact Table II numbers depend on the 2020 configs and the corrected V1_01 ground truth from the docs site; current master has changed defaults since.

## What a hackathon team can take from it
- A day-one VIO with a simulator: develop and test fusion logic before any hardware or bag works. See [integration card](../integration-cards/rpng__open_vins.md).
- The calibration lesson from Table I: with bad extrinsics/time offset, disabling online calibration diverges. Turn it on for any quickly-mounted camera/IMU rig.
- ov_eval gives ATE/RPE/NEES and Monte-Carlo tooling; usable for any estimator's output, alongside [evo](../integration-cards/michaelgrupp__evo.md).
- The type-based state system is a template for adding a new aiding measurement (baro, mag, terrain match) with a sparse Jacobian. [MINS](mins-2023.md) is the same group's multi-sensor extension.
- NEES as a consistency check: report it, not just ATE, when claiming an estimator is trustworthy under degraded sensing.
