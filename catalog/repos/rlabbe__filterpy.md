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

**Concepts:** [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [Tracking and data association](../concepts/target-tracking.md)

**Tags:** `kalman-filter`, `ukf`, `ekf`, `python`

**Domains:** multi

## Related

- same_org: [Kalman and Bayesian Filters in Python (book)](../repos/rlabbe__kalman-and-bayesian-filters-in-python.md)
- alternative_to: [navlie](../repos/decargroup__navlie.md)

## Referenced by

- [navlie](../repos/decargroup__navlie.md) (alternative_to)
- [Kalman and Bayesian Filters in Python (book)](../repos/rlabbe__kalman-and-bayesian-filters-in-python.md) (depends_on)
- [sfwa UKF](../repos/sfwa__ukf.md) (alternative_to)
- [Kalman and Bayesian Filters in Python](../resources/labbe-kalman-bayesian-filters-python.md) (has_code)
- [GNSS/INS EKF through a GNSS outage and a spoofing walk-off](../samples/gnss-ins-ekf-outage.md) (explains)

_Indexed by lane(s): ins-fusion_

_GitHub metadata fetched 2026-11-06._
