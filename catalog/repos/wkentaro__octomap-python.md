# octomap-python

`repo:wkentaro/octomap-python` - <https://github.com/wkentaro/octomap-python>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| ? | Python | ? | ? | ? | active-research | high |

Cython bindings for OctoMap, published on PyPI as octomap-python. Lets Python code insert point clouds, query occupancy and cast rays against an octree.

**Why it matters:** The shortest path from a Python sim to a real occupancy octree without ROS or a C++ build. Prebuilt wheels cover macOS arm64.

**Build notes:** License BSD-3-Clause, last push 2026-10-31 (gh api). PyPI 1.10.0.0 lists cp310 and cp311 macosx_11_0_arm64 wheels (checked on PyPI JSON, not installed). Use it when the team wants unknown-space semantics in a Python prototype; otherwise a numpy grid plus scipy distance transform is fewer moving parts.

**Concepts:** [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md)

**Tags:** `occupancy-map`, `octree`, `python-bindings`, `pip`, `bsd-3-clause`

**Domains:** air, ground

## Related

- depends_on: [OctoMap](../../catalog/repos/octomap__octomap.md)

## Referenced by

- [OctoMap](../../catalog/repos/octomap__octomap.md) (integrates_with)

_Indexed by lane(s): close-area-planning_
