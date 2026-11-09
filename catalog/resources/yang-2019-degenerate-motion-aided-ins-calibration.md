# Degenerate Motion Analysis for Aided INS with Online Spatial and Temporal Sensor Calibration

`res:yang-2019-degenerate-motion-aided-ins-calibration` - paper - <https://udel.edu/~pgeneva/downloads/papers/r05.pdf>

**By:** Yulin Yang, Patrick Geneva, Kevin Eckenhoff, Guoquan Huang - **Year:** 2019 - **Level:** advanced - **Access:** open

IEEE RA-L 2019; the linked file is the RPNG tech report (RPNG-2018-CALIB). Shows spatial and temporal calibration of any-source-aided INS is observable under general motion and identifies four degenerate motion primitives (pure translation, one-axis rotation, constant local angular and linear velocity, constant local angular velocity with constant global acceleration) that make calibration partially fail, even with global pose measurements.

## Key takeaways

- Named degenerate motions are the analogue of steady flight for aero parameters
- Recommends avoiding degenerate motions; does not gate the online calibration update

**Concepts:** [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md), [Sensor calibration](../../catalog/concepts/calibration.md), [Visual(-inertial) odometry](../../catalog/concepts/vio.md)

**Tags:** `degenerate-motion`, `observability`, `online-calibration`, `msckf`

_Indexed by lane(s): innovation-pa-aero-adaptation_
