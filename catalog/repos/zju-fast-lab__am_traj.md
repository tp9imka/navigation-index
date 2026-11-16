# AM-Traj

`repo:zju-fast-lab/am_traj` - <https://github.com/ZJU-FAST-Lab/am_traj>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 195 | C++ | GPL-3.0 | 2021-06-10 | False | research-prototype | low |

Alternating-minimisation trajectory generator for aggressive quadrotor flight: jointly optimises polynomial coefficients and segment durations, with a fast feasibility check on velocity and acceleration.

**Why it matters:** A compact, fast time-allocation solver for waypoint-to-trajectory conversion, a step most teams hand-tune.

**Build notes:** License GPL-3.0 (gh api), copyleft: fine for a demo, a problem if you want to ship closed source. Last push 2021-06-10. ROS 1 build. Read it for the algorithm; GCOPTER (MINCO) from the same lab is the newer successor.

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md)

**Tags:** `time-allocation`, `polynomial`, `multirotor`, `c++`, `gpl-3.0`

**Domains:** air

## Related

- alternative_to: [GCOPTER](../../catalog/repos/zju-fast-lab__gcopter.md)
- alternative_to: [mav_trajectory_generation](../../catalog/repos/ethz-asl__mav_trajectory_generation.md)

_Indexed by lane(s): guidance-planning_

_GitHub metadata fetched 2026-11-16._
