# UFOMap

`repo:unknownfreeoccupied/ufomap` - <https://github.com/UnknownFreeOccupied/ufomap>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 436 | C++ | BSD-2-Clause | 2025-06-27 | False | active-research | medium |

Octree occupancy mapping that represents unknown space explicitly and indexes free, occupied and unknown nodes so queries such as 'is this box all known free' are cheap. Has ROS 1 wrappers and a newer v2 branch.

**Why it matters:** The 'unknown is not free' failure mode is the main safety bug in close-area planners. UFOMap makes the unknown check a first-class query instead of an afterthought.

**Build notes:** License BSD-2-Clause, last push 2025-06-27 (gh api). Several devel branches (devel, v2, dufomap); pick master for stability. C++17 library, ROS 1 wrapper in a separate repo per the wiki. For 48h, copy the idea (three-state grid, collision checks reject unknown) into a numpy grid rather than integrating the library.

**Concepts:** [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Path and motion planning](../../catalog/concepts/path-planning.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `occupancy-map`, `octree`, `unknown-space`, `c++`, `bsd-2-clause`

**Domains:** air, ground

## Related

- alternative_to: [OctoMap](../../catalog/repos/octomap__octomap.md)

## Referenced by

- [OctoMap](../../catalog/repos/octomap__octomap.md) (alternative_to)
- [UFOMap: An Efficient Probabilistic 3D Mapping Framework That Embraces the Unknown](../../catalog/resources/duberg-ufomap-ral-2020.md) (has_code)

_Indexed by lane(s): close-area-planning_

_GitHub metadata fetched 2026-11-16._
