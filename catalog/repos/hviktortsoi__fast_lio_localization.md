# FAST_LIO_LOCALIZATION

`repo:hviktortsoi/fast_lio_localization` - <https://github.com/HViktorTsoi/FAST_LIO_LOCALIZATION>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,080 | C++ | GPL-2.0 | 2023-05-20 | False | research-prototype | high |

Relocalization in a prebuilt map using FAST-LIO odometry plus global scan-to-map registration.

**Why it matters:** Localize in a map you surveyed earlier, the standard pattern for GNSS-denied ground ops in known areas.

**Hackathon notes:** ROS 1; build a map with FAST-LIO first, then localize. Needs a rough initial pose (RViz or another sensor). The global-localization node needs Python 2.7 and Open3D 0.9, so plan for a Melodic-era environment or a container.

**Concepts:** [LiDAR odometry and SLAM](../concepts/lidar-slam.md), [Place recognition and loop closure](../concepts/place-recognition.md), [Ground vehicle autonomy](../concepts/ground-vehicle-nav.md)

**Tags:** `relocalization`, `prior-map`, `ros1`

**Domains:** ground

## Related

- extends: [FAST-LIO / FAST-LIO2](../repos/hku-mars__fast_lio.md)

## Referenced by

- [FAST-LIO / FAST-LIO2](../repos/hku-mars__fast_lio.md) (extends)

_Indexed by lane(s): slam_

_GitHub metadata fetched 2026-11-06._
