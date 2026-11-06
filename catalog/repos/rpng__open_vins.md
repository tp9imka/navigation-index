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
- [openvins-2020](../../docs/paper-digests/openvins-2020.md) (paper-digests)

**Concepts:** [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Sensor calibration](../../catalog/concepts/calibration.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md)

**Tags:** `msckf`, `ekf`, `ros1`, `ros2`, `simulator`

**Domains:** air, ground

## Related

- extends: [MINS](../../catalog/repos/rpng__mins.md)
- alternative_to: [MSCKF_VIO](../../catalog/repos/kumarrobotics__msckf_vio.md)
- evaluated_on: [evo](../../catalog/repos/michaelgrupp__evo.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Learning paths](../../docs/learning-paths.md) (mentions)
- [4. Vision, LiDAR and radar odometry](../../docs/primer/04-vision-lidar-radar-odometry.md) (mentions)
- [9. Evaluation and datasets](../../docs/primer/09-evaluation-and-datasets.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [Kalibr](../../catalog/repos/ethz-asl__kalibr.md) (integrates_with)
- [maplab](../../catalog/repos/ethz-asl__maplab.md) (integrates_with)
- [MSCKF_VIO](../../catalog/repos/kumarrobotics__msckf_vio.md) (alternative_to)
- [MAVROS](../../catalog/repos/mavlink__mavros.md) (integrates_with)
- [MINS](../../catalog/repos/rpng__mins.md) (extends)
- [COVINS / COVINS-G](../../catalog/repos/v4rl-ucy__covins.md) (integrates_with)
- [Basalt](../../catalog/repos/vladyslavusenko__basalt.md) (alternative_to)
- [Visual-Inertial Navigation: A Concise Review](../../catalog/resources/huang-vins-concise-review-2019.md) (explains)
- [OpenVINS documentation](../../catalog/resources/openvins-docs.md) (has_code)
- [Shield AI Hivemind autonomy stack](../../catalog/resources/shield-ai-hivemind.md) (alternative_to)
- [Spleenlab VISIONAIRY perception and GNSS-free navigation software](../../catalog/resources/spleenlab-visionairy.md) (alternative_to)
- [Distributed Visual-Inertial Cooperative Localization](../../catalog/resources/zhu-2021-distributed-vi-cooperative-localization.md) (uses)
- [Relative navigation benchmark on real data: KISS-ICP lidar odometry, OpenVINS VIO, mono and nadir VO, scored with evo](../../catalog/samples/relative-nav-benchmark.md) (uses)
- [VIO to MAVLink bridge with ENU/FLU to NED/FRD conversion](../../catalog/samples/vio-to-mavlink-bridge.md) (explains)

_Indexed by lane(s): slam_

_GitHub metadata fetched 2026-11-06._
