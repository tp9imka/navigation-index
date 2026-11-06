# Basalt

`repo:vladyslavusenko/basalt` - <https://github.com/VladyslavUsenko/basalt>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,021 | C++ | BSD-3-Clause | 2026-03-22 | False | active-research | medium |

GitHub mirror of Basalt, a visual-inertial odometry and mapping system built around non-linear factor recovery, with calibration tools; primary development is on GitLab.

**Why it matters:** Fast, accurate stereo VIO that runs well on CPUs; also ships camera-IMU calibration.

**Hackathon notes:** Submit issues upstream on GitLab. Install from GitLab release binaries (Ubuntu 22.04+ amd64, macOS arm64) or build from source with CMake presets + vcpkg; ROS integration is via community wrappers.

**Concepts:** [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Sensor calibration](../../catalog/concepts/calibration.md)

**Tags:** `stereo`, `factor-recovery`, `gitlab-mirror`

**Domains:** air, ground

## Related

- alternative_to: [OpenVINS](../../catalog/repos/rpng__open_vins.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)

_Indexed by lane(s): slam_

_GitHub metadata fetched 2026-11-06._
