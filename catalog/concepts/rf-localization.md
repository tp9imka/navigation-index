# RF localization and direction finding

`concept:rf-localization`

UWB, TDOA/AOA, direction finding, emitter geolocation, beacons.

## Repositories (18)

- [Crazyflie firmware](../repos/bitcraze__crazyflie-firmware.md) - fit: high - Firmware for the Crazyflie nano quad, Bolt and the Roadrunner positioning tag, with EKF and complementary estimators supporting UWB Loco positioning, Lighthouse, Flow deck and mocap.
- [KrakenSDR DoA DSP](../repos/krakenrf__krakensdr_doa.md) - fit: high - Direction-of-arrival processing and web UI for the five-channel coherent KrakenSDR, producing bearings to RF emitters.
- [UTIL UWB TDoA dataset tools](../repos/williamwenda__uwb_tdoa_dataset.md) - fit: high - Dataset and scripts for UWB time-difference-of-arrival measurements from Bitcraze's Loco Positioning System, collected by University of Toronto.
- [DroneSecurity (DJI DroneID receiver)](../repos/rub-syssec__dronesecurity.md) - fit: medium - Ruhr University Bochum receiver for DJI DroneID that works live with an SDR or offline on captures, released with their NDSS 2023 security analysis.
- [NTU VIRAL dataset](../repos/ntu-aris__ntu_viral_dataset.md) - fit: medium - Site repo for NTU VIRAL, an aerial dataset with lidars, cameras, IMU and UWB ranging from a drone.
- [Indoor Location Competition 2.0](../repos/location-competition__indoor-location-competition-20.md) - fit: medium - Data and baseline code from Microsoft Research's Indoor Location Competition 2.0: smartphone IMU, Wi-Fi, BLE and magnetic traces across many buildings with floor maps.
- [Heimdall DAQ firmware](../repos/krakenrf__heimdall_daq_fw.md) - fit: medium - Coherent multichannel SDR acquisition chain (sync, calibration, decimation) underneath KrakenSDR DoA and passive radar apps.
- [Loco Positioning node firmware](../repos/bitcraze__lps-node-firmware.md) - fit: medium - Firmware for Bitcraze Loco Positioning UWB anchors and tags (DW1000), supporting two-way ranging and TDoA modes.
- [MCD: Multi-Campus Dataset](../repos/mcdviral__mcdviral.github.io.md) - fit: medium - Site repo for MCD, a multi-campus dataset across Asia and Europe with spinning and non-repetitive lidar, stereo cameras, IMUs, UWB ranging, survey-grade prior maps and continuous-time ground truth.
- [samples2djidroneid](../repos/anarkiwi__samples2djidroneid.md) - fit: medium - Decodes DJI DroneID (OcuSync 2.0) frames from SDR I/Q recordings, building on proto17's reverse engineering and Kismet.
- [MILUV devkit](../repos/decargroup__miluv.md) - fit: medium - Python devkit for MILUV, a multi-UAV indoor localization dataset with UWB ranging (including inter-robot), vision and IMU data.
- [A Tutorial on 5G Positioning (code)](../repos/ita97__a-tutorial-on-5g-positioning.md) - fit: medium - MATLAB simulation code accompanying an IEEE tutorial on 5G positioning (timing, angle and multi-cell methods).
- [Swarm relative localization (ETH PBL)](../repos/eth-pbl__swarm-relative-localization.md) - fit: medium - Infrastructure-less relative localization for decentralized swarm formation of nano-drones using UWB ranging (IROS 2023).
- [UWB Software Library (USL)](../repos/vladniculescu__uwb-software-library.md) - fit: medium - FreeRTOS UWB library for DW1000 on Crazyflie providing double-sided two-way ranging and UWB data messaging between drones.
- [CoLRIO](../repos/pengyu-team__co-lrio.md) - fit: medium - ROS 2 centralized lidar-ranging-inertial state estimation for robotic swarms that offloads optimization to a server and uses UWB inter-robot ranges (ICRA 2024).
- [uwb-localization (MAV swarm)](../repos/lijx10__uwb-localization.md) - fit: low - ROS library fusing UWB ranging with IMU for accurate 3D localization of MAV swarms, used in a 2017 drone light show.
- [Omni-swarm](../repos/hkust-aerial-robotics__omni-swarm.md) - fit: low - Decentralized omnidirectional visual-inertial-UWB state estimation for aerial swarms from HKUST, combining VIO, UWB ranges and map-based place recognition.
- [GEARdrones](../repos/excitablecell__geardrones.md) - fit: low - Lightweight STM32 drone control and multi-agent localization system combining a flight controller, UWB relative localization and a monitor tool.

## Documents, talks, courses, datasets (10)

- [Cooperative Localization for GNSS-Denied Subterranean Navigation: A UAV-UGV Team Approach](../resources/ion-webinar-gross.md) - talk - West Virginia University work on UAV and UGV teams sharing ranging and odometry to localize jointly in GNSS-denied underground environments.
- [Drone Security and the Mysterious Case of DJI's DroneID](../resources/ndss-2023-dji-droneid.md) - paper - Security analysis of DJI drones that reverse-engineers the DroneID broadcast and shows it is unencrypted, with an open receiver released.
- [First results from three years of GNSS interference monitoring from low Earth orbit](../resources/ion-webinar-humphreys.md) - talk - UT Radionavigation Lab results from detecting and geolocating terrestrial GNSS jammers using receivers on LEO satellites, revealing persistent interference hotspots in conflict regions.
- [GPS-denied RTH for MAVLink systems using LoRa radio ranging](../resources/hyams-gps-denied-rth-lora-ranging.md) - blog - Blog (shared on ArduPilot Discourse) on returning a plane home without GPS using range measurements from a LoRa radio to a ground beacon; discussion covers multilateration and EKF3 range fusion.
- [Loco Positioning System documentation](../resources/bitcraze-loco-positioning.md) - doc - Bitcraze documentation for its UWB positioning system covering anchor placement, two-way ranging versus TDoA modes and configuration with Crazyflies.
- [LTE Receiver Design and Multipath Analysis for Navigation in Urban Environments](../resources/ion-webinar-shamaei-kassas.md) - talk - Design of a software receiver that extracts navigation observables from cellular LTE signals and analysis of multipath effects in urban settings.
- [Non-GPS Navigation](../resources/ardupilot-non-gps-navigation-docs.md) - doc - Landing page in the ArduPilot wiki listing every supported way to navigate without GNSS: optical flow, beacons, wheel encoders, visual odometry/VIO cameras, motion capture and MAVLink external position.
- [Onboard Ranging-based Relative Localization and Stability for Lightweight Aerial Swarms](../resources/li-onboard-relative-localization-swarms.md) - paper - Presents onboard UWB ranging with an EKF for relative localization among small quadrotors, with a stability analysis of formation control built on those estimates.
- [Researchers home in on origins of Russia's Baltic GPS jamming](../resources/defensenews-baltic-jamming-origins-2025.md) - blog - Report on Polish research tracing Baltic GNSS jamming to emitters in the Kaliningrad region, with context on the effects on aviation and shipping.
- [UTIL: UWB TDoA dataset](../resources/util-uwb-dataset.md) - dataset - Project page for a UWB TDoA dataset collected with Loco Positioning hardware, with ground truth for evaluating indoor UWB localization.

