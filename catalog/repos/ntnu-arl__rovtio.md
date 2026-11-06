# ROVTIO

`repo:ntnu-arl/rovtio` - <https://github.com/ntnu-arl/rovtio>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 130 | C++ | NOASSERTION | 2025-09-30 | False | active-research | medium |

Visual-thermal-inertial odometry extending ROVIO to fuse asynchronous thermal and visual images with IMU, switching to whichever camera is informative.

**Why it matters:** Thermal keeps odometry alive in darkness and smoke; NTNU ARL targets subterranean and degraded environments.

**Hackathon notes:** Needs a thermal camera synced to IMU (or their datasets). Thermal calibration targets need a heated pattern.

**Concepts:** [Visual(-inertial) odometry](../concepts/vio.md), [Sensor fusion and state estimation](../concepts/sensor-fusion.md)

**Tags:** `thermal`, `night`, `smoke`, `iekf`

**Domains:** air, ground

## Related

- extends: [ROVIO](../repos/ethz-asl__rovio.md)
- alternative_to: [ETIO](../repos/hitsz-nrsl__etio.md)
- alternative_to: [RRxIO](../repos/christopherdoer__rrxio.md)

## Referenced by

- [RRxIO](../repos/christopherdoer__rrxio.md) (alternative_to)
- [ROVIO](../repos/ethz-asl__rovio.md) (extends)
- [ETIO](../repos/hitsz-nrsl__etio.md) (alternative_to)
- [MIMOSA](../repos/ntnu-arl__mimosa.md) (same_org)

_Indexed by lane(s): slam_

_GitHub metadata fetched 2026-11-06._
