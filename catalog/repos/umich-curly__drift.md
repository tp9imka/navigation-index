# DRIFT

`repo:umich-curly/drift` - <https://github.com/UMich-CURLY/drift>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 189 | C++ | BSD-3-Clause | 2026-06-01 | False | active-research | high |

Symmetry-preserving (invariant) state estimation library from University of Michigan for legged, wheeled and other robots, with real-time ROS support.

**Why it matters:** Maintained InEKF stack for proprioceptive dead reckoning when GNSS and vision are unavailable.

**Hackathon notes:** Has ROS examples; try on a wheeled robot bag for GNSS-free odometry.

**Concepts:** [Inertial navigation (INS/IMU)](../concepts/ins.md), [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [Ground vehicle autonomy](../concepts/ground-vehicle-nav.md), [ROS / ROS 2 robotics middleware](../concepts/ros.md)

**Tags:** `inekf`, `dead-reckoning`, `legged`, `wheeled`

**Domains:** ground

## Related

- extends: [invariant-ekf (Hartley InEKF)](../repos/rosshartley__invariant-ekf.md)

## Referenced by

- [invariant-ekf (Hartley InEKF)](../repos/rosshartley__invariant-ekf.md) (extends)
- [The invariant extended Kalman filter as a stable observer](../resources/barrau-bonnabel-invariant-ekf.md) (explains)

_Indexed by lane(s): ins-fusion_

_GitHub metadata fetched 2026-11-06._
