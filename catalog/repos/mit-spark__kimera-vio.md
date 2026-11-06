# Kimera-VIO

`repo:mit-spark/kimera-vio` - <https://github.com/MIT-SPARK/Kimera-VIO>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,937 | C++ | BSD-2-Clause | 2026-08-06 | False | active-research | medium |

Stereo visual-inertial odometry with a factor-graph backend, robust loop closure and real-time 3D mesh generation; the odometry core of the Kimera stack.

**Why it matters:** Gives both a pose and a lightweight 3D mesh, useful for situational-awareness displays.

**Hackathon notes:** Heavier build (GTSAM, OpenGV, DBoW2); use the Docker setup. The ROS wrapper lives in a separate repo.

**Concepts:** [Visual(-inertial) odometry](../concepts/vio.md), [Visual SLAM](../concepts/visual-slam.md)

**Tags:** `gtsam`, `mesh`, `factor-graph`, `stereo`

**Domains:** air, ground

## Related

- depends_on: [Kimera-RPGO](../repos/mit-spark__kimera-rpgo.md)
- depends_on: [GTSAM](../repos/borglab__gtsam.md)
- extends: [Kimera-Multi](../repos/mit-spark__kimera-multi.md)

## Referenced by

- [Kimera-Multi](../repos/mit-spark__kimera-multi.md) (depends_on)
- [Kimera: an Open-Source Library for Real-Time Metric-Semantic Localization and Mapping](../resources/kimera-rosinol-2019.md) (has_code)
- [MIT 16.485 Visual Navigation for Autonomous Vehicles (VNAV)](../resources/mit-vnav-16485.md) (uses)

_Indexed by lane(s): slam_

_GitHub metadata fetched 2026-11-06._
