# DecompUtil

`repo:sikang/decomputil` - <https://github.com/sikang/DecompUtil>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| ? | C++ | ? | ? | ? | archived | medium |

Header-only C++ library that grows convex polytopes (safe flight corridors) around a piecewise-linear path using ellipsoid inflation against a point cloud.

**Why it matters:** The standard way to turn a grid path into convex free-space constraints that a QP or MPC can use. Corridors make the collision constraint linear, so the optimiser stays a QP.

**Build notes:** License BSD-3-Clause, last push 2018-09-10 (gh api). Header-only with Eigen, so it builds anywhere. A Python team can get a usable corridor faster with axis-aligned box inflation along the A* path.

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md)

**Tags:** `safe-flight-corridor`, `convex-decomposition`, `header-only`, `c++`, `bsd-3-clause`

**Domains:** air, ground

## Related

- integrates_with: [jps3d (MRSL Jump Point Search)](../../catalog/repos/kumarrobotics__jps3d.md)
- integrates_with: [FASTER](../../catalog/repos/mit-acl__faster.md)
- alternative_to: [GCOPTER](../../catalog/repos/zju-fast-lab__gcopter.md)

## Referenced by

- [IPC (Integrated Planning and Control)](../../catalog/repos/hku-mars__ipc.md) (alternative_to)
- [jps3d (MRSL Jump Point Search)](../../catalog/repos/kumarrobotics__jps3d.md) (integrates_with)
- [FASTER](../../catalog/repos/mit-acl__faster.md) (depends_on)
- [DecompROS](../../catalog/repos/sikang__decompros.md) (depends_on)
- [Planning Dynamically Feasible Trajectories for Quadrotors Using Safe Flight Corridors in 3-D Complex Environments](../../catalog/resources/liu-sfc-quadrotor-ral-2017.md) (has_code)

_Indexed by lane(s): close-area-planning_
