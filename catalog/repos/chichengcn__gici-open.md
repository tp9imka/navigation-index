# GICI-LIB

`repo:chichengcn/gici-open` - <https://github.com/chichengcn/gici-open>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 679 | C++ | GPL-3.0 | 2025-01-27 | False | active-research | medium |

GNSS/INS/Camera integrated navigation library supporting a range of GNSS modes (SPP, RTK, PPP and variants) tightly fused with inertial and visual data via factor graph optimization.

**Why it matters:** One of the most complete open tightly coupled GNSS/INS/vision stacks; good for showing positioning robustness in degraded GNSS.

**Hackathon notes:** Large codebase; run on the provided dataset first. Config files are the main interface.

**Concepts:** [GNSS/INS integration](../concepts/gnss-ins.md), [RTK / PPP precise positioning](../concepts/gnss-rtk-ppp.md), [Visual(-inertial) odometry](../concepts/vio.md), [Sensor fusion and state estimation](../concepts/sensor-fusion.md)

**Tags:** `tightly-coupled`, `rtk`, `ppp`, `factor-graph`

**Domains:** ground, multi

## Related

- alternative_to: [IC-GVINS](../repos/i2nav-whu__ic-gvins.md)
- extends: [RTKLIB](../repos/tomojitakasu__rtklib.md)
- alternative_to: [GraphGNSSLib](../repos/weisongwen__graphgnsslib.md)

## Referenced by

- [IC-GVINS](../repos/i2nav-whu__ic-gvins.md) (alternative_to)

_Indexed by lane(s): ins-fusion_

_GitHub metadata fetched 2026-11-06._
