# AI-IMU Dead-Reckoning - integration card
<!-- about: repo:mbrossar/ai-imu-dr -->
Research code for IMU-only car dead reckoning: an invariant EKF with zero lateral/vertical velocity pseudo-measurements whose noise covariances are set per-sample by a small 1D CNN. Useful as a GNSS-outage baseline for wheeled vehicles and as a template for "learned covariance" filters. Not a drop-in package.

| | |
|---|---|
| Install | No package, no `setup.py`. README: install PyTorch, then `pip3 install matplotlib numpy termcolor scipy navpy`, `git clone https://github.com/mbrossar/ai-imu-dr.git`. Data: `wget https://github.com/user-attachments/files/17930695/data.zip` and unzip into the repo (pickled KITTI 00-11 IMU). Trained parameters: README points at a Dropbox `temp.zip` that users report dead (issues #89, #91); issue #91 points to a copy in the fork `DragonEmperorG/ai-imu-dr` (`temp/temp.zip`), not verified. |
| Runs on | Python on CPU (README: "tested under Python 3.5"; trained on a PyTorch development branch). No GPU needed for test. Last code change 2021, README edit 2025-01. |
| Inputs | KITTI raw OXTS data converted to pickles (`KITTIDataset.read_data`, enable with `read_data = 1` in `KITTIArgs`). Filter input `u` is N x 6, `np.concatenate((gyro, acc))` (KITTI OXTS units rad/s, m/s^2), timestamps `t` in s from 0; ground-truth position via `navpy.lla2ned` from the first fix. Initial orientation and initial velocity are taken from ground truth (`init_run` uses `ang0` and `v_mes[0]`). |
| Outputs | Per sequence `<name>_filter.p` pickle in `results/` with `t, Rot, v, p, b_omega, b_acc, Rot_c_i, t_c_i, measurements_covs`; plots from `utils_plot.results_filter`. |
| Key API / entry points | `src/main_kitti.py` (edit the `KITTIArgs` class flags `read_data`, `train_filter`, `test_filter`, `results_filter`, and `path_data_base`), `KITTIParameters` (prior covariances `cov_lat`, `cov_up`, etc.). `utils_numpy_filter.NUMPYIEKF.run(t, u, measurements_covs, v_mes, p_mes, N, ang0)`; `utils_torch_filter.TORCHIEKF` with `MesNet` (the CNN covariance adapter) and `forward_nets(u)`; `train_torch_filter.train_filter(args, dataset)`. |
| Time to first result | Estimate: 30-60 min if the data zip and a working weights archive download; add debugging time for the weight/architecture mismatch below. |
| License | Code MIT (`LICENSE`, Copyright 2019 Martin Brossard). Data is derived from KITTI raw, which is CC BY-NC-SA 3.0 (non-commercial); the pickles inherit that. Trained-weights archive has no stated licence. |

## Minimal usage
Not run. From README:

```sh
pip3 install torch matplotlib numpy termcolor scipy navpy
git clone https://github.com/mbrossar/ai-imu-dr.git
wget "https://github.com/user-attachments/files/17930695/data.zip"
mkdir ai-imu-dr/results && unzip data.zip -d ai-imu-dr
# trained params: unzip temp.zip -d ai-imu-dr/temp   (source link dead upstream, see Gotchas)
cd ai-imu-dr/src && python3 main_kitti.py   # test_filter=1, results_filter=1 by default
```

## Wiring it into a nav stack
- Offline only as shipped: pickles in, pickles out. To use in a stack, port `NUMPYIEKF.propagate/update` and run `MesNet` on a sliding IMU window, then publish position/velocity as odometry to [robot_localization](./cra-ros-pkg__robot_localization.md) or MAVLink `ODOMETRY`.
- The zero lateral / zero vertical velocity constraint only holds for ground vehicles; it is wrong for UAVs and legged robots.
- Compare against [KF-GINS](./i2nav-whu__kf-gins.md) with a simulated GNSS outage, or score with [evo](./michaelgrupp__evo.md) after exporting `p` and `Rot` to TUM format.

## Gotchas
- Trained weights: the Dropbox link fails for users (#89, #91); state_dict mismatches between the archive and the code's `MesNet` are reported (#82 size mismatch `[64, 32, 5]` vs `[32, 32, 5]`, #88). Retraining may be needed.
- Issue #86: running with random (untrained) network weights gives near-paper results on KITTI; a commenter attributes it to KITTI-tuned `cov_lat` / `cov_up` priors in `KITTIParameters`. Treat the 1.10% KITTI figure (README) as specific to KITTI and these priors.
- Ground-truth initial attitude and velocity are used at t0; on your own data you need an alignment step.
- Hard-coded paths in `KITTIArgs.path_data_base`; parameters "trained on sequences 00, 01, 04-11, so only sequence 02 is a test sequence" (README).
- Old stack: Python 3.5 era code, `navpy` dependency, `.idea/` files committed; expect small fixes on current PyTorch.

## Alternatives
- [TLIO](../../catalog/repos/cathias__tlio.md) - learned displacement + EKF for head-mounted/pedestrian IMU, maintained data pipeline.
- [AirIMU](../../catalog/repos/haleqiu__airimu.md) - learned IMU correction and uncertainty for several platforms including drones.
- [denoise-imu-gyro](../../catalog/repos/mbrossar__denoise-imu-gyro.md) - same author, learned gyro denoising for attitude only.

Sources: `README.md`, `LICENSE`, `src/main_kitti.py`, `src/utils_numpy_filter.py`, `src/utils_torch_filter.py`, commit history, issues #82 #86 #88 #89 #91 (github.com/mbrossar/ai-imu-dr); KITTI licence from cvlibs.net (raw data CC BY-NC-SA 3.0).
