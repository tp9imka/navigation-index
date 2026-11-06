# Obstacle avoidance and collision avoidance

`concept:obstacle-avoidance`

Reactive avoidance, sense-and-avoid, DAA.

**Parent:** [Path and motion planning](../concepts/path-planning.md)

## Repositories (23)

- [Nav2 (ROS 2 Navigation)](../repos/ros-navigation__navigation2.md) - fit: high - The standard ROS 2 navigation stack: behavior-tree driven navigator, global planners (NavFn, Smac hybrid-A*/lattice, Theta*), local controllers (DWB, MPPI, Regulated Pure Pursuit), costmaps, recovery behaviors and waypoi
- [EGO-Swarm](../repos/zju-fast-lab__ego-planner-swarm.md) - fit: high - Decentralized multi-quadrotor extension of EGO-Planner with inter-agent collision avoidance and trajectory sharing over a network.
- [OMPL - Open Motion Planning Library](../repos/ompl__ompl.md) - fit: high - Library of sampling-based motion planners (RRT, RRT*, PRM, BIT*, informed variants, kinodynamic planners) with a clean state-space abstraction and Python bindings.
- [GNM / ViNT / NoMaD](../repos/robodhruv__visualnav-transformer.md) - fit: high - Code and checkpoints for general visual navigation foundation models (GNM, ViNT, NoMaD) that drive robots from camera images toward image goals or explore, with ROS deployment code.
- [CMU Autonomous Exploration Development Environment](../repos/hongbiaoz__autonomous_exploration_development_environment.md) - fit: high - CMU ground-robot development environment with simulated worlds, terrain analysis, local planner and waypoint tools used for exploration research (TARE, FAR planner).
- [Isaac ROS nvblox](../repos/nvidia-isaac-ros__isaac_ros_nvblox.md) - fit: high - GPU-accelerated 3D reconstruction (TSDF/ESDF) that provides Nav2 local costmaps from depth cameras.
- [MOOS-IvP](../repos/moos-ivp__moos-ivp.md) - fit: high - Long-running autonomy middleware (MOOS) plus the IvP Helm behaviour-based multi-objective decision engine, used widely for autonomous marine vehicles, including COLREGs-aware collision avoidance behaviours.
- [NTNU colav-simulator](../repos/ntnu-itk-autonomous-ship-lab__colav-simulator.md) - fit: high - Python framework from the NTNU Autoship centre for simulating and evaluating autonomous ship collision avoidance controllers, open-sourced in autumn 2025, with scenario generation and evaluation tooling.
- [Fast-Planner](../repos/hkust-aerial-robotics__fast-planner.md) - fit: medium - HKUST quadrotor planning framework: kinodynamic A* front-end plus B-spline optimization, with topological and perception-aware variants for fast flight in unknown environments.
- [EGO-Planner](../repos/zju-fast-lab__ego-planner.md) - fit: medium - ESDF-free gradient-based local planner for quadrotors from ZJU FAST Lab: optimizes B-spline trajectories using collision terms computed only where the trajectory hits obstacles.
- [FUEL - Fast UAV Exploration](../repos/hkust-aerial-robotics__fuel.md) - fit: medium - Frontier-information-structure based autonomous exploration for quadrotors, combining global tour planning over frontiers with local viewpoint refinement.
- [GBPlanner (CERBERUS)](../repos/ntnu-arl__gbplanner_ros.md) - fit: medium - NTNU ARL graph-based exploration planner for subterranean environments, used in the DARPA SubT challenge on legged and aerial robots.
- [Spatio-Temporal Voxel Layer](../repos/stevemacenski__spatio_temporal_voxel_layer.md) - fit: medium - Nav2 costmap layer using OpenVDB voxel grids with time decay to represent 3D obstacles from depth and LiDAR sensors.
- [KR Autonomous Flight](../repos/kumarrobotics__kr_autonomous_flight.md) - fit: medium - UPenn Kumar Robotics end-to-end autonomy stack for GPS-denied quadrotors: state estimation, mapping, planning and control in one system.
- [Aerial Gym Simulator](../repos/ntnu-arl__aerial_gym_simulator.md) - fit: medium - GPU-parallel aerial-robot simulator from NTNU ARL built on NVIDIA Isaac Gym, with depth/range sensors and RL navigation examples.
- [Ping Python](../repos/bluerobotics__ping-python.md) - fit: medium - Python library and examples for Blue Robotics Ping echosounder and Ping360 scanning sonar using the Ping protocol.
- [ping360_sonar ROS package](../repos/centralenantesrobotics__ping360_sonar.md) - fit: medium - ROS package that drives the Ping360 scanning sonar and publishes scans as images and laser-scan style messages.
- [MOOS-IvP COLREGs master's research code](../repos/d2snc__moos-ivp-masters.md) - fit: medium - MOOS-IvP applications from a 2025 master's project at Universidade de Sao Paulo implementing COLREGs-compliant collision avoidance for USVs, including a modified A* planner, a velocity-obstacle method and a virtual-conta
- [Flightmare](../repos/uzh-rpg__flightmare.md) - fit: low - Quadrotor simulator from UZH RPG with a decoupled Unity renderer and fast dynamics, aimed at RL and vision-based agile flight.
- [PX4 Avoidance](../repos/px4__px4-avoidance.md) - fit: low - Archived ROS nodes for local planning, global planning and safe landing using depth sensors with PX4.
- [MADER](../repos/mit-acl__mader.md) - fit: low - MIT ACL decentralized and asynchronous trajectory planner for multiple UAVs in dynamic environments with obstacle and agent avoidance.
- [MBPlanner](../repos/ntnu-arl__mbplanner_ros.md) - fit: low - Motion-primitive based exploration planner for fast aerial robots in confined spaces, used in CERBERUS flying platforms.
- [Aeolus Ocean](../repos/aavek__aeolus-ocean.md) - fit: low - Collision avoidance simulator for COLREG-compliant autonomous ship navigation intended for use as a digital twin under varied weather and day/night conditions.

## Documents, talks, courses, datasets (6)

- [COLREGs - Convention on the International Regulations for Preventing Collisions at Sea, 1972](../resources/imo-colregs.md) - standard - IMO page for the collision regulations that define give-way and stand-on duties, lights and signals; the rule set autonomous surface vessels must encode.
- [EGO-Planner: An ESDF-free Gradient-based Local Planner for Quadrotors](../resources/zhou-ego-planner-paper.md) - paper - Introduces a local planner that avoids building a full Euclidean signed distance field, computing collision penalties only from obstacles the trajectory intersects, cutting onboard compute.
- [MIT 2.680 Unmanned Marine Vehicle Autonomy, Sensing and Communications](../resources/mit-2680-marine-autonomy.md) - course - MIT course site with lectures and hands-on labs built on MOOS-IvP, covering behaviour-based autonomy, multi-vehicle coordination, collision avoidance and marine sensing.
- [NoMaD: Goal Masked Diffusion Policies for Navigation and Exploration](../resources/nomad-diffusion-nav-2023.md) - paper - Single diffusion policy that handles both goal-directed navigation and undirected exploration by masking the goal.
- [Robust and Efficient Quadrotor Trajectory Generation for Fast Autonomous Flight](../resources/zhou-fast-planner-paper.md) - paper - Fast-Planner paper: kinodynamic path search front-end plus B-spline optimization and time adjustment for fast quadrotor flight in unknown environments.
- [ViNT: A Foundation Model for Visual Navigation](../resources/vint-foundation-model-2023.md) - paper - Trains a transformer navigation policy across many robot datasets and shows it adapts to new robots and tasks with little data.

