# Using the ECL EKF (EKF2)

`res:px4-ekf2-tuning-guide` - doc - <https://docs.px4.io/main/en/advanced_config/tuning_the_ecl_ekf.html>

**By:** PX4 Dev Team - **Year:** None - **Level:** intermediate - **Access:** open

PX4 guide to its EKF2 estimator: which sensors it fuses (IMU, GNSS, baro, mag, optical flow, external vision, range), how to configure and tune them, and how to read innovation logs.

## Key takeaways

- Explains which aiding sources are required for position control
- Shows how to read innovations in logs
- How to feed VIO/visual positioning into PX4 instead of GNSS
- Innovation test tuning for spoof/glitch rejection

**Concepts:** [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [GNSS/INS integration](../concepts/gnss-ins.md), [Inertial navigation (INS/IMU)](../concepts/ins.md), [Autopilots and flight control](../concepts/autopilot.md), [Visual(-inertial) odometry](../concepts/vio.md)

**Tags:** `ekf2`, `px4`, `tuning`, `docs`

## Related

- explains: [PX4 Autopilot](../repos/px4__px4-autopilot.md)
- uses: [PX4 Flight Review](../repos/px4__flight_review.md)
- has_code: [PX4 Autopilot](../repos/px4__px4-autopilot.md)
- has_code: [PX4 ECL (Estimation & Control Library)](../repos/px4__px4-ecl.md)

_Indexed by lane(s): autopilots, learning_
