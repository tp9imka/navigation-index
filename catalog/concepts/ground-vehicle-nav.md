# Ground vehicle autonomy

`concept:ground-vehicle-nav`

UGV/off-road autonomy stacks, localization and navigation for ground robots.

## Repositories (40)

- [ArduPilot](../repos/ardupilot__ardupilot.md) - fit: high - GPL autopilot covering Copter, Plane (incl.
- [CARLA](../repos/carla-simulator__carla.md) - fit: high - Open-source autonomous-driving simulator on Unreal with camera, lidar, radar, GNSS and IMU sensors, traffic and weather control.
- [OSRM](../repos/project-osrm__osrm-backend.md) - fit: high - High-performance road routing engine on OpenStreetMap data using contraction hierarchies or multi-level Dijkstra.
- [Valhalla](../repos/valhalla__valhalla.md) - fit: high - Tiled OSM routing engine with dynamic costing per request (auto, truck, pedestrian, bicycle), isochrones and map matching.
- [Nav2 (ROS 2 Navigation)](../repos/ros-navigation__navigation2.md) - fit: high - The standard ROS 2 navigation stack: behavior-tree driven navigator, global planners (NavFn, Smac hybrid-A*/lattice, Theta*), local controllers (DWB, MPPI, Regulated Pure Pursuit), costmaps, recovery behaviors and waypoi
- [grid_map](../repos/anybotics__grid_map.md) - fit: high - C++ library and ROS integration for multi-layer 2.5D grid maps, widely used for elevation and traversability mapping.
- [robot_localization](../repos/cra-ros-pkg__robot_localization.md) - fit: high - ROS package with EKF and UKF state estimation nodes that fuse any number of odometry, IMU, pose and GNSS inputs, plus a navsat_transform node for GPS-to-map conversion.
- [rtabmap_ros](../repos/introlab__rtabmap_ros.md) - fit: high - ROS and ROS 2 integration for RTAB-Map, exposing SLAM, localization and odometry nodes.
- [pykitti](../repos/utiasstars__pykitti.md) - fit: high - Python loaders for the KITTI raw and odometry datasets.
- [elevation_mapping_cupy](../repos/leggedrobotics__elevation_mapping_cupy.md) - fit: high - GPU-accelerated elevation and traversability mapping from ETH Zurich, supporting semantic layers and learned traversability, used on ANYmal robots.
- [FAST_LIO_LOCALIZATION](../repos/hviktortsoi__fast_lio_localization.md) - fit: high - Relocalization in a prebuilt map using FAST-LIO odometry plus global scan-to-map registration.
- [CMU Autonomous Exploration Development Environment](../repos/hongbiaoz__autonomous_exploration_development_environment.md) - fit: high - CMU ground-robot development environment with simulated worlds, terrain analysis, local planner and waypoint tools used for exploration research (TARE, FAR planner).
- [AI-IMU Dead-Reckoning](../repos/mbrossar__ai-imu-dr.md) - fit: high - Car dead reckoning from IMU only, using an invariant EKF whose noise covariances are adapted by a neural network, evaluated on KITTI.
- [Nav2 tutorials](../repos/ros-navigation__navigation2_tutorials.md) - fit: high - Tutorial packages referenced by docs.nav2.org: example planner, controller and behavior-tree plugins, SLAM and GPS waypoint following setups.
- [Beluga](../repos/ekumen-os__beluga.md) - fit: high - Modern C++17 library of Monte Carlo Localization algorithms with a ROS 2 node that is a drop-in replacement for the Nav2 AMCL package.
- [DRIFT](../repos/umich-curly__drift.md) - fit: high - Symmetry-preserving (invariant) state estimation library from University of Michigan for legged, wheeled and other robots, with real-time ROS support.
- [Autoware](../repos/autowarefoundation__autoware.md) - fit: medium - Meta-repository for Autoware, the open-source ROS 2 autonomous driving stack covering localization (NDT, EKF), perception, planning and control.
- [Cartographer](../repos/cartographer-project__cartographer.md) - fit: medium - Real-time 2D and 3D SLAM with submaps and branch-and-bound loop closure across many sensor configurations.
- [GraphHopper](../repos/graphhopper__graphhopper.md) - fit: medium - Java OSM routing engine usable as library or server, with custom models for per-request costing and map matching.
- [Autoware Universe](../repos/autowarefoundation__autoware_universe.md) - fit: medium - The broad package collection of Autoware with experimental and production-candidate modules, including localization, pose initialization and GNSS/IMU fusion.
- [FAR Planner](../repos/michaelfyang__far_planner.md) - fit: medium - Visibility-graph route planner for known and unknown environments from the CMU SubT team.
- [fuse](../repos/locusrobotics__fuse.md) - fit: medium - ROS framework for sensor fusion as factor-graph optimization: plugin sensor models, motion models and publishers on top of Ceres, supporting both smoothing and fixed-lag estimation.
- [GBPlanner (CERBERUS)](../repos/ntnu-arl__gbplanner_ros.md) - fit: medium - NTNU ARL graph-based exploration planner for subterranean environments, used in the DARPA SubT challenge on legged and aerial robots.
- [AWSIM](../repos/autowarefoundation__awsim.md) - fit: medium - Unity-based digital-twin simulator for Autoware with simulated lidar, camera, GNSS and IMU.
- [RELLIS-3D](../repos/unmannedlab__rellis-3d.md) - fit: medium - Multi-modal off-road dataset from Texas A&M with lidar, camera, IMU and GNSS plus semantic annotations collected on a ground robot.
- [Wild Visual Navigation](../repos/leggedrobotics__wild_visual_navigation.md) - fit: medium - System that learns visual traversability online from pre-trained vision features and robot self-supervision, deployed on legged robots in forests.
- [opennav_coverage](../repos/open-navigation__opennav_coverage.md) - fit: medium - Nav2-compatible complete-coverage task server and navigator built on Fields2Cover, with behavior-tree utilities for field/area coverage and row following.
- [Oxford RobotCar SDK](../repos/ori-mrg__robotcar-dataset-sdk.md) - fit: medium - SDK for the Oxford RobotCar dataset with loaders and projection tools.
- [TartanDrive](../repos/castacks__tartan_drive.md) - fit: medium - Tools and utilities for the TartanDrive off-road driving dataset from CMU's AirLab, recorded on an ATV with multi-modal sensors.
- [pyboreas](../repos/utiasasrl__pyboreas.md) - fit: medium - Devkit for the Boreas multi-season driving dataset with radar, lidar, camera and GNSS/INS ground truth.
- [BenchNav](../repos/masafumiendo__benchnav.md) - fit: medium - Gymnasium-based PyTorch simulator for benchmarking off-road navigation planners under uncertain, probabilistic traversability, with synthetic terrain generation.
- [HOUND](../repos/prl-mushr__hound_core.md) - fit: medium - Autonomy stack for a small-scale high-speed off-road vehicle from the UW MuSHR group, with BeamNG simulator integration and Jetson Orin deployment.
- [safe-route (KosmoHackathon 2026)](../repos/kurligin__safe-route.md) - fit: medium - Controller for an autonomous ground cargo platform in the amr-sim simulator plus an operator workstation, built for the 'Безопасный маршрут' case of KosmoHackathon 2026 (2nd place in the final).
- [openpilot](../repos/commaai__openpilot.md) - fit: low - Open driver-assistance robotics stack whose localization uses GNSS (via laika) fused with IMU and vision.
- [Baidu Apollo](../repos/apolloauto__apollo.md) - fit: low - Baidu's open autonomous driving platform, including the multi-sensor fusion localization module combining GNSS RTK, IMU and lidar map matching.
- [LeGO-LOAM](../repos/robustfieldautonomylab__lego-loam.md) - fit: low - Lightweight ground-optimized LiDAR odometry and mapping that segments ground to speed up feature extraction on UGVs.
- [traversability_estimation](../repos/leggedrobotics__traversability_estimation.md) - fit: low - ETH package that computes traversability from elevation maps using slope, roughness and step-height filters.
- [Quatro](../repos/url-kaist__quatro.md) - fit: low - Fast, robust global registration for terrestrial robots that assumes near-planar motion to cut degrees of freedom.
- [WayFAST](../repos/matval__wayfast.md) - fit: low - Self-supervised traversability prediction for wheeled field robots that learns from RGB-D and estimates traction from kinodynamic models.
- [elevation_mapping](../repos/leggedrobotics__elevation_mapping.md) - fit: low - ETH Zurich robot-centric elevation mapping for rough terrain navigation that fuses range data into a probabilistic 2.5D map.

## Documents, talks, courses, datasets (19)

- [Advanced Navigation Boreas FOG INS with LVS laser velocity sensor](../resources/advanced-navigation-boreas.md) - product - Advanced Navigation's Boreas fibre-optic-gyro INS line, fused with its LVS laser velocity sensor or wheel odometry, is marketed for long GNSS-denied ground and maritime runs; reported trials include a US Army testbed and
- [AI-IMU Dead-Reckoning](../resources/brossard-ai-imu-dr.md) - paper - Car localisation from IMU alone by combining an invariant EKF with a neural network that adapts measurement noise covariances (pseudo-measurements), evaluated on KITTI.
- [Autoware documentation](../resources/autoware-docs.md) - doc - Official Autoware documentation with architecture, installation, tutorials and design notes for localization, perception and planning components.
- [Complex Urban Dataset](../resources/kaist-complex-urban-dataset.md) - dataset - Urban driving in dense city areas with lidar, stereo and navigation sensors where GNSS is degraded.
- [Contact-Aided Invariant Extended Kalman Filtering for Robot State Estimation](../resources/hartley-contact-aided-inekf.md) - paper - Applies the invariant EKF to legged robots, fusing IMU with leg contact kinematics, and evaluates it against a quaternion EKF.
- [DSEC: A Stereo Event Camera Dataset for Driving Scenarios](../resources/uzh-dsec-dataset.md) - dataset - Stereo event and frame cameras plus lidar and RTK GNSS on a car, including night and challenging illumination.
- [EUDIS Defence Hackathon Klagenfurt winners (Oct 2026)](../resources/eudis-2026-klagenfurt-winners.md) - blog - Report on the Klagenfurt site of the autumn 2026 EUDIS Defence Hackathon: IRNAS (Slovenia) won with multi-sensor fusion for ground robots; by the team's account path deviation fell from 37 cm to about 1 cm over 150+ test
- [KITTI Visual Odometry / SLAM Evaluation](../resources/kitti-odometry-benchmark.md) - dataset - Driving sequences with stereo cameras, Velodyne lidar and GPS/IMU ground truth, plus a public leaderboard for odometry.
- [KITTI-360](../resources/kitti-360-dataset.md) - dataset - Successor to KITTI with longer suburban drives, 360-degree perception sensors and dense annotations, with GPS/IMU poses.
- [Nav2 Documentation](../resources/nav2-docs.md) - doc - Official Nav2 documentation: concepts, configuration guides for every planner/controller/costmap plugin, tuning guide and tutorials including GPS-based navigation.
- [Nav2 first-time robot setup: Odometry and robot_localization](../resources/nav2-robot-localization-setup-guide.md) - doc - Setup guide for fusing wheel odometry and IMU with robot_localization's EKF to produce the odom frame Nav2 expects.
- [Navigating Using GPS Localization (Nav2 tutorial)](../resources/nav2-gps-navigation-tutorial.md) - doc - Nav2 tutorial on outdoor navigation with GPS: fusing GNSS, IMU and odometry with robot_localization's navsat_transform, configuring Nav2 for GPS waypoints, and demonstrating it in Gazebo.
- [Oxford RobotCar Dataset](../resources/oxford-robotcar-dataset.md) - dataset - Repeated drives of the same Oxford route over a year in all weather, with cameras, lidar and GPS/INS.
- [RELLIS-3D Dataset: Data, Benchmarks and Analysis](../resources/rellis3d-paper.md) - paper - Paper introducing the RELLIS-3D multimodal off-road dataset with annotated lidar and images and baseline results.
- [Self-Driving Cars Specialization (University of Toronto)](../resources/coursera-self-driving-cars-specialization.md) - course - Four-course specialization covering vehicle dynamics and control, state estimation and localization, visual perception, and motion planning, using the CARLA simulator for assignments.
- [Sensor Fusion and Non-linear Filtering for Automotive Systems (edX)](../resources/chalmers-sensor-fusion-nonlinear-filtering.md) - course - Self-paced edX course on Bayesian filtering: state-space and motion/measurement models, Kalman filter, EKF/UKF/CKF, and particle filters, with Matlab assignments building a personal filtering toolbox.
- [State Estimation and Localization for Self-Driving Cars (Coursera)](../resources/coursera-state-estimation-localization-sdc.md) - course - Course 2 of the UofT Self-Driving Cars specialization: least squares, KF/EKF/ES-EKF/UKF, IMU and GNSS sensor models, LiDAR scan matching with ICP, culminating in an error-state EKF that fuses IMU, GNSS and LiDAR on CARLA
- [The Marathon 2: A Navigation System](../resources/macenski-marathon2-nav2.md) - paper - Paper introducing Nav2: behavior-tree based navigation architecture for ROS 2, its design choices and a long-duration campus deployment test.
- [Wild Visual Navigation: Fast Traversability Learning via Pre-Trained Models and Online Self-Supervision](../resources/wild-visual-navigation-paper.md) - paper - Describes learning visual traversability online from pre-trained features and robot experience, adapting within minutes in forests and grassland.

