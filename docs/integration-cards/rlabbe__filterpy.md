# FilterPy - integration card
<!-- about: repo:rlabbe/filterpy -->
Readable NumPy implementations of KF, EKF, UKF, CKF, IMM, ensemble, information, square-root and fading-memory filters plus RTS / fixed-lag smoothers: the fastest way to stand up a prototype GNSS/INS or tracking filter in Python and tune it in a notebook.

| | |
|---|---|
| Install | `pip install filterpy` (PyPI 2.0.0, released 2026-10-26; deps numpy, scipy, matplotlib). Also `conda install -c conda-forge filterpy`. The author advises against installing from git. |
| Runs on | Any OS with Python 3 + numpy/scipy. CPU only; numpy overhead dominates for small state vectors. |
| Inputs | You supply matrices/functions: `x`, `P`, `F`, `Q`, `H`, `R` as numpy arrays (column vectors `(n,1)` in the README example); for EKF a Jacobian `HJacobian(x)` and `Hx(x)`; for UKF `fx(x, dt)` and `hx(x)` plus a sigma-point object. Units and frames are whatever you choose. |
| Outputs | State `x`, covariance `P`, prior/posterior copies (`x_prior`, `x_post`), innovation `y`, `S`, `K`, `log_likelihood`, `mahalanobis`; `batch_filter` returns arrays for `rts_smoother`. |
| Key API / entry points | `filterpy.kalman.KalmanFilter(dim_x, dim_z)` with `.predict(u=None, B=None, F=None, Q=None)`, `.update(z, R=None, H=None)`, `.batch_filter(zs, ...)`, `.rts_smoother(Xs, Ps, ...)`; `ExtendedKalmanFilter(dim_x, dim_z)` with `.predict(u=0)` and `.update(z, HJacobian, Hx, R=None, args=(), hx_args=(), residual=np.subtract)`; `UnscentedKalmanFilter(dim_x, dim_z, dt, hx, fx, points, ..., residual_x=None, state_add=None)`; `MerweScaledSigmaPoints(n, alpha, beta, kappa)`; `IMMEstimator`; `filterpy.common.Q_discrete_white_noise(dim, dt, var)`, `filterpy.common.Saver`. |
| Time to first result | Estimate: 30 min for a constant-velocity KF on GNSS positions; half a day for a 15-state error-state INS, because FilterPy gives you the update equations, not the INS mechanisation or attitude handling. |
| License | MIT |

## Minimal usage
Not run. Constant-velocity filter over local-frame GNSS fixes (README pattern, extended to 2D):

```python
import numpy as np
from filterpy.kalman import KalmanFilter
from filterpy.common import Q_discrete_white_noise
from scipy.linalg import block_diag

dt = 1.0
kf = KalmanFilter(dim_x=4, dim_z=2)               # state [n, vn, e, ve]
kf.F = block_diag([[1, dt], [0, 1]], [[1, dt], [0, 1]])
kf.H = np.array([[1, 0, 0, 0], [0, 0, 1, 0]], float)
kf.R = np.eye(2) * 2.5**2                         # from receiver hAcc if available
kf.Q = block_diag(Q_discrete_white_noise(2, dt, 0.1), Q_discrete_white_noise(2, dt, 0.1))
kf.P *= 100.
for z in fixes_ned:                               # (N, 2) array, e.g. from pymap3d.geodetic2ned
    kf.predict()
    y = z - kf.H @ kf.x.ravel()
    S = kf.H @ kf.P @ kf.H.T + kf.R
    if y @ np.linalg.solve(S, y) < 9.21:          # chi-square 2 dof, 99 %
        kf.update(z)
```

## Wiring it into a nav stack
- Inputs: GNSS fixes via [pyubx2](./semuconsulting__pyubx2.md) => [pymap3d](./geospace-code__pymap3d.md) local frame; IMU from logs or [gnss-ins-sim](./aceinna__gnss-ins-sim.md) synthetic data with known truth.
- Fault detection: compute the innovation before `update` (as above; after `update`, `kf.y`, `kf.S` and `kf.mahalanobis` hold the values of the step just applied) for chi-square gating against spoofing jumps; `IMMEstimator` switches between nominal and degraded motion models. The stdlib EKF in [samples/gnss-ins-ekf-outage](../../samples/gnss-ins-ekf-outage/) shows the gate idea without dependencies.
- Graduation path: once the model is right, move to [GTSAM](./borglab__gtsam.md) for smoothing with IMU preintegration, or to [robot_localization](./cra-ros-pkg__robot_localization.md) / [KF-GINS](./i2nav-whu__kf-gins.md) for a maintained runtime filter.
- Learning material: the companion book [Kalman-and-Bayesian-Filters-in-Python](../../catalog/repos/rlabbe__kalman-and-bayesian-filters-in-python.md) uses this library throughout.

## Gotchas
- Not Lie-group aware: attitude in the state needs a manual error-state formulation, or use [navlie](../../catalog/repos/decargroup__navlie.md) / [manif](../../catalog/repos/artivis__manif.md).
- UKF with angles: supply `residual_x`, `residual_z` and `x_mean_fn` that wrap angles, or the mean of 359 deg and 1 deg comes out as 180.
- Shapes: `x` as `(n,1)` vs `(n,)` mixes give silent broadcasting bugs; keep one convention.
- Version churn: 2.0.0 (2026-10-26) followed years on 1.4.5; it includes "Fix NumPy 2.4 and 2.5 incompatibilities" (commit message), so 1.4.5 on a recent NumPy is suspect. On master after the 2.0.0 tag, `KalmanFilter.__init__` dropped `dim_u` (`v2.0.0` still has `dim_x, dim_z, dim_u=0`); passing `dim_u=` will break on the next release.
- Author states the tests are not robust and the docs are generated from bleeding-edge master, so docs can describe features not yet on PyPI.
- Pure numpy: fine at 100 Hz for small states in Python, but not a real-time embedded runtime (no figures given in the README).

## Verified in this hub
Measured by hub samples that ran this code on 2026-11-06, unless a bullet says otherwise. The linked sample README holds the commands and raw output.

- filterpy 2.0.0 with numpy 2.5.4 on Python 3.12.14: `ExtendedKalmanFilter` (Joseph-form update) reproduced a hand-written 2D GNSS/INS EKF to the printed 0.1 m; a planted 100x R change moved the result, so the comparison exercises filterpy - [gnss-ins-ekf-outage](../../samples/gnss-ins-ekf-outage/README.md).

## Alternatives
- [navlie](../../catalog/repos/decargroup__navlie.md) - Lie-group EKF/UKF/batch with IMU models; prefer for attitude-bearing INS states.
- [GTSAM](./borglab__gtsam.md) - factor-graph smoothing with IMU preintegration when filtering is not enough.
- [ahrs](../../catalog/repos/mayitzin__ahrs.md) or [Fusion](./xiotechnologies__fusion.md) - when you only need attitude/heading from IMU+mag.

Sources: `gh api repos/rlabbe/filterpy/readme`, `filterpy/kalman/kalman_filter.py`, `EKF.py`, `UKF.py`, `sigma_points.py` (master and `?ref=v2.0.0`), `filterpy/changelog.txt`, recent commits list, PyPI JSON for 2.0.0, issue search.
