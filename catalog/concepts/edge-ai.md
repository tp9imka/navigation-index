# Onboard / edge AI perception

`concept:edge-ai`

Detection, segmentation, depth on embedded hardware supporting navigation.

## Samples (1)

- [Night / thermal UAV frame to RGB satellite geolocalization with a no-false-fix gate (ALIKED / DISK / SIFT + LightGlue, SGM baseline, Thermal-UAV)](../../catalog/samples/thermal-geolocalization.md) - Real nadir DJI M4T thermal frames (Thermal-UAV / SCC-Loc, Apache-2.0 card) matched against the dataset's 0.3 m RGB satellite GeoTIFF, by condition: city and village, day and night, day and night fog.

## Guides (1)

- [Model weights licenses: code vs weights vs training data](../../docs/model-weights-licenses.md) - Learned models in navigation pipelines carry three separate sets of terms:

## Repositories (54)

- [Ultralytics YOLO](../../catalog/repos/ultralytics__ultralytics.md) - fit: high - Widely used Python package for YOLO-family detection, segmentation and tracking with training, export to edge runtimes and built-in trackers.
- [Hello AI World (jetson-inference)](../../catalog/repos/dusty-nv__jetson-inference.md) - fit: high - NVIDIA's guide and library for deploying detection, segmentation and depth networks with TensorRT on Jetson, with camera streaming.
- [BoxMOT](../../catalog/repos/mikel-brostrom__boxmot.md) - fit: high - Pluggable collection of modern multi-object trackers (ByteTrack, BoT-SORT, OC-SORT, StrongSORT and others) for detector outputs, in Python and C++.
- [jetson-containers](../../catalog/repos/dusty-nv__jetson-containers.md) - fit: high - Build system and prebuilt containers for ML on Jetson (PyTorch, ROS, LLMs, VLMs) matched to JetPack versions.
- [torch2trt](../../catalog/repos/nvidia-ai-iot__torch2trt.md) - fit: high - Converts PyTorch models to TensorRT engines with a single call, aimed at Jetson deployment.
- [cuVSLAM](../../catalog/repos/nvidia-isaac__cuvslam.md) - fit: high - NVIDIA's CUDA-accelerated visual odometry and SLAM library supporting mono to multi-camera rigs with optional IMU, with Python bindings.
- [x-io Fusion](../../catalog/repos/xiotechnologies__fusion.md) - fit: high - x-io Technologies' C AHRS library (revised Madgwick-style algorithm) with gyro offset correction, acceleration and magnetic disturbance rejection, and Python bindings.
- [XFeat](../../catalog/repos/verlab__accelerated_features.md) - fit: high - Lightweight local feature extractor and matcher (CVPR 2024) designed for speed on constrained hardware.
- [Isaac ROS Visual SLAM](../../catalog/repos/nvidia-isaac-ros__isaac_ros_visual_slam.md) - fit: high - ROS 2 package wrapping NVIDIA's GPU-accelerated cuVSLAM for stereo visual(-inertial) odometry and SLAM on Jetson and x86 GPUs.
- [GNM / ViNT / NoMaD](../../catalog/repos/robodhruv__visualnav-transformer.md) - fit: high - Code and checkpoints for general visual navigation foundation models (GNM, ViNT, NoMaD) that drive robots from camera images toward image goals or explore, with ROS deployment code.
- [elevation_mapping_cupy](../../catalog/repos/leggedrobotics__elevation_mapping_cupy.md) - fit: high - GPU-accelerated elevation and traversability mapping from ETH Zurich, supporting semantic layers and learned traversability, used on ANYmal robots.
- [DepthAI](../../catalog/repos/luxonis__depthai.md) - fit: high - Landing repository for Luxonis OAK cameras, which run neural networks and stereo depth on the camera; the default branch now only points to the docs, and the old examples live on the `main` branch.
- [AI-IMU Dead-Reckoning](../../catalog/repos/mbrossar__ai-imu-dr.md) - fit: high - Car dead reckoning from IMU only, using an invariant EKF whose noise covariances are adapted by a neural network, evaluated on KITTI.
- [LightGlue-ONNX](../../catalog/repos/fabio-sim__lightglue-onnx.md) - fit: high - ONNX export and inference of LightGlue matching with SuperPoint, DISK and ALIKED extractors (including RaCo-ALIKED-LightGlue+), with TensorRT, OpenVINO and FP8 quantization workflows.
- [Isaac ROS nvblox](../../catalog/repos/nvidia-isaac-ros__isaac_ros_nvblox.md) - fit: high - GPU-accelerated 3D reconstruction (TSDF/ESDF) that provides Nav2 local costmaps from depth cameras.
- [Satellite-thermal geo-localization](../../catalog/repos/arplaboratory__satellite-thermal-geo-localization.md) - fit: high - IROS 2023 code for long-range UAV thermal geo-localization against satellite RGB imagery, using domain adaptation to bridge thermal and visible imagery; comes with the Boson-nighttime dataset.
- [GNSS jamming/spoofing classification notebooks](../../catalog/repos/alicmu2024__gnss-jamming-detection-and-classification-using-machine-learning-deep-learning-and-computer-vision.md) - fit: high - Colab notebooks for GNSS jamming-type classification (ML, DL and CV on spectrogram images) from a public raw-IQ jamming set, plus one GPS spoofing ML notebook; companion to arXiv 2501.02352.
- [Batear datasets](../../catalog/repos/batear-io__batear-datasets.md) - fit: high - Small Git LFS collection of drone and background audio for ESP32-S3 acoustic detection: about 89 WAV clips of DJI Mavic Pro, Mini 4 Pro and 5-inch FPV flights, ambient (urban, rural, fireworks, bat sites) and synthetic s
- [aerial-nav - GPS-denied navigation via Siamese network](../../catalog/repos/sviridov-aleksandr__aerial-nav.md) - fit: high - Matches onboard camera frames to a pre-built satellite map of the route: a ResNet-18 Siamese network with SAFA spatial aggregation ranks map tiles indexed at 13 altitude levels (0-1200 m), then SuperPoint/LightGlue with 
- [Gagarin - TERCOM for UAVs without GNSS](../../catalog/repos/danilka88__gag27062026.md) - fit: high - Python TERCOM pipeline from the June 2026 'Полёт вслепую' hackathon, continued into July: correlates radar-altimeter profiles with a DEM using a coarse-to-fine 360-degree search, a hybrid MAD+NCC metric, minima-ratio dis
- [RFClassification](../../catalog/repos/codymq__rfclassification.md) - fit: high - Notebooks that classify drone presence and type from RF using DroneRF and DroneDetect data (PSD+SVM and CNN approaches), aiming at real-time use with GamutRF hardware.
- [PINTO model zoo](../../catalog/repos/pinto0309__pinto_model_zoo.md) - fit: medium - Large collection of models converted between TensorFlow, TFLite, ONNX, OpenVINO, TensorRT and others.
- [NVIDIA Isaac Sim](../../catalog/repos/isaac-sim__isaacsim.md) - fit: medium - NVIDIA's Omniverse-based robot simulator, now open source, with RTX sensor simulation (cameras, lidar, IMU) and ROS 2 bridges.
- [MASt3R-SLAM](../../catalog/repos/rmurai0610__mast3r-slam.md) - fit: medium - Real-time dense monocular SLAM built on the MASt3R two-view 3D reconstruction prior, needing no fixed camera model (CVPR 2025).
- [RKNN Model Zoo](../../catalog/repos/airockchip__rknn_model_zoo.md) - fit: medium - Rockchip's examples and converted models for its NPU (RK3588 and similar), with deployment code.
- [DROID-SLAM](../../catalog/repos/princeton-vl__droid-slam.md) - fit: medium - Deep visual SLAM that iterates dense bundle adjustment through a recurrent update operator, for monocular, stereo and RGB-D input.
- [AirSLAM](../../catalog/repos/sair-lab__airslam.md) - fit: medium - Point-and-line visual(-inertial) SLAM using learned features, designed for illumination-robust operation, with TensorRT acceleration; successor to AirVO.
- [DPVO / DPV-SLAM](../../catalog/repos/princeton-vl__dpvo.md) - fit: medium - Deep Patch Visual Odometry: learned sparse patch tracking for VO, plus DPV-SLAM with loop closure.
- [ros_deep_learning](../../catalog/repos/dusty-nv__ros_deep_learning.md) - fit: medium - ROS/ROS 2 nodes wrapping jetson-inference for detection, classification and segmentation with TensorRT.
- [Hailo Raspberry Pi 5 examples](../../catalog/repos/hailo-ai__hailo-rpi5-examples.md) - fit: medium - Examples for Hailo-8/8L accelerators on Raspberry Pi 5 (AI Kit/HAT): detection, pose and segmentation pipelines; marked outdated in favor of hailo-apps.
- [VolAnti](../../catalog/repos/agamrossen__volanti.md) - fit: medium - Open-source acoustic drone detector that listens for propeller noise; explicitly detection and alerting only.
- [RFUAV](../../catalog/repos/kitoweeknd__rfuav.md) - fit: medium - Code for the RFUAV benchmark dataset for UAV detection and identification from RF signals, using a two-stage STFT spectrogram detection and classification model.
- [Batear](../../catalog/repos/batear-io__batear.md) - fit: medium - Low-cost edge-only acoustic drone detector on ESP32-S3 with encrypted LoRa or Ethernet alerting.
- [RoNIN](../../catalog/repos/sachini__ronin.md) - fit: medium - Robust Neural Inertial Navigation: smartphone IMU dataset and baseline networks (ResNet, LSTM, TCN) regressing pedestrian velocity from IMU.
- [TLIO](../../catalog/repos/cathias__tlio.md) - fit: medium - Tight Learned Inertial Odometry: a network regresses displacement and uncertainty from IMU windows, fused in a stochastic-cloning EKF.
- [DepthAI Core](../../catalog/repos/luxonis__depthai-core.md) - fit: medium - C++ core library and Python bindings for Luxonis OAK cameras: on-device stereo depth, neural inference and feature tracking pipelines.
- [DepthAI ROS](../../catalog/repos/luxonis__depthai-ros.md) - fit: medium - ROS 1/2 driver for Luxonis OAK cameras publishing depth, detections and IMU.
- [MixVPR](../../catalog/repos/amaralibey__mixvpr.md) - fit: medium - WACV 2023 place recognition descriptor built by MLP feature mixing; lightweight and fast.
- [Wild Visual Navigation](../../catalog/repos/leggedrobotics__wild_visual_navigation.md) - fit: medium - System that learns visual traversability online from pre-trained vision features and robot self-supervision, deployed on legged robots in forests.
- [OpenEB](../../catalog/repos/prophesee-ai__openeb.md) - fit: medium - Prophesee's open SDK for event-based vision: camera drivers, data formats, visualization and algorithm building blocks.
- [AirIO](../../catalog/repos/air-io__air-io.md) - fit: medium - Learning-based inertial odometry for UAVs that improves feature observability by changing the IMU data representation (IEEE RA-L 2025).
- [AirIMU](../../catalog/repos/haleqiu__airimu.md) - fit: medium - Learns IMU error correction and uncertainty with a network, combined with differentiable IMU preintegration (CMU AirLab).
- [Isaac ROS DNN Inference](../../catalog/repos/nvidia-isaac-ros__isaac_ros_dnn_inference.md) - fit: medium - ROS 2 packages for TensorRT and Triton inference on Jetson and x86, with encoder/decoder nodes for common model types.
- [galileo-osnma (Rust)](../../catalog/repos/daniestevez__galileo-osnma.md) - fit: medium - Rust implementation of Galileo OSNMA that can run on embedded no_std targets, with examples for live receivers.
- [SPEED+ baseline](../../catalog/repos/tpark94__speedplusbaseline.md) - fit: medium - PyTorch baselines and domain-bridging methods for spacecraft pose estimation on the SPEED+ dataset used in ESA Kelvins SPEC2021.
- [MBEG](../../catalog/repos/reza-zhu__acmmm23-solution-mbeg.md) - fit: medium - Modern-backbone efficient geo-localization solution for UAVM 2023 including distillation training.
- [VGGT](../../catalog/repos/facebookresearch__vggt.md) - fit: low - Visual Geometry Grounded Transformer: a feed-forward network predicting camera poses, depth and point maps from one or many images (CVPR 2025 best paper).
- [Denoise IMU Gyro](../../catalog/repos/mbrossar__denoise-imu-gyro.md) - fit: low - CNN that denoises low-cost gyroscope signals to improve attitude estimation.
- [Learned Inertial Odometry for Drone Racing](../../catalog/repos/uzh-rpg__learned_inertial_model_odometry.md) - fit: low - UZH RPG code fusing a learned inertial displacement model with an EKF for drone racing state estimation.
- [RadarHD](../../catalog/repos/akarsh-prabhakara__radarhd.md) - fit: low - Learns to generate high-resolution, lidar-like point clouds from low-cost single-chip mmWave radar.
- [WayFAST](../../catalog/repos/matval__wayfast.md) - fit: low - Self-supervised traversability prediction for wheeled field robots that learns from RGB-D, with labels from kinodynamic traction estimates.
- [EqNIO](../../catalog/repos/royinajayanth__eqnio.md) - fit: low - Subequivariant neural inertial odometry (ICLR 2025) that canonicalises IMU data so networks generalise across orientations; applied on top of TLIO and RoNIN.
- [Deep learning celestial navigation](../../catalog/repos/gregtozzi__deep_learning_celnav.md) - fit: low - Exploratory project on automating celestial navigation with deep learning and edge inference on synthetic sky images.
- [ViNet_AirSim_drone - learned VIO in AirSim](../../catalog/repos/sasha-lobov__vinet_airsim_drone.md) - fit: low - PyTorch CNN+RNN network that predicts relative pose between frames from a monocular camera and 6-axis IMU, trained on data collected in Microsoft AirSim with ground-truth poses and a composite loss to limit drift.

## Documents, talks, courses, datasets (21)

- [A Multi-Robot Platform for Robotic Triage Combining Onboard Sensing and Foundation Models](../../catalog/resources/arxiv-multi-robot-triage-platform.md) - paper - Technical report from a DARPA Triage Challenge team describing a multi-robot system and fine-tuned open vision-language models for injury identification.
- [AI-IMU Dead-Reckoning](../../catalog/resources/brossard-ai-imu-dr.md) - paper - Car localisation from IMU alone by combining an invariant EKF with a neural network that adapts measurement noise covariances (pseudo-measurements), evaluated on KITTI.
- [Airborne Magnetic Anomaly Navigation with Neural-Network-Augmented Online Calibration](../../catalog/resources/hager-2026-magnav-nn-online-calibration.md) - paper - Published in the Journal of Guidance, Control, and Dynamics (2026).
- [AirIO: Learning Inertial Odometry with Enhanced IMU Feature Observability](../../catalog/resources/airio-paper.md) - paper - UAV-focused learned inertial odometry that changes how IMU data are represented to the network to make motion features more observable.
- [Are State-of-the-art Visual Place Recognition Techniques any Good for Aerial Robotics?](../../catalog/resources/zaffar-2019-vpr-aerial-robotics.md) - paper - Early benchmark of eight ground-robot VPR techniques on two aerial place-recognition datasets, comparing matching performance, processing power and memory, and laying out why aerial VPR differs (viewpoint change, payload
- [Champion-level drone racing using deep reinforcement learning](../../catalog/resources/swift-champion-drone-racing-nature.md) - paper - Swift, a quadrotor using only onboard camera and IMU with an RL-trained policy, beat human world-champion pilots in head-to-head races.
- [cuVSLAM: CUDA accelerated visual odometry and mapping](../../catalog/resources/cuvslam-2025.md) - paper - Describes NVIDIA's GPU-accelerated VO/SLAM supporting from one to many cameras with optional IMU, designed for real-time edge deployment.
- [DARPA Triage Challenge](../../catalog/resources/darpa-triage-challenge.md) - competition - DARPA challenge for autonomous systems that find and assess casualties in mass-casualty scenes, combining drones and ground robots navigating degraded, GNSS-unreliable environments.
- [DROID-SLAM: Deep Visual SLAM for Monocular, Stereo, and RGB-D Cameras](../../catalog/resources/droid-slam-teed-2021.md) - paper - Learned SLAM that iteratively refines poses and depth through a differentiable dense bundle adjustment layer.
- [ESA Kelvins Satellite Pose Estimation Competition 2021 (SPEED+)](../../catalog/resources/kelvins-pose-estimation-2021.md) - competition - Follow-up Kelvins challenge focused on bridging the domain gap: train on synthetic images, test on hardware-in-the-loop lightbox and sunlamp images.
- [Isaac ROS Visual SLAM documentation](../../catalog/resources/isaac-ros-visual-slam-docs.md) - doc - Docs and quickstarts for NVIDIA's GPU-accelerated stereo visual-inertial odometry and SLAM package for ROS 2 on Jetson, including tutorials with Isaac Sim and RealSense cameras.
- [NVIDIA Jetson AI Lab](../../catalog/resources/nvidia-jetson-ai-lab.md) - doc - Tutorial hub for running generative AI, VLMs and robotics models on Jetson devices, built around jetson-containers.
- [Recent Advances on Jamming and Spoofing Detection in GNSS](../../catalog/resources/rados-2024-jamming-spoofing-detection-review.md) - paper - Open-access Sensors review of GNSS jamming and spoofing detection methods, finding machine learning is now the dominant approach, and covering combined jamming-plus-spoofing scenarios.
- [RoNIN: Robust Neural Inertial Navigation in the Wild: Benchmark, Evaluations, and New Methods](../../catalog/resources/ronin-paper.md) - paper - Introduces a large smartphone IMU dataset with ground truth and benchmarks neural architectures for pedestrian velocity regression.
- [Terrain-Aided Navigation Without Raycasting: A Sliding Grid Approach for Point Cloud Processing](../../catalog/resources/sanlan-2025-sliding-grid-tan-point-cloud.md) - paper - Compares two DEM-based measurement models for point-cloud (lidar-style) terrain-aided INS: classic ray casting versus a 'sliding grid' that needs no ray casting.
- [TLIO: Tight Learned Inertial Odometry](../../catalog/resources/tlio-paper.md) - paper - Combines a network that predicts displacement and uncertainty from IMU data with an EKF, for pedestrian inertial odometry.
- [Wild Visual Navigation: Fast Traversability Learning via Pre-Trained Models and Online Self-Supervision](../../catalog/resources/wild-visual-navigation-paper.md) - paper - Describes learning visual traversability online from pre-trained features and robot experience, adapting within minutes in forests and grassland.
- [XFeat: Accelerated Features for Lightweight Image Matching](../../catalog/resources/xfeat-2024.md) - paper - Lightweight feature extraction and matching architecture aimed at real-time use on constrained hardware.
- [Беспилотники научили видеть дорогу без GPS и ГЛОНАСС: «умную» навигацию создали в МФТИ](../../catalog/resources/www1-mipt-fasetka-visual-nav-2026.md) - blog - English: 'Drones taught to see the road without GPS and GLONASS: MIPT built smart navigation'.
- [Троє 20-річних хлопців за 24 години створили дрон, якому не потрібен GPS](../../catalog/resources/devua-24h-gps-free-drone-2024.md) - blog - English: 'Three 20-year-olds built a drone that needs no GPS in 24 hours'.
- [Уловки, подсмотренные у медоносных пчёл, помогают дронам возвращаться домой без GPS](../../catalog/resources/habr-bee-nav-translation-2026.md) - blog - English: 'Tricks borrowed from honeybees help drones return home without GPS'.

