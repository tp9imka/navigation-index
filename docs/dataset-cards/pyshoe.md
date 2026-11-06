# PyShoe / UTIAS foot-mounted inertial navigation dataset

<!-- about: repo:utiasstars/pyshoe -->

University of Toronto STARS lab foot-mounted IMU data released with PyShoe, an open zero-velocity-aided INS with classical and learned (LSTM, adaptive SVM) zero-velocity detectors (Wagstaff, Peretroukhin, Kelly, IEEE Sensors J. 2019).

| Field | Value |
|---|---|
| Platform | IMU on a shoe, walking/running/stairs subjects |
| Environment | Indoor: mocap area, hallways, stairwells |
| Sensors and rates | Foot-mounted IMU (model and rate not stated in README) |
| Ground truth | VICON set: full position truth from motion capture (~3x3 m area). Hallway set: intermediate surveyed points, given as IMU sample indices. Stair set: vertical position at each flight |
| Size | README: full dataset about 2.9 GB. Not verified by HEAD (FTP host timed out, 2026-11-06) |
| License | Not stated (no LICENSE in repo). IEEE DataPort listing is "open access" |
| Format | `.mat` processed files (`data/vicon/processed`), plus per-set folders |
| Index | [PyShoe](../../catalog/repos/utiasstars__pyshoe.md) |

## What's in it

- VICON: 56 trials, mixed motion, full truth.
- Hallway: 39 walking and running trials along three hallways.
- Stairs: 6 training + 8 test trials.

## Download

```bash
git clone --depth 1 https://github.com/utiasSTARS/pyshoe && cd pyshoe
bash download_data.sh        # wget -r ftp://128.100.201.179/2019-pyshoe/* (timed out from here on 2026-11-06)
# fallback, free account not required per README:
# https://ieee-dataport.org/open-access/university-toronto-foot-mounted-inertial-navigation-dataset
```

## Loading and tooling

`ins_demos.py` runs five demos (classical SHOE/ARED/AMVD/MBGTD detectors and the learned ones) on the three sets; `process_error_hallway.py` and `process_error_stairs.py` reproduce the paper tables. Scikit-learn 0.19.1 and PyTorch only needed for the learned detectors; otherwise remove the LSTM/SVM imports from `ins_tools/EKF.py` (README).

## Hackathon fit

- Dismounted navigation without GNSS: ZUPT-aided INS is the strongest simple baseline for soldiers/first responders indoors.
- Idea 5 (INS holdover budget): show error growth with and without ZUPT on the same IMU data.
- Idea 19 (cooperative localization): seed per-person dead reckoning before adding inter-person ranging.

## Pitfalls

- The FTP mirror is an IP address on plain FTP; it did not respond in testing. Grab the IEEE DataPort copy early.
- Old pinned scikit-learn (0.19.1) for the SVM detector; expect friction on new Python.
- Hallway and stair truth is sparse (checkpoints), so report checkpoint error, not continuous ATE.

## Sources

- utiasSTARS/pyshoe README and `download_data.sh` (gh api, 2026-11-06); FTP list attempt timed out
