# PyShoe / UTIAS foot-mounted inertial navigation dataset

<!-- about: repo:utiasstars/pyshoe, sample:dismounted-foot-ins -->

University of Toronto STARS lab foot-mounted IMU data released with PyShoe, an open zero-velocity-aided INS with classical and learned (LSTM, adaptive SVM) zero-velocity detectors (Wagstaff, Peretroukhin, Kelly, IEEE Sensors J. 2019).

| Field | Value |
|---|---|
| Platform | IMU on a shoe, walking/running/stairs subjects |
| Environment | Indoor: mocap area, hallways, stairwells |
| Sensors and rates | Foot-mounted IMU at 200 Hz (mean rate per hallway trial 199.95-200.06 Hz, measured by the dismounted-foot-ins sample); pyshoe's script labels it "microstrain", exact model not stated. Raw ROS CSVs also carry magnetometer and pressure |
| Ground truth | VICON set: full position truth from motion capture (~3x3 m area). Hallway set: intermediate surveyed points, given as IMU sample indices. Stair set: vertical position at each flight |
| Size | README: full dataset about 2.9 GB (not verified). Hallway subset as used: 36 `processed_data.mat` files, about 2 MB each, about 85 MB total, plus about 37 MB of magnetometer logs for 6 walk trials (dismounted-foot-ins sample, fetched from the FTP on 2026-11-06) |
| License | Not stated (no LICENSE in repo). IEEE DataPort listing is "open access" |
| Format | `.mat` processed files (`data/vicon/processed`), plus per-set folders |
| Index | [PyShoe](../../catalog/repos/utiasstars__pyshoe.md) |

## What's in it

- VICON: 56 trials, mixed motion, full truth.
- Hallway: README says 39 trials; the FTP holds 36 (walk 9, run 13, comb 14; 5 subjects), per the sample's listing. Every trial walks the same L-shaped out-and-back route, 214.6 m along the markers; walk / comb trials hit 15 markers, run trials 7.
- Stairs: 6 training + 8 test trials.

## Download

```bash
git clone --depth 1 https://github.com/utiasSTARS/pyshoe && cd pyshoe
bash download_data.sh        # wget -r ftp://128.100.201.179/2019-pyshoe/* (whole set)
# hallway subset only, ~120 MB, curl over the same FTP (worked on 2026-11-06)
sh samples/dismounted-foot-ins/fetch_data.sh
# fallback, free account not required per README:
# https://ieee-dataport.org/open-access/university-toronto-foot-mounted-inertial-navigation-dataset
```

## Used in this repo

[samples/dismounted-foot-ins](../../samples/dismounted-foot-ins/) (`fetch_data.sh`, `run_hallway.py`, `pyshoe_compare.py`), run 2026-11-06:

- The UTIAS FTP answered for this sample on 2026-11-06, although an earlier listing attempt the same day timed out. Keep the IEEE DataPort copy as the fallback.
- A 60-line stdlib MATLAB v5 reader (`matfile.py`) loads `processed_data.mat`, so no scipy is needed.
- Stdlib SHOE detector matches pyshoe's stance labels on 100 % of samples in all 36 trials; the 15-state stdlib filter gets 2.35 m marker ARMSE / 1.30 % final error vs pyshoe's 2.51 m / 1.49 %.
- Using ROS timestamps for dt instead of pyshoe's fixed T = 1/200 made run trials much worse (5.42 % final vs 1.33 %); check timestamps before trusting them.
- pyshoe itself needs numpy < 1.24 (`np.int`, `np.float`); its repo has no licence file, so nothing was vendored.

## Loading and tooling

`ins_demos.py` runs five demos (classical SHOE/ARED/AMVD/MBGTD detectors and the learned ones) on the three sets; `process_error_hallway.py` and `process_error_stairs.py` reproduce the paper tables. Scikit-learn 0.19.1 and PyTorch only needed for the learned detectors; otherwise remove the LSTM/SVM imports from `ins_tools/EKF.py` (README).

## Hackathon fit

- Dismounted navigation without GNSS: ZUPT-aided INS is the strongest simple baseline for soldiers/first responders indoors.
- Idea 5 (INS holdover budget): show error growth with and without ZUPT on the same IMU data.
- Idea 19 (cooperative localization): seed per-person dead reckoning before adding inter-person ranging.

## Pitfalls

- The FTP mirror is an IP address on plain FTP and is intermittent (one timeout, one full fetch on the same day). Grab the data or the IEEE DataPort copy early.
- Old pinned scikit-learn (0.19.1) for the SVM detector; expect friction on new Python.
- Hallway and stair truth is sparse (checkpoints), so report checkpoint error, not continuous ATE.

## Sources

- utiasSTARS/pyshoe README and `download_data.sh` (gh api, 2026-11-06); a first FTP list attempt timed out
- samples/dismounted-foot-ins/README.md and `fetch_data.sh` (trial count, rate, subset size, run facts)
