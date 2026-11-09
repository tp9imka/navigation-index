# OctoMap: an efficient probabilistic 3D mapping framework based on octrees

`res:hornung-octomap-auro-2013` - paper - <https://doi.org/10.1007/s10514-012-9321-0>

**By:** Armin Hornung, Kai M. Wurm, Maren Bennewitz, Cyrill Stachniss, Wolfram Burgard - **Year:** 2013 - **Level:** intermediate - **Access:** paywalled

Peer-reviewed (Autonomous Robots). Describes the octree occupancy map with log-odds updates, clamping for fast change, and explicit separation of free, occupied and unknown cells. Evaluates memory and update cost on large indoor and outdoor scans.

## Key takeaways

- Unknown is a separate state, not free
- Clamping log-odds keeps the map responsive to change
- Per-ray insertion cost grows with resolution and range

**Concepts:** [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Path and motion planning](../../catalog/concepts/path-planning.md)

**Tags:** `occupancy-map`, `octree`, `peer-reviewed`

## Related

- has_code: [OctoMap](../../catalog/repos/octomap__octomap.md)

_Indexed by lane(s): close-area-planning_
