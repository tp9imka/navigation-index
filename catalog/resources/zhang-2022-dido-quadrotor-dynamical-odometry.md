# DIDO: Deep Inertial Quadrotor Dynamical Odometry

`res:zhang-2022-dido-quadrotor-dynamical-odometry` - paper - <https://arxiv.org/abs/2203.03149>

**By:** Kunyi Zhang, Chenxing Jiang, Jinghang Li, Sheng Yang, Teng Ma, Chao Xu, Fei Gao - **Year:** 2022 - **Level:** advanced - **Access:** open

RA-L with IROS 2022 presentation. Uses only onboard inertial and dynamics signals: networks learn IMU bias, a quadrotor dynamics residual and motion state with uncertainty, and a two-stage EKF fuses them.

## Key takeaways

- Physics-plus-learning pattern: model what you can, learn the residual
- Abstract gives no headline number; claims advantage over conventional and learned baselines
- Dataset released in the repo, no license file

**Concepts:** [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `quadrotor-dynamics`, `learned-inertial-odometry`, `ekf`

## Related

- has_code: [DIDO](../../catalog/repos/zhangkunyi__dido.md)

## Referenced by

- [Differentiators scan: what to bring besides satellite matching](../../docs/differentiators-scan.md) (mentions)
- [AI-IO: An Aerodynamics-Inspired Real-Time Inertial Odometry for Quadrotors](../../catalog/resources/cui-2026-ai-io-aerodynamics-inertial-odometry.md) (cites)

_Indexed by lane(s): nav-differentiators_
