# The invariant extended Kalman filter as a stable observer

`res:barrau-bonnabel-invariant-ekf` - paper - <https://arxiv.org/abs/1410.1465>

**By:** Axel Barrau, Silvère Bonnabel - **Year:** 2014 - **Level:** advanced - **Access:** open

Foundational paper showing that for group-affine systems the invariant EKF has error dynamics independent of the trajectory, giving stability guarantees standard EKFs lack.

## Key takeaways

- Error defined on the Lie group, not in vector space
- Better consistency under large initial errors

**Concepts:** [Inertial navigation (INS/IMU)](../concepts/ins.md), [Sensor fusion and state estimation](../concepts/sensor-fusion.md)

**Tags:** `inekf`, `observer`, `lie-group`

## Related

- explains: [invariant-ekf (Hartley InEKF)](../repos/rosshartley__invariant-ekf.md)
- explains: [DRIFT](../repos/umich-curly__drift.md)

## Referenced by

- [Contact-Aided Invariant Extended Kalman Filtering for Robot State Estimation](../resources/hartley-contact-aided-inekf.md) (cites)

_Indexed by lane(s): ins-fusion_
