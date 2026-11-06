# GTSAM - integration card
<!-- about: repo:borglab/gtsam -->
One-line: a pip-installable factor-graph backend where IMU preintegration plus GNSS position (or pseudorange) factors give you a GNSS/INS smoother you can starve of GNSS to show outage behaviour.

| | |
|---|---|
| Install | `pip install gtsam` (PyPI latest 4.3.0, wheels for Linux x86_64/aarch64 and macOS universal2; no Windows wheel listed). Nightly develop wheels: `pip install gtsam-develop`. From source: `cmake -S . -B build -DGTSAM_BUILD_PYTHON=ON && cmake --build build --target python-install` (C++17; Boost optional per README). |
| Runs on | Linux, macOS (Intel and Apple Silicon via universal2 wheel). Windows only via source build. CPU only. No ROS needed (a `4.3.0-ros` tag exists for ROS packaging). |
| Inputs | Whatever you model. For nav: IMU specific force (m/s^2) and angular rate (rad/s) with dt; GNSS position as `Point3` in a local Cartesian nav frame (NED or ENU, your choice; ECEF also used by the GNSS factors); pseudoranges (m) with satellite ECEF position and clock bias for `PseudorangeFactor`. |
| Outputs | `Values` with `Pose3` (X), velocity `Vector3` (V), `imuBias.ConstantBias` (B) per keyframe; marginal covariances via `gtsam.Marginals`. |
| Key API / entry points | `gtsam.PreintegrationParams.MakeSharedU(g)` / `MakeSharedD(g)` (Z-up vs Z-down nav frame); `gtsam.PreintegratedImuMeasurements(params, bias)` + `.integrateMeasurement(acc, gyro, dt)`; `gtsam.ImuFactor(pose_i, vel_i, pose_j, vel_j, bias, pim)`; `gtsam.CombinedImuFactor(pose_i, vel_i, pose_j, vel_j, bias_i, bias_j, PreintegratedCombinedMeasurements)` (bias random walk inside the factor, params via `PreintegrationCombinedParams`); `gtsam.GPSFactor(key, Point3, noise)` and `GPSFactorArm(key, Point3, leverArm, noise)` (Pose3), `GPSFactor2` (NavState); `gtsam.PseudorangeFactor(posKey, clockKey, pr, satPos, satClk, noise)`; `gtsam.ISAM2` / `gtsam.LevenbergMarquardtOptimizer`; `gtsam.symbol_shorthand.X, V, B`. Names confirmed in `gtsam/navigation/navigation.i` (develop) and `python/gtsam/examples/IMUKittiExampleGPS.py`. |
| Time to first result | Estimate: 15 min to run `ImuFactorExample.py` / `IMUKittiExampleGPS.py` after `pip install gtsam` (bundled example data via `gtsam.findExampleDataFile`); 0.5-1 day to put your own IMU+GNSS log through iSAM2 with tuned noise. Assumes Python 3 on Linux/macOS and no source build. |
| License | GitHub: NOASSERTION. `LICENSE` says simplified BSD (`LICENSE.BSD`), with bundled third-party libs under their own (BSD-3 etc.) licenses. |

## Minimal usage
Adapted from `python/gtsam/examples/IMUKittiExampleGPS.py` (develop). Not run.

```python
import numpy as np, gtsam
from gtsam.symbol_shorthand import X, V, B

params = gtsam.PreintegrationParams.MakeSharedU(9.81)
params.setAccelerometerCovariance(np.eye(3) * 0.1**2)
params.setGyroscopeCovariance(np.eye(3) * 0.01**2)
params.setIntegrationCovariance(np.eye(3) * 1e-8)

isam = gtsam.ISAM2(gtsam.ISAM2Params())
graph, values = gtsam.NonlinearFactorGraph(), gtsam.Values()
bias = gtsam.imuBias.ConstantBias()
gps_noise = gtsam.noiseModel.Isotropic.Sigma(3, 2.0)

# k=0: priors on pose/vel/bias, then for each GNSS epoch k:
pim = gtsam.PreintegratedImuMeasurements(params, bias)
for acc, gyro, dt in imu_between(k - 1, k):           # your data
    pim.integrateMeasurement(acc, gyro, dt)
graph.add(gtsam.ImuFactor(X(k-1), V(k-1), X(k), V(k), B(k-1), pim))
graph.add(gtsam.BetweenFactorConstantBias(B(k-1), B(k), gtsam.imuBias.ConstantBias(),
                                          gtsam.noiseModel.Isotropic.Sigma(6, 1e-3)))
if gnss_ok(k):                                         # drop this to simulate an outage
    graph.add(gtsam.GPSFactor(X(k), gtsam.Point3(*enu_pos(k)), gps_noise))
values.insert(X(k), predicted_pose); values.insert(V(k), predicted_vel); values.insert(B(k), bias)
isam.update(graph, values); graph.resize(0); values.clear()
est = isam.calculateEstimate()
```

## Wiring it into a nav stack
- Convert GNSS LLA to a local tangent frame first (see [pymap3d card](./geospace-code__pymap3d.md)); `MakeSharedU` expects Z-up (ENU-like), `MakeSharedD` Z-down (NED).
- Raw GNSS: decode with [pyubx2](./semuconsulting__pyubx2.md) or post-process with [RTKLIB](./rtklibexplorer__rtklib.md) and feed position + covariance to `GPSFactor`; or go tightly coupled with `PseudorangeFactor` / `DopplerFactor` / `CarrierPhaseFactor` (in `gtsam/navigation`, also present at tag 4.3.0; notebooks `SinglePointPositioningExample.ipynb`, `RtkAndPppExample.ipynb` under `python/gtsam/examples/navigation`). [gnss_lib_py](./stanford-navlab__gnss_lib_py.md) can supply satellite positions.
- Simulated data: [gnss-ins-sim](./aceinna__gnss-ins-sim.md) for IMU/GNSS with outage windows; compare with the filter baseline in [samples/gnss-ins-ekf-outage](../../samples/gnss-ins-ekf-outage) and [KF-GINS](./i2nav-whu__kf-gins.md).
- Output pose to ROS via your own node, or to an autopilot as external nav (see [navigation2](./ros-navigation__navigation2.md) for ROS consumers).
- Catalog: [GTSAM page](../../catalog/repos/borglab__gtsam.md); downstream users [LIO-SAM](../../catalog/repos/tixiaoshan__lio-sam.md), [gtsam_gnss](../../catalog/repos/taroz__gtsam_gnss.md).

## Gotchas
- `IMUKittiExampleGPS.py` does not use `GPSFactor`: it adds the GNSS fix as `addPriorPose3` with the current rotation, and waits for `2 * gps_skip` epochs before the first `isam.update` so heading becomes observable. Copying it with `GPSFactor` means you still need that warm-up and a decent yaw prior.
- `GPSFactor` is a position-only unary factor on `Pose3`; the header says to use `GPSFactorArm` when the antenna is offset from the IMU. Ignoring the lever arm biases position during turns.
- Develop vs release API drift: README warns `develop` may change APIs. Examples on the `develop` branch (Galilean IMU, NavStateImuEKF, PseudorangeFactor notebooks) may not match the `pip install gtsam` version; pin and read examples at the matching tag (`4.3.0`).
- PEP 668 distros (Ubuntu 23.04+, Homebrew Python) block bare `pip install`; use a venv (python/README.md).
- Source builds: `make python-install` installs into the interpreter cmake found at configure time, not the active venv (python/README.md). Past build breaks on Ubuntu 22.04 / WSL Ubuntu 24 / g++13 + Boost 1.83 (issues #2366, #1994, #2468, all closed).
- Noise-model tuning dominates time. Wrong bias random-walk sigma makes the smoother either ignore GNSS or chase it.
- GitHub license metadata is NOASSERTION, but the code is BSD; fine for commercial use.

## Alternatives
- [Ceres Solver](../../catalog/repos/ceres-solver__ceres-solver.md): when you want your own residuals (e.g. reuse [OB_GINS](../../catalog/repos/i2nav-whu__ob_gins.md) preintegration) and C++ only.
- [g2o](../../catalog/repos/rainerkuemmerle__g2o.md): pose-graph back end; IMU factors less turnkey.
- [FilterPy](./rlabbe__filterpy.md) or [KF-GINS](./i2nav-whu__kf-gins.md): a filter is simpler to explain and real-time by construction if smoothing is not needed.

Sources: `README.md`, `python/README.md`, `LICENSE`, `gtsam/navigation/navigation.i`, `gtsam/navigation/GPSFactor.h`, `python/gtsam/examples/IMUKittiExampleGPS.py`, listings of `python/gtsam/examples/` and `gtsam/navigation/` (develop and tag 4.3.0), GitHub releases/tags, PyPI JSON for `gtsam`, issue search (`GPSFactor`, `python imu`).
