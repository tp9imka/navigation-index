# Sample: GNSS/INS EKF through a GNSS outage and a spoofing walk-off

`sample:gnss-ins-ekf-outage` - code and walkthrough in [samples/gnss-ins-ekf-outage](../../samples/gnss-ins-ekf-outage/)

A stdlib-only 2D loosely-coupled GNSS/INS EKF (8 states, hand-written matrix helpers) on a synthetic vehicle with biased, noisy 100 Hz IMU and 1 Hz GNSS. It compares INS-only, EKF, EKF with a chi-square innovation gate, and a gated EKF that latches into holdover through a 60 s outage and a slowly walking spoofed offset. A sweep shows that the gate catches fast walk-offs but misses slow ones.

**Verification:** ran with python3.14.7 stdlib on 2026-11-06 (default run and --sweep), output shown in README. filterpy_crosscheck.py re-ran both with filterpy 2.0.0's ExtendedKalmanFilter doing covariance, innovation and Joseph-form update (Python 3.12.14) and reproduced the tables to the printed 0.1 m; inflating R 100x in the filterpy path changed them, so that path is live. gnss-ins-sim, KF-GINS and GTSAM were not run.

## Practical readiness

| Compute | Hardware | Offline | Setup | Dataset download | Tested platforms | Validation |
|---|---|---|---|---|---|---|
| cpu | none | unknown | unknown | 0 MB | unknown | integrated |

**Main limitation:** Fully synthetic two-dimensional sensors; the innovation gate misses slow drags up to 0.5 m/s.

**Readiness evidence:** [samples/gnss-ins-ekf-outage/README.md](../../samples/gnss-ins-ekf-outage/README.md), [samples/gnss-ins-ekf-outage/sample.json](../../samples/gnss-ins-ekf-outage/sample.json)

**Concepts:** [GNSS/INS integration](../../catalog/concepts/gnss-ins.md), [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Jamming and spoofing](../../catalog/concepts/gnss-interference.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md)

**Tags:** `ekf`, `loosely-coupled`, `innovation-gate`, `chi-square`, `nis`, `gnss-outage`, `spoofing`, `holdover`, `stdlib`

## Related

- explains: [gnss-ins-sim](../../catalog/repos/aceinna__gnss-ins-sim.md)
- uses: [FilterPy](../../catalog/repos/rlabbe__filterpy.md)
- explains: [KF-GINS](../../catalog/repos/i2nav-whu__kf-gins.md)
- explains: [GTSAM](../../catalog/repos/borglab__gtsam.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Integrity monitoring for navigation and alt-PNT](../../docs/integrity-monitoring.md) (mentions)
- [Learning paths](../../docs/learning-paths.md) (mentions)
- [Choose a stack you can run](../../docs/practical-readiness.md) (mentions)
- [3. Inertial navigation and sensor fusion](../../docs/primer/03-inertial-and-fusion.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [UGV GNSS outage on a real log: wheel odometry + IMU, innovation gate, drag detector](../../catalog/samples/ugv-gnss-outage-real.md) (uses)

_Indexed by lane(s): samples_
