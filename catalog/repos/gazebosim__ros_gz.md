# ros_gz bridge

`repo:gazebosim/ros_gz` - <https://github.com/gazebosim/ros_gz>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 551 | C++ | Apache-2.0 | 2026-11-05 | False | production | high |

Bridge packages that relay topics, services and clock between Gazebo Sim transport and ROS 1/ROS 2.

**Why it matters:** Needed whenever a ROS 2 navigation or SLAM stack has to consume simulated sensor streams from Gazebo.

**Hackathon notes:** Use parameter_bridge with a YAML of topic mappings. Match the ros_gz branch to your ROS 2 distro and Gazebo release or builds fail.

**Concepts:** [Simulation and HIL/SITL](../concepts/simulation.md), [ROS / ROS 2 robotics middleware](../concepts/ros.md)

**Tags:** `gazebo`, `ros2`, `bridge`

**Domains:** multi

## Related

- integrates_with: [Gazebo Sim (gz-sim)](../repos/gazebosim__gz-sim.md)

## Referenced by

- [Gazebo Sim (gz-sim)](../repos/gazebosim__gz-sim.md) (integrates_with)

_Indexed by lane(s): sim-data_

_GitHub metadata fetched 2026-11-06._
