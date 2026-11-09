# Learned Inertial Odometry for Autonomous Drone Racing

`res:cioffi-2023-imo-learned-inertial-odometry-racing` - paper - <https://arxiv.org/abs/2210.15287>

**By:** Giovanni Cioffi, Leonard Bauersfeld, Elia Kaufmann, Davide Scaramuzza - **Year:** 2023 - **Level:** advanced - **Access:** open

RA-L 2023. IMU-Model Odometry (IMO): an EKF driven by IMU is updated with relative displacements predicted by a temporal convolutional network that also sees thrust (collective rotor) inputs.

## Key takeaways

- Thrust input is what separates it from pedestrian-style learned IO
- Claims better pose than filter- and optimization-based VIO on a racing drone (no number checked here)
- Code is GPL-3.0

**Concepts:** [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md)

**Tags:** `learned-inertial-odometry`, `thrust`, `drone-racing`, `tcn`

## Related

- has_code: [Learned Inertial Odometry for Drone Racing](../../catalog/repos/uzh-rpg__learned_inertial_model_odometry.md)

## Referenced by

- [Differentiators scan: what to bring besides satellite matching](../../docs/differentiators-scan.md) (mentions)

_Indexed by lane(s): nav-differentiators_
