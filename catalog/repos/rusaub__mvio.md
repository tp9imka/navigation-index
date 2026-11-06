# MVIO - monocular visual-inertial odometry in C++

`repo:rusaub/mvio` - <https://github.com/RusaUB/mvio>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 37 | C++ | ? | 2026-08-27 | False | research-prototype | medium |

C++ monocular VIO: ORB features tracked with Lucas-Kanade flow, parallax-based keyframes, essential-matrix initialisation then PnP, IMU preintegration, least-squares scale and gravity estimation, and a 15-state error-state Kalman filter. Built on OpenCV 4.6 and Eigen 3.4. Companion to a Russian Habr article.

**Why it matters:** A small, readable VIO you can actually step through, unlike the large research systems.

**Hackathon notes:** CMake build; configs in configs/. Calibrate your own camera (camera.yaml) as the article insists. No accuracy numbers are published.

## Deep dives

- [ua-ru-sources-overview](../../docs/landscape/ua-ru-sources-overview.md) (landscape)

**Concepts:** [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md)

**Tags:** `lang:ru`, `vio`, `eskf`, `imu-preintegration`, `opencv`, `eigen`, `raspberry-pi`

**Domains:** air

## Related

- alternative_to: [VINS-Mono](../../catalog/repos/hkust-aerial-robotics__vins-mono.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Ukrainian- and Russian-language sources: what they add](../../docs/landscape/ua-ru-sources-overview.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Visual-Odometry-VIO- (VO + IMU EKF)](../../catalog/repos/daudalbogachiev925__visual-odometry-vio-.md) (alternative_to)
- [Cистема визуально-инерциальной навигации для дрона на C++](../../catalog/resources/habr-kodoka-mvio-cpp-2026.md) (has_code)

_Indexed by lane(s): ua-ru-round2_

_GitHub metadata fetched 2026-11-06._
