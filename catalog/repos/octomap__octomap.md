# OctoMap

`repo:octomap/octomap` - <https://github.com/OctoMap/octomap>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| ? | C++ | ? | ? | ? | production | high |

Probabilistic 3D occupancy mapping on an octree, with explicit free, occupied and unknown cells and log-odds updates from ray casting. The repo also ships the octovis viewer and dynamicEDT3D, an incremental Euclidean distance map built on top of an octree.

**Why it matters:** The default occupancy map in drone planning papers and the format most planners can ingest. Plain CMake C++ with no ROS dependency, and Python wheels exist for Apple Silicon, so it runs on a laptop CPU.

**Hackathon notes:** License: the octomap library is New BSD (octomap/LICENSE.txt); octovis and dynamicEDT3D have their own license files, not checked here. Last push 2026-09-26 (gh api). ROS 2 server lives in OctoMap/octomap_mapping (ros2 branch). For a pure-Python build use the octomap-python wheel (macOS arm64 wheels on PyPI). Octree ray insertion is slow per point at fine resolution; for a small close area a dense numpy grid is simpler and faster.

**Concepts:** [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Path and motion planning](../../catalog/concepts/path-planning.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `occupancy-map`, `octree`, `mapping`, `esdf`, `c++`, `bsd-3-clause`

**Domains:** air, ground

## Related

- integrates_with: [octomap-python](../../catalog/repos/wkentaro__octomap-python.md)
- alternative_to: [UFOMap](../../catalog/repos/unknownfreeoccupied__ufomap.md)
- alternative_to: [voxblox](../../catalog/repos/ethz-asl__voxblox.md)
- alternative_to: [Isaac ROS nvblox](../../catalog/repos/nvidia-isaac-ros__isaac_ros_nvblox.md)

## Referenced by

- [voxblox](../../catalog/repos/ethz-asl__voxblox.md) (alternative_to)
- [wavemap](../../catalog/repos/ethz-asl__wavemap.md) (alternative_to)
- [Bonxai](../../catalog/repos/facontidavide__bonxai.md) (alternative_to)
- [UFOMap](../../catalog/repos/unknownfreeoccupied__ufomap.md) (alternative_to)
- [octomap-python](../../catalog/repos/wkentaro__octomap-python.md) (depends_on)
- [OctoMap: an efficient probabilistic 3D mapping framework based on octrees](../../catalog/resources/hornung-octomap-auro-2013.md) (has_code)

_Indexed by lane(s): close-area-planning_
