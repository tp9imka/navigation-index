# GCOPTER

`repo:zju-fast-lab/gcopter` - <https://github.com/zju-fast-lab/gcopter>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 1,328 | C++ | MIT | 2023-10-15 | False | research-prototype | low |

General-purpose multicopter trajectory optimizer (MINCO) handling safe-corridor constraints and dynamic limits with spatial-temporal deformation.

**Why it matters:** Efficient, well-documented trajectory optimizer to turn waypoint paths into flyable minimum-control trajectories.

**Build notes:** Header-heavy C++ with ROS1 examples; best used as a library behind your own front-end.

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md)

**Tags:** `minco`, `trajectory-optimization`, `safe-flight-corridor`

**Domains:** air

## Related

- same_org: [EGO-Planner](../../catalog/repos/zju-fast-lab__ego-planner.md)

## Referenced by

- [Guidance and planning for a navigation entry](../../docs/guidance-planning.md) (mentions)
- [Close-area A=>B: planning and mapping for a small multirotor](../../docs/research/close-area-nav/01-planning-and-mapping.md) (mentions)
- [04. Close-area navigation: prior art for three innovation angles, plus a wider scan](../../docs/research/close-area-nav/04-innovation-prior-art.md) (mentions)
- [mav_trajectory_generation](../../catalog/repos/ethz-asl__mav_trajectory_generation.md) (alternative_to)
- [DecompUtil](../../catalog/repos/sikang__decomputil.md) (alternative_to)
- [AM-Traj](../../catalog/repos/zju-fast-lab__am_traj.md) (alternative_to)
- [EGO-Planner](../../catalog/repos/zju-fast-lab__ego-planner.md) (same_org)
- [EGO-Planner-v2 (Swarm Playground)](../../catalog/repos/zju-fast-lab__ego-planner-v2.md) (same_org)
- [Geometrically Constrained Trajectory Optimization for Multicopters](../../catalog/resources/wang-minco-gcopter-2021.md) (has_code)

_Indexed by lane(s): planning-gis-c2_

_GitHub metadata fetched 2026-11-09._
