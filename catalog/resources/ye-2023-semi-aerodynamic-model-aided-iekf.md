# Semi-Aerodynamic Model Aided Invariant Kalman Filtering for UAV Full-State Estimation

`res:ye-2023-semi-aerodynamic-model-aided-iekf` - paper - <https://arxiv.org/abs/2310.01844>

**By:** Xiaoyu Ye, Fujun Song, Zongyu Zhang, Rui Zhang, Qinghua Zeng - **Year:** 2023 - **Level:** advanced - **Access:** open

arXiv preprint. Fixed-wing full-state estimation in a right-invariant error-state EKF fusing IMU, GNSS, magnetometer, barometer, airspeed and control-surface data; an LSTM predicts angle of attack and sideslip from control deflections so only ground-measurable aero parameters are needed. Estimates wind too.

## Key takeaways

- Abstract: maximum position error stays within 30 m over a 130 s GNSS denial
- Code promised (MATLAB/Simulink) but no repository link found
- Closest recent fixed-wing aerodynamic-model-aided INS

**Concepts:** [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md), [GNSS/INS integration](../../catalog/concepts/gnss-ins.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `fixed-wing`, `aerodynamic-model`, `invariant-ekf`, `wind`

## Related

- cites: [Assessment of VDM-based autonomous navigation of a UAV under operational conditions](../../catalog/resources/khaghani-skaloud-2018-vdm-navigation.md)

## Referenced by

- [Differentiators scan: what to bring besides satellite matching](../../docs/differentiators-scan.md) (mentions)

_Indexed by lane(s): nav-differentiators_
