# ROVTIO

`repo:ntnu-arl/rovtio` - <https://github.com/ntnu-arl/rovtio>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 130 | C++ | NOASSERTION | 2025-09-30 | False | active-research | medium |

Visual-thermal-inertial odometry extending ROVIO to fuse asynchronous thermal and visual images with IMU, switching to whichever camera is informative.

**Why it matters:** Thermal keeps odometry alive in darkness and smoke; NTNU ARL targets subterranean and degraded environments.

**Hackathon notes:** Needs a thermal camera synced to IMU (or their datasets). Thermal calibration targets need a heated pattern.

**Concepts:** [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `thermal`, `night`, `smoke`, `iekf`

**Domains:** air, ground

## Related

- extends: [ROVIO](../../catalog/repos/ethz-asl__rovio.md)
- alternative_to: [ETIO](../../catalog/repos/hitsz-nrsl__etio.md)
- alternative_to: [RRxIO](../../catalog/repos/christopherdoer__rrxio.md)

## Referenced by

- [RRxIO](../../catalog/repos/christopherdoer__rrxio.md) (alternative_to)
- [ROVIO](../../catalog/repos/ethz-asl__rovio.md) (extends)
- [ETIO](../../catalog/repos/hitsz-nrsl__etio.md) (alternative_to)
- [MIMOSA](../../catalog/repos/ntnu-arl__mimosa.md) (same_org)

_Indexed by lane(s): slam_

_GitHub metadata fetched 2026-11-06._
