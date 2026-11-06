# Анализ проблемных направлений автономной навигации беспилотных летательных аппаратов

`res:ipu-mlsd-dolgov-autonomous-nav-problems-2025` - paper - <https://mlsd2025.ipu.ru/proceedings/0784.pdf>

**By:** G. A. Dolgov - **Year:** 2025 - **Level:** intermediate - **Access:** open

English: 'Analysis of problem areas in autonomous UAV navigation' (MLSD-2025 conference, ICS RAS). Reviews GNSS jamming and spoofing threats to small UAVs and three families of countermeasures: neural matching of camera imagery to a geo-referenced map or terrain model, lidar or stereo SLAM combined with neural models, and other options such as radar methods and RSSI trilateration from relay UAVs. Notes the common practical stack of ArduPilot or INAV plus a companion computer and lists observed problems, such as the volume of map tiles to store onboard and the cost and weight of 3D lidars.

## Key takeaways

- Map-tile storage on board is a real constraint for VPS
- Relay-UAV RSSI trilateration is mentioned as an emerging option
- Author affiliation is a Russian defence test centre; content is navigation-only

## Deep dives

- [ua-ru-sources-overview](../../docs/landscape/ua-ru-sources-overview.md) (landscape)

**Concepts:** [Visual geo-localization (image-to-map)](../../catalog/concepts/visual-geolocalization.md), [LiDAR odometry and SLAM](../../catalog/concepts/lidar-slam.md), [Jamming and spoofing](../../catalog/concepts/gnss-interference.md), [RF localization and direction finding](../../catalog/concepts/rf-localization.md)

**Tags:** `lang:ru`, `survey`, `ipu-ras`, `ardupilot`, `inav`

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Ukrainian- and Russian-language sources: what they add](../../docs/landscape/ua-ru-sources-overview.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)

_Indexed by lane(s): ua-ru-round2_
