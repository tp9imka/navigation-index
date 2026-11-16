# g2o

`repo:rainerkuemmerle/g2o` - <https://github.com/RainerKuemmerle/g2o>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 3,480 | C++ | ? | 2026-11-15 | False | production | medium |

General framework for graph optimization, widely used for pose-graph SLAM back ends.

**Why it matters:** Lightweight pose-graph back end when you need loop closure or map alignment on top of an inertial front end.

**Build notes:** Best for pose graphs; IMU factors are less turnkey than in GTSAM.

**Concepts:** [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Visual SLAM](../../catalog/concepts/visual-slam.md)

**Tags:** `pose-graph`, `graph-optimization`

**Domains:** multi

## Related

- alternative_to: [GTSAM](../../catalog/repos/borglab__gtsam.md)
- alternative_to: [Ceres Solver](../../catalog/repos/ceres-solver__ceres-solver.md)

## Referenced by

- [ROAMFREE](../../catalog/repos/airlab-polimi__roamfree.md) (depends_on)
- [GTSAM](../../catalog/repos/borglab__gtsam.md) (alternative_to)

_Indexed by lane(s): ins-fusion_

_GitHub metadata fetched 2026-11-16._
