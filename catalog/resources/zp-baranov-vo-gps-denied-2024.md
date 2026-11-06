# Метод навігації БПЛА в умовах відсутності GPS-сигналу на основі візуальної одометрії

`res:zp-baranov-vo-gps-denied-2024` - paper - <https://eir.zp.edu.ua/handle/123456789/24160>

**By:** Ye. O. Baranov, N. I. Furmanova, Zaporizhzhia Polytechnic - **Year:** 2024 - **Level:** intermediate - **Access:** open

English: 'UAV navigation method in GPS-denied conditions based on visual odometry'. Short Ukrainian conference paper: ORB features, a modified RANSAC and Kalman refinement for frame-to-frame VO, targeting +/-5 m and 10 Hz. Authors report 4.8 m position error (33% better than their baseline) and 42 ms per frame on a 10,000-frame closed-loop flight set.

## Key takeaways

- Sets a concrete target spec (+/-5 m, +/-2 deg, >=10 Hz) typical of Ukrainian academic work
- Classic ORB + RANSAC + KF pipeline, not learned features
- Results are the authors'; dataset not published

## Deep dives

- [ua-ru-sources-overview](../../docs/landscape/ua-ru-sources-overview.md) (landscape)

**Concepts:** [Visual(-inertial) odometry](../concepts/vio.md), [Feature detection and matching](../concepts/feature-matching.md)

**Tags:** `lang:uk`, `visual-odometry`, `orb`, `ransac`

_Indexed by lane(s): ua-ru-sources_
