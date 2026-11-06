# PyShoe - integration card
<!-- about: repo:utiasstars/pyshoe -->
Foot-mounted zero-velocity-aided INS (error-state EKF with ZUPT pseudo-measurements) in plain numpy, with 5 classical zero-velocity detectors (SHOE, ARED, AMVD, MBGTD, VICON) plus LSTM and SVM-adaptive detectors, and the U of Toronto foot-mounted IMU dataset (VICON, hallway, stairs). Useful as a dismounted / pedestrian GNSS-denied dead-reckoning baseline.

| | |
|---|---|
| Install | No package, no `setup.py`, no `requirements.txt`. `git clone https://github.com/utiasSTARS/pyshoe && cd pyshoe`, then install `numpy scipy` (and `scikit-learn`, `torch` only for the learned detectors) into a venv, and run scripts from the repo root. Data (~2.9 GB): `bash download_data.sh` (plain `wget` from an FTP IP) or the IEEE DataPort mirror (see Gotchas). No releases or tags. |
| Runs on | Any OS with Python 3. CPU only (`ins_tools/LSTM.py` forces `device = torch.device("cpu")`). |
| Inputs | `imudata`: N x 6 numpy array, columns 0-2 accelerometer (m/s^2), 3-5 gyro (rad/s) in the sensor frame (`ins_tools/EKF.py` `nav_eq`). Sample period `T` (default 1/125 s; datasets are 200 Hz, `ins_demos.py`) or a per-sample `dt` array. Dataset trials are MATLAB `.mat` files with `imu`, `ts`, `gt` and pre-optimized thresholds (`G_shoe_opt`, `G_ared_opt`, ...). |
| Outputs | `INS.baseline()` returns an N x 9 state: position (0-2, m, local level frame starting at origin, heading initialised to 0), velocity (3-5), roll/pitch/yaw (6-8). Also `ins.zv` (boolean zero-velocity per sample), `ins.P` covariances. |
| Key API / entry points | `ins_tools.INS.INS(imudata, sigma_a=0.01, sigma_w=0.1*pi/180, T=1.0/125, dt=None)`; `INS.baseline(W=5, G=5e8, detector='shoe', zv=None)`; `ins_tools.EKF.Localizer.compute_zv_lrt(W=5, G=3e8, detector='shoe', return_zv=True)` and per-detector methods `SHOE`, `ARED`, `AMVD`, `MBGTD`, `vicon_zv`, `LSTM`, `adaptive_zv`; `ins_tools.util.optimize_gamma`, `compute_error`, `align_plots`; scripts `ins_demos.py`, `process_error_hallway.py`, `process_error_stairs.py`, `process_error_vicon.py`, `run_threshold_optimization.py`. |
| Time to first result | Estimate: 30-60 min for the VICON demo with SHOE/ARED, dominated by the 2.9 GB download and patching the sklearn import (Gotchas). |
| License | No LICENSE file in the repo and no licence in GitHub metadata, so default copyright applies; ask the authors before redistributing code. The dataset is published as "open access" on IEEE DataPort; its licence terms are not stated in the repo. |

## Minimal usage
Not run. Adapted from `ins_demos.py` (VICON demo), after downloading the data.

```python
import scipy.io as sio
from ins_tools.INS import INS
from ins_tools.util import compute_error, align_plots
d = sio.loadmat("data/vicon/processed/2017-11-27-11-13-10.mat")
ins = INS(d["imu"], sigma_a=0.00098, sigma_w=8.7266463e-5, T=1.0 / 200)
x = ins.baseline(W=5, G=float(d["G_shoe_opt"]), detector="shoe")
x, _ = align_plots(x, d["gt"])
print("ARMSE 2D:", compute_error(x, d["gt"], "2d"))
```

Own IMU: build an N x 6 `[ax ay az gx gy gz]` array at a fixed rate, start with the foot still for at least 20 samples (initial roll/pitch is taken from the mean of the first 20 accel samples), and tune `G` per detector, since thresholds are IMU-specific.

## Wiring it into a nav stack
- Output is a relative local-frame track with arbitrary initial heading. To place it on a map, align heading and origin from a GNSS fix before the outage, a magnetometer ([imu_tools](../../catalog/repos/ccnyroboticslab__imu_tools.md) Madgwick with mag) or a known start pose.
- As a fusion input: differentiate the ZUPT-corrected positions into per-step displacement and feed them as odometry to a higher-level filter ([robot_localization](./cra-ros-pkg__robot_localization.md), [pyins](./nmayorov__pyins.md) `BodyVelocity`).
- Benchmarking: the hallway and stair sets have intermediate ground truth indices, so they double as an IMU-only pedestrian benchmark next to [RoNIN](../../catalog/repos/sachini__ronin.md) or [TLIO](../../catalog/repos/cathias__tlio.md).

## Gotchas
- Import breakage: `ins_tools/EKF.py` unconditionally does `import ins_tools.LSTM` (needs torch), `import ins_tools.SVM` (needs sklearn) and `from sklearn.externals import joblib`. `sklearn.externals.joblib` was removed from scikit-learn years ago, so on a current sklearn the module fails to import even if you only want SHOE. README says to delete the LSTM/SVM imports; you must also delete or replace the `joblib` import (`import joblib`). Issue #9 (open): old pickled SVM model needs `sklearn.svm.classes`, i.e. scikit-learn 0.19.1, which does not install alongside modern packages.
- Data download: `download_data.sh` is `wget -r ftp://128.100.201.179/...` (no TLS); issue #8 reports it unreachable (it served 36 trials to the hub on 2026-11-06), and the authors point to IEEE DataPort: https://ieee-dataport.org/open-access/university-toronto-foot-mounted-inertial-navigation-dataset.
- Pretrained LSTM loads from `results/pretrained-models/zv_lstm_model.tar`, which is not in git (only `results/readme.txt`); it comes with the dataset download (issue #1, #4).
- No training code for new IMUs (maintainer reply in issue #6). Detector thresholds are IMU and gait specific.
- Repo is dormant: last push 2021-12-17. Treat as reference code.
- Yaw is unobservable with ZUPT only; long walks drift in heading.

## Verified in this hub
Measured by hub samples that ran this code on 2026-11-06, unless a bullet says otherwise. The linked sample README holds the commands and raw output.

- **Ran** pyshoe's own `INS.baseline` (SHOE) on all 36 hallway trials at commit 6bbc4df: needs Python 3.11 + numpy 1.23.5 + scipy 1.10.1 (`np.int`, `np.float`, `np.maximum_sctype` break on numpy >= 1.24); LSTM/SVM detectors and the `liegroups` import had to be stubbed. ARMSE 2.51 m, 1.49 % final error (mean of 36), ~4 min - [dismounted-foot-ins](../../samples/dismounted-foot-ins/README.md).
- The UTIAS FTP served 36 trials (README says 39) on 2026-11-06. Do not integrate with the per-sample ROS timestamps (bunched intervals): error doubled to 5.00 m; use T = 1/200. Gyro bias from the initial standstill made it worse (2.35 => 6.14 m with a 15-state filter) - [dismounted-foot-ins](../../samples/dismounted-foot-ins/README.md).
- No licence file in the repo; the hub vendors none of its code - [dismounted-foot-ins](../../samples/dismounted-foot-ins/README.md).

## Alternatives
- [zupt-aided-ins](../../catalog/repos/hcarlsso__zupt-aided-ins.md) - another ZUPT-aided INS implementation.
- [mpu6050_zupt](../../catalog/repos/mtahakoroglu__mpu6050_zupt.md) - low-cost MPU6050 foot-mounted ZUPT, closer to cheap hackathon hardware.
- [RoNIN](../../catalog/repos/sachini__ronin.md) - learned inertial odometry for a phone-held IMU when the sensor is not on the foot.

Sources: `README.md`, `download_data.sh`, `ins_demos.py`, `ins_tools/INS.py`, `ins_tools/EKF.py`, `ins_tools/LSTM.py`, repo root and `results/` listings, GitHub repo metadata, issues #1 #4 #6 #8 #9 (github.com/utiasSTARS/pyshoe).
