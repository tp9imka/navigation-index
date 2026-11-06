# Indoor and pedestrian navigation

`concept:indoor-pedestrian`

PDR, foot-mounted INS, dismounted soldier navigation, indoor positioning.

## Repositories (16)

- [Crazyflie firmware](../repos/bitcraze__crazyflie-firmware.md) - fit: high - Firmware for the Crazyflie nano quad, Bolt and the Roadrunner positioning tag, with EKF and complementary estimators supporting UWB Loco positioning, Lighthouse, Flow deck and mocap.
- [PyShoe](../repos/utiasstars__pyshoe.md) - fit: high - Open Python foot-mounted INS from UTIAS with a public inertial dataset and several zero-velocity detectors, including learned ones.
- [IEZ (INS-EKF-ZUPT)](../repos/pajaraca__iez.md) - fit: high - Python implementation (one 9-state script, plus ESP32 logger firmware) of a foot-mounted INS with EKF and zero-velocity updates for pedestrian dead reckoning, with sample datasets from two foot-mounted MPU6050 IMUs.
- [RoNIN](../repos/sachini__ronin.md) - fit: medium - Robust Neural Inertial Navigation: smartphone IMU dataset and baseline networks (ResNet, LSTM, TCN) regressing pedestrian velocity from IMU.
- [TLIO](../repos/cathias__tlio.md) - fit: medium - Tight Learned Inertial Odometry: a network regresses displacement and uncertainty from IMU windows, fused in a stochastic-cloning EKF.
- [Indoor Location Competition 2.0](../repos/location-competition__indoor-location-competition-20.md) - fit: medium - Data and baseline code from Microsoft Research's Indoor Location Competition 2.0: smartphone IMU, Wi-Fi, BLE and magnetic traces across many buildings with floor maps.
- [Loco Positioning node firmware](../repos/bitcraze__lps-node-firmware.md) - fit: medium - Firmware for Bitcraze Loco Positioning UWB anchors and tags (DW1000), supporting two-way ranging and TDoA modes.
- [PDR Android app](../repos/aureliencousin__pdr.md) - fit: medium - Android app implementing pedestrian dead reckoning with step detection and orientation from phone sensors.
- [MILUV devkit](../repos/decargroup__miluv.md) - fit: medium - Python devkit for MILUV, a multi-UAV indoor localization dataset with UWB ranging (including inter-robot), vision and IMU data.
- [ZUPT-aided INS (OpenShoe MATLAB)](../repos/hcarlsso__zupt-aided-ins.md) - fit: medium - MATLAB implementation of the OpenShoe zero-velocity-aided foot-mounted INS with several zero-velocity detectors (SHOE, acceleration variance and magnitude, angular rate energy).
- [Rao-Blackwellized SLAM smoothing (magnetic)](../repos/manonkok__rao-blackwellized-slam-smoothing.md) - fit: medium - MATLAB code for Rao-Blackwellized particle smoothing for SLAM, including magnetic field mapping and map-matching localization with a magnetometer.
- [MPU6050 ZUPT](../repos/mtahakoroglu__mpu6050_zupt.md) - fit: medium - Arduino library forked from MPU6050_tockn that reads and calibrates an MPU6050 and streams angles and time series to Python plotting scripts.
- [RIDI](../repos/higerra__ridi_imu.md) - fit: low - Code for RIDI, which regresses velocity from smartphone IMU data with learned models to reduce inertial drift for pedestrian navigation.
- [OpenPDR](../repos/wuzhiguocarter__openpdr.md) - fit: low - Planned device-independent pedestrian dead reckoning platform that never got past its outline: the repo holds MATLAB ellipsoid-fit accelerometer and magnetometer calibration scripts with sample logs, an Allan-variance no
- [EqNIO](../repos/royinajayanth__eqnio.md) - fit: low - Subequivariant neural inertial odometry (ICLR 2025) that canonicalises IMU data so networks generalise across orientations; applied on top of TLIO and RoNIN.
- [Audio localization dataset (Crazyflie)](../repos/lcav__audio-localization-dataset.md) - fit: low - Datasets for acoustic echolocation and sound-source localization recorded on a Crazyflie drone and an e-puck robot.

## Documents, talks, courses, datasets (3)

- [OpenShoe: open source embedded foot-mounted INS](../resources/openshoe-foot-mounted-ins-2012.md) - doc - Project site (offline since 2026; archived copy) for OpenShoe, an open hardware and software ZUPT-aided foot-mounted INS module, described in the PLANS 2012 paper 'Foot-mounted INS for Everybody' and follow-up IPIN 2014 
- [RoNIN: Robust Neural Inertial Navigation in the Wild: Benchmark, Evaluations, and New Methods](../resources/ronin-paper.md) - paper - Introduces a large smartphone IMU dataset with ground truth and benchmarks neural architectures for pedestrian velocity regression.
- [TLIO: Tight Learned Inertial Odometry](../resources/tlio-paper.md) - paper - Combines a network that predicts displacement and uncertainty from IMU data with an EKF, for pedestrian inertial odometry.

