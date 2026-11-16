# terrain-navigation (ROS 1)

`repo:ethz-asl/terrain-navigation` - <https://github.com/ethz-asl/terrain-navigation>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 188 | C++ | BSD-3-Clause | 2025-07-01 | False | research-prototype | medium |

Original ROS 1 implementation of 'Safe Low-Altitude Navigation in Steep Terrain with Fixed-Wing Aerial Vehicles' (RA-L 2024), with a Docker build for Noetic.

**Why it matters:** Same planner as terrain-navigation2 with a ready Dockerfile, which may be the faster way to see it run.

**Build notes:** License BSD-3-Clause (gh api). Last push 2025-07-01. README provides docker build for ROS Noetic; image size quoted there is 774 MB (not rebuilt here). Use it to get pictures of terrain-aware routes in the first day, then port the cost.

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Terrain-relative navigation](../../catalog/concepts/terrain-nav.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `fixed-wing`, `dubins-airplane`, `rrt-star`, `terrain`, `ros1`, `docker`, `bsd-3-clause`

**Domains:** air

## Related

- alternative_to: [terrain-navigation2](../../catalog/repos/ethz-asl__terrain-navigation2.md)

## Referenced by

- [Guidance and planning for a navigation entry](../../docs/guidance-planning.md) (mentions)
- [terrain-navigation2](../../catalog/repos/ethz-asl__terrain-navigation2.md) (fork_of)
- [Safe Low-Altitude Navigation in Steep Terrain With Fixed-Wing Aerial Vehicles](../../catalog/resources/lim-terrain-navigation-fixed-wing-2024.md) (has_code)

_Indexed by lane(s): guidance-planning_

_GitHub metadata fetched 2026-11-16._
