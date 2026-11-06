# Onboard / edge AI perception

`concept:edge-ai`

Detection, segmentation, depth on embedded hardware supporting navigation.

## Repositories (29)

- [Ultralytics YOLO](../repos/ultralytics__ultralytics.md) - fit: high - Widely used Python package for YOLO-family detection, segmentation and tracking with training, export to edge runtimes and built-in trackers.
- [BoxMOT](../repos/mikel-brostrom__boxmot.md) - fit: high - Pluggable collection of modern multi-object trackers (ByteTrack, BoT-SORT, OC-SORT, StrongSORT and others) for detector outputs, in Python and C++.
- [x-io Fusion](../repos/xiotechnologies__fusion.md) - fit: high - x-io Technologies' C AHRS library (revised Madgwick-style algorithm) with gyro offset correction, acceleration and magnetic disturbance rejection, and Python bindings.
- [XFeat](../repos/verlab__accelerated_features.md) - fit: high - Lightweight local feature extractor and matcher (CVPR 2024) designed for speed on constrained hardware.
- [elevation_mapping_cupy](../repos/leggedrobotics__elevation_mapping_cupy.md) - fit: high - GPU-accelerated elevation and traversability mapping from ETH Zurich, supporting semantic layers and learned traversability, used on ANYmal robots.
- [AI-IMU Dead-Reckoning](../repos/mbrossar__ai-imu-dr.md) - fit: high - Car dead reckoning from IMU only, using an invariant EKF whose noise covariances are adapted by a neural network, evaluated on KITTI.
- [Satellite-thermal geo-localization](../repos/arplaboratory__satellite-thermal-geo-localization.md) - fit: high - IROS 2023 code for long-range UAV thermal geo-localization against satellite RGB imagery, using domain adaptation to bridge thermal and visible imagery; comes with the Boson-nighttime dataset.
- [VGGT](../repos/facebookresearch__vggt.md) - fit: medium - Visual Geometry Grounded Transformer: a feed-forward network predicting camera poses, depth and point maps from one or many images (CVPR 2025 best paper).
- [NVIDIA Isaac Sim](../repos/isaac-sim__isaacsim.md) - fit: medium - NVIDIA's Omniverse-based robot simulator, now open source, with RTX sensor simulation (cameras, lidar, IMU) and ROS 2 bridges.
- [MASt3R-SLAM](../repos/rmurai0610__mast3r-slam.md) - fit: medium - Real-time dense monocular SLAM built on the MASt3R two-view 3D reconstruction prior, needing no fixed camera model (CVPR 2025).
- [DROID-SLAM](../repos/princeton-vl__droid-slam.md) - fit: medium - Deep visual SLAM that iterates dense bundle adjustment through a recurrent update operator, for monocular, stereo and RGB-D input.
- [AirSLAM](../repos/sair-lab__airslam.md) - fit: medium - Point-and-line visual(-inertial) SLAM using learned features, designed for illumination-robust operation, with TensorRT acceleration; successor to AirVO.
- [DPVO / DPV-SLAM](../repos/princeton-vl__dpvo.md) - fit: medium - Deep Patch Visual Odometry: learned sparse patch tracking for VO, plus DPV-SLAM with loop closure.
- [VolAnti](../repos/agamrossen__volanti.md) - fit: medium - Open-source acoustic drone detector that listens for propeller noise; explicitly detection and alerting only.
- [RFUAV](../repos/kitoweeknd__rfuav.md) - fit: medium - Code for the RFUAV benchmark dataset for UAV detection and identification from RF signals, using a two-stage STFT spectrogram detection and classification model.
- [Batear](../repos/batear-io__batear.md) - fit: medium - Low-cost edge-only acoustic drone detector on ESP32-S3 with encrypted LoRa or Ethernet alerting.
- [RoNIN](../repos/sachini__ronin.md) - fit: medium - Robust Neural Inertial Navigation: smartphone IMU dataset and baseline networks (ResNet, LSTM, TCN) regressing pedestrian velocity from IMU.
- [TLIO](../repos/cathias__tlio.md) - fit: medium - Tight Learned Inertial Odometry: a network regresses displacement and uncertainty from IMU windows, fused in a stochastic-cloning EKF.
- [MixVPR](../repos/amaralibey__mixvpr.md) - fit: medium - WACV 2023 place recognition descriptor built by MLP feature mixing; lightweight and fast.
- [Wild Visual Navigation](../repos/leggedrobotics__wild_visual_navigation.md) - fit: medium - System that learns visual traversability online from pre-trained vision features and robot self-supervision, deployed on legged robots in forests.
- [AirIO](../repos/air-io__air-io.md) - fit: medium - Learning-based inertial odometry for UAVs that improves feature observability by changing the IMU data representation (IEEE RA-L 2025).
- [AirIMU](../repos/haleqiu__airimu.md) - fit: medium - Learns IMU error correction and uncertainty with a network, combined with differentiable IMU preintegration (CMU AirLab).
- [galileo-osnma (Rust)](../repos/daniestevez__galileo-osnma.md) - fit: medium - Rust implementation of Galileo OSNMA that can run on embedded no_std targets, with examples for live receivers.
- [SPEED+ baseline](../repos/tpark94__speedplusbaseline.md) - fit: medium - PyTorch baselines and domain-bridging methods for spacecraft pose estimation on the SPEED+ dataset used in ESA Kelvins SPEC2021.
- [Denoise IMU Gyro](../repos/mbrossar__denoise-imu-gyro.md) - fit: low - CNN that denoises low-cost gyroscope signals to improve attitude estimation.
- [Learned Inertial Odometry for Drone Racing](../repos/uzh-rpg__learned_inertial_model_odometry.md) - fit: low - UZH RPG code fusing a learned inertial displacement model with an EKF for drone racing state estimation.
- [WayFAST](../repos/matval__wayfast.md) - fit: low - Self-supervised traversability prediction for wheeled field robots that learns from RGB-D and estimates traction from kinodynamic models.
- [EqNIO](../repos/royinajayanth__eqnio.md) - fit: low - Subequivariant neural inertial odometry (ICLR 2025) that canonicalises IMU data so networks generalise across orientations; applied on top of TLIO and RoNIN.
- [Deep learning celestial navigation](../repos/gregtozzi__deep_learning_celnav.md) - fit: low - Exploratory project on automating celestial navigation with deep learning and edge inference on synthetic sky images.

## Documents, talks, courses, datasets (13)

- [A Multi-Robot Platform for Robotic Triage](../resources/arxiv-multi-robot-triage-platform.md) - paper - Technical report from a DARPA Triage Challenge team describing a multi-robot system and fine-tuned open vision-language models for injury identification.
- [AI-IMU Dead-Reckoning](../resources/brossard-ai-imu-dr.md) - paper - Car localisation from IMU alone by combining an invariant EKF with a neural network that adapts measurement noise covariances (pseudo-measurements), evaluated on KITTI.
- [AirIO: Learning Inertial Odometry with Enhanced IMU Feature Observability](../resources/airio-paper.md) - paper - UAV-focused learned inertial odometry that changes how IMU data are represented to the network to make motion features more observable.
- [Champion-level drone racing using deep reinforcement learning](../resources/swift-champion-drone-racing-nature.md) - paper - Swift, a quadrotor using only onboard camera and IMU with an RL-trained policy, beat human world-champion pilots in head-to-head races.
- [DARPA Triage Challenge](../resources/darpa-triage-challenge.md) - competition - DARPA challenge for autonomous systems that find and assess casualties in mass-casualty scenes, combining drones and ground robots navigating degraded, GNSS-unreliable environments.
- [DROID-SLAM: Deep Visual SLAM for Monocular, Stereo, and RGB-D Cameras](../resources/droid-slam-teed-2021.md) - paper - Learned SLAM that iteratively refines poses and depth through a differentiable dense bundle adjustment layer.
- [ESA Kelvins Satellite Pose Estimation Competition 2021 (SPEED+)](../resources/kelvins-pose-estimation-2021.md) - competition - Follow-up Kelvins challenge focused on bridging the domain gap: train on synthetic images, test on hardware-in-the-loop lightbox and sunlamp images.
- [Isaac ROS Visual SLAM documentation](../resources/isaac-ros-visual-slam-docs.md) - doc - Docs and quickstarts for NVIDIA's GPU-accelerated stereo visual-inertial odometry and SLAM package for ROS 2 on Jetson, including tutorials with Isaac Sim and RealSense cameras.
- [Recent Advances on Jamming and Spoofing Detection in GNSS](../resources/rados-2024-jamming-spoofing-detection-review.md) - paper - Open-access Sensors review of GNSS jamming and spoofing detection methods, finding machine learning is now the dominant approach, and covering combined jamming-plus-spoofing scenarios.
- [RoNIN: Robust Neural Inertial Navigation in the Wild: Benchmark, Evaluations, and New Methods](../resources/ronin-paper.md) - paper - Introduces a large smartphone IMU dataset with ground truth and benchmarks neural architectures for pedestrian velocity regression.
- [TLIO: Tight Learned Inertial Odometry](../resources/tlio-paper.md) - paper - Combines a network that predicts displacement and uncertainty from IMU data with an EKF, for pedestrian inertial odometry.
- [Wild Visual Navigation: Fast Traversability Learning via Pre-Trained Models and Online Self-Supervision](../resources/wild-visual-navigation-paper.md) - paper - Describes learning visual traversability online from pre-trained features and robot experience, adapting within minutes in forests and grassland.
- [XFeat: Accelerated Features for Lightweight Image Matching](../resources/xfeat-2024.md) - paper - Lightweight feature extraction and matching architecture aimed at real-time use on constrained hardware.

