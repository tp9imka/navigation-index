# Learning-based Airflow Inertial Odometry for MAVs using Thermal Anemometers in a GPS and vision denied environment

`res:wang-2025-airflow-inertial-odometry-anemometers` - paper - <https://arxiv.org/abs/2505.15044>

**By:** Ze Wang, Jingang Qu, Zhenyu Gao, Pascal Morin - **Year:** 2025 - **Level:** advanced - **Access:** open

arXiv preprint (May 2025, no venue listed). Fuses thermal anemometer, IMU, ESC and barometer data with a learned speed estimator for multirotor dead reckoning without GPS or vision.

## Key takeaways

- Abstract: 5.7 m position drift over a 203 s manual flight, indoors and wind-free
- ESC data used as an input, i.e. propulsion as a sensor
- Wind-free test, so real-world wind sensitivity is open

**Concepts:** [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `airflow`, `anemometer`, `esc`, `dead-reckoning`

## Related

- has_code: [Flight Speed Estimation Airflow](../../catalog/repos/syroco-isir__flight-speed-estimation-airflow.md)

## Referenced by

- [Differentiators scan: what to bring besides satellite matching](../../docs/differentiators-scan.md) (mentions)

_Indexed by lane(s): nav-differentiators_
