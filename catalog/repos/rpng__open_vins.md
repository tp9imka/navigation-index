# OpenVINS

`repo:rpng/open_vins` - <https://github.com/rpng/open_vins>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 3,173 | C++ | GPL-3.0 | 2025-11-30 | False | active-research | high |

MSCKF-based visual-inertial navigation platform with online calibration, a simulator, and extensive documentation for research use.

**Why it matters:** Probably the best-documented VIO codebase; filter-based, light enough for embedded boards.

**Hackathon notes:** Supports ROS 1 and ROS 2. Its built-in simulator lets you test without hardware on day one. Docs site explains every estimator component.

## Deep dives

- [_index-perception-altnav](../../docs/integration-cards/_index-perception-altnav.md) (integration-cards)
- [rpng__open_vins](../../docs/integration-cards/rpng__open_vins.md) (integration-cards)

**Concepts:** [Visual(-inertial) odometry](../concepts/vio.md), [Sensor calibration](../concepts/calibration.md), [Simulation and HIL/SITL](../concepts/simulation.md)

**Tags:** `msckf`, `ekf`, `ros1`, `ros2`, `simulator`

**Domains:** air, ground

## Related

- extends: [MINS](../repos/rpng__mins.md)
- alternative_to: [MSCKF_VIO](../repos/kumarrobotics__msckf_vio.md)
- evaluated_on: [evo](../repos/michaelgrupp__evo.md)

## Referenced by

- [Kalibr](../repos/ethz-asl__kalibr.md) (integrates_with)
- [maplab](../repos/ethz-asl__maplab.md) (integrates_with)
- [MSCKF_VIO](../repos/kumarrobotics__msckf_vio.md) (alternative_to)
- [MAVROS](../repos/mavlink__mavros.md) (integrates_with)
- [MINS](../repos/rpng__mins.md) (extends)
- [COVINS / COVINS-G](../repos/v4rl-ucy__covins.md) (integrates_with)
- [Basalt](../repos/vladyslavusenko__basalt.md) (alternative_to)
- [Visual-Inertial Navigation: A Concise Review](../resources/huang-vins-concise-review-2019.md) (explains)
- [OpenVINS documentation](../resources/openvins-docs.md) (has_code)
- [Shield AI Hivemind autonomy stack](../resources/shield-ai-hivemind.md) (alternative_to)
- [Spleenlab VISIONAIRY perception and GNSS-free navigation software](../resources/spleenlab-visionairy.md) (alternative_to)
- [VIO to MAVLink bridge with ENU/FLU to NED/FRD conversion](../samples/vio-to-mavlink-bridge.md) (explains)

_Indexed by lane(s): slam_

_GitHub metadata fetched 2026-11-06._
