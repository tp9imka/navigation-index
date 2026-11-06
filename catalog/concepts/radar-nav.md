# Radar navigation and odometry

`concept:radar-nav`

Radar odometry, radar SLAM, radar altimeters, Doppler velocity.

## Repositories (22)

- [4DRadarSLAM](../repos/zhuge2333__4dradarslam.md) - fit: medium - 4D radar SLAM with scan-to-scan registration, loop closure and pose-graph optimization, released with an NTU 4D radar dataset.
- [RIO](../repos/christopherdoer__rio.md) - fit: medium - EKF-based radar-inertial odometry using 4D mmWave radar ego-velocity measurements.
- [STEAM-ICP](../repos/utiasasrl__steam_icp.md) - fit: medium - Continuous-time lidar, radar, lidar-inertial and radar-inertial odometry built on the STEAM library.
- [ORORA](../repos/url-kaist__outlier-robust-radar-odometry.md) - fit: medium - Outlier-robust radar odometry using graduated non-convexity-style estimation on radar feature correspondences (ICRA 2023).
- [HKUST 4D Radar-Inertial Odometry](../repos/hkust-aerial-robotics__rio.md) - fit: medium - Optimization-based, point-uncertainty-aware radar-inertial odometry for 4D radar.
- [ETH Radar-Inertial Odometry](../repos/ethz-asl__rio.md) - fit: medium - Graph-based, sparse radar-inertial odometry estimation from ETH ASL, using GTSAM.
- [MIMOSA](../repos/ntnu-arl__mimosa.md) - fit: medium - Tightly coupled sliding-window factor-graph fusion of IMU with LiDAR (geometric and photometric), radar radial-speed factors and external odometry such as VIO.
- [pyboreas](../repos/utiasasrl__pyboreas.md) - fit: medium - Devkit for the Boreas multi-season driving dataset with radar, lidar, camera and GNSS/INS ground truth.
- [REVE](../repos/christopherdoer__reve.md) - fit: medium - Radar Ego Velocity Estimator: robust 3D ego-velocity from 4D mmWave radar Doppler point clouds, the front-end used by Doer's radar-inertial odometry.
- [RRxIO](../repos/christopherdoer__rrxio.md) - fit: medium - Radar visual/thermal inertial odometry fusing 4D mmWave radar with a visual or thermal camera and IMU for degraded visual conditions.
- [Go-RIO](../repos/wooseongy__go-rio.md) - fit: medium - Ground-optimized 4D radar-inertial odometry integrating continuous velocity via Gaussian processes (ICRA 2025 best paper finalist).
- [OpenCPN radar_pi](../repos/opencpn-radar-pi__radar_pi.md) - fit: medium - OpenCPN plugin that connects to Navico and some Garmin and Raymarine marine radars and overlays radar imagery and ARPA-style targets on the chart.
- [TBV Radar SLAM](../repos/dan11003__tbv_slam_public.md) - fit: medium - Radar SLAM with verified loop closures built on CFEAR radar odometry.
- [CFEAR Radarodometry](../repos/dan11003__cfear_radarodometry.md) - fit: medium - Learning-free spinning-radar odometry that filters returns to sparse oriented surface points and registers against keyframes.
- [ReFeree](../repos/sparolab__referee.md) - fit: medium - Lightweight radar global descriptor for radar place recognition (RA-L 2024).
- [K-Radar](../repos/kaist-avelab__k-radar.md) - fit: low - 4D radar dataset and benchmark for object detection in diverse weather, with raw 4D tensors, lidar, cameras and GNSS.
- [RadarHD](../repos/akarsh-prabhakara__radarhd.md) - fit: low - Learns to generate high-resolution, lidar-like point clouds from low-cost single-chip mmWave radar.
- [Yeti radar odometry](../repos/keenan-burnett__yeti_radar_odometry.md) - fit: low - Radar odometry for Navtech spinning radar that compensates motion distortion and Doppler effects.
- [STEAM](../repos/utiasasrl__steam.md) - fit: low - Simultaneous Trajectory Estimation and Mapping engine from UTIAS: a C++ nonlinear least-squares library with continuous-time Gaussian-process trajectory priors on Lie groups.
- [RINO](../repos/yangsc4063__rino.md) - fit: low - Non-iterative, adaptively loosely coupled radar-inertial odometry for spinning (scanning) radar, built on the ORORA radar odometry baseline; the radar pose uncertainty from its voting step feeds a Kalman filter (T-ASE 20
- [Gaussian-RIO](../repos/robotics-upo__gaussian-rio.md) - fit: low - 4D radar-inertial odometry using Gaussian modeling of radar points and multi-hypothesis scan matching.
- [Open-RadVLAD](../repos/mttgdd__open-radvlad.md) - fit: low - Fast radar place recognition using VLAD-style aggregation over radar polar scans.

## Documents, talks, courses, datasets (9)

- [4D Millimeter-Wave Radar in Autonomous Driving: A Survey](../resources/han-4d-mmwave-radar-survey-2023.md) - paper - Survey of 4D imaging radar: signal processing, datasets, calibration, perception and SLAM/odometry uses.
- [CFEAR Radarodometry - Conservative Filtering for Efficient and Accurate Radar Odometry](../resources/cfear-radarodometry-adolfsson-2021.md) - paper - Learning-free spinning-radar odometry that keeps the strongest returns per azimuth, builds oriented surface points and registers against a keyframe history (IROS 2021).
- [DIAT-uSAT: micro-Doppler Signature Dataset of Small Unmanned Aerial Vehicle (SUAV)](../resources/diat-musat-micro-doppler-dataset.md) - dataset - 4,849 micro-Doppler signature images from an X-band (10 GHz) continuous-wave radar of small UAV-like targets: RC plane, two rotor types, quadcopter, bionic bird and mini-helicopter plus bionic bird.
- [From Sea to Space: Advancing Perception in Harsh Domains (ICRA 2026 workshop)](../resources/icra-2026-sea-to-space-perception-workshop.md) - talk - ICRA 2026 (Vienna) workshop on perception for underwater, space and terrestrial field robots, including localization and mapping in degraded sensing, GPS-denied global localization, novel sensors (sonar, radar, thermal, 
- [Honeywell HGuide o480 single-card INS and HGuide i700 IMU](../resources/honeywell-hguide-o480.md) - product - HGuide o480 (May 2025) is a single-card INS for small UAVs and ground robots that accepts velocity aiding (e.g.
- [MulRan: Multimodal Range Dataset for Urban Place Recognition](../resources/snu-mulran-dataset.md) - dataset - Urban sequences with radar and lidar for range-sensor place recognition and odometry.
- [Oxford Radar RobotCar Dataset](../resources/oxford-radar-robotcar-dataset.md) - dataset - RobotCar route re-driven with a scanning FMCW radar plus lidars and cameras, for radar odometry and localization.
- [Pohang Canal Dataset: A Multimodal Maritime Dataset for Autonomous Navigation in Restricted Waters](../resources/pohang-canal-dataset-2023.md) - dataset - Multimodal maritime dataset from a 7.5 km route through a narrow canal, port areas and near-coast waters, with LiDARs, marine radar, stereo, infrared and omnidirectional cameras, AHRS and RTK GPS.
- [SLAM Handbook: From Localization and Mapping to Spatial Intelligence](../resources/slam-handbook.md) - book - Community-written handbook released in three parts during 2024-2025 and published by Cambridge University Press; the free PDF is mirrored on the editors' project page.

