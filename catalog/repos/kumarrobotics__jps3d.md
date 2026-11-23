# jps3d (MRSL Jump Point Search)

`repo:kumarrobotics/jps3d` - <https://github.com/KumarRobotics/jps3d>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 488 | C++ | BSD-3-Clause | 2021-02-18 | False | archived | medium |

C++ Jump Point Search on 2D and 3D occupancy grids, plus a distance-map planner that adds a potential-field style clearance cost around obstacles. Builds with plain CMake or catkin.

**Why it matters:** JPS returns the same optimal grid path as A* on uniform grids while expanding far fewer nodes, which matters in 3D. The front end of several corridor-based drone planners (FASTER, Liu et al. RA-L 2017).

**Build notes:** License BSD-3-Clause, last push 2021-02-18 (gh api): unmaintained but small. Needs Eigen, yaml-cpp, Boost; ROS not required. In a Python build write A* with an octile heuristic instead; JPS is worth it only on large 3D grids.

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md)

**Tags:** `jps`, `a-star`, `grid-search`, `3d`, `c++`, `bsd-3-clause`

**Domains:** air, ground

## Related

- integrates_with: [DecompUtil](../../catalog/repos/sikang__decomputil.md)
- same_org: [mpl_ros (motion primitive library)](../../catalog/repos/sikang__mpl_ros.md)

## Referenced by

- [FASTER](../../catalog/repos/mit-acl__faster.md) (depends_on)
- [DecompUtil](../../catalog/repos/sikang__decomputil.md) (integrates_with)
- [mpl_ros (motion primitive library)](../../catalog/repos/sikang__mpl_ros.md) (same_org)
- [Online Graph Pruning for Pathfinding On Grid Maps](../../catalog/resources/harabor-grastien-jps-aaai-2011.md) (has_code)
- [Planning Dynamically Feasible Trajectories for Quadrotors Using Safe Flight Corridors in 3-D Complex Environments](../../catalog/resources/liu-sfc-quadrotor-ral-2017.md) (has_code)

_Indexed by lane(s): close-area-planning_

_GitHub metadata fetched 2026-11-23._
