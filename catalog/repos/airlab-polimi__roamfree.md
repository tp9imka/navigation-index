# ROAMFREE

`repo:airlab-polimi/roamfree` - <https://github.com/AIRLab-POLIMI/ROAMFREE>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 32 | C++ | ? | 2026-06-03 | False | active-research | low |

Pose-graph sensor fusion and self-calibration library on g2o with a catalogue of generic sensor models, used in UAV photogrammetry with raw inertial observations (Cucci, Skaloud).

**Why it matters:** A long-lived example of a sensor-agnostic fusion library where new sensors are declared, not coded, which is the plug-and-play idea.

**Build notes:** LGPL-3.0 per README (no SPDX on GitHub). ROS1 wrapper. Reference design.

**Concepts:** [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Sensor calibration](../../catalog/concepts/calibration.md)

**Tags:** `pose-graph`, `g2o`, `self-calibration`, `uav`

**Domains:** multi

## Related

- depends_on: [g2o](../../catalog/repos/rainerkuemmerle__g2o.md)

_Indexed by lane(s): nav-differentiators_

_GitHub metadata fetched 2026-11-23._
