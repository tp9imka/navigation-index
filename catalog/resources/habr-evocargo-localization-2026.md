# Локализовать нельзя ошибиться. Как работает локализация в автономном транспорте и почему это - самая сложная задача. 2/2

`res:habr-evocargo-localization-2026` - blog - <https://habr.com/ru/companies/evocargo_it/articles/1048670/>

**By:** Evocargo - **Year:** 2026 - **Level:** intermediate - **Access:** open

English: 'How localization works in autonomous transport and why it is the hardest task, part 2/2' (June 2026). Evocargo, a Russian autonomous-truck company, walks through GNSS/RTK, cameras against HD maps, lidar scan-to-map matching, IMU (bias growth example), wheel odometry and auxiliary RF sources, fused with Kalman or particle filters plus integrity monitoring and spoofing detection. Lists failure modes such as snow, featureless yards, tunnels and truck jammers near toll sites, and argues localization cannot be bought off the shelf.

## Key takeaways

- Localization is interpretation of conflicting data, not measurement
- Truck-mounted jammers near toll sites are a real ground GNSS threat
- Autoware, Apollo and robot_localization need heavy adaptation

## Deep dives

- [ua-ru-sources-overview](../../docs/landscape/ua-ru-sources-overview.md) (landscape)

**Concepts:** [Ground vehicle autonomy](../../catalog/concepts/ground-vehicle-nav.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [LiDAR odometry and SLAM](../../catalog/concepts/lidar-slam.md), [Jamming and spoofing](../../catalog/concepts/gnss-interference.md)

**Tags:** `lang:ru`, `habr`, `autonomous-trucks`, `integrity`, `hd-map`

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Ukrainian- and Russian-language sources: what they add](../../docs/landscape/ua-ru-sources-overview.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)

_Indexed by lane(s): ua-ru-round2_
