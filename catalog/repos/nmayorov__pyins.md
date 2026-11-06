# pyins

`repo:nmayorov/pyins` - <https://github.com/nmayorov/pyins>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 109 | Python | MIT | 2026-05-26 | False | active-research | high |

Python package for modelling and analysing inertial navigation systems: strapdown integration, error models, Kalman-filter aiding and sensor simulation.

**Why it matters:** Pure-Python INS/GNSS playground for quick outage and sensor-grade studies.

**Hackathon notes:** pip install python-ins (the PyPI name; import as pyins), pure Python with numba; docs on readthedocs. Good for scripted what-if plots (tactical vs MEMS IMU drift).

## Deep dives

- [_index-round5-nav](../../docs/integration-cards/_index-round5-nav.md) (integration-cards)
- [nmayorov__pyins](../../docs/integration-cards/nmayorov__pyins.md) (integration-cards)

**Concepts:** [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md), [GNSS/INS integration](../../catalog/concepts/gnss-ins.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md)

**Tags:** `strapdown`, `python`, `error-model`

**Domains:** multi

## Related

- alternative_to: [gnss-ins-sim](../../catalog/repos/aceinna__gnss-ins-sim.md)
- same_org: [allan-variance (Python)](../../catalog/repos/nmayorov__allan-variance.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [3. Inertial navigation and sensor fusion](../../docs/primer/03-inertial-and-fusion.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [gnss-ins-sim](../../catalog/repos/aceinna__gnss-ins-sim.md) (alternative_to)
- [strapdown-rs](../../catalog/repos/jbrodovsky__strapdown-rs.md) (alternative_to)
- [allan-variance (Python)](../../catalog/repos/nmayorov__allan-variance.md) (same_org)
- [Advanced Navigation Boreas FOG INS with LVS laser velocity sensor](../../catalog/resources/advanced-navigation-boreas.md) (alternative_to)
- [Honeywell HGuide o480 single-card INS and HGuide i700 IMU](../../catalog/resources/honeywell-hguide-o480.md) (alternative_to)
- [SBG Systems Ellipse INS - 2025 GNSS-denied firmware](../../catalog/resources/sbg-new-ellipse-firmware.md) (alternative_to)
- [Strapdown Inertial Navigation Technology, 2nd Edition](../../catalog/resources/titterton-weston-strapdown-ins-2e.md) (explains)
- [VectorNav - Iridium STL-aided INS collaboration with NAL Research](../../catalog/resources/vectornav-stl-aided-ins.md) (alternative_to)

_Indexed by lane(s): ins-fusion_

_GitHub metadata fetched 2026-11-06._
