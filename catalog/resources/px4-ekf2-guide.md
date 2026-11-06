# Using PX4's Navigation Filter (EKF2)

`res:px4-ekf2-guide` - doc - <https://docs.px4.io/main/en/advanced_config/tuning_the_ecl_ekf.html>

**By:** PX4 Dev Team - **Year:** 2025 - **Level:** intermediate - **Access:** open

PX4 guide to its EKF2 estimator: which sensors it fuses (IMU, GNSS, baro, mag, optical flow, external vision, range), how to configure and tune them, and how to read innovation logs.

## Key takeaways

- How to feed VIO/visual positioning into PX4 instead of GNSS
- Innovation test tuning for spoof/glitch rejection

**Concepts:** [Autopilots and flight control](../concepts/autopilot.md), [GNSS/INS integration](../concepts/gnss-ins.md), [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [Visual(-inertial) odometry](../concepts/vio.md)

**Tags:** `px4`, `ekf2`, `docs`

## Related

- has_code: [PX4 Autopilot](../repos/px4__px4-autopilot.md)
- has_code: [PX4 ECL (Estimation & Control Library)](../repos/px4__px4-ecl.md)

_Indexed by lane(s): learning_
