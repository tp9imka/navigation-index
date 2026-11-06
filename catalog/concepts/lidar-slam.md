# LiDAR odometry and SLAM

`concept:lidar-slam`

LiDAR(-inertial) odometry, scan matching, LiDAR mapping.

## Repositories (54)

- [FAST-LIO / FAST-LIO2](../repos/hku-mars__fast_lio.md) - fit: high - Computationally efficient LiDAR-inertial odometry using an iterated error-state Kalman filter and incremental k-d tree map, mapping raw points directly.
- [LIO-SAM](../repos/tixiaoshan__lio-sam.md) - fit: high - Tightly coupled LiDAR-inertial odometry via factor-graph smoothing, with optional GPS factors and loop closure.
- [evo](../repos/michaelgrupp__evo.md) - fit: high - Python package and CLI for evaluating odometry and SLAM trajectories (ATE/RPE, alignment, plotting) in TUM, KITTI, EuRoC and ROS bag formats.
- [RTAB-Map](../repos/introlab__rtabmap.md) - fit: high - Graph-based SLAM library and app supporting RGB-D, stereo and LiDAR, with memory management for large-scale loop closure and map reuse.
- [KISS-ICP](../repos/prbonn__kiss-icp.md) - fit: high - Minimal LiDAR odometry based on point-to-point ICP with adaptive thresholding, working across sensors with few parameters.
- [FAST_LIO_LOCALIZATION](../repos/hviktortsoi__fast_lio_localization.md) - fit: high - Relocalization in a prebuilt map using FAST-LIO odometry plus global scan-to-map registration.
- [small_gicp](../repos/koide3__small_gicp.md) - fit: high - Efficient, parallel point-cloud registration library (GICP, ICP variants) with C++ and Python APIs.
- [livox_ros_driver2](../repos/livox-sdk__livox_ros_driver2.md) - fit: high - ROS 1/ROS 2 driver for Livox LiDARs such as Mid-360 and HAP.
- [RKO-LIO](../repos/prbonn__rko_lio.md) - fit: high - LiDAR-inertial odometry aiming to work without sensor-specific modelling or heavy tuning.
- [KISS-SLAM](../repos/prbonn__kiss-slam.md) - fit: high - LiDAR SLAM that adds loop closure and pose-graph optimization on top of KISS-ICP odometry.
- [ardupilot_ros](../repos/ardupilot__ardupilot_ros.md) - fit: high - ROS 2 integration examples for ArduPilot, including Cartographer-based non-GPS navigation and Nav2 setups.
- [Autoware](../repos/autowarefoundation__autoware.md) - fit: medium - Meta-repository for Autoware, the open-source ROS 2 autonomous driving stack covering localization (NDT, EKF), perception, planning and control.
- [Cartographer](../repos/cartographer-project__cartographer.md) - fit: medium - Real-time 2D and 3D SLAM with submaps and branch-and-bound loop closure across many sensor configurations.
- [FAST-LIVO2](../repos/hku-mars__fast-livo2.md) - fit: medium - Direct LiDAR-inertial-visual odometry fusing LiDAR, camera and IMU in a sequential ESIKF update with a unified voxel map.
- [SLAM Handbook (public release)](../repos/slam-handbook-contributors__slam-handbook-public-release.md) - fit: medium - Release repo for the SLAM Handbook (Cambridge University Press), edited by Carlone, Kim, Barfoot, Cremers and Dellaert, published incrementally in three parts from late 2024.
- [TEASER++](../repos/mit-spark__teaser-plusplus.md) - fit: medium - Certifiable, outlier-robust point-cloud registration library with C++, Python and MATLAB bindings.
- [hdl_graph_slam](../repos/koide3__hdl_graph_slam.md) - fit: medium - 3D LiDAR graph SLAM with NDT/GICP scan matching odometry, loop detection and optional GPS, IMU and floor-plane constraints.
- [GLIM](../repos/koide3__glim.md) - fit: medium - Versatile point-cloud localization and mapping framework with GPU-accelerated factor graphs, supporting many range sensors and optional IMU.
- [Autoware Universe](../repos/autowarefoundation__autoware_universe.md) - fit: medium - The broad package collection of Autoware with experimental and production-candidate modules, including localization, pose initialization and GNSS/IMU fusion.
- [fast_gicp](../repos/koide3__fast_gicp.md) - fit: medium - Collection of fast GICP and VGICP point-cloud registration implementations, multithreaded and CUDA.
- [Faster-LIO](../repos/gaoxiang12__faster-lio.md) - fit: medium - Lightweight tightly coupled LiDAR-inertial odometry using parallel sparse incremental voxels instead of a k-d tree.
- [LiDAR_IMU_Init](../repos/hku-mars__lidar_imu_init.md) - fit: medium - Real-time LiDAR-inertial initialization estimating extrinsics, time offset, gravity and IMU bias online (IROS 2022).
- [Point-LIO](../repos/hku-mars__point-lio.md) - fit: medium - High-bandwidth LiDAR-inertial odometry that updates the state point by point, tolerating aggressive motion and IMU saturation.
- [DLIO](../repos/vectr-ucla__direct_lidar_inertial_odometry.md) - fit: medium - Lightweight LiDAR-inertial odometry with coarse-to-fine continuous-time motion correction (ICRA 2023).
- [SC-LIO-SAM](../repos/gisbi-kim__sc-lio-sam.md) - fit: medium - LIO-SAM combined with Scan Context loop closure for more reliable large-scale LiDAR-inertial SLAM.
- [STD](../repos/hku-mars__std.md) - fit: medium - Stable Triangle Descriptor for 3D point-cloud place recognition and loop closure.
- [Swarm-SLAM](../repos/mistlab__swarm-slam.md) - fit: medium - Sparse, decentralized collaborative SLAM for multi-robot systems on ROS 2, supporting lidar, stereo and RGB-D with inter-robot loop closures under limited communication.
- [MARSIM](../repos/hku-mars__marsim.md) - fit: medium - Lightweight point-realistic lidar simulator for UAVs from HKU MaRS, supporting rotating and solid-state lidar patterns.
- [Kimera-RPGO](../repos/mit-spark__kimera-rpgo.md) - fit: medium - Robust pose-graph optimization that rejects bad loop closures via pairwise consistency maximization on top of GTSAM.
- [MapClosures](../repos/prbonn__mapclosures.md) - fit: medium - Loop-closure detection using bird's-eye-view density images of local LiDAR maps.
- [OKVIS2-X](../repos/ethz-mrl__okvis2-x.md) - fit: medium - Extension of OKVIS2 that can additionally use dense depth or LiDAR and fuse GNSS.
- [LAMP (NeBula multi-robot SLAM)](../repos/nebula-autonomy__lamp.md) - fit: medium - Team CoSTAR's large-scale multi-robot lidar SLAM back end with robust loop closure, from the NASA JPL-led SubT entry.
- [DARPA SubT Virtual Challenge](../repos/osrf__subt.md) - fit: medium - Gazebo worlds, robot models, ROS interfaces and scoring tools from the virtual track of the DARPA Subterranean Challenge.
- [DCL-SLAM](../repos/zhongshp__dcl-slam.md) - fit: medium - Distributed collaborative lidar SLAM for robotic swarms with lightweight LiDAR-Iris descriptors for inter-robot place recognition and minimal data exchange.
- [4DRadarSLAM](../repos/zhuge2333__4dradarslam.md) - fit: medium - 4D radar SLAM with scan-to-scan registration, loop closure and pose-graph optimization, released with an NTU 4D radar dataset.
- [sonar-SLAM](../repos/jake3991__sonar-slam.md) - fit: medium - Underwater SLAM for robots with multibeam imaging sonar, from Stevens Institute research on BlueROV-class vehicles, combining sonar feature extraction and pose-graph optimization.
- [STEAM-ICP](../repos/utiasasrl__steam_icp.md) - fit: medium - Continuous-time lidar, radar, lidar-inertial and radar-inertial odometry built on the STEAM library.
- [MIMOSA](../repos/ntnu-arl__mimosa.md) - fit: medium - Tightly coupled sliding-window factor-graph fusion of IMU with LiDAR (geometric and photometric), radar radial-speed factors and external odometry such as VIO.
- [Scan Context](../repos/gisbi-kim__scancontext.md) - fit: medium - LiDAR global place descriptor for loop detection and relocalization (backup of the original IRAP KAIST repo).
- [Hilti SLAM Challenge 2023](../repos/hilti-research__hilti-slam-challenge-2023.md) - fit: medium - Repository for the 2023 Hilti SLAM Challenge, including multi-session sequences.
- [Hilti SLAM Challenge 2022](../repos/hilti-research__hilti-slam-challenge-2022.md) - fit: medium - Repository for the 2022 Hilti SLAM Challenge with dataset info and evaluation tooling.
- [NeBula multi-robot dataset](../repos/nebula-autonomy__nebula-multirobot-dataset.md) - fit: medium - Index for CoSTAR's multi-robot lidar/IMU/odometry datasets recorded in tunnels, mines and urban underground sites.
- [Swarm-SLAM](../repos/lajoiepy__cslam.md) - fit: medium - ROS 2 decentralized collaborative SLAM supporting LiDAR, stereo and RGB-D, with sparse inter-robot communication.
- [MCD: Multi-Campus Dataset](../repos/mcdviral__mcdviral.github.io.md) - fit: medium - Site repo for MCD, a multi-campus dataset across Asia and Europe with spinning and non-repetitive lidar, stereo cameras, IMUs, UWB ranging, survey-grade prior maps and continuous-time ground truth.
- [CoLRIO](../repos/pengyu-team__co-lrio.md) - fit: medium - ROS 2 centralized lidar-ranging-inertial state estimation for robotic swarms that offloads optimization to a server and uses UWB inter-robot ranges (ICRA 2024).
- [LeGO-LOAM](../repos/robustfieldautonomylab__lego-loam.md) - fit: low - Lightweight ground-optimized LiDAR odometry and mapping that segments ground to speed up feature extraction on UGVs.
- [R3LIVE](../repos/hku-mars__r3live.md) - fit: low - Tightly coupled LiDAR-inertial-visual estimation and RGB-colored mapping package.
- [LI-Calib](../repos/april-zju__lidar_imu_calib.md) - fit: low - Targetless LiDAR-IMU calibration based on continuous-time batch estimation (IROS 2020).
- [lidar_imu_calib](../repos/chennuo0125-hit__lidar_imu_calib.md) - fit: low - Automatic calibration of the extrinsic rotation between a 3D LiDAR and an IMU.
- [GLIO](../repos/xikunliu-huskit__glio.md) - fit: low - Tightly coupled GNSS/LiDAR/IMU integration (PolyU) for continuous, drift-free state estimation in urban canyons.
- [Quatro](../repos/url-kaist__quatro.md) - fit: low - Fast, robust global registration for terrestrial robots that assumes near-planar motion to cut degrees of freedom.
- [LE-VINS](../repos/i2nav-whu__le-vins.md) - fit: low - INS-centric visual-inertial navigation with LiDAR depth enhancement for visual features, from i2Nav.
- [STEAM](../repos/utiasasrl__steam.md) - fit: low - Simultaneous Trajectory Estimation and Mapping engine from UTIAS: a C++ nonlinear least-squares library with continuous-time Gaussian-process trajectory priors on Lie groups.
- [CELL](../repos/panagiotisq__cell.md) - fit: low - Event camera localization in prior lidar maps with confidence weighting.

## Documents, talks, courses, datasets (31)

- [Autoware documentation](../resources/autoware-docs.md) - doc - Official Autoware documentation with architecture, installation, tutorials and design notes for localization, perception and planning components.
- [CERBERUS: Autonomous Legged and Aerial Robotic Exploration in the Tunnel and Urban Circuits of the DARPA Subterranean Challenge](../resources/cerberus-tunnel-urban-paper.md) - paper - Field Robotics paper covering CERBERUS' systems and results in the earlier SubT circuits, including perception, planning and artifact reporting.
- [Cyrill Stachniss YouTube channel (incl. '5 Minutes with Cyrill')](../resources/stachniss-youtube-channel.md) - video - Channel hosting Stachniss's full lecture courses plus the '5 Minutes with Cyrill' series of short explainers on single concepts (Kalman filter, factor graphs, ICP, RANSAC, SIFT, occupancy grids).
- [DARPA SubT Reference Datasets](../resources/darpa-subt-reference-datasets.md) - dataset - Reference sensor datasets and artifact data released for the DARPA Subterranean Challenge, hosted on Bitbucket.
- [DARPA Subterranean (SubT) Challenge](../resources/darpa-subt-challenge.md) - competition - DARPA's 2018-2021 challenge for autonomous robot teams mapping and searching tunnels, urban underground and caves with no GNSS and degraded comms; systems and virtual tracks.
- [DCL-SLAM: A Distributed Collaborative LiDAR SLAM Framework for a Robotic Swarm](../resources/dcl-slam-paper.md) - paper - Describes a fully distributed lidar C-SLAM using compact descriptors for inter-robot place recognition.
- [ERF26 workshop: Innovation and developments in robotic GNSS-denied localisation for inspection & maintenance](../resources/erf26-sintef-gnss-denied-localisation-workshop.md) - talk - European Robotics Forum 2026 workshop (Stavanger) organised by SINTEF on GNSS-denied robot localisation in indoor, offshore, underground and urban-canyon settings, bringing together researchers, vendors and end users.
- [FAST-LIO2: Fast Direct LiDAR-inertial Odometry](../resources/fast-lio2-xu-2021.md) - paper - Introduces direct registration of raw LiDAR points in an iterated Kalman filter with an incremental k-d tree map, avoiding hand-crafted feature extraction.
- [FAST-LIVO2: Fast, Direct LiDAR-Inertial-Visual Odometry](../resources/fast-livo2-zheng-2024.md) - paper - Presents an error-state iterated Kalman filter that sequentially fuses LiDAR and image measurements against a shared voxel map, with exposure and plane-prior handling.
- [GSoC 2022: Update ROS integration for Non-GPS navigation and off-board path planning](../resources/ardupilot-gsoc2022-ros-non-gps.md) - blog - Wrap-up of a GSoC project updating ArduPilot's ROS integration for lidar/SLAM-based non-GPS navigation and off-board planning.
- [HeLiPR: Heterogeneous LiDAR Dataset for inter-LiDAR Place Recognition](../resources/snu-helipr-dataset.md) - dataset - Same routes captured with Ouster, Aeva, Livox and Velodyne lidars to test place recognition across different lidar types.
- [Hilti SLAM Challenge](../resources/hilti-slam-challenge.md) - competition - SLAM benchmark challenge with datasets from handheld and robot-mounted multi-sensor rigs in construction sites and buildings, run with an associated ICRA workshop and public leaderboard.
- [KISS-ICP: In Defense of Point-to-Point ICP -- Simple, Accurate, and Robust Registration If Done the Right Way](../resources/kiss-icp-vizzo-2022.md) - paper - Argues that a carefully engineered point-to-point ICP with motion compensation and adaptive thresholds matches far more complex LiDAR odometry across platforms.
- [KITTI Visual Odometry / SLAM Evaluation](../resources/kitti-odometry-benchmark.md) - dataset - Driving sequences with stereo cameras, Velodyne lidar and GPS/IMU ground truth, plus a public leaderboard for odometry.
- [LiDAR Odometry Survey: Recent Advancements and Remaining Challenges](../resources/lee-lidar-odometry-survey-2023.md) - paper - Survey of LiDAR-only, LiDAR-inertial and multi-sensor LiDAR odometry, with discussion of datasets, evaluation and open challenges such as degeneracy.
- [LIO-SAM: Tightly-coupled Lidar Inertial Odometry via Smoothing and Mapping](../resources/lio-sam-shan-2020.md) - paper - Formulates LiDAR-inertial odometry as factor-graph smoothing with IMU preintegration, LiDAR odometry, GPS and loop-closure factors.
- [MARS-LVIG Dataset](../resources/hku-mars-lvig-dataset.md) - dataset - Aerial robot SLAM dataset for lidar-visual-inertial-GNSS fusion, including sequences with raw GNSS measurements under different lighting.
- [MCD: Diverse Large-Scale Multi-Campus Dataset for Robot Perception](../resources/mcd-multi-campus-dataset.md) - dataset - Multi-campus sequences in Asia and Europe across seasons with two lidar types, stereo, IMUs, UWB and survey-grade prior maps.
- [Nav2 ROSCon Talks index](../resources/nav2-roscon-talks-index.md) - video - Index of ROSCon talks by Nav2 developers and the community (Vimeo links), including SLAM Toolbox and large-scale indoor mapping talks.
- [NeBula: Quest for Robotic Autonomy in Challenging Environments; TEAM CoSTAR at the DARPA Subterranean Challenge](../resources/nebula-costar-subt-paper.md) - paper - Describes the NeBula belief-space autonomy stack: multi-modal positioning, mapping, traversability, risk-aware mission planning and multi-robot reasoning; CoSTAR won the Urban circuit.
- [Newer College Dataset](../resources/ori-newer-college-dataset.md) - dataset - Handheld lidar plus stereo and multi-camera sequences around New College, Oxford, with precise ground truth from a survey-grade prior map.
- [Online Training: Mobile Robotics (Basics + Robotics blocks)](../resources/stachniss-mobile-robotics-online-training.md) - lecture-series - A curated self-study path of short recorded lectures from Bonn's Photogrammetry & Robotics lab, going from linear algebra, rotations and least squares through Bayes filters, EKF localization, particle filters, ICP, RANSA
- [Past, Present, and Future of Simultaneous Localization And Mapping: Towards the Robust-Perception Age](../resources/cadena-slam-past-present-future-2016.md) - paper - Landmark survey that frames modern SLAM as factor-graph MAP estimation and discusses robustness, scalability, representations and open problems.
- [Robot Mapping (SLAM course) WS 2013/14](../resources/stachniss-slam-course-2013.md) - lecture-series - Full semester recording of the Freiburg Robot Mapping course: EKF-SLAM, sparse extended information filters, FastSLAM, grid-based mapping, least-squares and graph-based SLAM, and front-end/back-end design.
- [Robot Mapping - WS 2013/14 course page (slides, exercises)](../resources/freiburg-robot-mapping-course.md) - course - Course page that accompanies the Robot Mapping lecture videos, with lecture slides and programming exercises (EKF-SLAM, UKF, FastSLAM, least-squares calibration, graph-SLAM) in Octave/Matlab.
- [SLAM Handbook: From Localization and Mapping to Spatial Intelligence](../resources/slam-handbook.md) - book - Community-written handbook released in three parts during 2024-2025 and published by Cambridge University Press; the free PDF is mirrored on the editors' project page.
- [State Estimation and Localization for Self-Driving Cars (Coursera)](../resources/coursera-state-estimation-localization-sdc.md) - course - Course 2 of the UofT Self-Driving Cars specialization: least squares, KF/EKF/ES-EKF/UKF, IMU and GNSS sensor models, LiDAR scan matching with ICP, culminating in an error-state EKF that fuses IMU, GNSS and LiDAR on CARLA
- [SubT-MRS Dataset](../resources/cmu-subt-mrs-dataset.md) - dataset - Multi-robot, multi-modal SLAM data in degraded environments - caves, tunnels, urban and off-road - with RGB, lidar, thermal and inertial sensing; used in ICCV SLAM challenges.
- [Swarm-SLAM: Sparse Decentralized Collaborative Simultaneous Localization and Mapping Framework for Multi-Robot Systems](../resources/swarm-slam-paper.md) - paper - Decentralized collaborative SLAM aimed at swarms, prioritizing which inter-robot loop closures to compute and share to limit communication.
- [Team CERBERUS Wins the DARPA Subterranean Challenge: Technical Overview and Lessons Learned](../resources/cerberus-subt-final-paper.md) - paper - Winning team's description of its legged-plus-aerial system: multi-modal perception, robust localization and mapping, exploration planning and artifact detection, with lessons from the final.
- [The University of Michigan North Campus Long-Term Vision and LIDAR Dataset](../resources/umich-nclt-dataset.md) - dataset - Segway robot sessions over many months on one campus with lidar, omnidirectional camera, GPS, IMU and odometry.

