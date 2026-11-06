# pyins - integration card
<!-- about: repo:nmayorov/pyins -->
Pure-Python strapdown INS with an error-state EKF (feedback or feedforward), GNSS position / NED velocity / body velocity aiding, IMU bias models and a trajectory + IMU simulator. Good for a quick loosely-coupled GNSS/INS baseline and for GNSS-outage drift studies on a laptop.

| | |
|---|---|
| Install | `pip install python-ins` (PyPI distribution name is `python-ins`, not `pyins`; `pyins` does not exist on PyPI). Import name is `pyins`. Latest PyPI release 1.0.1 (2024-02-08). Source: `git clone https://github.com/nmayorov/pyins && pip install .` (needed for anything after 1.0.1, see Gotchas). |
| Runs on | Any OS, CPU only. Pure Python since the Cython => numba switch (2023-11). Runtime deps `numpy`, `numba`, `scipy`, `pandas` (`pyproject.toml`). No `requires-python` set; your Python is bounded by what numba supports. |
| Inputs | pandas DataFrames indexed by time (s). IMU: columns `gyro_x..z`, `accel_x..z` (rate sensors, rad/s and m/s^2, specific force including gravity) or `theta_x..z`, `dv_x..z` for increment sensors. Initial PVA: `lat lon alt VN VE VD roll pitch heading` (deg, m, m/s; NED frame). Measurements: `Position` needs `lat lon alt` columns plus a scalar sd in metres and optional IMU-to-antenna lever arm in body frame; `NedVelocity`, `BodyVelocity` similar (`pyins/measurements.py`, `pyins/util.py`). |
| Outputs | Bunch with `trajectory`, `trajectory_sd` (DataFrames, same column set), `gyro`, `gyro_sd`, `accel`, `accel_sd` (estimated sensor errors), `innovations` (dict of normalized innovations per measurement class). |
| Key API / entry points | `pyins.strapdown.compute_increments_from_imu(imu, sensor_type)` ('rate' or 'increment'); `pyins.strapdown.Integrator` (pure dead reckoning); `pyins.filters.run_feedback_filter(initial_pva, position_sd, velocity_sd, level_sd, azimuth_sd, increments, gyro_model=None, accel_model=None, measurements=None, time_step=0.1, with_altitude=True, gmf_settings=GmfSettings())` and `run_feedforward_filter(...)`; `pyins.measurements.Position(data, sd, imu_to_antenna_b=None)`, `NedVelocity`, `BodyVelocity`; `pyins.inertial_sensor.EstimationModel(bias_sd, noise, bias_walk, ...)`; `pyins.sim.generate_imu(time, lla, rph, velocity_n=None, sensor_type="rate")`, `generate_position_measurements`, `generate_pva_error`, `perturb_pva`; `pyins.transform.compute_state_difference`. No CLI. |
| Time to first result | Estimate: 15-30 min to run `examples/real_data_processing.ipynb` (data shipped in `examples/data/`). Assumes numba installs cleanly for your Python. |
| License | MIT (`LICENSE.txt`, Copyright 2023 Nikolay Mayorov). Example data in `examples/data/` has no separate licence stated. |

## Minimal usage
Not run. Adapted from `examples/real_data_processing.ipynb` (run from `examples/`).

```python
import numpy as np, pandas as pd, pyins
ref = pd.read_csv("data/reference_trajectory.csv", index_col="time")
imu = pd.read_csv("data/imu.csv", index_col="time")
gnss = pd.read_csv("data/gnss.csv", index_col="time")
lever = np.array([0.645, 0.0, 0.0])
meas = [pyins.measurements.Position(gnss, 1.0, lever),
        pyins.measurements.NedVelocity(gnss, 0.3, lever)]
inc = pyins.strapdown.compute_increments_from_imu(imu, "rate")
err = pyins.sim.generate_pva_error(5.0, 0.5, 0.2, 1.0, 0)
pva0 = pyins.sim.perturb_pva(ref.iloc[0], err)
gyro = pyins.inertial_sensor.EstimationModel(bias_sd=300.0 * pyins.transform.DH_TO_RS,
        noise=1.0 * pyins.transform.DRH_TO_RRS, bias_walk=30.0 * pyins.transform.DH_TO_RS / 60)
accel = pyins.inertial_sensor.EstimationModel(bias_sd=0.05, noise=0.1 / 60, bias_walk=0.01 / 60)
res = pyins.filters.run_feedback_filter(pva0, 5.0, 0.5, 0.2, 1.0, inc, gyro, accel, measurements=meas)
print(pyins.transform.compute_state_difference(res.trajectory, ref).abs().max())
```

GNSS outage test: drop rows from `gnss` for a time window before building the measurements and compare `trajectory_sd` growth against the true error.

## Wiring it into a nav stack
- Offline only: everything is batch over DataFrames, there is no streaming / ROS interface. Feed it logs from [pyubx2](./semuconsulting__pyubx2.md) (NAV-PVT => `lat lon alt VN VE VD`) and a decoded IMU log, or PX4/ArduPilot logs converted to the column names above.
- Synthetic data: `pyins.sim` generates IMU from a trajectory; [gnss-ins-sim](./aceinna__gnss-ins-sim.md) is the richer alternative when you need realistic sensor error profiles.
- Odometry / VIO as aiding: `BodyVelocity` takes body-frame velocity, e.g. wheel odometry or a VIO velocity output.
- Evaluate with `compute_state_difference` (NED position error + velocity + attitude) or export to TUM and use [evo](./michaelgrupp__evo.md).

## Gotchas
- PyPI name trap: `pip install pyins` fails; the package is `python-ins` (README; PyPI JSON for `pyins` returns Not Found).
- PyPI 1.0.1 is from 2024-02. The Gaussian Mixture Filter for unknown initial heading (`azimuth_sd=None` => `run_gaussian_mixture_filter`, `pyins/_gmf.py`) first landed in master on 2026-05-26, so it is not in the PyPI wheel. Install from git if you need in-motion alignment without a heading.
- IMU rate matters: maintainer in issue #23 (KITTI OXTS at 10 Hz => `LinAlgError ... not positive definite`) says about 100 Hz is the realistic minimum; 10 Hz IMU aliases car vibration.
- Accelerometer columns must contain gravity (specific force), as raw IMU output does (issue #23 discussion).
- For increment sensors you need one extra "before" sample; `compute_increments_from_imu` returns n-1 increments (docstring).
- No GNSS raw measurement (pseudorange) model: loosely coupled only.

## Alternatives
- [KF-GINS](./i2nav-whu__kf-gins.md) - C++ loosely coupled GNSS/INS EKF from WHU with a well-defined file format; prefer for speed or a C++ target.
- [navlie](../../catalog/repos/decargroup__navlie.md) - Lie-group EKF / batch estimation toolkit in Python; prefer when you want to define your own states and measurement models.
- [OB_GINS](./i2nav-whu__ob_gins.md) - optimization-based GNSS/INS on the KF-GINS formats.

Sources: `README.md`, `pyproject.toml`, `LICENSE.txt`, `pyins/filters.py`, `pyins/measurements.py`, `pyins/strapdown.py`, `pyins/sim.py`, `pyins/inertial_sensor.py`, `pyins/util.py`, `examples/real_data_processing.ipynb`, commit history of `pyins/_gmf.py` and `pyproject.toml`, issues #23 #6 #20 (github.com/nmayorov/pyins), https://pypi.org/pypi/python-ins/json, https://pypi.org/pypi/pyins/json.
