# You Should Be Properly Scoring Your Odometry

`res:ronning-2026-properly-scoring-odometry` - paper - <https://arxiv.org/abs/2609.25900>

**By:** Ola Ronning, Usama Saqib, Andrzej Wasowski - **Year:** 2026 - **Level:** advanced - **Access:** open

Preprint (Sep 2026). Argues odometry should be scored with strictly proper scoring rules over the mean and the reported covariance, not RMSE alone, and adds a pairwise test that detects overconfidence without ground truth. Case study on ground-based LiDAR-inertial odometry finds all four tested filters overconfident, traced to over-crediting LiDAR measurements.

## Key takeaways

- RMSE ignores the covariance a planner would consume
- Four LIO filters were overconfident; worst case 'centimeter certainty with kilometer error'
- Code: smfeval (README example: FAST-LIO2 90% ellipsoid coverage 0.000)

**Concepts:** [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [LiDAR odometry and SLAM](../../catalog/concepts/lidar-slam.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md)

**Tags:** `nees`, `covariance`, `proper-scoring`, `lio`, `preprint`

## Related

- has_code: [smfeval](../../catalog/repos/svendbot__smfeval.md)
- evaluates: [FAST-LIO / FAST-LIO2](../../catalog/repos/hku-mars__fast_lio.md)

_Indexed by lane(s): close-area-localization_
