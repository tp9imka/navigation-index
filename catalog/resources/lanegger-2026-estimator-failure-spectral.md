# When Your State Estimator Has Lost The Plot: Detecting Estimator Failures Via Spectral Analysis

`res:lanegger-2026-estimator-failure-spectral` - paper - <https://arxiv.org/abs/2608.10623>

**By:** Christian Lanegger, Helen Oleynikova, Roland Siegwart, Michael Pantic - **Year:** 2026 - **Level:** advanced - **Access:** open

Preprint (Aug 2026). Sensor-agnostic failure detector that looks at the frequency-domain power of recent velocity estimates (signal power, spectral bandwidth, entropy). Tested on visual-, LiDAR- and radar-inertial odometry from real outdoor flights with labelled failures; detects 51-58% of failures at 60-84% precision.

## Key takeaways

- An estimator-agnostic health flag a planner can read without trusting the covariance
- Recall around half: use as one vote, not the only gate
- Real flight data, not simulation

**Concepts:** [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [LiDAR odometry and SLAM](../../catalog/concepts/lidar-slam.md), [Radar navigation and odometry](../../catalog/concepts/radar-nav.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `integrity`, `failure-detection`, `introspection`, `preprint`

_Indexed by lane(s): close-area-localization_
