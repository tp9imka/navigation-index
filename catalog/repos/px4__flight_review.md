# PX4 Flight Review

`repo:px4/flight_review` - <https://github.com/PX4/flight_review>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 279 | JavaScript | BSD-3-Clause | 2026-10-20 | False | production | medium |

Web app for uploading and plotting PX4 ULog flight logs, including estimator innovations and test ratios.

**Why it matters:** Fast way to judge whether EKF2 is healthy when fusing a new vision or flow source.

**Hackathon notes:** Use the hosted instance or run locally with Docker.

**Concepts:** [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [MAVLink, ground control and C2 links](../concepts/mavlink-gcs.md)

**Tags:** `ulog`, `log-analysis`, `bokeh`

**Domains:** air

## Related

- integrates_with: [PX4 Autopilot](../repos/px4__px4-autopilot.md)
- alternative_to: [UAV Log Viewer](../repos/ardupilot__uavlogviewer.md)

## Referenced by

- [UAV Log Viewer](../repos/ardupilot__uavlogviewer.md) (alternative_to)
- [PX4 Autopilot](../repos/px4__px4-autopilot.md) (integrates_with)
- [Using the ECL EKF (EKF2)](../resources/px4-ekf2-tuning-guide.md) (uses)
- [PX4 SITL GPS denial: inject, measure drift, recover](../samples/px4-sitl-gps-denial.md) (explains)

_Indexed by lane(s): autopilots_

_GitHub metadata fetched 2026-11-06._
