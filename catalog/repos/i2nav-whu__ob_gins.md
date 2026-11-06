# OB_GINS

`repo:i2nav-whu/ob_gins` - <https://github.com/i2Nav-WHU/OB_GINS>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 655 | C++ | GPL-3.0 | 2024-03-27 | False | research-prototype | high |

Optimization-based GNSS/INS integration from Wuhan University i2Nav, using IMU preintegration in a sliding-window factor graph solved with Ceres.

**Why it matters:** Shows the optimization alternative to KF-GINS on the same problem, useful for comparing filter vs smoother under outages.

**Hackathon notes:** Same data formats as KF-GINS, so run both on one dataset for a side-by-side comparison.

## Deep dives

- [_index-round3](../../docs/integration-cards/_index-round3.md) (integration-cards)
- [i2nav-whu__ob_gins](../../docs/integration-cards/i2nav-whu__ob_gins.md) (integration-cards)

**Concepts:** [GNSS/INS integration](../../catalog/concepts/gnss-ins.md), [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `factor-graph`, `imu-preintegration`, `ceres`, `i2nav`

**Domains:** ground, multi

## Related

- same_org: [KF-GINS](../../catalog/repos/i2nav-whu__kf-gins.md)
- depends_on: [Ceres Solver](../../catalog/repos/ceres-solver__ceres-solver.md)
- alternative_to: [GTSAM](../../catalog/repos/borglab__gtsam.md)

## Referenced by

- [3. Inertial navigation and sensor fusion](../../docs/primer/03-inertial-and-fusion.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [Ceres Solver](../../catalog/repos/ceres-solver__ceres-solver.md) (integrates_with)
- [KF-GINS](../../catalog/repos/i2nav-whu__kf-gins.md) (same_org)
- [On-Manifold Preintegration for Real-Time Visual-Inertial Odometry](../../catalog/resources/forster-imu-preintegration.md) (uses)

_Indexed by lane(s): ins-fusion_

_GitHub metadata fetched 2026-11-06._
