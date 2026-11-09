# voxblox

`repo:ethz-asl/voxblox` - <https://github.com/ethz-asl/voxblox>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| ? | C++ | ? | ? | ? | research-prototype | medium |

CPU voxel mapping library that fuses depth into a truncated signed distance field (TSDF) and grows a Euclidean signed distance field (ESDF) from it incrementally. Ships ROS 1 nodes, meshing and planning-oriented queries.

**Why it matters:** The CPU reference for ESDF maps used by gradient-based drone planners. The ESDF gives distance and gradient to the nearest obstacle at any point, which is what clearance costs need.

**Hackathon notes:** License BSD-3-Clause, last push 2024-07-01 (gh api), no ROS 2 branch on the main repo. catkin build in a Noetic Docker image is the realistic route; do not try a native macOS build in 48h. CPU only, no CUDA. Use it only if the platform already runs ROS 1; nvblox replaces it on a Jetson.

**Concepts:** [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Path and motion planning](../../catalog/concepts/path-planning.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `tsdf`, `esdf`, `mapping`, `ros1`, `c++`, `bsd-3-clause`

**Domains:** air

## Related

- alternative_to: [Isaac ROS nvblox](../../catalog/repos/nvidia-isaac-ros__isaac_ros_nvblox.md)
- alternative_to: [wavemap](../../catalog/repos/ethz-asl__wavemap.md)
- alternative_to: [OctoMap](../../catalog/repos/octomap__octomap.md)

## Referenced by

- [wavemap](../../catalog/repos/ethz-asl__wavemap.md) (alternative_to)
- [OctoMap](../../catalog/repos/octomap__octomap.md) (alternative_to)
- [Voxblox: Incremental 3D Euclidean Signed Distance Fields for On-Board MAV Planning](../../catalog/resources/oleynikova-voxblox-iros-2017.md) (has_code)

_Indexed by lane(s): close-area-planning_
