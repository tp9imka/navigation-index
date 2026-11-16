# HDVIO2.0

`repo:uzh-rpg/hdvio2.0` - <https://github.com/uzh-rpg/hdvio2.0>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 90 | C++ | AGPL-3.0 | 2026-02-03 | False | active-research | low |

Sliding-window VIO that adds a hybrid quadrotor dynamics model (point-mass model plus learned thrust and torque residual networks fed by commands and gyro history) and estimates wind and external disturbances. Built on SVO Pro; a sample rosbag and ONNX weights are linked.

**Why it matters:** State of the art (T-RO 2025) for using the vehicle's own dynamics to estimate wind while flying, which is the error term that dominates model-aided dead reckoning.

**Build notes:** Ubuntu 20.04 + ROS Noetic + catkin. GitHub reports AGPL-3.0 while the README says GPLv3 with commercial use by contacting the authors; treat as copyleft, reference only.

**Concepts:** [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md)

**Tags:** `hybrid-dynamics`, `wind-estimation`, `svo`, `tcn`, `ros1`

**Domains:** air

## Related

- extends: [SVO Pro](../../catalog/repos/uzh-rpg__rpg_svo_pro_open.md)
- same_org: [Learned Inertial Odometry for Drone Racing](../../catalog/repos/uzh-rpg__learned_inertial_model_odometry.md)

## Referenced by

- [HDVIO2.0: Wind and Disturbance Estimation with Hybrid Dynamics VIO](../../catalog/resources/cioffi-2025-hdvio2-wind-disturbance.md) (has_code)

_Indexed by lane(s): nav-differentiators_

_GitHub metadata fetched 2026-11-16._
