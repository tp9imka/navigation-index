# FilterPy

`repo:rlabbe/filterpy` - <https://github.com/rlabbe/filterpy>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 3,894 | Python | MIT | 2026-10-27 | False | production | high |

Python library of Kalman filters (linear, extended, unscented, ensemble), smoothers, particle filtering helpers and related estimators.

**Why it matters:** Quick prototyping of filters in notebooks before porting to embedded code.

**Hackathon notes:** pip install filterpy. Not Lie-group aware, so handle attitude error states manually or use navlie/manif for that.

## Deep dives

- [_index-gnss-fusion-gis](../../docs/integration-cards/_index-gnss-fusion-gis.md) (integration-cards)
- [rlabbe__filterpy](../../docs/integration-cards/rlabbe__filterpy.md) (integration-cards)

**Concepts:** [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Tracking and data association](../../catalog/concepts/target-tracking.md)

**Tags:** `kalman-filter`, `ukf`, `ekf`, `python`

**Domains:** multi

## Related

- same_org: [Kalman and Bayesian Filters in Python (book)](../../catalog/repos/rlabbe__kalman-and-bayesian-filters-in-python.md)
- alternative_to: [navlie](../../catalog/repos/decargroup__navlie.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Integrity monitoring for navigation and alt-PNT](../../docs/integrity-monitoring.md) (mentions)
- [Learning paths](../../docs/learning-paths.md) (mentions)
- [3. Inertial navigation and sensor fusion](../../docs/primer/03-inertial-and-fusion.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [navlie](../../catalog/repos/decargroup__navlie.md) (alternative_to)
- [Kalman and Bayesian Filters in Python (book)](../../catalog/repos/rlabbe__kalman-and-bayesian-filters-in-python.md) (depends_on)
- [sfwa UKF](../../catalog/repos/sfwa__ukf.md) (alternative_to)
- [Kalman and Bayesian Filters in Python](../../catalog/resources/labbe-kalman-bayesian-filters-python.md) (has_code)
- [Integrity monitoring for alt-PNT: solution-separation FDE, protection levels and a Stanford diagram](../../catalog/samples/altpnt-integrity.md) (explains)
- [GNSS/INS EKF through a GNSS outage and a spoofing walk-off](../../catalog/samples/gnss-ins-ekf-outage.md) (uses)

_Indexed by lane(s): ins-fusion_

_GitHub metadata fetched 2026-11-06._
