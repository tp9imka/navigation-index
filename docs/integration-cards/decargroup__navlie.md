# navlie - integration card
<!-- about: repo:decargroup/navlie -->
Pure-Python on-manifold estimation toolkit: define a `State` (vector or any Lie group), a process and a measurement model, and reuse EKF / iterated EKF / UKF / cubature / IMM / Gaussian-sum filters or batch MAP, with numerical Jacobians, IMU kinematics and preintegration, NEES plots and Monte Carlo runs. Fastest way to prototype and sanity-check a custom fusion idea (e.g. IMU + range beacons, IMU + baro + mag) before writing C++.

| | |
|---|---|
| Install | README: `git clone https://github.com/decargroup/navlie && cd navlie && pip install -e .`. `setup.py` pulls `pymlg @ git+https://github.com/decargroup/pymlg@main` (Lie group backend), numpy, scipy, matplotlib, joblib, tqdm, seaborn, evo. PyPI has `navlie` 0.0.1 (same project, uploaded 2023-07-28), but its metadata omits `pymlg` and `pymlg` is not on PyPI (404), so `pip install navlie` alone leaves `import navlie` broken; install from git. |
| Runs on | Python, CPU, any OS. CI (`.github/workflows/test_package.yml`) tests Python 3.9 to 3.13; README badge still says 3.8-3.10. Optional ROS 1 message conversion in `navlie/lib/states.py` imports `rospy` only if available. |
| Inputs | Python objects: `navlie.lib.imu.IMU` inputs (gyro, accel, stamp), `navlie.Measurement(value, stamp, model)` lists, and your own `ProcessModel` / `MeasurementModel` subclasses (`evaluate`, `covariance`, optional `jacobian`, else finite differences via `jacobian_fd`). Built-in datasets `navlie.lib.datasets.SimulatedInertialGPSDataset`, `SimulatedPoseRangingDataset` etc. and `data/MH_01_easy.txt` (EuRoC excerpt). |
| Outputs | `List[StateWithCovariance]` from `run_filter`; `GaussianResultList.from_estimates(estimates, ground_truth)` gives errors, NEES, 3-sigma bounds; `plot_error`, `plot_nees`, `plot_poses`, `plot_meas`. |
| Key API / entry points | `navlie.ExtendedKalmanFilter(process_model, reject_outliers=False)` with `.predict()` / `.correct()`; `IteratedKalmanFilter`, `UnscentedKalmanFilter`, `CubatureKalmanFilter`, `GaussHermiteKalmanFilter`, `InteractingModelFilter`, `GaussianSumFilter`; `navlie.run_filter(filter, x0, P0, input_data, meas_data)`; `navlie.BatchEstimator`; `navlie.DataGenerator`; `navlie.lib.states.VectorState/SO3State/SE3State/SE23State/IMUState`; `navlie.lib.imu.IMUKinematics`; models in `navlie.lib.models` (`RangePointToAnchor`, `RangePoseToAnchor`, `RangePoseToPose`, `GlobalPosition`, `AbsoluteVelocity`, `Altitude`, `Gravitometer`, `Magnetometer`, `CameraProjection`, `InvariantMeasurement`). Preintegration in `navlie.lib.preintegration`. |
| Time to first result | Estimate: 15 min (clone, `pip install -e .`, run `examples/ex_inertial_gps.py`). |
| License | MIT (`LICENSE`, Copyright 2022 DECAR). Backend `pymlg` is a separate repo (licence not checked here). `data/MH_01_easy.txt` is from EuRoC MAV (its own licence terms; not stated in this repo). |

## Minimal usage
Not run. Condensed from `examples/ex_inertial_gps.py`:

```python
import numpy as np
import navlie as nav
from navlie.lib.datasets import SimulatedInertialGPSDataset

data = SimulatedInertialGPSDataset(t_start=0, t_end=20)
gt = data.get_ground_truth()
P0 = np.eye(15) * 0.1**2
x0 = gt[0].plus(nav.randvec(P0))
ekf = nav.ExtendedKalmanFilter(data.process_model)
est = nav.run_filter(ekf, x0, P0, data.get_input_data(), data.get_measurement_data())
res = nav.GaussianResultList.from_estimates(est, gt)
fig, axs = nav.plot_error(res)          # attitude / velocity / position / gyro bias / accel bias
```

## Wiring it into a nav stack
- Prototype stage: replay a rosbag or CSV into `IMU` and `Measurement` lists, test a measurement model (e.g. a UWB range or a terrain-height `Altitude`), check NEES consistency, then port to C++ with [manif](./artivis__manif.md) (same group conventions style) or [GTSAM](./borglab__gtsam.md).
- Ground truth and trajectory metrics come via `evo` (a dependency): see [evo](./michaelgrupp__evo.md).
- For production ROS fusion use [robot_localization](./cra-ros-pkg__robot_localization.md) or [fuse](./locusrobotics__fuse.md); navlie has no real-time node.
- IMM filter is a ready path for manoeuvre-switching target or platform models in tracking prototypes.

## Gotchas
- `pymlg` git dependency (see Install); pin a commit for reproducibility since it tracks `main`.
- Speed: pure Python per-step loops; fine for minutes of data at IMU rates in offline runs, not for onboard real time (no number published; not measured here).
- Finite-difference Jacobians are the default when `jacobian()` is not overridden; correct but slow and step-size sensitive.
- `IMUState` tangent ordering and group conventions follow pymlg (SE_2(3)); check before mixing with other libraries' covariances.
- Reported IMM problems were closed (#114); tests import errors fixed (#115). Examples now run in CI (commit 2026-04-28).
- README disclaimer: "still definitely not perfect".

## Alternatives
- [FilterPy](./rlabbe__filterpy.md) - vector-space KF/UKF/IMM in Python, no manifold handling.
- [manif](./artivis__manif.md) - C++ Lie groups with analytic Jacobians when you move off Python.
- [GTSAM](./borglab__gtsam.md) Python bindings - factor graphs with IMU preintegration at C++ speed.

Sources: `README.rst`, `LICENSE`, `setup.py`, `navlie/__init__.py`, `navlie/filters.py`, `navlie/lib/models.py`, `navlie/lib/imu.py`, `navlie/lib/states.py`, `examples/ex_inertial_gps.py`, `.github/workflows/test_package.yml`, commit history, issues #114 #115 (github.com/decargroup/navlie); pypi.org/pypi/navlie/json, pypi.org/pypi/pymlg/json (404).
