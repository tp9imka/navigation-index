# VID-Dataset

`repo:zju-fast-lab/vid-dataset` - <https://github.com/ZJU-FAST-Lab/VID-Dataset>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 66 | C++ | AGPL-3.0 | 2026-04-29 | False | research-prototype | medium |

Visual-inertial-dynamical multirotor dataset: stereo/depth camera, hardware-timestamped IMU, commanded and measured rotor speed and motor current for all four motors, flight-controller GPS, RTK and mocap ground truth, recorded as ROS bags with a time-sync tool.

**Why it matters:** One of very few open datasets with measured motor speed and current next to IMU and truth, which is exactly what a propulsion-aided estimator needs.

**Build notes:** AGPL-3.0 on the repo. Bags are behind a NAS share link with a password listed in the README; total size not verified. Convert bags to CSV once and cache.

**Concepts:** [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md), [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md)

**Tags:** `dataset`, `rotor-speed`, `motor-current`, `rtk`, `mocap`, `rosbag`

**Domains:** air

## Related

- integrates_with: [VID-Fusion](../../catalog/repos/zju-fast-lab__vid-fusion.md)

## Referenced by

- [Differentiators scan: what to bring besides satellite matching](../../docs/differentiators-scan.md) (mentions)
- [Neural-Fly](../../catalog/repos/aerorobotics__neural-fly.md) (alternative_to)
- [VID-Fusion](../../catalog/repos/zju-fast-lab__vid-fusion.md) (evaluated_on)
- [The Visual-Inertial-Dynamical Multirotor Dataset](../../catalog/resources/zhang-2021-vid-dataset-paper.md) (has_code)

_Indexed by lane(s): nav-differentiators_

_GitHub metadata fetched 2026-11-16._
