# mav_trajectory_generation

`repo:ethz-asl/mav_trajectory_generation` - <https://github.com/ethz-asl/mav_trajectory_generation>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 674 | C++ | Apache-2.0 | 2023-05-20 | False | archived | medium |

C++ library for polynomial (minimum-snap style) trajectory generation for multirotors, with linear and nonlinear optimisation of segment times and derivative constraints. Ships ROS 1 wrappers, examples and a MATLAB folder.

**Why it matters:** The reference open implementation of the Richter / Bry / Roy polynomial method. Turns a waypoint list from a route planner into a smooth, dynamically feasible reference an MPC or autopilot can track.

**Hackathon notes:** License Apache-2.0 (gh api), commercial-friendly. Last push 2023-05-20, effectively unmaintained. Build is catkin / ROS 1 (Noetic-era), so budget a Docker image. For a pure-Python 48h build, RotorPy's MinSnap class gives the same idea with less setup; use this one when you want the C++ core for the product story.

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Autopilots and flight control](../../catalog/concepts/autopilot.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `minimum-snap`, `polynomial`, `trajectory-generation`, `multirotor`, `c++`, `apache-2.0`

**Domains:** air

## Related

- alternative_to: [RotorPy](../../catalog/repos/spencerfolk__rotorpy.md)
- alternative_to: [GCOPTER](../../catalog/repos/zju-fast-lab__gcopter.md)
- integrates_with: [mav_control_rw](../../catalog/repos/ethz-asl__mav_control_rw.md)
- integrates_with: [RotorS](../../catalog/repos/ethz-asl__rotors_simulator.md)

## Referenced by

- [Guidance and planning for a navigation entry](../../docs/guidance-planning.md) (mentions)
- [mav_control_rw](../../catalog/repos/ethz-asl__mav_control_rw.md) (integrates_with)
- [OSQP](../../catalog/repos/osqp__osqp.md) (alternative_to)
- [AM-Traj](../../catalog/repos/zju-fast-lab__am_traj.md) (alternative_to)
- [Polynomial Trajectory Planning for Aggressive Quadrotor Flight in Dense Indoor Environments](../../catalog/resources/richter-bry-roy-polynomial-trajectories-isrr2013.md) (has_code)

_Indexed by lane(s): guidance-planning_

_GitHub metadata fetched 2026-11-09._
