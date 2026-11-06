# Sample: GNSS/INS EKF through a GNSS outage and a spoofing walk-off

`sample:gnss-ins-ekf-outage` - code and walkthrough in [samples/gnss-ins-ekf-outage](../../samples/gnss-ins-ekf-outage/)

A stdlib-only 2D loosely-coupled GNSS/INS EKF (8 states, hand-written matrix helpers) on a synthetic vehicle with biased, noisy 100 Hz IMU and 1 Hz GNSS. It compares INS-only, EKF, EKF with a chi-square innovation gate, and a gated EKF that latches into holdover through a 60 s outage and a slowly walking spoofed offset. A sweep shows that the gate catches fast walk-offs but misses slow ones.

**Verification:** ran with python3.14.7 stdlib on 2026-11-06 (default run and --sweep), output shown in README. filterpy_crosscheck.py re-ran both with filterpy 2.0.0's ExtendedKalmanFilter doing covariance, innovation and Joseph-form update (Python 3.12.14) and reproduced the tables to the printed 0.1 m; inflating R 100x in the filterpy path changed them, so that path is live. gnss-ins-sim, KF-GINS and GTSAM were not run.

**Concepts:** [GNSS/INS integration](../concepts/gnss-ins.md), [Inertial navigation (INS/IMU)](../concepts/ins.md), [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [Jamming and spoofing](../concepts/gnss-interference.md), [Assured / resilient PNT](../concepts/assured-pnt.md), [Simulation and HIL/SITL](../concepts/simulation.md)

**Tags:** `ekf`, `loosely-coupled`, `innovation-gate`, `chi-square`, `nis`, `gnss-outage`, `spoofing`, `holdover`, `stdlib`

## Related

- explains: [gnss-ins-sim](../repos/aceinna__gnss-ins-sim.md)
- uses: [FilterPy](../repos/rlabbe__filterpy.md)
- explains: [KF-GINS](../repos/i2nav-whu__kf-gins.md)
- explains: [GTSAM](../repos/borglab__gtsam.md)

_Indexed by lane(s): samples_
