# GraphGNSSLib

`repo:weisongwen/graphgnsslib` - <https://github.com/weisongwen/GraphGNSSLib>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 632 | C | ? | 2022-12-29 | False | research-prototype | low |

Open-source GNSS positioning and RTK package using factor graph optimization, built on RTKLIB data handling and ROS.

**Why it matters:** Shows FGO-based GNSS positioning outperforming filters in urban canyons; good research baseline.

**Hackathon notes:** ROS 1 + Ceres; uses RTKLIB internals for observation handling.

**Concepts:** [GNSS positioning](../../catalog/concepts/gnss.md), [RTK / PPP precise positioning](../../catalog/concepts/gnss-rtk-ppp.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `factor-graph`, `rtk`, `ros`, `urban`, `ceres`

**Domains:** ground

## Related

- depends_on: [RTKLIB](../../catalog/repos/tomojitakasu__rtklib.md)
- alternative_to: [gtsam_gnss](../../catalog/repos/taroz__gtsam_gnss.md)
- integrates_with: [GLIO](../../catalog/repos/xikunliu-huskit__glio.md)

## Referenced by

- [GICI-LIB](../../catalog/repos/chichengcn__gici-open.md) (alternative_to)
- [gtsam_gnss](../../catalog/repos/taroz__gtsam_gnss.md) (alternative_to)
- [GLIO](../../catalog/repos/xikunliu-huskit__glio.md) (integrates_with)

_Indexed by lane(s): gnss, ins-fusion_

_GitHub metadata fetched 2026-11-06._
