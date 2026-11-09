# Improved State Estimation in Quadrotor MAVs: A Novel Drift-Free Velocity Estimator

`res:abeywardena-2013-drift-free-velocity-estimator` - paper - <https://arxiv.org/abs/1509.03388>

**By:** Dinuka Abeywardena, Sarath Kodagoda, Gamini Dissanayake, Rohan Munasinghe - **Year:** 2013 - **Level:** intermediate - **Access:** open

IEEE Robotics and Automation Magazine 20(4), 2013. An EKF that uses the blade-flapping drag relation between body-frame acceleration and body-frame velocity to estimate lateral and longitudinal velocity without drift, validated on a commercial quadrotor against Vicon.

## Key takeaways

- Body-frame velocity becomes observable from the accelerometer alone
- Position still drifts with wind and integration
- Short, readable derivation to copy into a filter

**Concepts:** [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `rotor-drag`, `blade-flapping`, `velocity-estimation`

## Referenced by

- [Differentiators scan: what to bring besides satellite matching](../../docs/differentiators-scan.md) (mentions)
- [03. Adapt aerodynamic navigation parameters only when the data make them identifiable](../../docs/research/innovation-prior-art/03-identifiability-gated-aero-adaptation.md) (mentions)
- [Quadrotors and Accelerometers: State Estimation with an Improved Dynamic Model](../../catalog/resources/leishman-2014-quadrotors-accelerometers.md) (cites)

_Indexed by lane(s): nav-differentiators_
