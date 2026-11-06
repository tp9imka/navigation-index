# Extended Kalman Filter (EKF) navigation overview

`res:ardupilot-ekf-overview` - doc - <https://ardupilot.org/copter/docs/common-apm-navigation-extended-kalman-filter-overview.html>

**By:** ArduPilot Dev Team - **Year:** None - **Level:** intermediate - **Access:** open

Overview of ArduPilot's EKF2/EKF3 estimators: states, sensor inputs, innovation checks, lane switching across multiple IMUs and tuning guidance.

## Key takeaways

- Multiple EKF cores run per IMU with automatic lane switching
- Innovation gates reject inconsistent sensor data

**Concepts:** [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [Inertial navigation (INS/IMU)](../concepts/ins.md), [GNSS/INS integration](../concepts/gnss-ins.md)

**Tags:** `ekf3`, `ekf2`, `estimator`

## Related

- explains: [ArduPilot](../repos/ardupilot__ardupilot.md)

_Indexed by lane(s): autopilots_
