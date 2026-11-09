# wavemap

`repo:ethz-asl/wavemap` - <https://github.com/ethz-asl/wavemap>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| ? | C++ | ? | ? | ? | active-research | medium |

Multi-resolution occupancy mapping that stores the map as wavelet-compressed octree coefficients. Offers C++ and Python APIs plus a ROS 1 interface and is tested on Intel, AMD and ARM CPUs.

**Why it matters:** A CPU-only map with a Python API and an ARM-tested build, which suits a companion computer without a GPU. Handles thin obstacles and large ranges better than a fixed-resolution grid per its RSS 2023 paper.

**Hackathon notes:** License BSD-3-Clause, last push 2024-12-30 (gh api). ROS 2 work sits on an unmerged feature/ros2 branch. The Python package builds from source (no pywavemap on PyPI as of 2026-11-09). Docker files are provided. Not built here.

**Concepts:** [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Path and motion planning](../../catalog/concepts/path-planning.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `occupancy-map`, `multi-resolution`, `wavelet`, `python-api`, `c++`, `bsd-3-clause`

**Domains:** air, ground

## Related

- alternative_to: [OctoMap](../../catalog/repos/octomap__octomap.md)
- alternative_to: [voxblox](../../catalog/repos/ethz-asl__voxblox.md)

## Referenced by

- [voxblox](../../catalog/repos/ethz-asl__voxblox.md) (alternative_to)
- [Efficient volumetric mapping of multi-scale environments using wavelet-based compression](../../catalog/resources/reijgwart-wavemap-rss-2023.md) (has_code)

_Indexed by lane(s): close-area-planning_
