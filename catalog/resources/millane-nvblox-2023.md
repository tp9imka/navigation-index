# nvblox: GPU-Accelerated Incremental Signed Distance Field Mapping

`res:millane-nvblox-2023` - paper - <https://arxiv.org/abs/2311.00626>

**By:** Alexander Millane, Helen Oleynikova, Emilie Wirbel, Remo Steiner, Vikram Ramasamy, David Tingdahl, Roland Siegwart - **Year:** 2023 - **Level:** intermediate - **Access:** open

Preprint on arXiv. Moves TSDF and ESDF integration onto the GPU and reports large speedups over CPU voxblox, targeting Jetson-class robots with RGB-D cameras.

## Key takeaways

- Same TSDF to ESDF pipeline as voxblox, on CUDA
- Needs an NVIDIA GPU: no Apple Silicon path
- Fits a Jetson companion with a depth camera

**Concepts:** [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md)

**Tags:** `esdf`, `tsdf`, `gpu`, `cuda`, `preprint`

## Related

- has_code: [Isaac ROS nvblox](../../catalog/repos/nvidia-isaac-ros__isaac_ros_nvblox.md)
- same_author: [Voxblox: Incremental 3D Euclidean Signed Distance Fields for On-Board MAV Planning](../../catalog/resources/oleynikova-voxblox-iros-2017.md)

_Indexed by lane(s): close-area-planning_
