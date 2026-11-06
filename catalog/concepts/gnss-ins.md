# GNSS/INS integration

`concept:gnss-ins`

Loosely, tightly and deeply coupled GNSS/INS.

**Parent:** [Sensor fusion and state estimation](../concepts/sensor-fusion.md)

## Repositories (31)

- [ArduPilot](../repos/ardupilot__ardupilot.md) - fit: high - GPL autopilot covering Copter, Plane (incl.
- [PX4 Autopilot](../repos/px4__px4-autopilot.md) - fit: high - Dronecode flight stack for multirotors, fixed-wing, VTOL, rovers and boats, built on NuttX with a uORB pub/sub middleware.
- [LIO-SAM](../repos/tixiaoshan__lio-sam.md) - fit: high - Tightly coupled LiDAR-inertial odometry via factor-graph smoothing, with optional GPS factors and loop closure.
- [GTSAM](../repos/borglab__gtsam.md) - fit: high - Georgia Tech factor-graph library for smoothing and mapping, with incremental solvers (iSAM2) and a full IMU preintegration factor set.
- [robot_localization](../repos/cra-ros-pkg__robot_localization.md) - fit: high - ROS package with EKF and UKF state estimation nodes that fuse any number of odometry, IMU, pose and GNSS inputs, plus a navsat_transform node for GPS-to-map conversion.
- [gnss-ins-sim](../repos/aceinna__gnss-ins-sim.md) - fit: high - Python GNSS/INS simulator that generates trajectories, IMU/GNSS/magnetometer measurements with configurable error models, and runs navigation algorithms on them.
- [KF-GINS](../repos/i2nav-whu__kf-gins.md) - fit: high - Wuhan University i2Nav reference implementation of loosely coupled GNSS/INS integration with an error-state EKF, with sample data and documentation.
- [imu_x_fusion](../repos/cggos__imu_x_fusion.md) - fit: high - Loosely coupled IMU + GNSS / 6-DoF odometry fusion with multiple estimators side by side (ESKF, IEKF, UKF variants, MAP).
- [MINS](../repos/rpng__mins.md) - fit: high - Multi-sensor aided inertial navigation that fuses IMU with camera, LiDAR, GNSS and wheel odometry, including online spatial/temporal calibration and a multi-sensor simulator.
- [imu_gps_localization](../repos/ydsf16__imu_gps_localization.md) - fit: high - Error-state Kalman filter fusing IMU and GPS for localization, small and readable.
- [OB_GINS](../repos/i2nav-whu__ob_gins.md) - fit: high - Optimization-based GNSS/INS integration from Wuhan University i2Nav, using IMU preintegration in a sliding-window factor graph solved with Ceres.
- [UrbanNav](../repos/ipnl-polyu__urbannavdataset.md) - fit: high - Open multisensor urban positioning dataset from PolyU IPNL with GNSS, IMU, lidar and camera in deep urban canyons.
- [pyins](../repos/nmayorov__pyins.md) - fit: high - Python package for modelling and analysing inertial navigation systems: strapdown integration, error models, Kalman-filter aiding and sensor simulation.
- [VINS-Fusion](../repos/hkust-aerial-robotics__vins-fusion.md) - fit: medium - Extension of VINS-Mono supporting mono+IMU, stereo, and stereo+IMU, with optional loose fusion of global sensors such as GPS.
- [INAV](../repos/inavflight__inav.md) - fit: medium - Navigation-focused fork of the Cleanflight/Betaflight lineage for small multirotors, fixed-wing and rovers, adding GPS position hold, return-to-home and waypoint missions on cheap F4/F7/H7 boards.
- [hdl_graph_slam](../repos/koide3__hdl_graph_slam.md) - fit: medium - 3D LiDAR graph SLAM with NDT/GICP scan matching odometry, loop detection and optional GPS, IMU and floor-plane constraints.
- [M2DGR](../repos/sjtu-visys__m2dgr.md) - fit: medium - Multi-modal, multi-scenario ground robot dataset from SJTU with cameras, lidar, IMU, GNSS and more, indoor and outdoor.
- [eskf-gps-imu-fusion](../repos/zm0612__eskf-gps-imu-fusion.md) - fit: medium - ESKF fusing GPS and IMU for improved positioning, with documentation in Chinese.
- [IC-GVINS](../repos/i2nav-whu__ic-gvins.md) - fit: medium - INS-centric GNSS-visual-inertial navigation system from i2Nav, where the precise INS drives the visual front end and GNSS is fused in a factor graph.
- [GICI-LIB](../repos/chichengcn__gici-open.md) - fit: medium - GNSS/INS/Camera integrated navigation library supporting a range of GNSS modes (SPP, RTK, PPP and variants) tightly fused with inertial and visual data via factor graph optimization.
- [NaveGo](../repos/rodralez__navego.md) - fit: medium - Open MATLAB/GNU Octave toolbox for simulating and processing integrated INS/GNSS navigation, including IMU error modelling and Allan variance analysis.
- [OKVIS2-X](../repos/ethz-mrl__okvis2-x.md) - fit: medium - Extension of OKVIS2 that can additionally use dense depth or LiDAR and fuse GNSS.
- [GVINS dataset](../repos/hkust-aerial-robotics__gvins-dataset.md) - fit: medium - Dataset with synchronized visual, inertial and raw GNSS measurements released with GVINS.
- [ESKF ROS (EliaTarasov)](../repos/eliatarasov__eskf.md) - fit: medium - ROS error-state Kalman filter derived from PX4/ecl that fuses IMU with GPS, magnetometer, vision pose and optical flow.
- [gtsam_gnss](../repos/taroz__gtsam_gnss.md) - fit: medium - Custom GTSAM factors and MATLAB wrappers for GNSS factor-graph positioning, including pseudorange, Doppler and carrier-phase factors with ambiguity estimation.
- [GSDC 2023 solution (taroz)](../repos/taroz__gsdc2023.md) - fit: medium - Winning-team code for the Google Smartphone Decimeter Challenge 2023, using factor-graph style smartphone GNSS/IMU processing in MATLAB.
- [Baidu Apollo](../repos/apolloauto__apollo.md) - fit: low - Baidu's open autonomous driving platform, including the multi-sensor fusion localization module combining GNSS RTK, IMU and lidar map matching.
- [PX4 ECL (Estimation & Control Library)](../repos/px4__px4-ecl.md) - fit: low - Former home of PX4's estimation and control library including the EKF2 navigation filter; archived after the code moved into PX4-Autopilot.
- [GLIO](../repos/xikunliu-huskit__glio.md) - fit: low - Tightly coupled GNSS/LiDAR/IMU integration (PolyU) for continuous, drift-free state estimation in urban canyons.
- [gnss_comm](../repos/hkust-aerial-robotics__gnss_comm.md) - fit: low - C++/ROS definitions and utilities for raw GNSS measurement processing (ephemeris, satellite positions, pseudorange models) used by GVINS.
- [gps_imu_fusion](../repos/shelfcol__gps_imu_fusion.md) - fit: low - GPS/IMU fusion examples implemented with ESKF, EKF, UKF and other filters.

## Documents, talks, courses, datasets (22)

- [Complex Urban Dataset](../resources/kaist-complex-urban-dataset.md) - dataset - Urban driving in dense city areas with lidar, stereo and navigation sensors where GNSS is degraded.
- [EKF Source Selection and Switching](../resources/ardupilot-ekf3-sources.md) - doc - Reference for EKF3 source parameters (position, velocity, yaw per axis) and how fusion of multiple velocity sources works.
- [Extended Kalman Filter (EKF) navigation overview](../resources/ardupilot-ekf-overview.md) - doc - Overview of ArduPilot's EKF2/EKF3 estimators: states, sensor inputs, innovation checks, lane switching across multiple IMUs and tuning guidance.
- [FAA SAFO 24002: Recognizing and Mitigating GPS/GNSS Disruptions](../resources/faa-safo-24002-gnss-disruptions.md) - doc - FAA Safety Alert for Operators describing jamming vs spoofing effects on aircraft systems, typical locations near conflict and counter-UAS areas, and recommended crew and operator actions.
- [Factor Graphs for Robot Perception](../resources/dellaert-kaess-factor-graphs.md) - book - Foundations and Trends monograph (free author PDF) explaining SLAM and sensor fusion as inference on factor graphs, with incremental smoothing (iSAM) and the reasoning behind the GTSAM library.
- [GPS / Non-GPS Transitions](../resources/ardupilot-gps-non-gps-transitions.md) - doc - Explains configuring EKF3 with two source sets (e.g.
- [GTSAM Tutorial: Factor Graphs and GTSAM](../resources/gtsam-tutorial-intro.md) - doc - Hands-on introduction to the GTSAM library: modelling robot odometry, landmark and pose-graph SLAM as factor graphs, solving with Levenberg-Marquardt or iSAM2, and reading marginal covariances, with C++ and Python snippe
- [ION GNSS+ Tutorials](../resources/ion-gnss-plus-tutorials.md) - course - Pre-conference tutorial programme of ION GNSS+, the main annual GNSS technical meeting: half-day in-depth courses by field experts on topics such as GNSS signals, receivers, PPP/RTK, inertial integration and interference
- [LIO-SAM: Tightly-coupled Lidar Inertial Odometry via Smoothing and Mapping](../resources/lio-sam-shan-2020.md) - paper - Formulates LiDAR-inertial odometry as factor-graph smoothing with IMU preintegration, LiDAR odometry, GPS and loop-closure factors.
- [MARS-LVIG Dataset](../resources/hku-mars-lvig-dataset.md) - dataset - Aerial robot SLAM dataset for lidar-visual-inertial-GNSS fusion, including sequences with raw GNSS measurements under different lighting.
- [Navigating Using GPS Localization (Nav2 tutorial)](../resources/nav2-gps-navigation-tutorial.md) - doc - Nav2 tutorial on outdoor navigation with GPS: fusing GNSS, IMU and odometry with robot_localization's navsat_transform, configuring Nav2 for GPS waypoints, and demonstrating it in Gazebo.
- [Principles of GNSS, Inertial, and Multisensor Integrated Navigation Systems, Second Edition](../resources/groves-pnt-book-2e.md) - book - Standard reference on satellite, inertial and terrestrial radio navigation and their integration, including INS/GNSS integration architectures, dead reckoning, feature matching and integrity monitoring.
- [PX4 Developer Summit (talks and recordings)](../resources/px4-developer-summit.md) - talk - Annual PX4 developer conference; recordings are posted on the PX4 YouTube channel.
- [PX4 state estimation update (PX4 Developer Summit Virtual 2020)](../resources/riseborough-px4-state-estimation-2020.md) - talk - Slide deck from the EKF2 lead developer covering estimator changes, including operation without GPS and handling of non-GPS aiding sensors.
- [Quaternion kinematics for the error-state Kalman filter](../resources/sola-quaternion-eskf.md) - paper - Widely used tutorial on quaternion algebra, rotation integration and the error-state Kalman filter for IMU-driven navigation, including full IMU+GPS-style ESKF derivations.
- [robot_localization package documentation](../resources/robot-localization-docs.md) - doc - Documentation for the widely used ROS EKF/UKF state estimation package, including state-estimation node configuration, sensor integration, and navsat_transform for GPS.
- [ROSCon UK 2025 - State Estimation for Mobile Robotics Workshop](../resources/nav2-roscon-uk-2025-state-estimation-workshop.md) - masterclass - Hands-on workshop material comparing two ROS 2 state-estimation approaches: Kalman filtering with robot_localization (EKF/UKF, covariance tuning, frames, rate handling) and factor-graph fixed-lag smoothing with fuse.
- [State Estimation and Localization for Self-Driving Cars (Coursera)](../resources/coursera-state-estimation-localization-sdc.md) - course - Course 2 of the UofT Self-Driving Cars specialization: least squares, KF/EKF/ES-EKF/UKF, IMU and GNSS sensor models, LiDAR scan matching with ICP, culminating in an error-state EKF that fuses IMU, GNSS and LiDAR on CARLA
- [Understanding Sensor Fusion and Tracking (MATLAB Tech Talks)](../resources/mathworks-understanding-sensor-fusion-tracking.md) - video - Short video series on sensor fusion for autonomous systems: what sensor fusion is, IMU/magnetometer orientation estimation, fusing GPS and IMU for pose with an asynchronous EKF, single- and multi-object tracking, and tra
- [UrbanLoco: A Full Sensor Suite Dataset for Mapping and Localization in Urban Scenes](../resources/polyu-urbanloco-dataset.md) - dataset - Driving data from Hong Kong and California urban canyons with a full sensor suite, targeted at GNSS outliers and degraded localization.
- [Using PX4's Navigation Filter (EKF2)](../resources/px4-ekf2-guide.md) - doc - PX4 guide to its EKF2 estimator: which sensors it fuses (IMU, GNSS, baro, mag, optical flow, external vision, range), how to configure and tune them, and how to read innovation logs.
- [Using the ECL EKF (EKF2)](../resources/px4-ekf2-tuning-guide.md) - doc - PX4's main EKF2 guide: states, sensor fusion options (GNSS, flow, external vision, range, airspeed), aiding modes, innovation monitoring and tuning.

