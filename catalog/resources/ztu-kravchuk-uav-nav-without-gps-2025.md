# Аналіз методів автономної навігації БПЛА в умовах відсутності GPS-сигналу

`res:ztu-kravchuk-uav-nav-without-gps-2025` - paper - <https://ten.ztu.edu.ua/article/view/334764/323707>

**By:** A. Kravchuk, A. Tkachuk, O. Dobrzhanskyi, Yu. Bohoiavlenska, D. Tkachuk (Zhytomyr Polytechnic) - **Year:** 2025 - **Level:** intro - **Access:** open

English: 'Analysis of autonomous UAV navigation methods in GPS-denied environments' (Technical Engineering, No. 1(95), 2025). Survey comparing optical flow, visual odometry, visual SLAM, IMU, lidar SLAM, radar SLAM, RF (Wi-Fi/UWB/BLE) and multi-sensor fusion on accuracy, latency, compute and power, with a summary table and a power-draw chart for small UAVs. Concludes no single method fits all conditions and names gaps: no unified test methodology, power cost, lack of realistic datasets and integration into flight controllers.

## Key takeaways

- Rule-of-thumb drift figures per method (e.g. optical flow ~5% of distance, VO ~2%, VSLAM <1% with loop closure) are the authors' rough comparisons, not measurements
- Recommends optical flow for small drones' stabilisation, fusion with SLAM for long missions, radar for bad weather, UWB/visual indoors
- Flags the dataset gap for degraded and emergency conditions
- Funded under Horizon Europe WIDE AcrossEU

## Deep dives

- [ua-ru-sources-overview](../../docs/landscape/ua-ru-sources-overview.md) (landscape)

**Concepts:** [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Visual SLAM](../../catalog/concepts/visual-slam.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md)

**Tags:** `lang:uk`, `survey`, `zhytomyr-polytechnic`, `gps-denied`

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Ukrainian- and Russian-language sources: what they add](../../docs/landscape/ua-ru-sources-overview.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)

_Indexed by lane(s): ua-ru-round2_
