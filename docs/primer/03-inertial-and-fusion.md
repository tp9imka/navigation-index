# 3. Inertial navigation and sensor fusion

After this chapter you can explain why an IMU drifts, write the predict/update loop of
a Kalman filter, choose between a filter and a factor graph, and configure an off-the-shelf
estimator to survive a GNSS outage.

Prev: [GNSS and its threats](02-gnss-and-threats.md) | Next: [Vision, LiDAR and radar odometry](04-vision-lidar-radar-odometry.md) | [Primer index](README.md)

## Inertial navigation

An IMU measures specific force (accelerometers) and angular rate (gyroscopes) in the body
frame. Strapdown mechanisation integrates them:

```
attitude:  R_k+1 = R_k * Exp(  (omega_meas - b_g) * dt )
velocity:  v_k+1 = v_k + ( R_k * (a_meas - b_a) + g ) * dt
position:  p_k+1 = p_k + v_k * dt + 0.5 * (...) * dt^2
```

It needs no external signal, so it cannot be jammed. The price is drift: a small gyro bias
tilts the attitude estimate, which leaks gravity into the horizontal acceleration, which is
integrated twice into position error. Error growth depends on sensor grade, so pick numbers
from your own IMU, not from a slide. The standard way to characterise an IMU is an
**Allan variance** plot from a long static log, giving white-noise density and bias random
walk ([Kalibr IMU noise model](../../catalog/resources/kalibr-imu-noise-model-wiki.md);
tool: [allan_variance_ros](../../catalog/repos/ori-drs__allan_variance_ros.md)). Record that
log before the event.

Deep references: [Titterton and Weston](../../catalog/resources/titterton-weston-strapdown-ins-2e.md)
for INS physics, [Groves](../../catalog/resources/groves-pnt-book-2e.md) for integration.
For "what if" plots of tactical vs MEMS drift, [pyins](../../catalog/repos/nmayorov__pyins.md)
and [gnss-ins-sim](../../catalog/repos/aceinna__gnss-ins-sim.md) simulate IMUs of chosen grade.

Attitude-only filters (AHRS) such as Madgwick or Mahony fuse gyro, accelerometer and
magnetometer into orientation cheaply
([Madgwick report](../../catalog/resources/madgwick-orientation-filter-report.md),
[ahrs](../../catalog/repos/mayitzin__ahrs.md), [x-io Fusion](../../catalog/repos/xiotechnologies__fusion.md)).

## The Kalman filter in five lines

```
predict:  x = f(x, u)                 P = F P F^T + Q
update:   y = z - h(x)                S = H P H^T + R
          K = P H^T S^-1
          x = x + K y                 P = (I - K H) P
```

- `Q` (process noise) says how much you distrust your motion model (the IMU); `R` says how
  much you distrust each measurement. Tuning is mostly about these two.
- **EKF**: linearise `f` and `h` with Jacobians. **UKF**: propagate sigma points instead.
- **Error-state KF (ESKF)**: run the IMU mechanisation as the nominal state and filter only
  the small error, then reset. This is how most INS/GNSS filters are written
  ([Sola, quaternion kinematics for the ESKF](../../catalog/resources/sola-quaternion-kinematics-eskf.md)).
- Rotations are not vectors. Use Lie-group plus/minus operators to add errors to attitude
  ([micro Lie theory](../../catalog/resources/sola-micro-lie-theory.md),
  [manif](../../catalog/repos/artivis__manif.md)). The **invariant EKF** defines error on
  the group itself and stays consistent under large initial errors
  ([Barrau and Bonnabel](../../catalog/resources/barrau-bonnabel-invariant-ekf.md)).

## GNSS/INS coupling

| Coupling | What GNSS gives the filter | Trade-off |
|----------|----------------------------|-----------|
| **Loose** | Position/velocity fixes | Simple; needs a full fix (4+ satellites) |
| **Tight** | Raw pseudoranges/Doppler | Uses partial constellations; per-satellite outlier rejection |
| **Deep / ultra-tight** | INS aids receiver tracking loops | Better under jamming; requires receiver access |

[Groves](../../catalog/resources/groves-pnt-book-2e.md) explains all three. For a hackathon,
start loose ([KF-GINS](../../catalog/repos/i2nav-whu__kf-gins.md)), mask GNSS epochs to
simulate an outage, and plot drift.

## Filters vs factor graphs

A **factor graph** writes the whole problem as a sparse nonlinear least-squares over a
window (or all) of past states, with one factor per measurement. Benefits: you can
relinearise, add delayed or out-of-order measurements, and add or drop sensors without
rewriting the filter
([Dellaert and Kaess](../../catalog/resources/dellaert-kaess-factor-graphs-robot-perception.md)).
iSAM2 makes this incremental ([paper](../../catalog/resources/kaess-isam2.md)); IMU
preintegration summarises many IMU samples into one factor between keyframes
([Forster et al.](../../catalog/resources/forster-imu-preintegration.md)).
[GTSAM](../../catalog/repos/borglab__gtsam.md) implements all of this with Python bindings.

Rule of thumb: an EKF is the fastest thing to get working in 48 hours; a factor graph pays
off once you have three or more sensors or intermittent absolute fixes.

## All-source and plug-and-play fusion

DARPA's ASPN programme set the goal that later GNSS-denied architectures inherit:
navigation software that accepts arbitrary combinations of sensors and reconfigures
quickly ([ANS/ASPN](../../catalog/resources/darpa-adaptable-navigation-systems.md),
[DARPA briefing](../../catalog/resources/darpa-aspn-briefing-2019.md)). AFIT work runs
multiple filters in parallel and monitors integrity to isolate a faulty or spoofed input
([Gipson webinar](../../catalog/resources/ion-webinar-gipson.md)). Autopilots do a light
version of this: ArduPilot runs one EKF core per IMU and switches lanes on inconsistency
([EKF overview](../../catalog/resources/ardupilot-ekf-overview.md)).

## Learned inertial odometry

Networks can regress displacement or noise covariance from raw IMU windows and feed a
classical filter: AI-IMU for cars
([paper](../../catalog/resources/brossard-ai-imu-dr.md), [code](../../catalog/repos/mbrossar__ai-imu-dr.md)),
TLIO and RoNIN for pedestrians (chapter 8), AirIO for drones
([paper](../../catalog/resources/airio-paper.md)). These reduce drift on data like their
training set; test on your own motion profile before claiming anything.

## Failure modes under EW

- **Spoofed GNSS drags the filter.** A slow spoofer stays inside the innovation gate. Defend
  with tighter gates during suspicion, cross-checks against other sources (chapters 4 and 5),
  and never let GNSS hard-reset the state. FAA notes hybrid GPS/inertial solutions can also
  be corrupted ([SAFO 24002](../../catalog/resources/faa-safo-24002.md)).
- **Jammed GNSS:** pure inertial drift. The value of better inertial sensors is longer
  holdover, which is how DIU frames quantum inertial sensing
  ([DIU solicitation](../../catalog/resources/diu-transition-quantum-sensing-2024.md)).
- **Overconfidence:** a filter with too-small `Q` rejects the true fix after an outage. Watch
  the normalised innovation squared.
- **Magnetometer interference:** heading from a magnetometer is corrupted by motors and
  current; ArduPilot/PX4 allow other yaw sources
  ([ArduPilot EKF source selection](../../catalog/resources/ardupilot-ekf3-sources.md)).
- **Timestamp misalignment and wrong extrinsics** look like sensor faults. Calibrate first.

## Learn it

1. [Kalman and Bayesian Filters in Python (Labbe)](../../catalog/resources/labbe-kalman-bayesian-filters-python.md) - intuition-first notebooks.
2. [kalmanfilter.net tutorial](../../catalog/resources/kalmanfilter-net-tutorial.md) - numeric examples by hand.
3. [Understanding Sensor Fusion and Tracking (MATLAB Tech Talks)](../../catalog/resources/mathworks-understanding-sensor-fusion-tracking.md) - 10-15 minute videos; the GPS+IMU episode maps to a nav filter.
4. [Udacity AI for Robotics](../../catalog/resources/udacity-ai-for-robotics-cs373.md) - localization filters in Python.
5. [Stachniss Mobile Robotics online training](../../catalog/resources/stachniss-mobile-robotics-online-training.md) - Bayes filter to EKF to particle filter.
6. [Coursera: State Estimation and Localization for Self-Driving Cars](../../catalog/resources/coursera-state-estimation-localization-sdc.md) - ends in an IMU/GNSS/LiDAR ES-EKF.
7. [Sola, quaternion kinematics for the ESKF](../../catalog/resources/sola-quaternion-kinematics-eskf.md) and [micro Lie theory](../../catalog/resources/sola-micro-lie-theory.md).
8. [Chalmers sensor fusion and nonlinear filtering (edX)](../../catalog/resources/chalmers-sensor-fusion-nonlinear-filtering.md).
9. [GTSAM tutorial](../../catalog/resources/gtsam-intro-tutorial.md) then [Factor graphs for robot perception](../../catalog/resources/dellaert-kaess-factor-graphs-robot-perception.md).
10. [Forster IMU preintegration](../../catalog/resources/forster-imu-preintegration.md), [iSAM2](../../catalog/resources/kaess-isam2.md), [invariant EKF](../../catalog/resources/barrau-bonnabel-invariant-ekf.md).
11. [Groves](../../catalog/resources/groves-pnt-book-2e.md), [Barfoot, State Estimation for Robotics](../../catalog/resources/barfoot-state-estimation-robotics-2e.md), [Titterton and Weston](../../catalog/resources/titterton-weston-strapdown-ins-2e.md).

## Build with it

- [FilterPy](../../catalog/repos/rlabbe__filterpy.md) - KF/EKF/UKF classes for prototypes (not Lie-group aware).
- [GTSAM](../../catalog/repos/borglab__gtsam.md) - factor graphs with ImuFactor; add a GNSS factor.
- [KF-GINS](../../catalog/repos/i2nav-whu__kf-gins.md) and [OB_GINS](../../catalog/repos/i2nav-whu__ob_gins.md) - filter vs optimisation GNSS/INS on the same data.
- [robot_localization](../../catalog/repos/cra-ros-pkg__robot_localization.md) - ROS EKF/UKF for any odometry, IMU and GNSS.
- [imu_x_fusion](../../catalog/repos/cggos__imu_x_fusion.md) - ESKF, IEKF, UKF side by side.
- [MINS](../../catalog/repos/rpng__mins.md) - multi-sensor aided INS; disable GNSS mid-run for a demo.
- [manif](../../catalog/repos/artivis__manif.md) and [navlie](../../catalog/repos/decargroup__navlie.md) - Lie-group estimation tooling.
- [gnss-ins-sim](../../catalog/repos/aceinna__gnss-ins-sim.md) and [pyins](../../catalog/repos/nmayorov__pyins.md) - simulated IMU/GNSS data with chosen error grades.
- [allan_variance_ros](../../catalog/repos/ori-drs__allan_variance_ros.md) and [allan-variance](../../catalog/repos/nmayorov__allan-variance.md) - IMU noise parameters.
- [NaveGo](../../catalog/repos/rodralez__navego.md) - INS/GNSS in MATLAB or Octave.

Samples in this hub: [`samples/gnss-ins-ekf-outage`](../../samples/gnss-ins-ekf-outage/).

Related concepts: [INS](../../catalog/concepts/ins.md), [sensor fusion](../../catalog/concepts/sensor-fusion.md),
[GNSS/INS](../../catalog/concepts/gnss-ins.md), [calibration](../../catalog/concepts/calibration.md).
