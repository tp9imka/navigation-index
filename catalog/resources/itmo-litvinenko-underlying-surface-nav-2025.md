# Разработка метода навигации беспилотных летательных аппаратов по изображению подстилающей поверхности в условиях отсутствия сигналов внешних навигационных систем

`res:itmo-litvinenko-underlying-surface-nav-2025` - paper - <https://kmu.itmo.ru/file/download/application/45885>

**By:** A. I. Litvinenko, M. Yu. Budko (supervisor), ITMO - **Year:** 2025 - **Level:** intro - **Access:** open

English: 'A method for UAV navigation by images of the underlying surface without external navigation signals'. Short ITMO young-scientists congress abstract (file dated January 2025): keypoint detection, FLANN matching and a transformation matrix against a reference map of the underlying surface give the UAV's local position. Tested only in Gazebo, where coordinates were fed to the flight controller and the authors report accuracy to about 2 m.

## Key takeaways

- Classic keypoints + FLANN + homography, not deep features
- Simulation-only result (Gazebo), about 2 m self-reported
- Reviews image-matching families: correlation-extremal, keypoints, neural

## Deep dives

- [ua-ru-sources-overview](../../docs/landscape/ua-ru-sources-overview.md) (landscape)

**Concepts:** [Visual geo-localization (image-to-map)](../../catalog/concepts/visual-geolocalization.md), [Feature detection and matching](../../catalog/concepts/feature-matching.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md)

**Tags:** `lang:ru`, `itmo`, `abstract`, `gazebo`, `flann`

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Ukrainian- and Russian-language sources: what they add](../../docs/landscape/ua-ru-sources-overview.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)

_Indexed by lane(s): ua-ru-round2_
