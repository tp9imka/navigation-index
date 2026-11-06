# Simulation and HIL/SITL

`concept:simulation`

Physics and sensor simulators, software/hardware-in-the-loop, GNSS signal simulators.

## Samples (4)

- [ArduPilot EKF3 source-set switch under GPS denial](../samples/ardupilot-ekf3-source-switch.md) - Flies ArduCopter SITL on GPS, switches EKF3 to an external-nav source set (SITL vicon) with MAV_CMD_SET_EKF_SOURCE_SET, cuts simulated GPS, flies a 15 m leg, then restores it.
- [GNSS/INS EKF through a GNSS outage and a spoofing walk-off](../samples/gnss-ins-ekf-outage.md) - A stdlib-only 2D loosely-coupled GNSS/INS EKF (8 states, hand-written matrix helpers) on a synthetic vehicle with biased, noisy 100 Hz IMU and 1 Hz GNSS.
- [Headless SITL in Docker: ArduCopter and PX4 SIH with one compose file](../samples/sitl-docker.md) - Dockerfiles and a compose file that run ArduCopter 4.6.3 SITL (with a simulated vicon for ExternalNav) and PX4 v1.17.0 SIH quadrotor without Gazebo or a GUI, plus a Python client image with pymavlink and mavsdk-grpc that
- [PX4 SITL GPS denial: inject, measure drift, recover](../samples/px4-sitl-gps-denial.md) - Flies a square mission in PX4 SITL (SIH quadrotor, headless; Gazebo also works per PX4 docs), denies GPS mid-mission, logs EKF2 health and estimated vs ground-truth position, then restores GPS and returns home.

## Repositories (74)

- [ArduPilot](../repos/ardupilot__ardupilot.md) - fit: high - GPL autopilot covering Copter, Plane (incl.
- [CARLA](../repos/carla-simulator__carla.md) - fit: high - Open-source autonomous-driving simulator on Unreal with camera, lidar, radar, GNSS and IMU sensors, traffic and weather control.
- [PX4 Autopilot](../repos/px4__px4-autopilot.md) - fit: high - Dronecode flight stack for multirotors, fixed-wing, VTOL, rovers and boats, built on NuttX with a uORB pub/sub middleware.
- [GPS-SDR-SIM](../repos/osqzss__gps-sdr-sim.md) - fit: high - Generates GPS L1 C/A baseband IQ sample files for a user-defined static or moving trajectory from a broadcast ephemeris file, for playback through an SDR.
- [OpenVINS](../repos/rpng__open_vins.md) - fit: high - MSCKF-based visual-inertial navigation platform with online calibration, a simulator, and extensive documentation for research use.
- [gym-pybullet-drones](../repos/learnsyslab__gym-pybullet-drones.md) - fit: high - Gymnasium environments on PyBullet for single and multi-agent quadcopter control and RL (formerly under utiasDSL).
- [Gazebo Sim (gz-sim)](../repos/gazebosim__gz-sim.md) - fit: high - Current-generation Gazebo robotics simulator with pluggable physics, rendering and a large sensor library (IMU, GPS/NavSat, lidar, cameras, magnetometer, altimeter).
- [gnss-ins-sim](../repos/aceinna__gnss-ins-sim.md) - fit: high - Python GNSS/INS simulator that generates trajectories, IMU/GNSS/magnetometer measurements with configurable error models, and runs navigation algorithms on them.
- [CMU Autonomous Exploration Development Environment](../repos/hongbiaoz__autonomous_exploration_development_environment.md) - fit: high - CMU ground-robot development environment with simulated worlds, terrain analysis, local planner and waypoint tools used for exploration research (TARE, FAR planner).
- [Virtual RobotX (VRX)](../repos/osrf__vrx.md) - fit: high - Gazebo-based simulation environment for the RobotX maritime autonomy competition, with a WAM-V USV model, waves, wind, sensors and scored tasks such as station keeping, wayfinding and perception.
- [COEX Clover](../repos/copterexpress__clover.md) - fit: high - ROS-based software stack and Raspberry Pi image for the Clover educational quadcopter (PX4 underneath).
- [ros_gz bridge](../repos/gazebosim__ros_gz.md) - fit: high - Bridge packages that relay topics, services and clock between Gazebo Sim transport and ROS 1/ROS 2.
- [v2e](../repos/sensorsini__v2e.md) - fit: high - Converts conventional video into realistic synthetic DVS event streams with sensor noise modeling.
- [Stonefish](../repos/patrykcieslak__stonefish.md) - fit: high - C++ simulation library for marine robotics with hydrodynamics, underwater rendering and sensors including DVL, USBL, multibeam and forward-looking sonar; has a ROS wrapper.
- [RotorPy](../repos/spencerfolk__rotorpy.md) - fit: high - Python multirotor simulator with aerodynamic effects (drag, wind) for education and research.
- [ardupilot_gazebo](../repos/ardupilot__ardupilot_gazebo.md) - fit: high - Gazebo Sim plugins and models that connect ArduPilot SITL to Gazebo physics for copters, rovers and boats.
- [Game4Loc / GTA-UAV](../repos/yux1angji__gta-uav.md) - fit: high - Benchmark and code for UAV geo-localization trained on synthetic game imagery with partial-match drone-satellite pairs (AAAI 2025).
- [tartanairpy](../repos/castacks__tartanairpy.md) - fit: high - Python package for downloading, customizing and iterating the TartanAir-V2 synthetic dataset.
- [pyins](../repos/nmayorov__pyins.md) - fit: high - Python package for modelling and analysing inertial navigation systems: strapdown integration, error models, Kalman-filter aiding and sensor simulation.
- [NTNU colav-simulator](../repos/ntnu-itk-autonomous-ship-lab__colav-simulator.md) - fit: high - Python framework from the NTNU Autoship centre for simulating and evaluating autonomous ship collision avoidance controllers, open-sourced in autumn 2025, with scenario generation and evaluation tooling.
- [OSNMA-SDR-SIM](../repos/haiyang-wong__osnma-sdr-sim.md) - fit: high - Galileo E1-B/E5b signal simulator with OSNMA authentication data embedded, configurable OSNMA parameters and USRP or file output, tested against GNSS-SDR and OSNMAlib.
- [AirSim](../repos/microsoft__airsim.md) - fit: medium - Unreal Engine based simulator for drones and cars with camera, depth, lidar, IMU, GPS, barometer and magnetometer models and a Python/C++ API.
- [Isaac Lab](../repos/isaac-sim__isaaclab.md) - fit: medium - Robot-learning framework on Isaac Sim for massively parallel RL and imitation learning, with navigation and locomotion task examples.
- [Webots](../repos/cyberbotics__webots.md) - fit: medium - General-purpose open-source robot simulator with many robot models and sensors including GPS, compass, IMU, lidar and radar.
- [NVIDIA Isaac Sim](../repos/isaac-sim__isaacsim.md) - fit: medium - NVIDIA's Omniverse-based robot simulator, now open source, with RTX sensor simulation (cameras, lidar, IMU) and ROS 2 bridges.
- [JSBSim](../repos/jsbsim-team__jsbsim.md) - fit: medium - Open-source flight dynamics model library for fixed-wing and other aircraft, used by FlightGear and as an ArduPilot SITL backend.
- [PromptCraft-Robotics](../repos/microsoft__promptcraft-robotics.md) - fit: medium - Microsoft's collection of prompts and an AirSim-based ChatGPT drone simulator accompanying the 'ChatGPT for Robotics' work.
- [InternNav](../repos/internrobotics__internnav.md) - fit: medium - PyTorch toolbox for embodied navigation on Habitat and Isaac Sim, covering vision-language navigation (VLN-CE and continuous-trajectory VLN) and point, image or trajectory goal navigation, with 10+ baselines, 6 benchmark
- [Project AirSim](../repos/iamaisim__projectairsim.md) - fit: medium - Open-source release of Project AirSim, the rewrite and successor of AirSim, for building and testing autonomous aerial systems in high-fidelity Unreal environments.
- [Pegasus Simulator](../repos/pegasussimulator__pegasussimulator.md) - fit: medium - Framework on top of NVIDIA Isaac Sim for simulating multirotors with PX4 in the loop and Python-defined vehicles and sensors.
- [Aerial Gym Simulator](../repos/ntnu-arl__aerial_gym_simulator.md) - fit: medium - GPU-parallel aerial-robot simulator from NTNU ARL built on NVIDIA Isaac Gym, with depth/range sensors and RL navigation examples.
- [AWSIM](../repos/autowarefoundation__awsim.md) - fit: medium - Unity-based digital-twin simulator for Autoware with simulated lidar, camera, GNSS and IMU.
- [NaveGo](../repos/rodralez__navego.md) - fit: medium - Open MATLAB/GNU Octave toolbox for simulating and processing integrated INS/GNSS navigation, including IMU error modelling and Allan variance analysis.
- [MARSIM](../repos/hku-mars__marsim.md) - fit: medium - Lightweight point-realistic lidar simulator for UAVs from HKU MaRS, supporting rotating and solid-state lidar patterns.
- [PX4 SITL Gazebo Classic](../repos/px4__px4-sitl_gazebo-classic.md) - fit: medium - Plugins, vehicle models and worlds that connect PX4 SITL/HITL to Gazebo Classic, including GPS, IMU, magnetometer, barometer and optical-flow plugins.
- [AerialVLN](../repos/airvln__airvln.md) - fit: medium - Benchmark and simulator (AirSim/UE-based) for vision-and-language navigation by UAVs in city-scale environments, with baseline agents.
- [OpenFly](../repos/shailab-ipec__openfly-platform.md) - fit: medium - Platform for outdoor aerial vision-language navigation: multi-engine simulators (UE, GTA V, Google Earth, 3DGS), automated data collection toolchain, a large benchmark and a keyframe-aware VLN model.
- [DARPA SubT Virtual Challenge](../repos/osrf__subt.md) - fit: medium - Gazebo worlds, robot models, ROS interfaces and scoring tools from the virtual track of the DARPA Subterranean Challenge.
- [GRID playground (AirGen)](../repos/genrobo__grid-playground.md) - fit: medium - Notebooks and examples for the GRID platform from Scaled Foundations, which pairs the AirSim-derived AirGen simulator with foundation-model perception and LLM-driven robot control.
- [Project DAVE](../repos/field-robotics-lab__dave.md) - fit: medium - Gazebo-based underwater simulation environment from the Naval Postgraduate School and partners, extending UUV Simulator with DVL, sonar, bathymetry and manipulation models.
- [multi-sdr-gps-sim](../repos/mictronics__multi-sdr-gps-sim.md) - fit: medium - Maintained derivative of GPS-SDR-SIM that streams GPS L1 baseband on the fly to several SDRs (HackRF, ADALM-Pluto, bladeRF) or files.
- [Crazyswarm2](../repos/imrclab__crazyswarm2.md) - fit: medium - ROS 2 framework for flying many Crazyflie nano-quadrotors with motion capture or onboard localization, including simulation backends.
- [ArduPilot SITL Models](../repos/ardupilot__sitl_models.md) - fit: medium - Collection of aircraft and vehicle models and parameter files for ArduPilot SITL across several simulator backends.
- [PX4 Gazebo models](../repos/px4__px4-gazebo-models.md) - fit: medium - Model and world repository for the new Gazebo, used by PX4 SITL targets such as gz_x500.
- [jMAVSim](../repos/px4__jmavsim.md) - fit: medium - Lightweight Java multirotor simulator that speaks MAVLink to PX4, without a 3D-world physics engine.
- [ROSflight ROS packages](../repos/rosflight__rosflight_ros_pkgs.md) - fit: medium - ROS 2 interface, simulator and utilities for the ROSflight autopilot.
- [MBZIRC Maritime Grand Challenge simulator](../repos/osrf__mbzirc.md) - fit: medium - Simulator (Ignition Fortress + ROS 2) for the MBZIRC Maritime Grand Challenge where UAVs and USVs cooperate in a GNSS-denied environment.
- [Crazyflie simulation](../repos/bitcraze__crazyflie-simulation.md) - fit: medium - Simulation models and tooling for Crazyflie in Webots and Gazebo.
- [ardupilot_gz](../repos/ardupilot__ardupilot_gz.md) - fit: medium - ROS 2 + Gazebo packages for ArduPilot SITL integration and testing.
- [BenchNav](../repos/masafumiendo__benchnav.md) - fit: medium - Gymnasium-based PyTorch simulator for benchmarking off-road navigation planners under uncertain, probabilistic traversability, with synthetic terrain generation.
- [HoloOcean ROS bridge](../repos/byu-holoocean__holoocean-ros.md) - fit: medium - ROS bridge for HoloOcean, BYU's Unreal Engine based underwater simulator with DVL, IMU, depth, sonar and acoustic modem sensors.
- [HoloOcean (documentation)](../repos/byu-holoocean__holoocean-docs.md) - fit: medium - Documentation repository for HoloOcean, BYU's Unreal-based underwater simulator with sonar, DVL, IMU, depth and camera sensors and multi-agent support.
- [HOUND](../repos/prl-mushr__hound_core.md) - fit: medium - Autonomy stack for a small-scale high-speed off-road vehicle from the UW MuSHR group, with BeamNG simulator integration and Jetson Orin deployment.
- [USBL Simulator](../repos/maximilian-nitsch__usbl-simulator.md) - fit: medium - C++ library and ROS 2 node that simulates ultra-short baseline acoustic positioning measurements, with a Gazebo plugin.
- [LEO-SPINE](../repos/xyangll__leospine.md) - fit: medium - Open toolkit for LEO/MEO/GEO constellation simulation and single/multi-satellite positioning.
- [strapdown-rs](../repos/jbrodovsky__strapdown-rs.md) - fit: medium - Rust implementation of a strapdown inertial navigation system, aimed at simulation and research on INS behaviour.
- [ORB_SLAM3_system_local](../repos/sasha-lobov__orb_slam3_system_local.md) - fit: medium - Pet project for local UAV navigation without GNSS: AirSim video streamed over ZeroMQ into monocular ORB-SLAM3, a ROS node converts NED/ENU frames, IMU data corrects monocular scale, and a PID controller tracks a trajecto
- [UT Starlink signal simulator](../repos/gitlab.com__radionavlab__public__ut-starlink-signal-simulator.md) - fit: medium - MATLAB-style utility functions from UT Austin's Radionavigation Lab for simulating Starlink Ku-band downlink signals, with playground examples.
- [Paparazzi UAV](../repos/paparazzi__paparazzi.md) - fit: low - Long-running academic autopilot (ENAC, TU Delft and others) for fixed-wing, rotorcraft and hybrids, with its own ground segment, flight-plan language and INS modules.
- [RotorS](../repos/ethz-asl__rotors_simulator.md) - fit: low - Gazebo Classic MAV simulator from ETH ASL with multirotor models, IMU and odometry sensor plugins and example controllers.
- [Flightmare](../repos/uzh-rpg__flightmare.md) - fit: low - Quadrotor simulator from UZH RPG with a decoupled Unity renderer and fast dynamics, aimed at RL and vision-based agile flight.
- [UUV Simulator](../repos/uuvsimulator__uuv_simulator.md) - fit: low - Gazebo/ROS packages for underwater vehicle simulation with hydrodynamics, thrusters and sensors; archived.
- [ESIM](../repos/uzh-rpg__rpg_esim.md) - fit: low - Event camera simulator from UZH RPG that renders event streams from simulated scenes.
- [Colosseum (AirSim fork)](../repos/codexlabsllc__colosseum.md) - fit: low - Community fork of AirSim that moved it to newer Unreal Engine 5 releases.
- [OmniDrones](../repos/btx0424__omnidrones.md) - fit: low - GPU-parallel drone simulation and RL platform built on Isaac Sim.
- [FlightGoggles](../repos/mit-aera__flightgoggles.md) - fit: low - Unity3D and ROS framework from MIT for photorealistic camera rendering with real or simulated vehicle dynamics in the loop.
- [bladeGPS](../repos/osqzss__bladegps.md) - fit: low - Real-time GPS L1 signal simulator variant of GPS-SDR-SIM for bladeRF hardware.
- [LimeGPS](../repos/osqzss__limegps.md) - fit: low - Real-time GPS L1 signal simulator variant for LimeSDR.
- [CrossLoc](../repos/topo-epfl__crossloc.md) - fit: low - CVPR 2022 cross-modal visual representation learning for absolute camera localization of aerial imagery, trained largely on synthetic data rendered from geodata.
- [Aeolus Ocean](../repos/aavek__aeolus-ocean.md) - fit: low - Collision avoidance simulator for COLREG-compliant autonomous ship navigation intended for use as a digital twin under varied weather and day/night conditions.
- [NPS underwater multibeam sonar plugin](../repos/field-robotics-lab__nps_uw_multibeam_sonar.md) - fit: low - GPU (CUDA) multibeam sonar simulation plugin for Gazebo producing physically motivated sonar imagery.
- [Loran-C reference signal generator](../repos/cheolj__loran-c-reference-code.md) - fit: low - NumPy API that generates Loran-C master and secondary station pulse groups with phase codes for simulation (Korean docs).
- [Beidou-SDR-SIM](../repos/haiyang-wong__beidou-sdr-sim.md) - fit: low - Open-source generator for BeiDou B1C baseband signals for SDR playback or file output.
- [graduate_work (UAV INS module thesis)](../repos/danamarkova__graduate_work.md) - fit: low - Russian graduate thesis code: 'Development of a UAV inertial navigation module using auxiliary navigation data'.

## Documents, talks, courses, datasets (15)

- [AirSim Documentation](../resources/microsoft-airsim-docs.md) - doc - Docs for AirSim covering setup, APIs, sensor configuration and PX4/ArduPilot integration.
- [ArduPilot SITL Simulator (Software in the Loop)](../resources/ardupilot-sitl-docs.md) - doc - Developer docs for running ArduPilot vehicles in SITL, connecting GCS and external simulators.
- [Champion-level drone racing using deep reinforcement learning](../resources/swift-champion-drone-racing-nature.md) - paper - Swift, a quadrotor using only onboard camera and IMU with an RL-trained policy, beat human world-champion pilots in head-to-head races.
- [Game4Loc: A UAV Geo-Localization Benchmark from Game Data](../resources/game4loc-2024.md) - paper - Builds a large synthetic drone-satellite dataset from a video game with partial-match pairs and trains weighted contrastive geo-localization.
- [Gazebo documentation and tutorials](../resources/gazebo-docs-tutorials.md) - doc - Official Gazebo (gz) docs and tutorials: building worlds, sensors (IMU, GPS/NavSat, cameras, LiDAR), ROS 2 bridging and plugins.
- [HACKtheMACHINE Unmanned (ONR / NavalX)](../resources/onr-hackthemachine-unmanned-2021.md) - competition - US Navy prize challenge on unmanned and autonomous systems with tracks on securing a simulated autopilot, separating benign from malicious data, and model-based mission requirements.
- [HoloOcean Documentation](../resources/byu-holoocean-docs.md) - doc - Install guide, sensor reference (sonar, DVL, IMU, depth) and examples for the HoloOcean underwater simulator.
- [Mid-Air Dataset](../resources/midair-synthetic-drone-dataset.md) - dataset - Synthetic low-altitude quadcopter flights with RGB, depth, normals, semantics and stereo plus navigation sensors, each trajectory recorded under several weather and season conditions.
- [OpenFly: A Comprehensive Platform for Aerial Vision-Language Navigation](../resources/openfly-aerial-vln-2025.md) - paper - Presents a multi-engine aerial VLN platform with automated data generation, a large outdoor benchmark and a keyframe-aware VLN model.
- [OpenSky: A Modular and Open-Source Simulator of Sky Polarization Measurements](../resources/opensky-sky-polarization-simulator-2024.md) - paper - Open simulator of what a polarimetric camera sees of the sky (intensity, angle and degree of polarization), validated against real captures, for developing polarization compasses.
- [PX4 Simulation (Gazebo, SITL) documentation](../resources/px4-simulation-docs.md) - doc - How to run PX4 software-in-the-loop with Gazebo and other simulators, including multi-vehicle setups and connecting ROS 2 and ground stations.
- [Safran Skydel simulation engine / GSG-8 GNSS simulator (ex-Orolia)](../resources/safran-skydel-gsg8.md) - product - Skydel is the SDR/GPU-based simulation engine behind Safran's GSG-8 simulators, with built-in jamming and spoofing scenarios, CRPA wavefront variants and LEO PNT signal options; Safran offers it to universities through a
- [Self-Driving Cars Specialization (University of Toronto)](../resources/coursera-self-driving-cars-specialization.md) - course - Four-course specialization covering vehicle dynamics and control, state estimation and localization, visual perception, and motion planning, using the CARLA simulator for assignments.
- [Spirent GSS7000 and PNT X GNSS/PNT simulators](../resources/spirent-gss7000-pntx.md) - product - Spirent's lab simulators generate multi-GNSS RF with controllable interference and spoofing (meaconing, trajectory spoofing, nav data spoofing) for hardware-in-the-loop receiver testing; PNT X extends this to combined PN
- [TartanAir: A Dataset to Push the Limits of Visual SLAM](../resources/cmu-tartanair-dataset.md) - dataset - Large synthetic dataset rendered in AirSim/Unreal environments with challenging lighting, weather and motion, with perfect ground truth for many modalities.

