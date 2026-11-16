# RNIN-VIO

`repo:zju3dv/rnin-vio` - <https://github.com/zju3dv/rnin-vio>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 161 | Python | Apache-2.0 | 2022-04-06 | False | archived | low |

Inertial network from RNIN-VIO (ISMAR 2021) that regresses displacement and uncertainty from IMU windows, meant to keep a VIO alive when vision fails.

**Why it matters:** Shows the learned-inertial-plus-VIO coupling pattern a team would copy when the camera drops out at night or over water.

**Build notes:** Apache-2.0, last push 2022, pedestrian/handheld oriented. Use as a design reference.

**Concepts:** [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md), [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md)

**Tags:** `learned-inertial-odometry`, `vio`, `pytorch`

**Domains:** multi

## Related

- extends: [RoNIN](../../catalog/repos/sachini__ronin.md)

_Indexed by lane(s): nav-differentiators_

_GitHub metadata fetched 2026-11-16._
