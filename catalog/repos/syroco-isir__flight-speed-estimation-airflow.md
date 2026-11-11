# Flight Speed Estimation Airflow

`repo:syroco-isir/flight-speed-estimation-airflow` - <https://github.com/SyRoCo-ISIR/Flight-Speed-Estimation-Airflow>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 0 | Python | MIT | 2022-05-13 | False | research-prototype | low |

GRU network that estimates multirotor flight speed from thermal anemometer readings, linked from the 2025 airflow-inertial odometry preprint.

**Why it matters:** A cheap airflow sensor as a velocity source for multirotors is a rare angle; the preprint reports 5.7 m drift over a 203 s indoor flight.

**Build notes:** MIT license but last push 2022, zero stars, needs custom hardware. Reference only.

**Concepts:** [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md)

**Tags:** `anemometer`, `airflow`, `gru`, `multirotor`

**Domains:** air

## Referenced by

- [Learning-based Airflow Inertial Odometry for MAVs using Thermal Anemometers in a GPS and vision denied environment](../../catalog/resources/wang-2025-airflow-inertial-odometry-anemometers.md) (has_code)

_Indexed by lane(s): nav-differentiators_

_GitHub metadata fetched 2026-11-09._
