# ethzasl_msf (Multi Sensor Fusion)

`repo:ethz-asl/ethzasl_msf` - <https://github.com/ethz-asl/ethzasl_msf>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,105 | C++ | NOASSERTION | 2026-10-19 | False | research-prototype | medium |

Modular EKF framework from ETH ASL for fusing IMU propagation with pose, position and other sensor updates, with delayed-measurement handling.

**Why it matters:** Classic MAV state estimator that shows how to fuse delayed vision/GPS measurements into an IMU-driven filter.

**Hackathon notes:** ROS 1 era; building on modern distros takes effort. Read it for the design more than to run it.

**Concepts:** [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [Inertial navigation (INS/IMU)](../concepts/ins.md), [ROS / ROS 2 robotics middleware](../concepts/ros.md)

**Tags:** `ekf`, `mav`, `ros1`

**Domains:** air

## Related

- alternative_to: [MaRS (Modular and Robust Sensor-Fusion)](../repos/aau-cns__mars_lib.md)
- alternative_to: [robot_localization](../repos/cra-ros-pkg__robot_localization.md)
- same_org: [ROVIO](../repos/ethz-asl__rovio.md)

## Referenced by

- [MaRS (Modular and Robust Sensor-Fusion)](../repos/aau-cns__mars_lib.md) (alternative_to)
- [robot_localization](../repos/cra-ros-pkg__robot_localization.md) (alternative_to)

_Indexed by lane(s): ins-fusion_

_GitHub metadata fetched 2026-11-06._
