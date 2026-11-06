# Indoor and pedestrian navigation

`concept:indoor-pedestrian`

PDR, foot-mounted INS, dismounted soldier navigation, indoor positioning.

## Repositories (8)

- [Crazyflie firmware](../repos/bitcraze__crazyflie-firmware.md) - fit: high - Firmware for the Crazyflie nano quad, Bolt and the Roadrunner positioning tag, with EKF and complementary estimators supporting UWB Loco positioning, Lighthouse, Flow deck and mocap.
- [PyShoe](../repos/utiasstars__pyshoe.md) - fit: high - Open Python foot-mounted INS from UTIAS with a public inertial dataset and several zero-velocity detectors, including learned ones.
- [RoNIN](../repos/sachini__ronin.md) - fit: medium - Robust Neural Inertial Navigation: smartphone IMU dataset and baseline networks (ResNet, LSTM, TCN) regressing pedestrian velocity from IMU.
- [TLIO](../repos/cathias__tlio.md) - fit: medium - Tight Learned Inertial Odometry: a network regresses displacement and uncertainty from IMU windows, fused in a stochastic-cloning EKF.
- [Loco Positioning node firmware](../repos/bitcraze__lps-node-firmware.md) - fit: medium - Firmware for Bitcraze Loco Positioning UWB anchors and tags (DW1000), supporting two-way ranging and TDoA modes.
- [ZUPT-aided INS (OpenShoe MATLAB)](../repos/hcarlsso__zupt-aided-ins.md) - fit: medium - MATLAB implementation of the OpenShoe zero-velocity-aided foot-mounted INS with several zero-velocity detectors (SHOE, acceleration variance and magnitude, angular rate energy).
- [Rao-Blackwellized SLAM smoothing (magnetic)](../repos/manonkok__rao-blackwellized-slam-smoothing.md) - fit: medium - MATLAB code for Rao-Blackwellized particle smoothing for SLAM, including magnetic field mapping and map-matching localization with a magnetometer.
- [EqNIO](../repos/royinajayanth__eqnio.md) - fit: low - Subequivariant neural inertial odometry (ICLR 2025) that canonicalises IMU data so networks generalise across orientations; applied on top of TLIO and RoNIN.

## Documents, talks, courses, datasets (2)

- [RoNIN: Robust Neural Inertial Navigation in the Wild: Benchmark, Evaluations, and New Methods](../resources/ronin-paper.md) - paper - Introduces a large smartphone IMU dataset with ground truth and benchmarks neural architectures for pedestrian velocity regression.
- [TLIO: Tight Learned Inertial Odometry](../resources/tlio-paper.md) - paper - Combines a network that predicts displacement and uncertainty from IMU data with an EKF, for pedestrian inertial odometry.

