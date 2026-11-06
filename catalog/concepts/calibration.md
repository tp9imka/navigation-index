# Sensor calibration

`concept:calibration`

Camera-IMU, LiDAR-IMU extrinsics, intrinsics, time offset, Allan variance.

**Parent:** [Sensor fusion and state estimation](../concepts/sensor-fusion.md)

## Samples (1)

- [MagNav.jl quickstart: Tolles-Lawson and EKF on the SGL 2020 flight](../samples/magnav-quickstart.md) - A Julia walkthrough with MagNav.jl that downloads the public SGL 2020 challenge flight and Ottawa anomaly maps, compensates the scalar magnetometer with Tolles-Lawson on a calibration box, and runs the MagNav EKF against

## Repositories (22)

- [OpenVINS](../repos/rpng__open_vins.md) - fit: high - MSCKF-based visual-inertial navigation platform with online calibration, a simulator, and extensive documentation for research use.
- [MINS](../repos/rpng__mins.md) - fit: high - Multi-sensor aided inertial navigation that fuses IMU with camera, LiDAR, GNSS and wheel odometry, including online spatial/temporal calibration and a multi-sensor simulator.
- [allan_variance_ros](../repos/ori-drs__allan_variance_ros.md) - fit: high - ROS tool (Oxford DRS) that computes Allan deviation plots from an IMU bag and outputs noise parameters in a Kalibr-compatible format.
- [allantools](../repos/aewallin__allantools.md) - fit: high - Python library for time and frequency stability statistics: Allan, modified Allan, overlapping, Hadamard and time deviation, plus confidence intervals and power-law noise generators.
- [allan-variance (Python)](../repos/nmayorov__allan-variance.md) - fit: high - Small Python package computing Allan variance and fitting standard noise parameters.
- [Kalibr](../repos/ethz-asl__kalibr.md) - fit: medium - ETH ASL calibration toolbox for multi-camera and camera-IMU systems (extrinsics and time offset), plus IMU intrinsics and rolling-shutter calibration.
- [imu_utils](../repos/gaowenliang__imu_utils.md) - fit: medium - ROS package for analysing IMU performance with Allan variance to estimate noise and bias instability.
- [LiDAR_IMU_Init](../repos/hku-mars__lidar_imu_init.md) - fit: medium - Real-time LiDAR-inertial initialization estimating extrinsics, time offset, gravity and IMU bias online (IROS 2022).
- [Basalt](../repos/vladyslavusenko__basalt.md) - fit: medium - GitHub mirror of Basalt, a visual-inertial odometry and mapping system built around non-linear factor recovery, with calibration tools; primary development is on GitLab.
- [iKalibr](../repos/unsigned-long__ikalibr.md) - fit: medium - Continuous-time, targetless multi-sensor calibration framework (IMU, cameras, LiDAR, radar, RGB-D, event cameras) estimating extrinsics and time offsets (IEEE T-RO 2025).
- [NaveGo](../repos/rodralez__navego.md) - fit: medium - Open MATLAB/GNU Octave toolbox for simulating and processing integrated INS/GNSS navigation, including IMU error modelling and Allan variance analysis.
- [imu_tk](../repos/kyle-ak__imu_tk.md) - fit: medium - Tool for calibrating IMU intrinsics (misalignment, scale factors and biases of accelerometer and gyro) from a sequence of static poses, without a turntable.
- [rpg_dvs_ros](../repos/uzh-rpg__rpg_dvs_ros.md) - fit: medium - ROS drivers and tools for DVS/DAVIS event cameras, including calibration and rendering.
- [NASA COTS Star Tracker](../repos/nasa__cots-star-tracker.md) - fit: medium - NASA software for building a star tracker from commercial off-the-shelf cameras, including calibration and attitude solution.
- [Heimdall DAQ firmware](../repos/krakenrf__heimdall_daq_fw.md) - fit: medium - Coherent multichannel SDR acquisition chain (sync, calibration, decimation) underneath KrakenSDR DoA and passive radar apps.
- [cuckoo_time_translator](../repos/ethz-asl__cuckoo_time_translator.md) - fit: medium - ROS algorithms that translate a sensor's own hardware timestamps into host system time from one-way timing, estimating skew and offset.
- [MagNav deep-learning compensation](../repos/naatyu__magnav.md) - fit: medium - Deep-learning approach to aircraft magnetic disturbance compensation built around the MagNav challenge data.
- [TAPR TICC](../repos/tapr__ticc.md) - fit: medium - Firmware and design files for TAPR's Arduino-based sub-nanosecond time interval counter, used to compare 1PPS outputs.
- [LI-Calib](../repos/april-zju__lidar_imu_calib.md) - fit: low - Targetless LiDAR-IMU calibration based on continuous-time batch estimation (IROS 2020).
- [kalibr_allan (archived)](../repos/rpng__kalibr_allan.md) - fit: low - MATLAB scripts producing IMU Allan standard deviation charts and Kalibr-ready noise values.
- [lidar_imu_calib](../repos/chennuo0125-hit__lidar_imu_calib.md) - fit: low - Automatic calibration of the extrinsic rotation between a 3D LiDAR and an IMU.
- [AV-Matlab-SW](../repos/jaffarrell__av-matlab-sw.md) - fit: low - MATLAB software for Allan variance calculations accompanying a published article on IMU noise characterisation (Farrell et al.).

## Documents, talks, courses, datasets (8)

- [Handbook of Frequency Stability Analysis (NIST SP 1065)](../resources/nist-sp1065-frequency-stability-handbook.md) - book - NIST tutorial and reference on characterizing clocks and oscillators: Allan, modified Allan, Hadamard and time deviation, power-law noise types, drift removal and confidence intervals.
- [Kalibr wiki: camera-IMU calibration tutorials](../resources/kalibr-wiki.md) - doc - Wiki for Kalibr covering multi-camera, camera-IMU and rolling-shutter calibration, target generation and data collection practice.
- [Kalibr wiki: IMU Noise Model](../resources/kalibr-imu-noise-model-wiki.md) - doc - Practical explanation of white noise and random-walk bias parameters for IMUs, how to convert datasheet values to continuous/discrete form and how to inflate them for real use.
- [LeapSecond.com (Tom Van Baak time and frequency pages)](../resources/leapsecond-tvb.md) - doc - Long-running personal site with measurements of oscillators, GPSDOs and atomic clocks, Allan deviation tutorials and experiments.
- [OpenVINS documentation](../resources/openvins-docs.md) - doc - Documentation for the OpenVINS MSCKF-based visual-inertial estimator, including derivations of the propagation and update steps, calibration, evaluation tooling and ROS usage.
- [Photogrammetry I & II](../resources/stachniss-photogrammetry-i-ii.md) - lecture-series - Recorded two-semester photogrammetry course (2015/16 playlist): camera models, direct linear transform, projective geometry, epipolar geometry, bundle adjustment, and image-based 3D reconstruction.
- [Vision Algorithms for Mobile Robotics (UZH/ETH)](../resources/scaramuzza-vision-algorithms-mobile-robotics.md) - course - Graduate course building a monocular visual odometry pipeline step by step: image formation, calibration, feature detection, two-view geometry, P3P+RANSAC, bundle adjustment, KLT tracking, place recognition, visual-inert
- [Навигация по Optical Flow · Clover](../resources/coex-clover-docs-optical-flow-ru.md) - doc - English: 'Optical Flow navigation - Clover docs'.

