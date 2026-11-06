# GVINS

`repo:hkust-aerial-robotics/gvins` - <https://github.com/HKUST-Aerial-Robotics/GVINS>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,169 | C++ | GPL-3.0 | 2021-09-11 | False | research-prototype | medium |

Tightly coupled GNSS-visual-inertial estimator that fuses raw GNSS pseudorange and Doppler with VIO in a factor graph, giving drift-free global poses and smooth local tracking.

**Why it matters:** Shows how raw GNSS measurements degrade gracefully into VIO when satellites are blocked, a core pattern for contested or urban PNT.

**Hackathon notes:** ROS1 (Melodic/Noetic) only; run on the GVINS dataset bags. Porting to ROS 2 is non-trivial.

## Deep dives

- [gvins](../../docs/dataset-cards/gvins.md) (dataset-cards)

**Concepts:** [GNSS/INS integration](../concepts/gnss-ins.md), [Visual(-inertial) odometry](../concepts/vio.md), [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [GNSS positioning](../concepts/gnss.md)

**Tags:** `vins`, `raw-gnss`, `factor-graph`, `ros1`

**Domains:** air, ground

## Related

- evaluated_on: [GVINS dataset](../repos/hkust-aerial-robotics__gvins-dataset.md)
- extends: [VINS-Fusion](../repos/hkust-aerial-robotics__vins-fusion.md)
- alternative_to: [IC-GVINS](../repos/i2nav-whu__ic-gvins.md)

## Referenced by

- [gnss_comm](../repos/hkust-aerial-robotics__gnss_comm.md) (same_org)
- [GVINS dataset](../repos/hkust-aerial-robotics__gvins-dataset.md) (evaluated_on)

_Indexed by lane(s): gap-fill_

_GitHub metadata fetched 2026-11-06._
