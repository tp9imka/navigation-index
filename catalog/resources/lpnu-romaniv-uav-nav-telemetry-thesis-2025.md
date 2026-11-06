# Програмна реалізація алгоритмів навігації БПЛА із використанням систем обробки телеметрії

`res:lpnu-romaniv-uav-nav-telemetry-thesis-2025` - report - <https://ena.lpnu.ua/handle/ntb/124079>

**By:** V. Romaniv (Lviv Polytechnic) - **Year:** 2025 - **Level:** intermediate - **Access:** open

English: 'Software implementation of UAV navigation algorithms using telemetry processing systems'. Master's thesis that fuses GPS, IMU, barometer and optical-camera telemetry with an EKF, a complementary filter and ML-based correction, then tests three scenarios: EKF vs IMU-only, GPS+IMU+barometer fusion, and map-matching with trajectory correction under simulated GPS jamming. Implemented in Python with NumPy, OpenCV and Matplotlib.

## Key takeaways

- Includes a simulated-jamming experiment measuring recovery after GPS loss
- Compares EKF and complementary filter on the same telemetry
- Student work; results are self-reported

## Deep dives

- [ua-ru-sources-overview](../../docs/landscape/ua-ru-sources-overview.md) (landscape)

**Concepts:** [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [GNSS/INS integration](../../catalog/concepts/gnss-ins.md), [Jamming and spoofing](../../catalog/concepts/gnss-interference.md)

**Tags:** `lang:uk`, `thesis`, `lviv-polytechnic`, `ekf`, `python`

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Ukrainian- and Russian-language sources: what they add](../../docs/landscape/ua-ru-sources-overview.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)

_Indexed by lane(s): ua-ru-round2_
