# Quaternion kinematics for the ESKF (Sola) - paper digest
<!-- about: res:sola-quaternion-kinematics-eskf, repo:je310/eskf -->
**Quaternion kinematics for the error-state Kalman filter** - Joan Sola, arXiv technical note, 2017 (PDF dated November 8, 2017). [paper](https://arxiv.org/abs/1711.02508) | [code](https://github.com/je310/ESKF) (third-party implementation) | Read: full text extracted from the arXiv PDF (figures not viewed). This is a tutorial: there are no benchmarks; "results" below are the derivations and conventions it pins down.

## Problem
Quaternion and rotation formulas are scattered across conventions (Hamilton vs JPL, local vs global perturbations, active vs passive), and mixing them silently breaks IMU filters. The note collects one consistent set and derives a full IMU-driven error-state Kalman filter (ESKF) from it.

## Method
- Sec. 1-2: quaternion algebra, SO(3), exponential / log maps, Rodrigues formula, composition, SLERP; quaternion and rotation-matrix forms side by side.
- Sec. 3: conventions. Table 2 lists the 4 binary choices (component order, algebra / handedness, passive function, direction of right-to-left products). Author picks **Hamilton** (scalar first, ij = k, right-handed, local-to-global), matching Eigen, ROS, Ceres.
- Sec. 4: perturbations, derivatives, Jacobians (right Jacobian and its inverse), local vs global perturbations, time derivatives, zeroth- and first-order integration of rates.
- Sec. 5: ESKF kinematics. Why error state (Sec. 5.1): minimal orientation error, operates near origin away from singularities, second-order terms negligible, slow error dynamics allow lower-rate corrections.
- Nominal state x = [p, v, q, a_b, w_b, g] (gravity estimated as a state); error state dx = [dp, dv, dtheta, da_b, dw_b, dg], 18 dims. Angular error defined locally (Table 3).
- Discrete prediction (eq. 268-271): dx <- F_x dx, P <- F_x P F_x' + F_i Q_i F_i', with explicit F_x, F_i, Q_i.
- Sec. 6: correction with H = H_x X_dx via chain rule (Q_dtheta, eq. 281); injection into the nominal state (eq. 283); reset with Jacobian G = blkdiag(I6, I - [0.5 dtheta]x, I9) (eq. 288). Footnote recommends Joseph form over P <- (I - KH)P.
- Sec. 7: same filter with **global** angular errors (cites Li and Mourikis 2012 for better properties).
- Appendices A-E: Euler, midpoint, RK4, general Runge-Kutta; closed-form integration with a simplified and a full IMU example; truncated-series transition matrices; integration of noise into perturbation impulses.

## Data and sensors
- Sensors: 6-axis IMU (accelerometer + gyrometer with bias and noise) plus any "complementary" absolute sensor (GPS, vision) for corrections. Earth rotation rate neglected (footnote 23). No datasets.

## Headline results (as reported)
No experimental results; key derivations instead:
- Table 2: Hamilton vs JPL, 4 binary choices; "12 different combinations" exist.
- Eq. 235: true-state IMU kinematics with bias random walks and constant gravity.
- Eq. 270-271: the full discrete error-state Jacobian F_x and perturbation Jacobian F_i for the 18-dim error state.
- Eq. 288: reset Jacobian G. Text: most implementations use G = I18 ("trivial reset"); the full form "might be of interest for reducing long-term error drift in odometry systems".
- Appendix B.2 / B.3 / D.1 / E.2: symbolic worked examples (simplified IMU, full IMU, error-state transition matrix, noise impulses). No numeric worked example.

## Limitations
- Stated by author: the locally-defined angular error is "not necessarily the optimal way"; the global version (Sec. 7) is offered as an alternative. The simple covariance update has poor numerical stability; use symmetric or Joseph forms. Earth rotation neglected.
- Our read: flat-earth, local-frame INS. For long GNSS-denied runs with a tactical-grade IMU, Earth rate and transport rate matter; use a navigation-grade mechanization (e.g. KF-GINS) instead.
- Our read: equation numbers changed between versions of the notes. The je310 code cites "eqn 280, page 62" for Q_dtheta, which is eq. 281 on page 64 in the arXiv PDF we read. Cross-check by content, not by number.

## Code, weights, license
- `je310/ESKF`: MIT (GitHub API), last push 2019-04-12, effectively unmaintained. C++ / Eigen, `float`, aimed at an STM32 board. Measurements: position and quaternion (mocap style), with a state history buffer for delayed measurements.
- Our read from `include/ESKF.h`: the code drops the gravity state, so its error state is 15-dim (dPOS, dVEL, dTHETA, dAB, dGB), not Sola's 18. Fine for a fixed, known gravity.
- No weights (not learned). The note itself is free on arXiv.

## Reproduction effort (estimate)
Estimate:
- Reading: half a day for Sec. 3, 5 and 6; skip the rest until needed.
- Code: `je310/ESKF` builds with CMake + Eigen in minutes; wiring your IMU and a position source in is 0.5-1 day. A clean Python ESKF from Sec. 5-6 is about a day for one engineer.
- Nothing to "reproduce" numerically.

## What a hackathon team can take from it
- Decide conventions on day one (Hamilton, scalar first, local error) and write them in the README. Most fusion bugs in 48 h are convention bugs; Table 2 is the checklist.
- The 18-dim ESKF (or 15-dim without gravity) is the default GNSS / visual-fix fusion core: propagate at IMU rate, correct whenever a fix arrives. Pair with [filterpy](../integration-cards/rlabbe__filterpy.md) for the KF plumbing or compare against [KF-GINS](../integration-cards/i2nav-whu__kf-gins.md).
- Use the Joseph-form update and the full reset Jacobian G; both are cheap and remove a class of slow divergence.
- Any learned measurement (TLIO displacement, AirIO velocity, a terrain or visual fix) enters through Sec. 6: write h(x), get H via the chain rule with Q_dtheta, update, inject, reset.
- For an AHRS-only baseline use [Fusion](../integration-cards/xiotechnologies__fusion.md) and keep the ESKF for full position.
