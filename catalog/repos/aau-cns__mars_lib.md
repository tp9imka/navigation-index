# MaRS (Modular and Robust Sensor-Fusion)

`repo:aau-cns/mars_lib` - <https://github.com/aau-cns/mars_lib>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 360 | C++ | NOASSERTION | 2025-04-23 | False | active-research | medium |

Modular IMU-driven sensor-fusion framework from University of Klagenfurt designed so sensors can be added, removed or fail at runtime without reworking the core filter.

**Why it matters:** Directly relevant to graceful degradation when GNSS or another aiding sensor drops out.

**Hackathon notes:** Core library builds standalone; ROS wrapper exists separately (mars_ros). Good fit for a sensor-dropout demo. Licence is BSD-2-Clause with an added condition that forbids selling the software or services based on it (source-available, no commercial use).

**Concepts:** [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md)

**Tags:** `ekf`, `modular`, `uav`

**Domains:** air

## Related

- alternative_to: [ethzasl_msf (Multi Sensor Fusion)](../../catalog/repos/ethz-asl__ethzasl_msf.md)
- same_org: [cnspy trajectory evaluation](../../catalog/repos/aau-cns__cnspy_trajectory_evaluation.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [1. PNT fundamentals](../../docs/primer/01-pnt-fundamentals.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [ethzasl_msf (Multi Sensor Fusion)](../../catalog/repos/ethz-asl__ethzasl_msf.md) (alternative_to)

_Indexed by lane(s): ins-fusion_

_GitHub metadata fetched 2026-11-06._
