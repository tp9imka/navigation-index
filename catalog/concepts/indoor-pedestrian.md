# Indoor and pedestrian navigation

`concept:indoor-pedestrian`

PDR, foot-mounted INS, dismounted soldier navigation, indoor positioning.

## Samples (1)

- [Dismounted foot-mounted INS: stdlib 15-state ZUPT EKF on the real pyshoe hallway data, cross-checked against pyshoe, with corridor heading, UWB and TAK output](../../catalog/samples/dismounted-foot-ins.md) - A stdlib-only error-state EKF (position, velocity, attitude, accel and gyro bias) with SHOE, ARED, AMVD and MBGTD stance detectors, run on all 36 real foot-mounted IMU trials of the UTIAS pyshoe hallway dataset (214.6 m 

## Guides (1)

- [8. Maritime, underwater, ground and dismounted](../../docs/primer/08-maritime-underwater-ground.md) - After this chapter you know how navigation changes off the drone: what ships broadcast and how spoofing shows up in it, how vehicles navigate underwater where no radio reaches, how ground robots and pedestrians dead-reck

## Repositories (16)

- [Crazyflie firmware](../../catalog/repos/bitcraze__crazyflie-firmware.md) - fit: high - Firmware for the Crazyflie nano quad, Bolt and the Roadrunner positioning tag, with EKF and complementary estimators supporting UWB Loco positioning, Lighthouse, Flow deck and mocap.
- [PyShoe](../../catalog/repos/utiasstars__pyshoe.md) - fit: high - Open Python foot-mounted INS from UTIAS with a public inertial dataset and several zero-velocity detectors, including learned ones.
- [IEZ (INS-EKF-ZUPT)](../../catalog/repos/pajaraca__iez.md) - fit: high - Python implementation (one 9-state script, plus ESP32 logger firmware) of a foot-mounted INS with EKF and zero-velocity updates for pedestrian dead reckoning, with sample datasets from two foot-mounted MPU6050 IMUs.
- [RoNIN](../../catalog/repos/sachini__ronin.md) - fit: medium - Robust Neural Inertial Navigation: smartphone IMU dataset and baseline networks (ResNet, LSTM, TCN) regressing pedestrian velocity from IMU.
- [TLIO](../../catalog/repos/cathias__tlio.md) - fit: medium - Tight Learned Inertial Odometry: a network regresses displacement and uncertainty from IMU windows, fused in a stochastic-cloning EKF.
- [Indoor Location Competition 2.0](../../catalog/repos/location-competition__indoor-location-competition-20.md) - fit: medium - Data and baseline code from Microsoft Research's Indoor Location Competition 2.0: smartphone IMU, Wi-Fi, BLE and magnetic traces across many buildings with floor maps.
- [Loco Positioning node firmware](../../catalog/repos/bitcraze__lps-node-firmware.md) - fit: medium - Firmware for Bitcraze Loco Positioning UWB anchors and tags (DW1000), supporting two-way ranging and TDoA modes.
- [PDR Android app](../../catalog/repos/aureliencousin__pdr.md) - fit: medium - Android app implementing pedestrian dead reckoning with step detection and orientation from phone sensors.
- [MILUV devkit](../../catalog/repos/decargroup__miluv.md) - fit: medium - Python devkit for MILUV, a multi-UAV indoor localization dataset with UWB ranging (including inter-robot), vision and IMU data.
- [ZUPT-aided INS (OpenShoe MATLAB)](../../catalog/repos/hcarlsso__zupt-aided-ins.md) - fit: medium - MATLAB implementation of the OpenShoe zero-velocity-aided foot-mounted INS with several zero-velocity detectors (SHOE, acceleration variance and magnitude, angular rate energy).
- [Rao-Blackwellized SLAM smoothing (magnetic)](../../catalog/repos/manonkok__rao-blackwellized-slam-smoothing.md) - fit: medium - MATLAB code for Rao-Blackwellized particle smoothing for SLAM, including magnetic field mapping and map-matching localization with a magnetometer.
- [MPU6050 ZUPT](../../catalog/repos/mtahakoroglu__mpu6050_zupt.md) - fit: medium - Arduino library forked from MPU6050_tockn that reads and calibrates an MPU6050 and streams angles and time series to Python plotting scripts.
- [RIDI](../../catalog/repos/higerra__ridi_imu.md) - fit: low - Code for RIDI, which regresses velocity from smartphone IMU data with learned models to reduce inertial drift for pedestrian navigation.
- [OpenPDR](../../catalog/repos/wuzhiguocarter__openpdr.md) - fit: low - Planned device-independent pedestrian dead reckoning platform that never got past its outline: the repo holds MATLAB ellipsoid-fit accelerometer and magnetometer calibration scripts with sample logs, an Allan-variance no
- [EqNIO](../../catalog/repos/royinajayanth__eqnio.md) - fit: low - Subequivariant neural inertial odometry (ICLR 2025) that canonicalises IMU data so networks generalise across orientations; applied on top of TLIO and RoNIN.
- [Audio localization dataset (Crazyflie)](../../catalog/repos/lcav__audio-localization-dataset.md) - fit: low - Datasets for acoustic echolocation and sound-source localization recorded on a Crazyflie drone and an e-puck robot.

## Documents, talks, courses, datasets (6)

- [OpenShoe: open source embedded foot-mounted INS](../../catalog/resources/openshoe-foot-mounted-ins-2012.md) - doc - Project site (offline since 2026; archived copy) for OpenShoe, an open hardware and software ZUPT-aided foot-mounted INS module, described in the PLANS 2012 paper 'Foot-mounted INS for Everybody' and follow-up IPIN 2014 
- [RoNIN: Robust Neural Inertial Navigation in the Wild: Benchmark, Evaluations, and New Methods](../../catalog/resources/ronin-paper.md) - paper - Introduces a large smartphone IMU dataset with ground truth and benchmarks neural architectures for pedestrian velocity regression.
- [TLIO: Tight Learned Inertial Odometry](../../catalog/resources/tlio-paper.md) - paper - Combines a network that predicts displacement and uncertainty from IMU data with an EKF, for pedestrian inertial odometry.
- [University of Toronto Foot-Mounted Inertial Navigation Dataset](../../catalog/resources/uoft-foot-mounted-ins-dataset.md) - dataset - Foot-mounted IMU recordings from five subjects over more than 7.6 km with ground-truth positioning, built to evaluate zero-velocity-aided pedestrian INS.
- [В поисках автономного полета](../../catalog/resources/vcru-zimkov-autonomous-flight-2025.md) - blog - English: 'In search of autonomous flight' (15 Dec 2025).
- [Дроны: Автономные беспилотные воздушные системы](../../catalog/resources/lektorium-geoscan-autonomous-drones-course.md) - course - English: 'Drones: autonomous unmanned aerial systems'.

