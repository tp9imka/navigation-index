# GNSS/INS integration

`concept:gnss-ins`

Loosely, tightly and deeply coupled GNSS/INS.

**Parent:** [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

## Samples (1)

- [GNSS/INS EKF through a GNSS outage and a spoofing walk-off](../../catalog/samples/gnss-ins-ekf-outage.md) - A stdlib-only 2D loosely-coupled GNSS/INS EKF (8 states, hand-written matrix helpers) on a synthetic vehicle with biased, noisy 100 Hz IMU and 1 Hz GNSS.

## Guides (2)

- [3. Inertial navigation and sensor fusion](../../docs/primer/03-inertial-and-fusion.md) - After this chapter you can explain why an IMU drifts, write the predict/update loop of a Kalman filter, choose between a filter and a factor graph, and configure an off-the-shelf estimator to survive a GNSS outage.
- [GNSS-denied navigation: products and companies](../../docs/landscape/gnss-denied-nav-products.md) - What judges from industry already know.

## Repositories (36)

- [ArduPilot](../../catalog/repos/ardupilot__ardupilot.md) - fit: high - GPL autopilot covering Copter, Plane (incl.
- [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md) - fit: high - Dronecode flight stack for multirotors, fixed-wing, VTOL, rovers and boats, built on NuttX with a uORB pub/sub middleware.
- [LIO-SAM](../../catalog/repos/tixiaoshan__lio-sam.md) - fit: high - Tightly coupled LiDAR-inertial odometry via factor-graph smoothing, with optional GPS factors and loop closure.
- [GTSAM](../../catalog/repos/borglab__gtsam.md) - fit: high - Georgia Tech factor-graph library for smoothing and mapping, with incremental solvers (iSAM2) and a full IMU preintegration factor set.
- [robot_localization](../../catalog/repos/cra-ros-pkg__robot_localization.md) - fit: high - ROS package with EKF and UKF state estimation nodes that fuse any number of odometry, IMU, pose and GNSS inputs, plus a navsat_transform node for GPS-to-map conversion.
- [gnss-ins-sim](../../catalog/repos/aceinna__gnss-ins-sim.md) - fit: high - Python GNSS/INS simulator that generates trajectories, IMU/GNSS/magnetometer measurements with configurable error models, and runs navigation algorithms on them.
- [KF-GINS](../../catalog/repos/i2nav-whu__kf-gins.md) - fit: high - Wuhan University i2Nav reference implementation of loosely coupled GNSS/INS integration with an error-state EKF, with sample data and documentation.
- [imu_x_fusion](../../catalog/repos/cggos__imu_x_fusion.md) - fit: high - Loosely coupled IMU + GNSS / 6-DoF odometry fusion with multiple estimators side by side (ESKF, IEKF, UKF variants, MAP).
- [MINS](../../catalog/repos/rpng__mins.md) - fit: high - Multi-sensor aided inertial navigation that fuses IMU with camera, LiDAR, GNSS and wheel odometry, including online spatial/temporal calibration and a multi-sensor simulator.
- [imu_gps_localization](../../catalog/repos/ydsf16__imu_gps_localization.md) - fit: high - Error-state Kalman filter fusing IMU and GPS for localization, small and readable.
- [OB_GINS](../../catalog/repos/i2nav-whu__ob_gins.md) - fit: high - Optimization-based GNSS/INS integration from Wuhan University i2Nav, using IMU preintegration in a sliding-window factor graph solved with Ceres.
- [UrbanNav](../../catalog/repos/ipnl-polyu__urbannavdataset.md) - fit: high - Open multisensor urban positioning dataset from PolyU IPNL with GNSS, IMU, lidar and camera in deep urban canyons.
- [pyins](../../catalog/repos/nmayorov__pyins.md) - fit: high - Python package for modelling and analysing inertial navigation systems: strapdown integration, error models, Kalman-filter aiding and sensor simulation.
- [ROSCon UK 2025 State Estimation workshop](../../catalog/repos/locusrobotics__roscon-uk-2025-se-workshop.md) - fit: high - Materials for an eight-task ROS 2 state estimation workshop at ROSCon UK 2025, with a Docker image, recorded bags and step-by-step exercises using robot_localization and fuse.
- [VINS-Fusion](../../catalog/repos/hkust-aerial-robotics__vins-fusion.md) - fit: medium - Extension of VINS-Mono supporting mono+IMU, stereo, and stereo+IMU, with optional loose fusion of global sensors such as GPS.
- [INAV](../../catalog/repos/inavflight__inav.md) - fit: medium - Navigation-focused fork of the Cleanflight/Betaflight lineage for small multirotors, fixed-wing and rovers, adding GPS position hold, return-to-home and waypoint missions on cheap F4/F7/H7 boards.
- [hdl_graph_slam](../../catalog/repos/koide3__hdl_graph_slam.md) - fit: medium - 3D LiDAR graph SLAM with NDT/GICP scan matching odometry, loop detection and optional GPS, IMU and floor-plane constraints.
- [M2DGR](../../catalog/repos/sjtu-visys__m2dgr.md) - fit: medium - Multi-modal, multi-scenario ground robot dataset from SJTU with cameras, lidar, IMU, GNSS and more, indoor and outdoor.
- [GVINS](../../catalog/repos/hkust-aerial-robotics__gvins.md) - fit: medium - Tightly coupled GNSS-visual-inertial estimator that fuses raw GNSS pseudorange and Doppler with VIO in a factor graph, giving drift-free global poses and smooth local tracking.
- [eskf-gps-imu-fusion](../../catalog/repos/zm0612__eskf-gps-imu-fusion.md) - fit: medium - ESKF fusing GPS and IMU for improved positioning, with documentation in Chinese.
- [IC-GVINS](../../catalog/repos/i2nav-whu__ic-gvins.md) - fit: medium - INS-centric GNSS-visual-inertial navigation system from i2Nav, where the precise INS drives the visual front end and GNSS is fused in a factor graph.
- [GICI-LIB](../../catalog/repos/chichengcn__gici-open.md) - fit: medium - GNSS/INS/Camera integrated navigation library supporting a range of GNSS modes (SPP, RTK, PPP and variants) tightly fused with inertial and visual data via factor graph optimization.
- [NaveGo](../../catalog/repos/rodralez__navego.md) - fit: medium - Open MATLAB/GNU Octave toolbox for simulating and processing integrated INS/GNSS navigation, including IMU error modelling and Allan variance analysis.
- [OKVIS2-X](../../catalog/repos/ethz-mrl__okvis2-x.md) - fit: medium - Extension of OKVIS2 that can additionally use dense depth or LiDAR and fuse GNSS.
- [GVINS dataset](../../catalog/repos/hkust-aerial-robotics__gvins-dataset.md) - fit: medium - Dataset with synchronized visual, inertial and raw GNSS measurements released with GVINS.
- [ESKF ROS (EliaTarasov)](../../catalog/repos/eliatarasov__eskf.md) - fit: medium - ROS error-state Kalman filter derived from PX4/ecl that fuses IMU with GPS, magnetometer, vision pose and optical flow.
- [gtsam_gnss](../../catalog/repos/taroz__gtsam_gnss.md) - fit: medium - Custom GTSAM factors and MATLAB wrappers for GNSS factor-graph positioning, including pseudorange, Doppler and carrier-phase factors with ambiguity estimation.
- [GSDC 2023 solution (taroz)](../../catalog/repos/taroz__gsdc2023.md) - fit: medium - Code reproducing Taro Suzuki's Google Smartphone Decimeter Challenge 2023 entry (1st on the public leaderboard, 2nd on the private one), using factor graph optimization of smartphone GNSS and IMU in MATLAB.
- [Baidu Apollo](../../catalog/repos/apolloauto__apollo.md) - fit: low - Baidu's open autonomous driving platform, including the multi-sensor fusion localization module combining GNSS RTK, IMU and lidar map matching.
- [PX4 ECL (Estimation & Control Library)](../../catalog/repos/px4__px4-ecl.md) - fit: low - Former home of PX4's estimation and control library including the EKF2 navigation filter; archived after the code moved into PX4-Autopilot.
- [GLIO](../../catalog/repos/xikunliu-huskit__glio.md) - fit: low - Tightly coupled GNSS/LiDAR/IMU integration (PolyU) for continuous, drift-free state estimation in urban canyons.
- [gnss_comm](../../catalog/repos/hkust-aerial-robotics__gnss_comm.md) - fit: low - C++/ROS definitions and utilities for raw GNSS measurement processing (ephemeris, satellite positions, pseudorange models) used by GVINS.
- [gps_imu_fusion](../../catalog/repos/shelfcol__gps_imu_fusion.md) - fit: low - GPS/IMU fusion examples derived from zm0612/eskf-gps-imu-fusion, implementing an EKF, the original ESKF and a Sola-style quaternion ESKF, plus an observability analysis; UKF is only listed as TODO.
- [GSDC 10th place solution](../../catalog/repos/fkaneko__kaggle_google_smartphone_decimeter_challenge.md) - fit: low - 10th-place solution for the Kaggle Google Smartphone Decimeter Challenge.
- [ML GNSS/IMU integration (GSDC 2022)](../../catalog/repos/akpozi__machine_learning_gnss_imu_integration.md) - fit: low - GSDC 2022 pipeline: an ML classifier picks the drive environment (highway, tree-lined, downtown) to set rtklib-py PPK options, then a loosely coupled GNSS/IMU Kalman filter refines the result.
- [graduate_work (UAV INS module thesis)](../../catalog/repos/danamarkova__graduate_work.md) - fit: low - Russian graduate thesis code: 'Development of a UAV inertial navigation module using auxiliary navigation data'.

## Documents, talks, courses, datasets (30)

- [Complex Urban Dataset](../../catalog/resources/kaist-complex-urban-dataset.md) - dataset - Urban driving in dense city areas with lidar, stereo and navigation sensors where GNSS is degraded.
- [Data-Driven Analysis of PNT Resilience: Insights and Lessons from Jammertest 2024 Vehicular Data](../../catalog/resources/jammertest-2024-vehicular-pnt-resilience.md) - paper - Analyses vehicle-mounted GNSS, phone, IMU and camera data collected at Jammertest 2024.
- [EKF Source Selection and Switching](../../catalog/resources/ardupilot-ekf3-sources.md) - doc - Reference for EKF3 source parameters (position, velocity, yaw per axis) and how fusion of multiple velocity sources works.
- [Extended Kalman Filter (EKF)](../../catalog/resources/ardupilot-ekf-overview.md) - doc - Overview of ArduPilot's EKF2/EKF3 estimators: states, sensor inputs, innovation checks, lane switching across multiple IMUs and tuning guidance.
- [FAA SAFO 24002: Recognizing and Mitigating GPS/GNSS Disruptions](../../catalog/resources/faa-safo-24002-gnss-disruptions.md) - doc - FAA Safety Alert for Operators describing jamming vs spoofing effects on aircraft systems, typical locations near conflict and counter-UAS areas, and recommended crew and operator actions.
- [Factor Graphs and GTSAM: A Hands-on Introduction](../../catalog/resources/gtsam-intro-tutorial.md) - doc - Hands-on introduction to the GTSAM library: modelling robot odometry, landmark and pose-graph SLAM as factor graphs, solving with Levenberg-Marquardt or iSAM2, and reading marginal covariances, with C++ and MATLAB snippe
- [Factor Graphs for Robot Perception](../../catalog/resources/dellaert-kaess-factor-graphs-robot-perception.md) - paper - Foundations and Trends monograph (free author PDF) explaining SLAM and sensor fusion as inference on factor graphs, with incremental smoothing (iSAM) and the reasoning behind the GTSAM library.
- [GPS / Non-GPS Transitions](../../catalog/resources/ardupilot-gps-non-gps-transitions.md) - doc - Explains configuring EKF3 with two source sets (e.g.
- [Honeywell HGuide o480 single-card INS and HGuide i700 IMU](../../catalog/resources/honeywell-hguide-o480.md) - product - HGuide o480 (May 2025) is a single-card INS for small UAVs and ground robots that accepts velocity aiding (e.g.
- [Inertial Labs VINS visual-aided INS (with Maxar Raptor)](../../catalog/resources/inertial-labs-vins.md) - product - Launched June 2025, VINS combines an Inertial Labs INS with Maxar Raptor software that matches camera frames to Maxar Precision3D satellite-derived 3D maps for absolute position on long-range UAV flights.
- [ION GNSS+ Tutorials](../../catalog/resources/ion-gnss-plus-tutorials.md) - course - Pre-conference tutorial programme of ION GNSS+, the main annual GNSS technical meeting: full-day course series taught by field experts (2026: Survey of GNSS Systems, Advanced Algorithms for Navigation, Space and Spacecra
- [ION Smartphone Decimeter Challenge (with Google)](../../catalog/resources/ion-smartphone-decimeter-challenge.md) - competition - ION page for the 3rd Smartphone Decimeter Challenge (Google, ION Satellite Division and Kaggle; ran Sep 12, 2023 - May 23, 2024).
- [LIO-SAM: Tightly-coupled Lidar Inertial Odometry via Smoothing and Mapping](../../catalog/resources/lio-sam-shan-2020.md) - paper - Formulates LiDAR-inertial odometry as factor-graph smoothing with IMU preintegration, LiDAR odometry, GPS and loop-closure factors.
- [MARS-LVIG Dataset: A multi-sensor aerial robots SLAM dataset for LiDAR-visual-inertial-GNSS fusion](../../catalog/resources/hku-mars-lvig-dataset.md) - dataset - Aerial robot SLAM dataset for lidar-visual-inertial-GNSS fusion, including sequences with raw GNSS measurements under different lighting.
- [Navigating Using GPS Localization (Nav2 tutorial)](../../catalog/resources/nav2-gps-navigation-tutorial.md) - doc - Nav2 tutorial on outdoor navigation with GPS: fusing GNSS, IMU and odometry with robot_localization's navsat_transform, configuring Nav2 for GPS waypoints, and demonstrating it in Gazebo.
- [Principles of GNSS, Inertial, and Multisensor Integrated Navigation Systems, Second Edition](../../catalog/resources/groves-pnt-book-2e.md) - book - Standard reference on satellite, inertial and terrestrial radio navigation and their integration, including INS/GNSS integration architectures, dead reckoning, feature matching and integrity monitoring.
- [PX4 Developer Summit (talks and recordings)](../../catalog/resources/px4-developer-summit.md) - talk - Annual PX4 developer conference; recordings are posted on the PX4 YouTube channel.
- [PX4 State Estimation](../../catalog/resources/riseborough-px4-state-estimation-2020.md) - talk - Slide deck from the EKF2 lead developer covering estimator changes: yaw alignment from IMU and GPS velocity without a magnetometer, external vision improvements, range finder and optical flow fixes, and plans to expand n
- [Quaternion kinematics for the error-state Kalman filter](../../catalog/resources/sola-quaternion-kinematics-eskf.md) - paper - Long tutorial report covering quaternion conventions, rotation perturbations and their derivatives, and a full derivation of an IMU-driven error-state Kalman filter including the reset step.
- [robot_localization package documentation](../../catalog/resources/robot-localization-docs.md) - doc - Documentation for the widely used ROS EKF/UKF state estimation package, including state-estimation node configuration, sensor integration, and navsat_transform for GPS.
- [ROSCon UK 2025 - State Estimation for Mobile Robotics Workshop](../../catalog/resources/nav2-roscon-uk-2025-state-estimation-workshop.md) - masterclass - Hands-on workshop material comparing two ROS 2 state-estimation approaches: Kalman filtering with robot_localization (EKF/UKF, covariance tuning, frames, rate handling) and factor-graph fixed-lag smoothing with fuse.
- [SBG Systems Ellipse INS - 2025 GNSS-denied firmware](../../catalog/resources/sbg-new-ellipse-firmware.md) - product - A March 2025 free firmware update for SBG's Ellipse (v3 hardware) adds jamming/spoofing detection flags and lets users reject or re-enable GNSS and other aiding sensors without resetting the filter.
- [State Estimation and Localization for Self-Driving Cars (Coursera)](../../catalog/resources/coursera-state-estimation-localization-sdc.md) - course - Course 2 of the UofT Self-Driving Cars specialization: least squares, KF/EKF/ES-EKF/UKF, IMU and GNSS sensor models, LiDAR scan matching with ICP, culminating in an error-state EKF that fuses IMU, GNSS and LiDAR on CARLA
- [Understanding Sensor Fusion and Tracking (MATLAB Tech Talks)](../../catalog/resources/mathworks-understanding-sensor-fusion-tracking.md) - video - Short video series on sensor fusion for autonomous systems: what sensor fusion is, IMU/magnetometer orientation estimation, fusing GPS and IMU for pose with an asynchronous EKF, single- and multi-object tracking, and tra
- [UrbanLoco: A Full Sensor Suite Dataset for Mapping and Localization in Urban Scenes](../../catalog/resources/polyu-urbanloco-dataset.md) - dataset - Driving data from Hong Kong and California urban canyons with a full sensor suite, targeted at GNSS outliers and degraded localization.
- [Using PX4's Navigation Filter (EKF2)](../../catalog/resources/px4-ekf2-tuning-guide.md) - doc - PX4 guide to its EKF2 estimator: which sensors it fuses (IMU, GNSS, baro, mag, optical flow, external vision, range), how to configure and tune them, and how to read innovation logs.
- [VectorNav - Iridium STL-aided INS collaboration with NAL Research](../../catalog/resources/vectornav-stl-aided-ins.md) - company - VectorNav makes small tactical-grade IMU/GNSS-INS units widely used on research drones (PX4 has a driver).
- [Програмна реалізація алгоритмів навігації БПЛА із використанням систем обробки телеметрії](../../catalog/resources/lpnu-romaniv-uav-nav-telemetry-thesis-2025.md) - report - English: 'Software implementation of UAV navigation algorithms using telemetry processing systems'.
- [Разработка алгоритма абсолютной визуально-инерциальной навигации беспилотных воздушных судов](../../catalog/resources/preprints-lazareva-absolute-vi-nav.md) - paper - English: 'Development of an absolute visual-inertial navigation algorithm for unmanned aircraft'.
- [Способи навігації БПЛА у складних умовах зовнішнього середовища](../../catalog/resources/kpi-hehelskyi-avrutov-uav-nav-complex-env-2025.md) - paper - English: 'UAV navigation methods in complex environmental conditions' (Mechanics of Gyroscopic Systems, No.

