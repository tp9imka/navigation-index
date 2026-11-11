# Sensor calibration

`concept:calibration`

Camera-IMU, LiDAR-IMU extrinsics, intrinsics, time offset, Allan variance.

**Parent:** [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

## Samples (1)

- [MagNav.jl quickstart: Tolles-Lawson and EKF on the SGL 2020 flight](../../catalog/samples/magnav-quickstart.md) - A Julia walkthrough with MagNav.jl that downloads the public SGL 2020 challenge flight and Ottawa anomaly maps, compensates the scalar magnetometer with Tolles-Lawson on a calibration box, and runs the MagNav EKF against

## Guides (4)

- [03. Adapt aerodynamic navigation parameters only when the data make them identifiable](../../docs/research/innovation-prior-art/03-identifiability-gated-aero-adaptation.md) - Research date 2026-11-09, for an autonomous flight navigation task.
- [3. Inertial navigation and sensor fusion](../../docs/primer/03-inertial-and-fusion.md) - After this chapter you can explain why an IMU drifts, write the predict/update loop of a Kalman filter, choose between a filter and a factor graph, and configure an off-the-shelf estimator to survive a GNSS outage.
- [Offline kit](../../templates/offline-kit/README.md) - Use this when you prepare laptops in the week or night before you work without a reliable network (a field site, a lab with locked-down Wi-Fi, an air-gapped room), or share a cache with teammates there.
- [Timing resilience: the T in PNT](../../docs/timing-resilience.md) - After this page you can explain why a GNSS-denied system loses time before it loses position, estimate how long a given oscillator holds time from its datasheet, name the attacks on GNSS and network time, and pick a 24-4

## Repositories (29)

- [OpenVINS](../../catalog/repos/rpng__open_vins.md) - fit: high - MSCKF-based visual-inertial navigation platform with online calibration, a simulator, and extensive documentation for research use.
- [MINS](../../catalog/repos/rpng__mins.md) - fit: high - Multi-sensor aided inertial navigation that fuses IMU with camera, LiDAR, GNSS and wheel odometry, including online spatial/temporal calibration and a multi-sensor simulator.
- [allan_variance_ros](../../catalog/repos/ori-drs__allan_variance_ros.md) - fit: high - ROS tool (Oxford DRS) that computes Allan deviation plots from an IMU bag and outputs noise parameters in a Kalibr-compatible format.
- [allantools](../../catalog/repos/aewallin__allantools.md) - fit: high - Python library for time and frequency stability statistics: Allan, modified Allan, overlapping, Hadamard and time deviation, plus confidence intervals and power-law noise generators.
- [allan-variance (Python)](../../catalog/repos/nmayorov__allan-variance.md) - fit: high - Small Python package computing Allan variance and fitting standard noise parameters.
- [AprilTag 3](../../catalog/repos/aprilrobotics__apriltag.md) - fit: high - C library for detecting AprilTag fiducial markers and estimating the 6-DoF pose of each tag relative to a calibrated camera.
- [realsense-ros](../../catalog/repos/realsenseai__realsense-ros.md) - fit: high - ROS 2 wrapper for RealSense depth cameras (D400 series), publishing stereo IR, depth, colour and IMU topics.
- [Kalibr](../../catalog/repos/ethz-asl__kalibr.md) - fit: medium - ETH ASL calibration toolbox for multi-camera and camera-IMU systems (extrinsics and time offset), plus IMU intrinsics and rolling-shutter calibration.
- [imu_utils](../../catalog/repos/gaowenliang__imu_utils.md) - fit: medium - ROS package for analysing IMU performance with Allan variance to estimate noise and bias instability.
- [SymForce](../../catalog/repos/symforce-org__symforce.md) - fit: medium - Symbolic computation and code generation library with a fast sparse nonlinear least-squares optimizer, from Skydio, which says it uses it in production for SLAM, calibration and MPC.
- [LiDAR_IMU_Init](../../catalog/repos/hku-mars__lidar_imu_init.md) - fit: medium - Real-time LiDAR-inertial initialization estimating extrinsics, time offset, gravity and IMU bias online (IROS 2022).
- [Basalt](../../catalog/repos/vladyslavusenko__basalt.md) - fit: medium - GitHub mirror of Basalt, a visual-inertial odometry and mapping system built around non-linear factor recovery, with calibration tools; primary development is on GitLab.
- [iKalibr](../../catalog/repos/unsigned-long__ikalibr.md) - fit: medium - Continuous-time, targetless multi-sensor calibration framework (IMU, cameras, LiDAR, radar, RGB-D, event cameras) estimating extrinsics and time offsets (IEEE T-RO 2025).
- [NaveGo](../../catalog/repos/rodralez__navego.md) - fit: medium - Open MATLAB/GNU Octave toolbox for simulating and processing integrated INS/GNSS navigation, including IMU error modelling and Allan variance analysis.
- [imu_tk](../../catalog/repos/kyle-ak__imu_tk.md) - fit: medium - Tool for calibrating IMU intrinsics (misalignment, scale factors and biases of accelerometer and gyro) from a sequence of static poses, without a turntable.
- [rpg_dvs_ros](../../catalog/repos/uzh-rpg__rpg_dvs_ros.md) - fit: medium - ROS drivers and tools for DVS/DAVIS event cameras, including calibration and rendering.
- [NASA COTS Star Tracker](../../catalog/repos/nasa__cots-star-tracker.md) - fit: medium - NASA software for building a star tracker from commercial off-the-shelf cameras, including calibration and attitude solution.
- [Heimdall DAQ firmware](../../catalog/repos/krakenrf__heimdall_daq_fw.md) - fit: medium - Coherent multichannel SDR acquisition chain (sync, calibration, decimation) underneath KrakenSDR DoA and passive radar apps.
- [cuckoo_time_translator](../../catalog/repos/ethz-asl__cuckoo_time_translator.md) - fit: medium - ROS algorithms that translate a sensor's own hardware timestamps into host system time from one-way timing, estimating skew and offset.
- [MagNav deep-learning compensation](../../catalog/repos/naatyu__magnav.md) - fit: medium - Deep-learning approach to aircraft magnetic disturbance compensation built around the MagNav challenge data.
- [TAPR TICC](../../catalog/repos/tapr__ticc.md) - fit: medium - Firmware and design files for TAPR's Arduino-based sub-nanosecond time interval counter, used to compare 1PPS outputs.
- [LI-Calib](../../catalog/repos/april-zju__lidar_imu_calib.md) - fit: low - Targetless LiDAR-IMU calibration based on continuous-time batch estimation (IROS 2020).
- [kalibr_allan (archived)](../../catalog/repos/rpng__kalibr_allan.md) - fit: low - MATLAB scripts producing IMU Allan standard deviation charts and Kalibr-ready noise values.
- [lidar_imu_calib](../../catalog/repos/chennuo0125-hit__lidar_imu_calib.md) - fit: low - Automatic calibration of the extrinsic rotation between a 3D LiDAR and an IMU.
- [VersaVIS](../../catalog/repos/ethz-asl__versavis.md) - fit: low - Open hardware and firmware board that hardware-triggers multiple cameras and an IMU and timestamps them on one clock, with ROS drivers.
- [VID-Fusion](../../catalog/repos/zju-fast-lab__vid-fusion.md) - fit: low - Visual-inertial-dynamics odometry: adds a thrust-model (from measured rotor speed) factor to a VINS-style sliding-window optimizer and estimates the external force on the multirotor together with its pose.
- [AV-Matlab-SW](../../catalog/repos/jaffarrell__av-matlab-sw.md) - fit: low - MATLAB scripts (plus a Python port, AV_Python) for Allan variance analysis and Gauss-Markov IMU error modelling, accompanying Farrell et al., 'Inertial measurement unit error modeling tutorial', IEEE Control Systems Maga
- [ROAMFREE](../../catalog/repos/airlab-polimi__roamfree.md) - fit: low - Pose-graph sensor fusion and self-calibration library on g2o with a catalogue of generic sensor models, used in UAV photogrammetry with raw inertial observations (Cucci, Skaloud).
- [White Rabbit calibration](../../catalog/repos/gitlab.com__ohwr__project__wr-calibration.md) - fit: low - Procedures and notes for calibrating White Rabbit equipment: fixed hardware delays and fibre asymmetry that must be measured for absolute time accuracy.

## Documents, talks, courses, datasets (26)

- [A Nonlinear Model-Based Wind Velocity Observer for Unmanned Aerial Vehicles](../../catalog/resources/borup-fossen-johansen-2016-wind-velocity-observer.md) - paper - NOLCOS 2016 (author PDF read).
- [A Singular Value Maximizing Data Recording Algorithm for Concurrent Learning](../../catalog/resources/chowdhary-johnson-2011-concurrent-learning-data-recording.md) - paper - ACC 2011 (abstract read from proceedings PDF).
- [Advanced Aeromagnetic Compensation Models for Airborne Magnetic Anomaly Navigation](../../catalog/resources/gnadt-2022-mit-phd-aeromagnetic-compensation.md) - report - MIT AeroAstro PhD thesis (advisor Alan Edelman) on removing the aircraft's own magnetic field so magnetic anomaly maps can be used for navigation.
- [Airborne Magnetic Anomaly Navigation with Neural-Network-Augmented Online Calibration](../../catalog/resources/hager-2026-magnav-nn-online-calibration.md) - paper - Published in the Journal of Guidance, Control, and Dynamics (2026).
- [Airspeed estimation for UAVs using only propeller feedback](../../catalog/resources/ntouros-2025-airspeed-propeller-feedback.md) - paper - arXiv preprint, later in Aerospace Science and Technology per TU Delft listing (abstract read).
- [Degenerate Motion Analysis for Aided INS with Online Spatial and Temporal Sensor Calibration](../../catalog/resources/yang-2019-degenerate-motion-aided-ins-calibration.md) - paper - IEEE RA-L 2019; the linked file is the RPNG tech report (RPNG-2018-CALIB).
- [Derivation and Extensions of the Tolles-Lawson Model for Aeromagnetic Compensation](../../catalog/resources/gnadt-2022-tolles-lawson-derivation.md) - paper - Short open reference note that re-derives the Tolles-Lawson aircraft magnetic field model (permanent, induced and eddy-current terms), states where the assumptions enter, describes the calibration procedure, and adds a s
- [Handbook of Frequency Stability Analysis (NIST SP 1065)](../../catalog/resources/nist-sp1065-frequency-stability-handbook.md) - book - NIST tutorial and reference on characterizing clocks and oscillators: Allan, modified Allan, Hadamard and time deviation, power-law noise types, drift removal and confidence intervals.
- [Identifying Aerodynamics of Small Fixed-Wing Drones Using Inertial Measurements for Model-Based Navigation](../../catalog/resources/sharma-laupre-skaloud-2023-identifying-aerodynamics-fixed-wing.md) - paper - NAVIGATION 70(4), open access.
- [IMU-Based Inertia Estimation for a Quadrotor Using Newton-Euler Dynamics](../../catalog/resources/svacha-2020-imu-inertia-estimation-quadrotor.md) - paper - IEEE RA-L 5(3).
- [Kalibr wiki: camera-IMU calibration tutorials](../../catalog/resources/kalibr-wiki.md) - doc - Wiki for Kalibr covering multi-camera, camera-IMU and rolling-shutter calibration, target generation and data collection practice.
- [Kalibr wiki: IMU Noise Model](../../catalog/resources/kalibr-imu-noise-model-wiki.md) - doc - Practical explanation of white noise and random-walk bias parameters for IMUs, how to convert datasheet values to continuous/discrete form and how to inflate them for real use.
- [LeapSecond.com (Tom Van Baak time and frequency pages)](../../catalog/resources/leapsecond-tvb.md) - doc - Long-running personal site with measurements of oscillators, GPSDOs and atomic clocks, Allan deviation tutorials and experiments.
- [Magnetic Navigation on an F-16 Aircraft Using Online Calibration](../../catalog/resources/canciani-2022-f16-magnav-online-calibration.md) - paper - IEEE TAES 58(1) paper on magnetic anomaly navigation flown on an F-16, where the platform's magnetic interference is far larger than on survey aircraft and drifts.
- [Moving Horizon Estimation of Air Data Parameters for UAVs](../../catalog/resources/wenz-johansen-2019-mhe-air-data.md) - paper - IEEE Transactions on Aerospace and Electronic Systems (NTNU Open record; abstract-level read).
- [Observability-aware Self-Calibration of Visual and Inertial Sensors for Ego-Motion Estimation](../../catalog/resources/schneider-2019-observability-aware-vi-self-calibration.md) - paper - IEEE Sensors Journal (arXiv preprint read).
- [Observability-Aware Trajectory Optimization for Self-Calibration with Application to UAVs](../../catalog/resources/hausman-2016-observability-aware-trajectory-optimization.md) - paper - arXiv preprint.
- [OpenVINS documentation](../../catalog/resources/openvins-docs.md) - doc - Documentation for the OpenVINS MSCKF-based visual-inertial estimator, including derivations of the propagation and update steps, calibration, evaluation tooling and ROS usage.
- [Photogrammetry I & II](../../catalog/resources/stachniss-photogrammetry-i-ii.md) - lecture-series - Recorded two-semester photogrammetry course (2015/16 playlist): camera models, direct linear transform, projective geometry, epipolar geometry, bundle adjustment, and image-based 3D reconstruction.
- [PX4 EKF2 drag fusion, wind process noise and IMU bias inhibit (source, v1.16.0)](../../catalog/resources/px4-ekf2-drag-wind-source-v1-16.md) - doc - Source read at v1.16.0 (drag_fusion.cpp differs at v1.17.0 only in parameter names).
- [Reliable strategies for implementing model-based navigation on fixed-wing drones](../../catalog/resources/laupre-pirlet-skaloud-2023-reliable-vdm-navigation.md) - paper - The Journal of Navigation, open access (CC BY).
- [Revisiting multi-GNSS Navigation for UAVs -- An Equivariant Filtering Approach](../../catalog/resources/scheiber-2023-multi-gnss-eqf-uav.md) - paper - Preprint.
- [Sampling-based Motion Planning for Active Multirotor System Identification](../../catalog/resources/bahnemann-2017-active-multirotor-system-identification.md) - paper - ICRA 2017 (arXiv preprint read at abstract level).
- [Trajectory Optimization for Self-Calibration and Navigation](../../catalog/resources/preiss-2017-trajectory-optimization-self-calibration.md) - paper - RSS 2017.
- [Vision Algorithms for Mobile Robotics (UZH/ETH)](../../catalog/resources/scaramuzza-vision-algorithms-mobile-robotics.md) - course - Graduate course building a monocular visual odometry pipeline step by step: image formation, calibration, feature detection, two-view geometry, P3P+RANSAC, bundle adjustment, KLT tracking, place recognition, visual-inert
- [Навигация по Optical Flow · Clover](../../catalog/resources/coex-clover-docs-optical-flow-ru.md) - doc - English: 'Optical Flow navigation - Clover docs'.

