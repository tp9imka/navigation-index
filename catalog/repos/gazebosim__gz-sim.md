# Gazebo Sim (gz-sim)

`repo:gazebosim/gz-sim` - <https://github.com/gazebosim/gz-sim>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,568 | C++ | Apache-2.0 | 2026-11-06 | False | production | high |

Current-generation Gazebo robotics simulator with pluggable physics, rendering and a large sensor library (IMU, GPS/NavSat, lidar, cameras, magnetometer, altimeter). Successor to Gazebo Classic.

**Why it matters:** The default SITL backend for both PX4 and ArduPilot today; the place to inject sensor noise, GNSS dropouts and degraded conditions into a full autopilot stack.

**Hackathon notes:** Install a binary release (Harmonic or later) plus ros_gz. Pair with PX4 'make px4_sitl gz_x500' or ardupilot_gazebo. GPU helps for camera sensors; headless server mode works for CI.

**Concepts:** [Simulation and HIL/SITL](../concepts/simulation.md), [Autopilots and flight control](../concepts/autopilot.md), [ROS / ROS 2 robotics middleware](../concepts/ros.md)

**Tags:** `gazebo`, `sitl`, `sensors`, `physics`

**Domains:** air, ground, maritime, multi

## Related

- integrates_with: [PX4 Autopilot](../repos/px4__px4-autopilot.md)
- integrates_with: [ArduPilot](../repos/ardupilot__ardupilot.md)
- integrates_with: [ros_gz bridge](../repos/gazebosim__ros_gz.md)
- integrates_with: [ardupilot_gazebo](../repos/ardupilot__ardupilot_gazebo.md)
- integrates_with: [PX4 Gazebo models](../repos/px4__px4-gazebo-models.md)

## Referenced by

- [ardupilot_gazebo](../repos/ardupilot__ardupilot_gazebo.md) (integrates_with)
- [Webots](../repos/cyberbotics__webots.md) (alternative_to)
- [RotorS](../repos/ethz-asl__rotors_simulator.md) (alternative_to)
- [ros_gz bridge](../repos/gazebosim__ros_gz.md) (integrates_with)
- [Virtual RobotX (VRX)](../repos/osrf__vrx.md) (depends_on)
- [jMAVSim](../repos/px4__jmavsim.md) (alternative_to)
- [PX4 Gazebo models](../repos/px4__px4-gazebo-models.md) (integrates_with)
- [PX4 SITL Gazebo Classic](../repos/px4__px4-sitl_gazebo-classic.md) (alternative_to)
- [Gazebo documentation and tutorials](../resources/gazebo-docs-tutorials.md) (has_code)
- [PX4 Simulation (Gazebo, SITL) documentation](../resources/px4-simulation-docs.md) (explains)
- [PX4 Simulation (Gazebo, SITL) documentation](../resources/px4-simulation-docs.md) (uses)
- [PX4 SITL GPS denial: inject, measure drift, recover](../samples/px4-sitl-gps-denial.md) (uses)

_Indexed by lane(s): sim-data_

_GitHub metadata fetched 2026-11-06._
