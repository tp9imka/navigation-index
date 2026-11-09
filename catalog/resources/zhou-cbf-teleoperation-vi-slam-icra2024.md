# Control-Barrier-Aided Teleoperation with Visual-Inertial SLAM for Safe MAV Navigation in Complex Environments

`res:zhou-cbf-teleoperation-vi-slam-icra2024` - paper - <https://arxiv.org/abs/2403.04331>

**By:** Siqi Zhou, Sotiris Papatheodorou, Stefan Leutenegger, Angela P. Schoellig - **Year:** 2024 - **Level:** advanced - **Access:** open

CBF safety filter on top of onboard VI-SLAM and dense occupancy mapping that corrects unsafe operator commands; unmapped space counts as unsafe. Real flights with onboard IMU, stereo infrared and depth only. ICRA 2024.

## Key takeaways

- Map-based safety filter on real VI-SLAM
- Treats unknown space as unsafe
- Does not react to estimator health

**Concepts:** [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Visual(-inertial) odometry](../../catalog/concepts/vio.md)

**Tags:** `control-barrier-function`, `vi-slam`, `teleoperation`

_Indexed by lane(s): close-area-innovation_
