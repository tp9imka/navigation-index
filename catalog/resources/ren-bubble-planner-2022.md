# Bubble Planner: Planning High-speed Smooth Quadrotor Trajectories using Receding Corridors

`res:ren-bubble-planner-2022` - paper - <https://arxiv.org/abs/2202.12177>

**By:** Yunfan Ren, Fangcheng Zhu, Wenyi Liu, Zhepei Wang, Yi Lin, Fei Gao, Fu Zhang - **Year:** 2022 - **Level:** advanced - **Access:** open

Preprint on arXiv (authors list it as IROS 2022, not checked here). Builds a corridor of free-space spheres directly from a point cloud using a KD-tree, then optimises a smooth trajectory through it with a receding horizon. No official code release was found; third-party reproductions exist.

## Key takeaways

- Sphere corridors skip building a voxel map
- Receding corridor gives high speed with modest compute
- Only third-party code exists, so treat any repo as unvalidated

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md)

**Tags:** `safe-flight-corridor`, `point-cloud`, `preprint`

## Related

- same_author: [Integrated Planning and Control for Quadrotor Navigation in Presence of Suddenly Appearing Objects and Disturbances](../../catalog/resources/liu-ipc-ral-2024.md)

_Indexed by lane(s): close-area-planning_
