# UTIL - UWB TDoA indoor localization dataset (U. Toronto)

<!-- about: res:util-uwb-dataset, repo:williamwenda/uwb_tdoa_dataset, repo:bitcraze/crazyflie-firmware -->

University of Toronto Dynamic Systems Lab dataset of UWB time-difference-of-arrival measurements from Bitcraze's Loco Positioning System, with LOS/NLOS identification experiments and about 150 min of quadrotor flights. Published in IJRR 43(10), 2024 (Zhao, Goudar, Qiao, Schoellig). An older, smaller TDoA2-only release from the same author is also indexed.

| Field | Value |
|---|---|
| Platform | Custom quadrotor on Crazyflie Bolt with LPS UWB tag (DWM1000), flow deck, ToF ranger, SD-card logger (flight set); static tag + 2 anchors (identification set) |
| Environment | 7.0 x 8.0 x 3.5 m indoor arena; 8 anchors per constellation, 4 constellations; constellation 4 adds static and dynamic (metal) obstacles |
| Sensors and rates | UWB TDoA2 (centralized) and TDoA3 (decentralized), IMU accel/gyro, optical flow, ToF laser, barometer; event-stream logging with microsecond timestamps. Per-sensor rates not stated on the page |
| Ground truth | 10 Vicon Vantage+ cameras ("millimeter-accurate", page); anchors surveyed with a Leica total station, frame alignment RMSE about 1.12 mm (page); ground station to firmware latency about 10 ms |
| Size | Release asset `dataset.7z` = 1,861,803,968 B (GitHub releases API, 2026-11-06). Older repo `Williamwenda/UWB_TDOA_dataset` is 574 MB (GitHub repo size) |
| License | Not stated on the page or repo (GitHub reports none) |
| Format | CSV per sub-dataset, ROS1 bags, anchor survey `.npz`/txt; ROS2 via SFUISE2 conversion script |
| Index | [UTIL page](../../catalog/resources/util-uwb-dataset.md), [older TDoA dataset tools](../../catalog/repos/williamwenda__uwb_tdoa_dataset.md), [Crazyflie firmware](../../catalog/repos/bitcraze__crazyflie-firmware.md) |

## What's in it

- Identification dataset: LOS distance (0.5-6.5 m) and angle tests; NLOS with cardboard, metal, wood, plastic, foam between anchor and tag or between anchors. Includes SNR and power-difference values.
- Flight dataset: about 120 s per sub-dataset, six trajectories, names like `const1-trial3-tdoa2`, `const4-trial6-tdoa2-traj1` (dynamic obstacle).
- An error-state KF baseline in `scripts/estimation/main.py`.
- Older repo (Williamwenda): TDoA2 from 7 constellations, Vicon truth, bias CSVs and a NN bias-correction demo (PyTorch 1.6).

## Download

```bash
git clone --depth 1 https://github.com/utiasDSL/util-uwb-dataset && cd util-uwb-dataset
curl -LO https://github.com/utiasDSL/util-uwb-dataset/releases/download/dataset-v1.0/dataset.7z   # 1.86 GB
7z x dataset.7z
```

Do not run `setupscript.bash` as-is: it asks for your sudo password, apt-installs packages and pip-installs globally. The two lines above are what it does for the data.

## Used in this repo

Not downloaded or run by any sample yet (checked 2026-11-06). [samples/swarm-coop-localization](../../samples/swarm-coop-localization/) names UTIL as the source of measured UWB NLOS / obstacle statistics to replace its simulated Markov bias model. The size on this card is the GitHub release asset, not a download.

## Loading and tooling

```bash
cd scripts/estimation
python3 main.py -i ../../dataset/flight-dataset/survey-results/anchor_const1.npz \
  ../../dataset/flight-dataset/csv-data/const1/const1-trial1-tdoa2.csv
```

Plot scripts in `scripts/flight-dataset/` (`visual_tdoa2_csv.py`, `visual_bias_csv.py`). For TDoA3 set `TDOA2=False` in `main.py`. Firmware-side LPS estimator: [crazyflie-firmware](../../catalog/repos/bitcraze__crazyflie-firmware.md).

## Hackathon fit

- Idea 13 (radio-ranging return-to-home): real TDoA with NLOS to test outlier rejection before trusting your own anchors.
- Idea 19 (cooperative localization): TDoA EKF baseline plus flow/ToF fusion; NLOS classification from identification data.

## Pitfalls

- No license: fine for a hackathon demo, ask before redistribution or product use.
- Truth is the Vicon pose logged onboard, sent over radio; clock drift ignored because sub-datasets are about 2 min.
- TDoA3 trials need the `TDOA2=False` flag, which triggers a downsampling step in `main.py`.
- Scripts were written for Ubuntu 20.04 + ROS Noetic and pinned `matplotlib==3.4.2`; use the CSVs if ROS is a hassle.

## Sources

- https://utiasdsl.github.io/util-uwb-dataset/ (rendered from `index.md` on the `gh-pages` branch, read via gh api)
- utiasDSL/util-uwb-dataset README, `setupscript.bash`, releases API; Williamwenda/UWB_TDOA_dataset README (2026-11-06)
