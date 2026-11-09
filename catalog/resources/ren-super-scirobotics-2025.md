# Safety-assured high-speed navigation for MAVs

`res:ren-super-scirobotics-2025` - paper - <https://doi.org/10.1126/scirobotics.ado6187>

**By:** Yunfan Ren, Fangcheng Zhu, Guozheng Lu, Yixi Cai, Longji Yin, Fanze Kong, Jiarong Lin, Nan Chen, Fu Zhang - **Year:** 2025 - **Level:** advanced - **Access:** paywalled

Peer-reviewed (Science Robotics). LiDAR MAV planner that plans on point clouds and keeps an exploratory trajectory plus a backup trajectory in known free space each cycle. Reports far fewer failures than baselines and real flights above 20 m/s through clutter.

## Key takeaways

- Backup trajectory in known free space is the core safety mechanism
- Planning directly on point clouds avoids map latency
- Hardware: 3D LiDAR, high thrust-to-weight airframe

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [LiDAR odometry and SLAM](../../catalog/concepts/lidar-slam.md)

**Tags:** `lidar`, `high-speed`, `unknown-space`, `peer-reviewed`

## Related

- has_code: [SUPER](../../catalog/repos/hku-mars__super.md)
- cites: [FASTER: Fast and Safe Trajectory Planner for Navigation in Unknown Environments](../../catalog/resources/tordesillas-faster-tro-2022.md)

_Indexed by lane(s): close-area-planning_
