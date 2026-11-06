# VINS-Mono - paper digest
<!-- about: res:vins-mono-qin-2017, repo:hkust-aerial-robotics/vins-mono -->
**VINS-Mono: A Robust and Versatile Monocular Visual-Inertial State Estimator** - Qin, Li, Shen (HKUST), IEEE T-RO 2018 (arXiv 2017, DOI 10.1109/TRO.2018.2853729). [paper](https://arxiv.org/abs/1708.03852) | [code](https://github.com/HKUST-Aerial-Robotics/VINS-Mono) | Read: full text, ar5iv HTML of arXiv v1

## Problem
One camera + one low-cost IMU is the minimal sensor set that recovers metric scale, roll and pitch. Making it work in practice needs initialization from an unknown moving state, online camera-IMU extrinsics, bias handling, failure recovery and long-term drift correction. The paper builds the full system, not just the odometry core.

## Method
- Frontend: KLT tracking of 100-300 corners per image, RANSAC on the fundamental matrix; keyframes by average parallax (rotation-compensated with gyro) and track quality (Sec. IV).
- IMU preintegration with bias correction; first-order bias update instead of re-integration when bias changes are small (Sec. IV).
- Loosely coupled initialization: vision-only sliding-window SfM (needs >30 features and >20 px parallax), then gyro bias, velocity, gravity and metric scale by linear alignment; gravity refined on a 2-DOF sphere. Accelerometer bias ignored at init (Sec. V).
- Tightly coupled sliding-window nonlinear optimization (Ceres): marginalization prior + IMU residuals + visual residuals on the unit sphere, Huber loss; also estimates camera-IMU extrinsics (Sec. VI).
- Two-way marginalization (drop oldest frame or only the newest non-keyframe); motion-only BA at camera rate; IMU forward propagation for 100 Hz control output.
- Failure detection (few features, pose jumps, large bias/extrinsic change) => reinitialize and start a new pose-graph segment.
- Relocalization with DBoW2 (500 extra BRIEF corners per keyframe, 2D-2D then 3D-2D RANSAC checks), tightly coupled into the window (Sec. VII).
- 4-DOF global pose graph (x, y, z, yaw; roll/pitch observable from gravity), run in a separate thread; pose graph save/reuse (Sec. VIII).

## Data and sensors
- Monocular global or rolling shutter camera + MEMS IMU.
- [EuRoC MAV](../dataset-cards/euroc-mav.md) (left camera only); own indoor, mixed indoor/outdoor (>700 m) and 5.62 km campus runs (VI-Sensor); DJI A3-based drone with OptiTrack ground truth; iPhone 7 Plus vs Google Tango.

## Headline results (as reported)
- EuRoC (Sec. IX-A, Fig. 11-14): only plotted, no numeric RMSE table located. Per text, VINS with loop closure has the smallest translation error on MH_03 and MH_05 vs OKVIS mono/stereo; OKVIS better on roll/pitch on MH_05; pure VIO accuracy similar to OKVIS.
- Mixed indoor/outdoor >700 m (Sec. IX-C1, Fig. 19): final drift VINS-Mono without loop [-5.47, 2.76, -0.29] m (0.88%) vs OKVIS [13.80, -5.26, 7.23] m (2.36%); with loop closure [-0.032, 0.09, -0.07] m.
- Drone figure-eight, 61.97 m, loop closure off (Sec. IX-D): final drift [0.08, 0.09, 0.13] m, 0.29%.
- Table I (timing): feature detector 15 ms and KLT 5 ms at 25 Hz; window optimization 50 ms at 10 Hz; loop detection 100 ms; pose graph optimization 130 ms. Hardware in text: Intel i7-4790 (campus), i7-5500U (drone), iPhone 7 Plus.
- Mobile (Sec. IX-E, Fig. 25): authors concede Tango is more accurate locally; VINS-Mobile stays stable when a door opens in view while Tango's yaw jumps.

## Limitations
- Stated by authors: needs enough motion to initialize; accel bias not estimated at init; first-order preintegration approximation blamed for weaker roll/pitch than OKVIS; marginalization fixes linearization points early. Future work: observability-aware motion planning, broader online calibration, dense mapping.
- Our read: most quantitative evidence is figures and single-run drift numbers, not tables over many sequences. Monocular init on a slow ground vehicle or a hovering drone is a known weak spot. Successor VINS-Fusion (stereo, GPS fusion) is the more usual starting point today.

## Code, weights, license
- [HKUST-Aerial-Robotics/VINS-Mono](https://github.com/HKUST-Aerial-Robotics/VINS-Mono), GPL-3.0 (GitHub API), last push 2024-08-14, not archived, ~6.1k stars.
- README: Ubuntu 16.04 + ROS Kinetic, ROS 1 only; Docker folder provided. iOS version is a separate repo (VINS-Mobile).
- No learned weights; DBoW2 vocabulary file ships with the repo.

## Reproduction effort (estimate)
Estimate:
- Hardware: x86 laptop.
- Data: EuRoC bags (a few GB).
- Time-to-first-result: ~half a day; ROS Kinetic-era code needs a Melodic/Noetic container and possibly small fixes (Ceres/OpenCV version drift).
- Not reproducible: own campus, drone and phone experiments (data not public in the paper).

## What a hackathon team can take from it
- The initialization recipe (vision-only SfM => align with preintegrated IMU => refine gravity on a sphere) is the reference design for bootstrapping any monocular VIO.
- 4-DOF pose graph: when roll/pitch are observable from gravity, only optimize x, y, z, yaw. Same idea fits any IMU-aided loop closure or map-matching correction.
- Failure detection + reinit + new pose-graph segment is a pattern for graceful recovery after a visual outage.
- Compare against OpenVINS ([digest](openvins-2020.md)) and ORB-SLAM3 ([digest](orb-slam3-campos-2020.md)) before choosing; ORB-SLAM3's Table II lists VINS-Mono at 0.110 m average EuRoC ATE vs 0.043 m for ORB-SLAM3 mono-inertial.
- Evaluate with [evo](../integration-cards/michaelgrupp__evo.md).
