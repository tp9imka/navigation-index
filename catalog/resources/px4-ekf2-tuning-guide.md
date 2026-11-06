# Using PX4's Navigation Filter (EKF2)

`res:px4-ekf2-tuning-guide` - doc - <https://docs.px4.io/main/en/advanced_config/tuning_the_ecl_ekf.html>

**By:** PX4 Dev Team - **Year:** None - **Level:** intermediate - **Access:** open

PX4 guide to its EKF2 estimator: which sensors it fuses (IMU, GNSS, baro, mag, optical flow, external vision, range), how to configure and tune them, and how to read innovation logs.

## Key takeaways

- Explains which aiding sources are required for position control
- Shows how to read innovations in logs
- How to feed VIO/visual positioning into PX4 instead of GNSS
- Innovation test tuning for spoof/glitch rejection

**Concepts:** [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [GNSS/INS integration](../../catalog/concepts/gnss-ins.md), [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md), [Autopilots and flight control](../../catalog/concepts/autopilot.md), [Visual(-inertial) odometry](../../catalog/concepts/vio.md)

**Tags:** `ekf2`, `px4`, `tuning`, `docs`

## Related

- explains: [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md)
- uses: [PX4 Flight Review](../../catalog/repos/px4__flight_review.md)
- has_code: [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md)
- has_code: [PX4 ECL (Estimation & Control Library)](../../catalog/repos/px4__px4-ecl.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Learning paths](../../docs/learning-paths.md) (mentions)
- [1. PNT fundamentals](../../docs/primer/01-pnt-fundamentals.md) (mentions)
- [6. Autopilots and C2](../../docs/primer/06-autopilots-and-c2.md) (mentions)

_Indexed by lane(s): autopilots, learning_
