# On-Manifold Preintegration for Real-Time Visual-Inertial Odometry

`res:forster-imu-preintegration` - paper - <https://arxiv.org/abs/1512.02363>

**By:** Christian Forster, Luca Carlone, Frank Dellaert, Davide Scaramuzza - **Year:** 2015 - **Level:** advanced - **Access:** open

Derives IMU preintegration on the SO(3) manifold with bias-correction Jacobians, enabling IMU factors between keyframes in factor-graph optimization.

## Key takeaways

- Summarise many IMU samples into one relative-motion factor
- First-order bias correction avoids re-integration

## Deep dives

- [forster-imu-preintegration](../../docs/paper-digests/forster-imu-preintegration.md) (paper-digests)

**Concepts:** [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md), [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `imu-preintegration`, `factor-graph`

## Related

- has_code: [GTSAM](../../catalog/repos/borglab__gtsam.md)
- uses: [OB_GINS](../../catalog/repos/i2nav-whu__ob_gins.md)

## Referenced by

- [Learning paths](../../docs/learning-paths.md) (mentions)
- [3. Inertial navigation and sensor fusion](../../docs/primer/03-inertial-and-fusion.md) (mentions)

_Indexed by lane(s): ins-fusion_
