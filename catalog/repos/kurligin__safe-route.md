# safe-route (KosmoHackathon 2026)

`repo:kurligin/safe-route` - <https://github.com/Kurligin/safe-route>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 0 | Python | ? | 2026-10-26 | False | research-prototype | medium |

Controller for an autonomous ground cargo platform in the amr-sim simulator plus an operator workstation, built for the 'Безопасный маршрут' case of KosmoHackathon 2026 (2nd place in the final). A Kalman filter fuses wheel odometry, gyro and lidar-to-wall-map matching to keep position in GNSS shadow, and speed is set from a 3 s pedestrian motion forecast.

**Why it matters:** Worked example of GNSS-shadow ground navigation with a scored simulator benchmark, written in Russian.

**Hackathon notes:** README reports position error and collision results against the organisers' baseline (their numbers, not verified here). Depends on the organisers' amr-sim, which may not be public.

## Deep dives

- [ua-ru-sources-overview](../../docs/landscape/ua-ru-sources-overview.md) (landscape)

**Concepts:** [Ground vehicle autonomy](../../catalog/concepts/ground-vehicle-nav.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [LiDAR odometry and SLAM](../../catalog/concepts/lidar-slam.md), [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md)

**Tags:** `lang:ru`, `amr`, `kalman`, `lidar`, `hackathon`, `fastapi`, `react`

**Domains:** ground

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Ukrainian- and Russian-language sources: what they add](../../docs/landscape/ua-ru-sources-overview.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)

_Indexed by lane(s): ua-ru-sources_

_GitHub metadata fetched 2026-11-06._
