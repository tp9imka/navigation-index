# Inertial navigation (INS/IMU)

`concept:ins`

Strapdown mechanization, IMU error models, calibration, dead reckoning.

## Samples (1)

- [Terrain-relative navigation with a particle filter](../samples/terrain-relative-nav-pf.md) - A stdlib-only simulation of TERCOM/TRN: an aircraft with a biased INS and a radar altimeter matches its measured terrain profile against a seeded synthetic DEM with a particle filter that also estimates the INS velocity 

## Repositories (62)

- [FAST-LIO / FAST-LIO2](../repos/hku-mars__fast_lio.md) - fit: high - Computationally efficient LiDAR-inertial odometry using an iterated error-state Kalman filter and incremental k-d tree map, mapping raw points directly.
- [GTSAM](../repos/borglab__gtsam.md) - fit: high - Georgia Tech factor-graph library for smoothing and mapping, with incremental solvers (iSAM2) and a full IMU preintegration factor set.
- [robot_localization](../repos/cra-ros-pkg__robot_localization.md) - fit: high - ROS package with EKF and UKF state estimation nodes that fuse any number of odometry, IMU, pose and GNSS inputs, plus a navsat_transform node for GPS-to-map conversion.
- [manif](../repos/artivis__manif.md) - fit: high - Header-only C++11 library for Lie theory (SO2, SE2, SO3, SE3, SE_2(3) and more) with Jacobians, built around Sola's micro Lie theory paper; Python bindings available.
- [x-io Fusion](../repos/xiotechnologies__fusion.md) - fit: high - x-io Technologies' C AHRS library (revised Madgwick-style algorithm) with gyro offset correction, acceleration and magnetic disturbance rejection, and Python bindings.
- [gnss-ins-sim](../repos/aceinna__gnss-ins-sim.md) - fit: high - Python GNSS/INS simulator that generates trajectories, IMU/GNSS/magnetometer measurements with configurable error models, and runs navigation algorithms on them.
- [KF-GINS](../repos/i2nav-whu__kf-gins.md) - fit: high - Wuhan University i2Nav reference implementation of loosely coupled GNSS/INS integration with an error-state EKF, with sample data and documentation.
- [imu_tools](../repos/ccnyroboticslab__imu_tools.md) - fit: high - ROS tools for IMUs: Madgwick and complementary orientation filters and an RViz IMU visualisation plugin.
- [imu_x_fusion](../repos/cggos__imu_x_fusion.md) - fit: high - Loosely coupled IMU + GNSS / 6-DoF odometry fusion with multiple estimators side by side (ESKF, IEKF, UKF variants, MAP).
- [AI-IMU Dead-Reckoning](../repos/mbrossar__ai-imu-dr.md) - fit: high - Car dead reckoning from IMU only, using an invariant EKF whose noise covariances are adapted by a neural network, evaluated on KITTI.
- [imu_gps_localization](../repos/ydsf16__imu_gps_localization.md) - fit: high - Error-state Kalman filter fusing IMU and GPS for localization, small and readable.
- [AHRS (Python)](../repos/mayitzin__ahrs.md) - fit: high - Python collection of attitude estimation algorithms (Madgwick, Mahony, complementary, EKF, QUEST, TRIAD and more) plus utilities such as the World Magnetic Model and WGS84.
- [allan_variance_ros](../repos/ori-drs__allan_variance_ros.md) - fit: high - ROS tool (Oxford DRS) that computes Allan deviation plots from an IMU bag and outputs noise parameters in a Kalibr-compatible format.
- [RKO-LIO](../repos/prbonn__rko_lio.md) - fit: high - LiDAR-inertial odometry aiming to work without sensor-specific modelling or heavy tuning.
- [OB_GINS](../repos/i2nav-whu__ob_gins.md) - fit: high - Optimization-based GNSS/INS integration from Wuhan University i2Nav, using IMU preintegration in a sliding-window factor graph solved with Ceres.
- [RotorPy](../repos/spencerfolk__rotorpy.md) - fit: high - Python multirotor simulator with aerodynamic effects (drag, wind) for education and research.
- [navlie](../repos/decargroup__navlie.md) - fit: high - Python state estimation package on Lie groups (McGill DECAR): EKF, iterated EKF, sigma-point filters, batch estimation, and IMU kinematics models.
- [DRIFT](../repos/umich-curly__drift.md) - fit: high - Symmetry-preserving (invariant) state estimation library from University of Michigan for legged, wheeled and other robots, with real-time ROS support.
- [MagNav.jl](../repos/mit-ai-accelerator__magnav.jl.md) - fit: high - Julia package from the DAF-MIT AI Accelerator for airborne magnetic anomaly navigation: flight/INS data import or simulation, anomaly maps, aircraft magnetic compensation (Tolles-Lawson and neural models) and navigation 
- [PyShoe](../repos/utiasstars__pyshoe.md) - fit: high - Open Python foot-mounted INS from UTIAS with a public inertial dataset and several zero-velocity detectors, including learned ones.
- [pyins](../repos/nmayorov__pyins.md) - fit: high - Python package for modelling and analysing inertial navigation systems: strapdown integration, error models, Kalman-filter aiding and sensor simulation.
- [allan-variance (Python)](../repos/nmayorov__allan-variance.md) - fit: high - Small Python package computing Allan variance and fitting standard noise parameters.
- [ESP-Drone](../repos/espressif__esp-drone.md) - fit: medium - Espressif's mini quadcopter firmware for ESP32/ESP32-S2/S3, derived from Crazyflie code, controlled over Wi-Fi.
- [imu_utils](../repos/gaowenliang__imu_utils.md) - fit: medium - ROS package for analysing IMU performance with Allan variance to estimate noise and bias instability.
- [Faster-LIO](../repos/gaoxiang12__faster-lio.md) - fit: medium - Lightweight tightly coupled LiDAR-inertial odometry using parallel sparse incremental voxels instead of a k-d tree.
- [LiDAR_IMU_Init](../repos/hku-mars__lidar_imu_init.md) - fit: medium - Real-time LiDAR-inertial initialization estimating extrinsics, time offset, gravity and IMU bias online (IROS 2022).
- [dRehmFlight VTOL](../repos/nickrehm__drehmflight.md) - fit: medium - Single-file Arduino/Teensy flight controller for small VTOL and multirotor craft, written to be read and modified by students.
- [Point-LIO](../repos/hku-mars__point-lio.md) - fit: medium - High-bandwidth LiDAR-inertial odometry that updates the state point by point, tolerating aggressive motion and IMU saturation.
- [ethzasl_msf (Multi Sensor Fusion)](../repos/ethz-asl__ethzasl_msf.md) - fit: medium - Modular EKF framework from ETH ASL for fusing IMU propagation with pose, position and other sensor updates, with delayed-measurement handling.
- [DLIO](../repos/vectr-ucla__direct_lidar_inertial_odometry.md) - fit: medium - Lightweight LiDAR-inertial odometry with coarse-to-fine continuous-time motion correction (ICRA 2023).
- [eskf-gps-imu-fusion](../repos/zm0612__eskf-gps-imu-fusion.md) - fit: medium - ESKF fusing GPS and IMU for improved positioning, with documentation in Chinese.
- [IC-GVINS](../repos/i2nav-whu__ic-gvins.md) - fit: medium - INS-centric GNSS-visual-inertial navigation system from i2Nav, where the precise INS drives the visual front end and GNSS is fused in a factor graph.
- [NaveGo](../repos/rodralez__navego.md) - fit: medium - Open MATLAB/GNU Octave toolbox for simulating and processing integrated INS/GNSS navigation, including IMU error modelling and Allan variance analysis.
- [MadgwickAHRS (Arduino)](../repos/arduino-libraries__madgwickahrs.md) - fit: medium - Official Arduino library implementing the Madgwick AHRS filter.
- [invariant-ekf (Hartley InEKF)](../repos/rosshartley__invariant-ekf.md) - fit: medium - C++ library implementing the invariant EKF for aided inertial navigation, including contact-aided legged-robot state estimation.
- [imu_tk](../repos/kyle-ak__imu_tk.md) - fit: medium - Tool for calibrating IMU intrinsics (misalignment, scale factors and biases of accelerometer and gyro) from a sequence of static poses, without a turntable.
- [TLIO](../repos/cathias__tlio.md) - fit: medium - Tight Learned Inertial Odometry: a network regresses displacement and uncertainty from IMU windows, fused in a stochastic-cloning EKF.
- [MaRS (Modular and Robust Sensor-Fusion)](../repos/aau-cns__mars_lib.md) - fit: medium - Modular IMU-driven sensor-fusion framework from University of Klagenfurt designed so sensors can be added, removed or fail at runtime without reworking the core filter.
- [RIO](../repos/christopherdoer__rio.md) - fit: medium - EKF-based radar-inertial odometry using 4D mmWave radar ego-velocity measurements.
- [AirIO](../repos/air-io__air-io.md) - fit: medium - Learning-based inertial odometry for UAVs that improves feature observability by changing the IMU data representation (IEEE RA-L 2025).
- [ESKF ROS (EliaTarasov)](../repos/eliatarasov__eskf.md) - fit: medium - ROS error-state Kalman filter derived from PX4/ecl that fuses IMU with GPS, magnetometer, vision pose and optical flow.
- [ESKF (je310)](../repos/je310__eskf.md) - fit: medium - Error-state Kalman filter implementation following Sola's quaternion ESKF formulation.
- [AirIMU](../repos/haleqiu__airimu.md) - fit: medium - Learns IMU error correction and uncertainty with a network, combined with differentiable IMU preintegration (CMU AirLab).
- [ROSflight firmware](../repos/rosflight__rosflight_firmware.md) - fit: medium - Lean research autopilot (BYU) that keeps only attitude estimation and low-level control on the flight board and pushes everything else to a ROS companion.
- [Go-RIO](../repos/wooseongy__go-rio.md) - fit: medium - Ground-optimized 4D radar-inertial odometry integrating continuous velocity via Gaussian processes (ICRA 2025 best paper finalist).
- [ZUPT-aided INS (OpenShoe MATLAB)](../repos/hcarlsso__zupt-aided-ins.md) - fit: medium - MATLAB implementation of the OpenShoe zero-velocity-aided foot-mounted INS with several zero-velocity detectors (SHOE, acceleration variance and magnitude, angular rate energy).
- [Water Linked DVL Python](../repos/waterlinked__dvl-python.md) - fit: medium - Example Python code for talking to Water Linked DVLs over their serial and TCP/JSON protocols, parsing velocity and dead-reckoning reports.
- [strapdown-rs](../repos/jbrodovsky__strapdown-rs.md) - fit: medium - Rust implementation of a strapdown inertial navigation system, aimed at simulation and research on INS behaviour.
- [AuvEstimator](../repos/alliwong__auvestimator.md) - fit: medium - Work-in-progress EKF that fuses DVL, IMU and barometer data for AUV state estimation, with a ROS wrapper.
- [Paparazzi UAV](../repos/paparazzi__paparazzi.md) - fit: low - Long-running academic autopilot (ENAC, TU Delft and others) for fixed-wing, rotorcraft and hybrids, with its own ground segment, flight-plan language and INS modules.
- [kalibr_allan (archived)](../repos/rpng__kalibr_allan.md) - fit: low - MATLAB scripts producing IMU Allan standard deviation charts and Kalibr-ready noise values.
- [PX4 ECL (Estimation & Control Library)](../repos/px4__px4-ecl.md) - fit: low - Former home of PX4's estimation and control library including the EKF2 navigation filter; archived after the code moved into PX4-Autopilot.
- [sfwa UKF](../repos/sfwa__ukf.md) - fit: low - Templated C++ unscented Kalman filter library for state and parameter estimation, including square-root variants, aimed at embedded use.
- [Denoise IMU Gyro](../repos/mbrossar__denoise-imu-gyro.md) - fit: low - CNN that denoises low-cost gyroscope signals to improve attitude estimation.
- [LibrePilot](../repos/librepilot__librepilot.md) - fit: low - GitHub mirror of LibrePilot, the community continuation of OpenPilot for CC3D/Revolution boards, with the GCS bundled.
- [Learned Inertial Odometry for Drone Racing](../repos/uzh-rpg__learned_inertial_model_odometry.md) - fit: low - UZH RPG code fusing a learned inertial displacement model with an EKF for drone racing state estimation.
- [madgwick_py](../repos/morgil__madgwick_py.md) - fit: low - Minimal Python implementation of Madgwick's IMU and AHRS algorithms.
- [LE-VINS](../repos/i2nav-whu__le-vins.md) - fit: low - INS-centric visual-inertial navigation with LiDAR depth enhancement for visual features, from i2Nav.
- [gps_imu_fusion](../repos/shelfcol__gps_imu_fusion.md) - fit: low - GPS/IMU fusion examples implemented with ESKF, EKF, UKF and other filters.
- [iekf (contagon)](../repos/contagon__iekf.md) - fit: low - Invariant Kalman filter implementation on SE(2) and SE(3).
- [AV-Matlab-SW](../repos/jaffarrell__av-matlab-sw.md) - fit: low - MATLAB software for Allan variance calculations accompanying a published article on IMU noise characterisation (Farrell et al.).
- [Gaussian-RIO](../repos/robotics-upo__gaussian-rio.md) - fit: low - 4D radar-inertial odometry using Gaussian modeling of radar points and multi-hypothesis scan matching.

## Documents, talks, courses, datasets (29)

- [A micro Lie theory for state estimation in robotics](../resources/sola-micro-lie-theory.md) - paper - Tutorial paper giving just enough Lie theory (groups, exponential map, adjoint, Jacobians, uncertainty on manifolds) to write correct estimators for 3D pose; it is the basis of Solà's 'Lie theory for the roboticist' cour
- [Adaptable Navigation Systems (ANS)](../resources/darpa-adaptable-navigation-systems.md) - doc - DARPA program page for ANS, which pursued GPS-quality PNT in denied environments through precision inertial sensors (PINS) and the All Source Positioning and Navigation (ASPN) sensor-fusion effort.
- [AI-IMU Dead-Reckoning](../resources/brossard-ai-imu-dr.md) - paper - Car localisation from IMU alone by combining an invariant EKF with a neural network that adapts measurement noise covariances (pseudo-measurements), evaluated on KITTI.
- [AirIO: Learning Inertial Odometry with Enhanced IMU Feature Observability](../resources/airio-paper.md) - paper - UAV-focused learned inertial odometry that changes how IMU data are represented to the network to make motion features more observable.
- [An efficient orientation filter for inertial and inertial/magnetic sensor arrays](../resources/madgwick-orientation-filter-report.md) - report - Internal report introducing the gradient-descent orientation filter now known as the Madgwick filter, for IMU and MARG sensors.
- [ArduPilot Developer Conference Kaga 2024 - schedule and YouTube links](../resources/ardupilot-devcon-kaga-2024.md) - talk - Schedule and day-by-day livestream recordings of the 2024 ArduPilot developer conference in Japan, including a 'High Altitude Non-GPS' session and a talk on a CINS (DCM replacement) attitude estimator.
- [Contact-Aided Invariant Extended Kalman Filtering for Robot State Estimation](../resources/hartley-contact-aided-inekf.md) - paper - Applies the invariant EKF to legged robots, fusing IMU with leg contact kinematics, and evaluates it against a quaternion EKF.
- [DARPA eying new quantum sensing program: Robust Quantum Sensors (RoQS)](../resources/darpa-roqs-2024.md) - blog - Report on DARPA's RoQS program to make quantum sensors robust to platform interference so they can support navigation without GPS on real vehicles.
- [Developer Unconference - Paul Riseborough (EKF)](../resources/riseborough-ardupilot-unconference-2017-ekf.md) - talk - Forum post for the EKF talk at the 2017 ArduPilot developer un-conference in Canberra, given by the main author of ArduPilot's EKF.
- [DIU solicitation: Transition of Quantum Sensing for navigation](../resources/diu-transition-quantum-sensing-2024.md) - blog - Coverage of DIU's Transition of Quantum Sensing call seeking quantum inertial sensors and magnetometers to extend navigation holdover when GPS is unavailable.
- [Extended Kalman Filter (EKF) navigation overview](../resources/ardupilot-ekf-overview.md) - doc - Overview of ArduPilot's EKF2/EKF3 estimators: states, sensor inputs, innovation checks, lane switching across multiple IMUs and tuning guidance.
- [FAST-LIO2: Fast Direct LiDAR-inertial Odometry](../resources/fast-lio2-xu-2021.md) - paper - Introduces direct registration of raw LiDAR points in an iterated Kalman filter with an incremental k-d tree map, avoiding hand-crafted feature extraction.
- [GAO-21-320SP: Defense Navigation Capabilities - DOD Is Developing PNT Alternatives to GPS](../resources/gao-21-320sp-gps-alternatives.md) - report - Technology assessment of DoD's alternative PNT efforts (inertial, vision, celestial, magnetic, signals of opportunity, clocks), with maturity status and challenges.
- [GPS Spoofing WorkGroup 2024 - Final Report](../resources/opsgroup-gps-spoofing-final-report-2024.md) - report - Crowd-sourced industry report from a six-week OPSGROUP workgroup of pilots, controllers, regulators and manufacturers on GPS spoofing hitting civil flights, mainly near Middle East and Black Sea / Baltic conflict areas.
- [Kalibr wiki: IMU Noise Model](../resources/kalibr-imu-noise-model-wiki.md) - doc - Practical explanation of white noise and random-walk bias parameters for IMUs, how to convert datasheet values to continuous/discrete form and how to inflate them for real use.
- [Kalman and Bayesian Filters in Python](../resources/labbe-kalman-bayesian-filters-python.md) - book - Free interactive book as Jupyter notebooks: g-h filters, discrete Bayes, univariate and multivariate Kalman filters, EKF, UKF, particle filters and smoothers, all with runnable code built on the companion FilterPy librar
- [On-Manifold Preintegration for Real-Time Visual-Inertial Odometry](../resources/forster-imu-preintegration.md) - paper - Derives IMU preintegration on the SO(3) manifold with bias-correction Jacobians, enabling IMU factors between keyframes in factor-graph optimization.
- [Principles of GNSS, Inertial, and Multisensor Integrated Navigation Systems, Second Edition](../resources/groves-pnt-book-2e.md) - book - Standard reference on satellite, inertial and terrestrial radio navigation and their integration, including INS/GNSS integration architectures, dead reckoning, feature matching and integrity monitoring.
- [Quantum Sensors for Navigation, From Physics to Field Deployment](../resources/ion-webinar-kealy.md) - talk - Overview of quantum sensing for navigation (atom interferometers, quantum magnetometers, clocks) and what it takes to move them from lab to field.
- [Quaternion kinematics for the error-state Kalman filter](../resources/sola-quaternion-kinematics-eskf.md) - paper - Long tutorial report covering quaternion conventions, rotation perturbations and their derivatives, and a full derivation of an IMU-driven error-state Kalman filter including the reset step.
- [Quaternion kinematics for the error-state Kalman filter](../resources/sola-quaternion-eskf.md) - paper - Widely used tutorial on quaternion algebra, rotation integration and the error-state Kalman filter for IMU-driven navigation, including full IMU+GPS-style ESKF derivations.
- [Stanford PNT Symposium 2024 (18th annual)](../resources/stanford-pnt-symposium-2024.md) - talk - Page for the 28-29 October 2024 symposium with agenda, student and invited-speaker video albums, and slides; topics span GNSS, inertial sensing, timing and alternative navigation.
- [State Estimation for Robotics (Second Edition)](../resources/barfoot-state-estimation-robotics-2e.md) - book - Textbook on probabilistic estimation for robotics, from linear-Gaussian filtering and batch estimation to matrix Lie groups for 3D pose; the second edition adds variational inference and inertial navigation material.
- [Strapdown Inertial Navigation Technology, 2nd Edition](../resources/titterton-weston-strapdown-ins-2e.md) - book - Classic IET text on strapdown inertial navigation: sensor technologies, mechanisation, error propagation and compensation, and aided navigation.
- [The invariant extended Kalman filter as a stable observer](../resources/barrau-bonnabel-invariant-ekf.md) - paper - Foundational paper showing that for group-affine systems the invariant EKF has error dynamics independent of the trajectory, giving stability guarantees standard EKFs lack.
- [TLIO: Tight Learned Inertial Odometry](../resources/tlio-paper.md) - paper - Combines a network that predicts displacement and uncertainty from IMU data with an EKF, for pedestrian inertial odometry.
- [Using the ECL EKF (EKF2)](../resources/px4-ekf2-tuning-guide.md) - doc - PX4's main EKF2 guide: states, sensor fusion options (GNSS, flow, external vision, range, airspeed), aiding modes, innovation monitoring and tuning.
- [Visual-Inertial Navigation: A Concise Review](../resources/huang-vins-concise-review-2019.md) - paper - Compact review of visual-inertial navigation: filtering vs optimization, observability, calibration and representative systems.
- [Water Linked documentation (DVL and Underwater GPS)](../resources/waterlinked-docs.md) - doc - Vendor documentation for Water Linked DVLs and Underwater GPS (USBL-style) systems, including the JSON-over-TCP and serial protocols.

