# VID-Fusion

`repo:zju-fast-lab/vid-fusion` - <https://github.com/ZJU-FAST-Lab/VID-Fusion>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 154 | C++ | GPL-3.0 | 2026-03-15 | False | research-prototype | low |

Visual-inertial-dynamics odometry: adds a thrust-model (from measured rotor speed) factor to a VINS-style sliding-window optimizer and estimates the external force on the multirotor together with its pose.

**Why it matters:** Shows how a propulsion model enters a VIO back-end as one more factor, and gives an external-force estimate that doubles as a wind or payload signal.

**Build notes:** GPL-3.0, ROS1 build. Needs hover data to identify the thrust coefficient. Useful as a reference design, not a 48h base.

**Concepts:** [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Sensor calibration](../../catalog/concepts/calibration.md)

**Tags:** `visual-inertial-dynamics`, `thrust-model`, `external-force`, `ros1`

**Domains:** air

## Related

- evaluated_on: [VID-Dataset](../../catalog/repos/zju-fast-lab__vid-dataset.md)
- extends: [VINS-Fusion](../../catalog/repos/hkust-aerial-robotics__vins-fusion.md)

## Referenced by

- [VID-Dataset](../../catalog/repos/zju-fast-lab__vid-dataset.md) (integrates_with)
- [The Visual-Inertial-Dynamical Multirotor Dataset](../../catalog/resources/zhang-2021-vid-dataset-paper.md) (dataset_for)

_Indexed by lane(s): nav-differentiators_

_GitHub metadata fetched 2026-11-16._
