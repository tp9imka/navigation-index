# smfeval

`repo:svendbot/smfeval` - <https://github.com/svendbot/smfeval>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| ? | Python | ? | ? | ? | active-research | medium |

Python tool that scores an odometry estimate together with its reported covariance (NEES, scale gap, coverage, proper scoring rules), plus a pairwise test that flags overconfidence between two filters without ground truth.

**Why it matters:** Direct way to check whether the covariance a VIO or LIO stack publishes can be trusted before a planner or EKF2 consumes it. Ships covariance exporters for FAST-LIO2, Faster-LIO, Point-LIO and I2EKF-LO.

**Hackathon notes:** License Apache-2.0 (gh api), created 2026-05. Depends only on NumPy and SciPy. README example (not run here): FAST-LIO2 on Oxford Spires christ-church-03 gives median NEES 1.04e3 vs calibrated 2.37, about 21x too tight per axis, 90% coverage 0.000. Use it on Day 1 recordings to set an honest covariance inflation before feeding VISION_POSITION_ESTIMATE.

**Concepts:** [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md), [LiDAR odometry and SLAM](../../catalog/concepts/lidar-slam.md)

**Tags:** `nees`, `covariance`, `consistency`, `evaluation`, `python`, `apache-2.0`

**Domains:** multi

## Related

- evaluated_on: [FAST-LIO / FAST-LIO2](../../catalog/repos/hku-mars__fast_lio.md)
- evaluated_on: [Point-LIO](../../catalog/repos/hku-mars__point-lio.md)
- alternative_to: [cnspy trajectory evaluation](../../catalog/repos/aau-cns__cnspy_trajectory_evaluation.md)
- alternative_to: [evo](../../catalog/repos/michaelgrupp__evo.md)

## Referenced by

- [09. Measuring OpenVINS covariance realism (NEES) in under 30 minutes](../../docs/research/close-area-nav/09-vio-nees-feasibility.md) (mentions)
- [You Should Be Properly Scoring Your Odometry](../../catalog/resources/ronning-2026-properly-scoring-odometry.md) (has_code)

_Indexed by lane(s): close-area-localization_
