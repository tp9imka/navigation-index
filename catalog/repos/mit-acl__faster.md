# FASTER

`repo:mit-acl/faster` - <https://github.com/mit-acl/faster>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 1,262 | C++ | BSD-3-Clause | 2025-03-10 | False | research-prototype | low |

Receding-horizon multirotor planner for unknown environments that optimises a fast trajectory through known-free and unknown space while always keeping a safe backup trajectory inside known-free space. Corridors come from JPS plus convex decomposition; the optimisation is a mixed-integer QP.

**Why it matters:** The clearest published answer to 'unknown space treated as free': plan fast through unknown space but commit only to a prefix that has a safe stop in known free space.

**Build notes:** License BSD-3-Clause, last push 2025-03-10 (gh api). Tested on ROS Kinetic and Melodic only. Needs Gurobi (commercial solver, academic license), which is a hard blocker for a 48h team without one. Borrow the 'safe backup trajectory' rule, not the code.

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `receding-horizon`, `safe-corridor`, `miqp`, `gurobi`, `ros1`, `c++`, `bsd-3-clause`

**Domains:** air, ground

## Related

- depends_on: [jps3d (MRSL Jump Point Search)](../../catalog/repos/kumarrobotics__jps3d.md)
- depends_on: [DecompUtil](../../catalog/repos/sikang__decomputil.md)
- same_org: [MADER](../../catalog/repos/mit-acl__mader.md)
- alternative_to: [SUPER](../../catalog/repos/hku-mars__super.md)

## Referenced by

- [SUPER](../../catalog/repos/hku-mars__super.md) (alternative_to)
- [DecompUtil](../../catalog/repos/sikang__decomputil.md) (integrates_with)
- [FASTER: Fast and Safe Trajectory Planner for Navigation in Unknown Environments](../../catalog/resources/tordesillas-faster-tro-2022.md) (has_code)

_Indexed by lane(s): close-area-planning_

_GitHub metadata fetched 2026-11-16._
