# MaRS (Modular and Robust Sensor-Fusion)

`repo:aau-cns/mars_lib` - <https://github.com/aau-cns/mars_lib>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 360 | C++ | NOASSERTION | 2025-04-23 | False | active-research | medium |

Modular IMU-driven sensor-fusion framework from University of Klagenfurt designed so sensors can be added, removed or fail at runtime without reworking the core filter.

**Why it matters:** Directly relevant to graceful degradation when GNSS or another aiding sensor drops out.

**Hackathon notes:** Core library builds standalone; ROS wrapper exists separately. Good fit for a sensor-dropout demo.

**Concepts:** [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [Inertial navigation (INS/IMU)](../concepts/ins.md), [Assured / resilient PNT](../concepts/assured-pnt.md)

**Tags:** `ekf`, `modular`, `uav`

**Domains:** air

## Related

- alternative_to: [ethzasl_msf (Multi Sensor Fusion)](../repos/ethz-asl__ethzasl_msf.md)
- same_org: [cnspy trajectory evaluation](../repos/aau-cns__cnspy_trajectory_evaluation.md)

## Referenced by

- [ethzasl_msf (Multi Sensor Fusion)](../repos/ethz-asl__ethzasl_msf.md) (alternative_to)

_Indexed by lane(s): ins-fusion_

_GitHub metadata fetched 2026-11-06._
