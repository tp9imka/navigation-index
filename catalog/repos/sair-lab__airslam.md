# AirSLAM

`repo:sair-lab/airslam` - <https://github.com/sair-lab/AirSLAM>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,217 | C++ | GPL-3.0 | 2025-11-19 | False | active-research | medium |

Point-and-line visual(-inertial) SLAM using learned features, designed for illumination-robust operation, with TensorRT acceleration; successor to AirVO.

**Why it matters:** Targets lighting changes (dawn/dusk/night), a common failure mode for camera navigation.

**Hackathon notes:** Needs an NVIDIA GPU (TensorRT). Docker recommended.

**Concepts:** [Visual SLAM](../concepts/visual-slam.md), [Visual(-inertial) odometry](../concepts/vio.md), [Feature detection and matching](../concepts/feature-matching.md), [Onboard / edge AI perception](../concepts/edge-ai.md)

**Tags:** `point-line`, `tensorrt`, `illumination`, `ros1`

**Domains:** air, ground

## Related

- alternative_to: [ORB-SLAM3](../repos/uz-slamlab__orb_slam3.md)

_Indexed by lane(s): slam_

_GitHub metadata fetched 2026-11-06._
