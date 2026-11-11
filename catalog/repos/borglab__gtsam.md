# GTSAM

`repo:borglab/gtsam` - <https://github.com/borglab/gtsam>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 3,780 | Jupyter Notebook | NOASSERTION | 2026-11-08 | False | production | high |

Georgia Tech factor-graph library for smoothing and mapping, with incremental solvers (iSAM2) and a full IMU preintegration factor set. Ships Python bindings and navigation examples combining IMU with GPS-style measurements.

**Why it matters:** The default backbone for building a custom GNSS/INS or multi-sensor navigation estimator where you add or drop sensor factors as GNSS degrades.

**Build notes:** pip install gtsam gives Python bindings; start from the ImuFactor examples and add a GNSS position factor. Noise model tuning is where time goes.

## Deep dives

- [_index-gnss-fusion-gis](../../docs/integration-cards/_index-gnss-fusion-gis.md) (integration-cards)
- [borglab__gtsam](../../docs/integration-cards/borglab__gtsam.md) (integration-cards)
- [dellaert-kaess-factor-graphs-robot-perception](../../docs/paper-digests/dellaert-kaess-factor-graphs-robot-perception.md) (paper-digests)
- [forster-imu-preintegration](../../docs/paper-digests/forster-imu-preintegration.md) (paper-digests)
- [kaess-isam2](../../docs/paper-digests/kaess-isam2.md) (paper-digests)

**Concepts:** [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md), [GNSS/INS integration](../../catalog/concepts/gnss-ins.md), [Visual SLAM](../../catalog/concepts/visual-slam.md)

**Tags:** `factor-graph`, `isam2`, `imu-preintegration`, `python`

**Domains:** multi

## Related

- alternative_to: [Ceres Solver](../../catalog/repos/ceres-solver__ceres-solver.md)
- alternative_to: [g2o](../../catalog/repos/rainerkuemmerle__g2o.md)
- depends_on: [LIO-SAM](../../catalog/repos/tixiaoshan__lio-sam.md)
- same_org: [GTSfM](../../catalog/repos/borglab__gtsfm.md)

## Referenced by

- [Competition playbook: navigation and PNT under GNSS denial](../../docs/competition-playbook.md) (mentions)
- [Differentiators scan: what to bring besides satellite matching](../../docs/differentiators-scan.md) (mentions)
- [The first three hours](../../docs/first-three-hours.md) (mentions)
- [Integration cards](../../docs/integration-cards/README.md) (mentions)
- [Integrity monitoring for navigation and alt-PNT](../../docs/integrity-monitoring.md) (mentions)
- [Paper digests](../../docs/paper-digests/README.md) (mentions)
- [3. Inertial navigation and sensor fusion](../../docs/primer/03-inertial-and-fusion.md) (mentions)
- [Brief decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [GTSfM](../../catalog/repos/borglab__gtsfm.md) (depends_on)
- [Ceres Solver](../../catalog/repos/ceres-solver__ceres-solver.md) (alternative_to)
- [OB_GINS](../../catalog/repos/i2nav-whu__ob_gins.md) (alternative_to)
- [Kimera-RPGO](../../catalog/repos/mit-spark__kimera-rpgo.md) (depends_on)
- [Kimera-VIO](../../catalog/repos/mit-spark__kimera-vio.md) (depends_on)
- [g2o](../../catalog/repos/rainerkuemmerle__g2o.md) (alternative_to)
- [gnssFGO](../../catalog/repos/rwth-irt__gnssfgo.md) (depends_on)
- [SymForce](../../catalog/repos/symforce-org__symforce.md) (alternative_to)
- [gtsam_gnss](../../catalog/repos/taroz__gtsam_gnss.md) (depends_on)
- [LIO-SAM](../../catalog/repos/tixiaoshan__lio-sam.md) (depends_on)
- [libRSF](../../catalog/repos/tuc-proaut__librsf.md) (alternative_to)
- [Factor Graphs for Robot Perception](../../catalog/resources/dellaert-kaess-factor-graphs-robot-perception.md) (has_code)
- [On-Manifold Preintegration for Real-Time Visual-Inertial Odometry](../../catalog/resources/forster-imu-preintegration.md) (has_code)
- [Factor Graphs and GTSAM: A Hands-on Introduction](../../catalog/resources/gtsam-intro-tutorial.md) (explains)
- [Factor Graphs and GTSAM: A Hands-on Introduction](../../catalog/resources/gtsam-intro-tutorial.md) (has_code)
- [iSAM2: Incremental Smoothing and Mapping Using the Bayes Tree](../../catalog/resources/kaess-isam2.md) (has_code)
- [Shield AI Hivemind autonomy stack](../../catalog/resources/shield-ai-hivemind.md) (alternative_to)
- [SLAM Handbook: From Localization and Mapping to Spatial Intelligence](../../catalog/resources/slam-handbook.md) (explains)
- [SLAM Handbook: From Localization and Mapping to Spatial Intelligence](../../catalog/resources/slam-handbook.md) (uses)
- [Graduated Non-Convexity for Robust Spatial Perception: From Non-Minimal Solvers to Global Outlier Rejection](../../catalog/resources/yang-2020-graduated-non-convexity.md) (has_code)
- [Integrity monitoring for alt-PNT: solution-separation FDE, protection levels and a Stanford diagram](../../catalog/samples/altpnt-integrity.md) (explains)
- [GNSS/INS EKF through a GNSS outage and a spoofing walk-off](../../catalog/samples/gnss-ins-ekf-outage.md) (explains)

_Indexed by lane(s): ins-fusion_

_GitHub metadata fetched 2026-11-09._
