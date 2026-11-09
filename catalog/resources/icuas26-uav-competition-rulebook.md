# ICUAS '26 UAV Competition Rulebook

`res:icuas26-uav-competition-rulebook` - competition - <https://github.com/larics/icuas26_competition/tree/main/rulebook>

**By:** LARICS, University of Zagreb - **Year:** 2025 - **Level:** intermediate - **Access:** open

Rulebook v1.0 (October 2025) for the ICUAS 2026 multi-UAV competition: Crazyflies in CrazySim (Gazebo, ROS 2 Humble) find ArUco-marked threats in a known urban world, keep a line-of-sight relay to a ground vehicle and manage battery with ArUco landing spots. Solutions are ROS 2 nodes in Docker, run by the organisers.

## Key takeaways

- Run void on crash, battery below 20 %, out of bounds or landing off a spot
- Only the provided camera, pose and octomap may be used (organiser answer)
- Detection points full within about 15 cm, none beyond about 1 m (organiser answer)

**Concepts:** [Swarms and multi-agent navigation](../../catalog/concepts/multi-agent.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md), [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md)

**Tags:** `icuas`, `competition`, `crazyflie`, `aruco`, `rules`

_Indexed by lane(s): loop-12_
