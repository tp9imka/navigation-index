# Bonxai

`repo:facontidavide/bonxai` - <https://github.com/facontidavide/Bonxai>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| ? | C++ | ? | ? | ? | active-research | medium |

Header-only C++ sparse hierarchical voxel grid inspired by OpenVDB, with an occupancy-map layer. Aimed at fast insertion and lookup with a small memory footprint.

**Why it matters:** A maintained, dependency-light alternative to OctoMap for a C++ companion process. Useful when the team wants an occupancy grid in a product-style C++ node without ROS 1.

**Build notes:** License MPL-2.0 (file-level copyleft: modified Bonxai files must stay open, linking code does not). Last push 2026-09-29 (gh api). PyPI has bonxai 0.1.1 but no macOS arm64 wheel listed. Pick it only if the build is C++ from the start.

**Concepts:** [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Path and motion planning](../../catalog/concepts/path-planning.md)

**Tags:** `voxel-grid`, `occupancy-map`, `header-only`, `c++`, `mpl-2.0`

**Domains:** air, ground

## Related

- alternative_to: [OctoMap](../../catalog/repos/octomap__octomap.md)

_Indexed by lane(s): close-area-planning_
