# KF-GINS

`repo:i2nav-whu/kf-gins` - <https://github.com/i2Nav-WHU/KF-GINS>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,222 | C++ | GPL-3.0 | 2026-06-10 | False | active-research | high |

Wuhan University i2Nav reference implementation of loosely coupled GNSS/INS integration with an error-state EKF, with sample data and documentation.

**Why it matters:** Clean, readable GNSS/INS baseline in the PSINS/Groves tradition; ideal to adapt for GNSS-outage experiments.

**Hackathon notes:** Builds with CMake and Eigen; includes demo dataset. Simulate outages by masking GNSS epochs and watch drift.

## Deep dives

- [_index-gnss-fusion-gis](../../docs/integration-cards/_index-gnss-fusion-gis.md) (integration-cards)
- [i2nav-whu__kf-gins](../../docs/integration-cards/i2nav-whu__kf-gins.md) (integration-cards)

**Concepts:** [GNSS/INS integration](../concepts/gnss-ins.md), [Inertial navigation (INS/IMU)](../concepts/ins.md), [Sensor fusion and state estimation](../concepts/sensor-fusion.md)

**Tags:** `ekf`, `loosely-coupled`, `i2nav`

**Domains:** ground, multi

## Related

- same_org: [OB_GINS](../repos/i2nav-whu__ob_gins.md)
- alternative_to: [NaveGo](../repos/rodralez__navego.md)

## Referenced by

- [OB_GINS](../repos/i2nav-whu__ob_gins.md) (same_org)
- [NaveGo](../repos/rodralez__navego.md) (alternative_to)
- [Advanced Navigation Boreas FOG INS with LVS laser velocity sensor](../resources/advanced-navigation-boreas.md) (alternative_to)
- [Principles of GNSS, Inertial, and Multisensor Integrated Navigation Systems, Second Edition](../resources/groves-pnt-book-2e.md) (explains)
- [Honeywell HGuide o480 single-card INS and HGuide i700 IMU](../resources/honeywell-hguide-o480.md) (alternative_to)
- [SBG Systems Ellipse INS - 2025 GNSS-denied firmware](../resources/sbg-new-ellipse-firmware.md) (alternative_to)
- [VectorNav - Iridium STL-aided INS collaboration with NAL Research](../resources/vectornav-stl-aided-ins.md) (alternative_to)
- [GNSS/INS EKF through a GNSS outage and a spoofing walk-off](../samples/gnss-ins-ekf-outage.md) (explains)

_Indexed by lane(s): ins-fusion_

_GitHub metadata fetched 2026-11-06._
