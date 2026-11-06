# Extended Kalman Filter (EKF)

`res:ardupilot-ekf-overview` - doc - <https://ardupilot.org/copter/docs/common-apm-navigation-extended-kalman-filter-overview.html>

**By:** ArduPilot Dev Team - **Year:** None - **Level:** intermediate - **Access:** open

Overview of ArduPilot's EKF2/EKF3 estimators: states, sensor inputs, innovation checks, lane switching across multiple IMUs and tuning guidance.

## Key takeaways

- Multiple EKF cores run per IMU with automatic lane switching
- Innovation gates reject inconsistent sensor data

**Concepts:** [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md), [GNSS/INS integration](../../catalog/concepts/gnss-ins.md)

**Tags:** `ekf3`, `ekf2`, `estimator`

## Related

- explains: [ArduPilot](../../catalog/repos/ardupilot__ardupilot.md)

## Referenced by

- [1. PNT fundamentals](../../docs/primer/01-pnt-fundamentals.md) (mentions)
- [3. Inertial navigation and sensor fusion](../../docs/primer/03-inertial-and-fusion.md) (mentions)
- [6. Autopilots and C2](../../docs/primer/06-autopilots-and-c2.md) (mentions)

_Indexed by lane(s): autopilots_
