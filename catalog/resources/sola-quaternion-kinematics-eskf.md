# Quaternion kinematics for the error-state Kalman filter

`res:sola-quaternion-kinematics-eskf` - paper - <https://arxiv.org/abs/1711.02508>

**By:** Joan Solà - **Year:** 2017 - **Level:** intermediate - **Access:** open

Long tutorial report covering quaternion conventions, rotation perturbations and their derivatives, and a full derivation of an IMU-driven error-state Kalman filter including the reset step.

## Key takeaways

- Pins down Hamilton vs JPL quaternion conventions
- Step-by-step ESKF prediction, correction and reset
- Global vs local error definitions
- Standard reference for implementing an INS/ESKF
- Covers local vs global perturbation conventions

## Deep dives

- [sola-quaternion-kinematics-eskf](../../docs/paper-digests/sola-quaternion-kinematics-eskf.md) (paper-digests)

**Concepts:** [Inertial navigation (INS/IMU)](../concepts/ins.md), [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [GNSS/INS integration](../concepts/gnss-ins.md)

**Tags:** `eskf`, `quaternion`, `tutorial`, `imu`, `sola`

## Related

- has_code: [ESKF (je310)](../repos/je310__eskf.md)
- same_author: [manif](../repos/artivis__manif.md)
- same_author: [A micro Lie theory for state estimation in robotics](../resources/sola-micro-lie-theory.md)
- same_author: [SLAM Toolbox (MATLAB)](../repos/joansola__slamtb.md)

## Referenced by

- [A micro Lie theory for state estimation in robotics](../resources/sola-micro-lie-theory.md) (same_author)

_Indexed by lane(s): ins-fusion, learning_
