# gnss-ins-sim

`repo:aceinna/gnss-ins-sim` - <https://github.com/Aceinna/gnss-ins-sim>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,498 | Python | MIT | 2024-11-27 | False | research-prototype | high |

Python GNSS/INS simulator that generates trajectories, IMU/GNSS/magnetometer measurements with configurable error models, and runs navigation algorithms on them.

**Why it matters:** Quick way to produce synthetic IMU and GNSS data with known truth to test filters and dead reckoning under GNSS outage.

**Hackathon notes:** Pure Python; define a motion profile CSV and sensor grade, then plug your filter in as an algorithm.

## Deep dives

- [_index-gnss-fusion-gis](../../docs/integration-cards/_index-gnss-fusion-gis.md) (integration-cards)
- [aceinna__gnss-ins-sim](../../docs/integration-cards/aceinna__gnss-ins-sim.md) (integration-cards)

**Concepts:** [Simulation and HIL/SITL](../concepts/simulation.md), [Inertial navigation (INS/IMU)](../concepts/ins.md), [GNSS/INS integration](../concepts/gnss-ins.md)

**Tags:** `imu-simulation`, `trajectory`, `python`, `imu`, `gnss`, `simulation`

**Domains:** multi

## Related

- alternative_to: [pyins](../repos/nmayorov__pyins.md)
- alternative_to: [NaveGo](../repos/rodralez__navego.md)

## Referenced by

- [pyins](../repos/nmayorov__pyins.md) (alternative_to)
- [NaveGo](../repos/rodralez__navego.md) (alternative_to)
- [Advanced Navigation Boreas FOG INS with LVS laser velocity sensor](../resources/advanced-navigation-boreas.md) (alternative_to)
- [Honeywell HGuide o480 single-card INS and HGuide i700 IMU](../resources/honeywell-hguide-o480.md) (alternative_to)
- [SBG Systems Ellipse INS - 2025 GNSS-denied firmware](../resources/sbg-new-ellipse-firmware.md) (alternative_to)
- [VectorNav - Iridium STL-aided INS collaboration with NAL Research](../resources/vectornav-stl-aided-ins.md) (alternative_to)
- [GNSS/INS EKF through a GNSS outage and a spoofing walk-off](../samples/gnss-ins-ekf-outage.md) (explains)

_Indexed by lane(s): ins-fusion, sim-data_

_GitHub metadata fetched 2026-11-06._
