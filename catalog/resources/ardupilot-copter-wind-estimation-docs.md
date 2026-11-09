# Windspeed Estimation and Baro Compensation (ArduCopter)

`res:ardupilot-copter-wind-estimation-docs` - doc - <https://ardupilot.org/copter/docs/airspeed-estimation.html>

**By:** ArduPilot Dev Team - **Year:** 2024 - **Level:** intro - **Access:** open

How to make EKF3 estimate wind on a multicopter without an airspeed sensor by setting ballistic coefficients (EK3_DRAG_BCOEF_X/Y = mass / frontal or side area) and a momentum drag coefficient (EK3_DRAG_MCOEF) from a flight test. Year is approximate; the page carries no date.

## Key takeaways

- EK3_DRAG_MCOEF is normally 0.1-1.0 per the page
- In the EKF3 source (Copter-4.6.3) drag fusion counts as velocity aiding and enables a wind-relative dead-reckoning mode
- SITL multicopter frame model in 4.6.3 includes momentum and bluff-body drag

**Concepts:** [Autopilots and flight control](../../catalog/concepts/autopilot.md), [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md)

**Tags:** `ardupilot`, `ekf3`, `drag-fusion`, `wind`

## Related

- explains: [ArduPilot](../../catalog/repos/ardupilot__ardupilot.md)
- part_of: [Extended Kalman Filter (EKF)](../../catalog/resources/ardupilot-ekf-overview.md)

## Referenced by

- [Differentiators scan: what to bring besides satellite matching](../../docs/differentiators-scan.md) (mentions)
- [Dead Reckoning Failsafe (ArduCopter)](../../catalog/resources/ardupilot-copter-dead-reckoning-failsafe-docs.md) (cites)
- [ArduPilot EKF3 drag fusion and wind-state gating (source, Copter-4.6.3)](../../catalog/resources/ardupilot-ekf3-drag-wind-source-copter-4-6-3.md) (explains)

_Indexed by lane(s): nav-differentiators_
