# SUPER

`repo:hku-mars/super` - <https://github.com/hku-mars/SUPER>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| ? | C++ | ? | ? | ? | active-research | low |

LiDAR-based high-speed MAV planner that plans directly on point clouds. Each cycle produces an exploratory trajectory through known and unknown space plus a backup trajectory confined to known free space, so the vehicle always has a safe fallback. Includes ROG-Map and a simulator.

**Why it matters:** The 2025 state of the art for safe flight through clutter with explicit handling of unknown space (Science Robotics). Good to cite as the target architecture.

**Hackathon notes:** No license file in the repo (gh api shows none): read-only. Last push 2025-06-04. ROS 1 Noetic is tier 1; ROS 2 Foxy preview is flagged unstable in the README. Needs a 3D LiDAR + LIO for real flight. Cite it; do not build it in 48h.

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md), [LiDAR odometry and SLAM](../../catalog/concepts/lidar-slam.md)

**Tags:** `lidar`, `backup-trajectory`, `unknown-space`, `ros1`, `ros2-preview`, `c++`, `no-license`

**Domains:** air

## Related

- depends_on: [ROG-Map](../../catalog/repos/hku-mars__rog-map.md)
- integrates_with: [FAST-LIO / FAST-LIO2](../../catalog/repos/hku-mars__fast_lio.md)
- alternative_to: [FASTER](../../catalog/repos/mit-acl__faster.md)
- same_org: [IPC (Integrated Planning and Control)](../../catalog/repos/hku-mars__ipc.md)

## Referenced by

- [IPC (Integrated Planning and Control)](../../catalog/repos/hku-mars__ipc.md) (same_org)
- [ROG-Map](../../catalog/repos/hku-mars__rog-map.md) (integrates_with)
- [FASTER](../../catalog/repos/mit-acl__faster.md) (alternative_to)
- [Safety-assured high-speed navigation for MAVs](../../catalog/resources/ren-super-scirobotics-2025.md) (has_code)

_Indexed by lane(s): close-area-planning_
