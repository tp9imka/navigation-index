# GTSAM

`repo:borglab/gtsam` - <https://github.com/borglab/gtsam>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 3,776 | Jupyter Notebook | NOASSERTION | 2026-11-06 | False | production | high |

Georgia Tech factor-graph library for smoothing and mapping, with incremental solvers (iSAM2) and a full IMU preintegration factor set. Ships Python bindings and navigation examples combining IMU with GPS-style measurements.

**Why it matters:** The default backbone for building a custom GNSS/INS or multi-sensor navigation estimator where you add or drop sensor factors as GNSS degrades.

**Hackathon notes:** pip install gtsam gives Python bindings; start from the ImuFactor examples and add a GNSS position factor. Noise model tuning is where time goes.

## Deep dives

- [_index-gnss-fusion-gis](../../docs/integration-cards/_index-gnss-fusion-gis.md) (integration-cards)
- [borglab__gtsam](../../docs/integration-cards/borglab__gtsam.md) (integration-cards)
- [dellaert-kaess-factor-graphs-robot-perception](../../docs/paper-digests/dellaert-kaess-factor-graphs-robot-perception.md) (paper-digests)
- [forster-imu-preintegration](../../docs/paper-digests/forster-imu-preintegration.md) (paper-digests)
- [kaess-isam2](../../docs/paper-digests/kaess-isam2.md) (paper-digests)

**Concepts:** [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [Inertial navigation (INS/IMU)](../concepts/ins.md), [GNSS/INS integration](../concepts/gnss-ins.md), [Visual SLAM](../concepts/visual-slam.md)

**Tags:** `factor-graph`, `isam2`, `imu-preintegration`, `python`

**Domains:** multi

## Related

- alternative_to: [Ceres Solver](../repos/ceres-solver__ceres-solver.md)
- alternative_to: [g2o](../repos/rainerkuemmerle__g2o.md)
- depends_on: [LIO-SAM](../repos/tixiaoshan__lio-sam.md)
- same_org: [GTSfM](../repos/borglab__gtsfm.md)

## Referenced by

- [GTSfM](../repos/borglab__gtsfm.md) (depends_on)
- [Ceres Solver](../repos/ceres-solver__ceres-solver.md) (alternative_to)
- [OB_GINS](../repos/i2nav-whu__ob_gins.md) (alternative_to)
- [Kimera-RPGO](../repos/mit-spark__kimera-rpgo.md) (depends_on)
- [Kimera-VIO](../repos/mit-spark__kimera-vio.md) (depends_on)
- [g2o](../repos/rainerkuemmerle__g2o.md) (alternative_to)
- [gtsam_gnss](../repos/taroz__gtsam_gnss.md) (depends_on)
- [LIO-SAM](../repos/tixiaoshan__lio-sam.md) (depends_on)
- [Factor Graphs for Robot Perception](../resources/dellaert-kaess-factor-graphs-robot-perception.md) (has_code)
- [On-Manifold Preintegration for Real-Time Visual-Inertial Odometry](../resources/forster-imu-preintegration.md) (has_code)
- [Factor Graphs and GTSAM: A Hands-on Introduction](../resources/gtsam-intro-tutorial.md) (explains)
- [Factor Graphs and GTSAM: A Hands-on Introduction](../resources/gtsam-intro-tutorial.md) (has_code)
- [iSAM2: Incremental Smoothing and Mapping Using the Bayes Tree](../resources/kaess-isam2.md) (has_code)
- [Shield AI Hivemind autonomy stack](../resources/shield-ai-hivemind.md) (alternative_to)
- [SLAM Handbook: From Localization and Mapping to Spatial Intelligence](../resources/slam-handbook.md) (explains)
- [SLAM Handbook: From Localization and Mapping to Spatial Intelligence](../resources/slam-handbook.md) (uses)
- [GNSS/INS EKF through a GNSS outage and a spoofing walk-off](../samples/gnss-ins-ekf-outage.md) (explains)

_Indexed by lane(s): ins-fusion_

_GitHub metadata fetched 2026-11-06._
