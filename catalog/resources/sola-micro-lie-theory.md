# A micro Lie theory for state estimation in robotics

`res:sola-micro-lie-theory` - paper - <https://arxiv.org/abs/1812.01537>

**By:** Joan Solà, Jeremie Deray, Dinesh Atchuthan - **Year:** 2018 - **Level:** intermediate - **Access:** open

Tutorial paper giving just enough Lie theory (groups, exponential map, adjoint, Jacobians, uncertainty on manifolds) to write correct estimators for 3D pose; it is the basis of Solà's 'Lie theory for the roboticist' course and the manif library.

## Key takeaways

- Unified plus/minus notation for manifold states
- Ready-to-use Jacobians for SO(3), SE(3) and others
- Ready-to-use Jacobians for SO(3)/SE(3)
- Fixes the most common EKF-on-rotations mistakes

**Concepts:** [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [Inertial navigation (INS/IMU)](../concepts/ins.md), [Visual(-inertial) odometry](../concepts/vio.md)

**Tags:** `lie-group`, `jacobians`, `lie-groups`, `sola`, `manifolds`

## Related

- has_code: [manif](../repos/artivis__manif.md)
- same_author: [Quaternion kinematics for the error-state Kalman filter](../resources/sola-quaternion-eskf.md)

## Referenced by

- [Quaternion kinematics for the error-state Kalman filter](../resources/sola-quaternion-eskf.md) (same_author)
- [SLAM toolbox for Matlab (EKF-SLAM teaching code)](../resources/sola-slamtb-ekf-slam-toolbox.md) (same_author)

_Indexed by lane(s): ins-fusion, learning_
