# Cooperative localization on real UWB: MILUV drones through the swarm-coop filters

<!-- about: repo:decargroup/miluv, res:miluv-dataset-2025, sample:swarm-coop-localization -->

## Goal

[swarm-coop-localization](../swarm-coop-localization/README.md) compares dead reckoning, a
centralized EKF, naive decentralized fusion and covariance intersection (CI), with and without
robust ranging, and tests integrity monitors against a spoofed anchor. All of it on simulated
UWB. This sample runs the same filter code, unmodified, on real two-way ranges from the
[MILUV](../../docs/dataset-cards/miluv.md) dataset (3 quadcopters, 6 anchors, mocap truth) and
checks which of the sim's conclusions survive:

- how the real range error compares with the sim's UWB model (bias, NLOS tail);
- position error per drone: DR vs centralized vs naive vs CI, plain vs robust ranging;
- an injected fault (biased anchor ranges on one drone, or biased inter-drone ranges) and the
  time each monitor takes to detect it.

## Run

```bash
python3 fetch_miluv.py                                # 31 MB over HTTP from an 11.1 GB zip, ~1-2 min
python3 fetch_miluv.py --exp default_3_random_0       # 82 s flight, 3.2 GB zip
python3 fetch_miluv.py --exp cirObstacles_3_random_0  # obstacles, for range statistics only
python3 run_real.py stats                             # < 2 s
python3 run_real.py nominal                           # ~2 min
python3 run_real.py fault                             # ~3 min (anchor fault)
python3 run_real.py fault --kind peer                 # ~3 min (inter-drone range fault)
python3 -m unittest -v                                # 15 tests, ~4 s; 8 skip without data
```

Python 3.10+, stdlib only. `fetch_miluv.py` reads the zip's central directory with HTTP range
requests and pulls only `mocap.csv`, `uwb_range.csv` and `height.csv` per drone, so no camera
frames are downloaded. Data lands in `data/` (gitignored). The filters are imported from
`../swarm-coop-localization/` (`filters.py`, `sim.py`, `coop_loc.py`); nothing there is edited.
Saved outputs: `out/stats.txt`, `out/nominal.txt`, `out/fault_anchor.txt`,
`out/fault_peer.txt`, `out/fetch.txt`.

## Data used

| Experiment | Flight | Zip | Fetched | Use |
|---|---|---|---|---|
| `default_3_zigzag_0` | 296 s, 3 drones, anchor constellation 0 | 11.10 GB | 31.4 MB | main runs: nominal and faults |
| `default_3_random_0` | 81 s, 3 drones | 3.23 GB | 12.6 MB | nominal, tests |
| `cirObstacles_3_random_0` | 78 s, 3 drones, obstacles, CIR logging (ranging rate ~20x lower) | 3.15 GB | 10.6 MB | range statistics only |

Sizes from the figshare API and from `fetch_miluv.py` output (`out/fetch.txt`), 2026-11-06.
MILUV data is CC BY 4.0 (Shalaby et al., arXiv 2504.14376); the anchor positions, tag lever
arms and height biases in `miluv_io.py` are copied from the MIT devkit's `config/`.

Truth check: re-deriving every range's truth from mocap pose + tag lever arm (own quaternion
code) matches the devkit's `gt_range` within 1 cm on 99.91 % of zigzag rows (max 0.33 m, at a
mocap gap) and 100 % of the other two.

## How the real data is mapped onto the sim's filters

| Sim | Here |
|---|---|
| 2 GNSS agents | 2 "anchored" drones: one 2-D fix per 0.5 s epoch from plain Gauss-Newton multilateration of their own real anchor ranges, projected to horizontal with their real downward rangefinder |
| 4 GNSS-denied agents | 1 denied drone (anchor ranges ignored). Every run is repeated with each of the 3 drones as the denied one |
| inter-agent UWB | real tag-to-tag ranges, projected to horizontal with both height sensors; one range per drone pair per epoch (median of that epoch's 4 tag pairs ~ 5-6 ranges), matching the sim's one-slot-per-pair structure. Tag lever arms (~0.22 m) are not modelled |
| odometry | **synthetic**: mocap displacement x per-drone scale N(0, 2 %) and heading N(0, 1.5 deg) errors + 0.05 m/s white noise. The experiment zips carry no VIO or wheel odometry, and PX4 IMU strapdown alone was not tried. 10 odometry seeds per configuration |
| mesh | ideal: every broadcast heard, one hop |
| constants | `adapter.INDOOR` rescales lengths and per-epoch noise for a 6 m arena at 2 Hz (R_GNSS 0.25 m, P0 0.3 m, Q_POS, Q_BIAS, PB0, lock-out 0.5 m, NLOS slack 1 m, reset 3 m, SS sigma cap 1 m). Gates, Huber knees, windows and **R_UWB = 0.15 m are the sim's own** |

`synthetic` range source: the same runs with each real inter-drone range replaced by the sim's
UWB model (0.10 m noise, Markov NLOS +1..8 m, 3 % outliers +5..30 m) applied to the same true
tag-to-tag distance. Same geometry, same timestamps, only the error model differs.

## Results

### Real range error vs the sim's model (`out/stats.txt`)

Error = range - mocap truth, metres. `cal` = devkit-calibrated range (antenna delay and
power-dependent bias removed). `air` = every drone involved above 0.3 m.

```
source                         n    mean     sd  rob sd      p1  median     p99     max  >0.3%  >0.5%   >1m%   >2m%   >5m%
zigzag_0 anchor air cal    13375   0.097  0.256   0.104  -0.180   0.005   0.968   1.726   15.4    9.5    0.8   0.00   0.00
zigzag_0 anchor air raw    13375   0.185  0.272   0.143  -0.162   0.106   1.091   1.815   19.6   12.1    2.0   0.00   0.00
zigzag_0 anchor ground cal  1477  -0.005  0.056   0.049  -0.115  -0.009   0.154   0.196    0.0    0.0    0.0   0.00   0.00
zigzag_0 inter air cal      8878   0.004  0.173   0.103  -0.251  -0.035   0.686   1.782    5.9    2.4    0.2   0.00   0.00
zigzag_0 inter air raw      8878   0.098  0.183   0.123  -0.190   0.060   0.797   1.877   10.4    3.9    0.4   0.00   0.00
random_0 anchor air cal     3405   0.104  0.276   0.108  -0.189  -0.000   1.022   1.636   17.6   11.4    1.1   0.00   0.00
random_0 inter air cal      2259  -0.002  0.178   0.093  -0.233  -0.045   0.750   1.236    6.4    3.1    0.3   0.00   0.00
obstacles anchor air cal     159   0.124  0.253   0.110  -0.146   0.023   0.908   1.391   18.9    9.4    0.6   0.00   0.00
obstacles inter air cal      109   0.037  0.188   0.117  -0.213  -0.012   0.707   0.820    8.3    4.6    0.0   0.00   0.00
sim model (all draws)       5780   1.196  3.702   0.128  -0.225   0.023  21.637  37.876   17.1   17.0   17.0  15.52   8.96
```

(Rows abridged; the full table with ground rows is in `out/stats.txt`.) What the 2-D filters
actually receive in zigzag (median per pair per epoch, horizontal projection, no lever arm):
inter-drone error sd 0.170 m, p1 -0.40 m, p99 +0.50 m, max 0.79 m. Anchor fixes: median error
0.183 m, p95 0.512 m, max 1.675 m.

- The core matches the sim: robust sd 0.09-0.12 m vs the sim's 0.10 m draw.
- The tail does not. Real ranges in flight have a positive tail (mean > median, p99 0.7-1.0 m,
  9-11 % of anchor ranges > 0.5 m) but nothing beyond 1.9 m in 32 k ranges. The sim puts 17 %
  of ranges more than 1 m long and 9 % more than 5 m.
- The tail only appears in flight: drones on the ground give sd 0.05-0.08 m and no range over
  0.25 m off (zigzag; one random_0 ground inter range reached 1.9 m). Why is not checked here;
  body blockage between a tag and the far side of the drone is one candidate.
- The obstacle experiment does not look worse in this sample, but has only 317 ranges (CIR
  logging slows ranging), so it says little.
- Calibration removes ~0.09-0.10 m of mean bias and roughly halves the > 1 m share.

### Position error, nominal (`out/nominal.txt`)

Mean [min, max] over 30 runs (3 choices of denied drone x 10 odometry seeds).

```
default_3_zigzag_0 (296 s), REAL inter-drone ranges
method                   denied-drone RMSE         anchored RMSE  denied final     NEES
dead-reckoning       0.484 [0.256, 0.961]   0.161 [0.142,0.176]         0.637      1.4
central-plain        0.202 [0.174, 0.239]   0.149 [0.125,0.167]         0.170      2.4
central-robust       0.198 [0.163, 0.242]   0.146 [0.122,0.166]         0.146      2.3
naive-robust         0.188 [0.152, 0.212]   0.146 [0.123,0.164]         0.152      3.2
ci-plain             0.296 [0.227, 0.446]   0.161 [0.142,0.176]         0.254      1.6
ci-robust            0.272 [0.227, 0.325]   0.161 [0.142,0.176]         0.231      1.6

default_3_zigzag_0, SYNTHETIC inter-drone ranges (sim model, same geometry)
dead-reckoning       0.484 [0.256, 0.961]   0.161 [0.142,0.176]         0.637      1.4
central-plain        3.082 [2.173, 3.981]   1.029 [0.823,1.320]         2.583    386.6
central-robust       0.191 [0.144, 0.272]   0.147 [0.123,0.164]         0.299      2.0
naive-robust         0.191 [0.163, 0.244]   0.147 [0.123,0.164]         0.307      2.8
ci-plain             3.302 [2.069, 4.281]   0.161 [0.142,0.176]         1.924     66.6
ci-robust            0.380 [0.211, 1.833]   0.161 [0.142,0.177]         0.452      2.3

default_3_random_0 (81 s), REAL inter-drone ranges
dead-reckoning       0.311 [0.140, 0.526]   0.164 [0.143,0.178]         0.396      1.4
central-plain        0.218 [0.153, 0.331]   0.139 [0.121,0.155]         0.252      2.0
central-robust       0.178 [0.128, 0.266]   0.136 [0.119,0.151]         0.173      1.9
naive-robust         0.203 [0.113, 0.355]   0.143 [0.120,0.169]         0.180      3.3
ci-plain             0.424 [0.187, 0.619]   0.164 [0.143,0.178]         0.488      1.7
ci-robust            0.398 [0.194, 0.628]   0.164 [0.143,0.178]         0.478      1.7
```

DR numbers depend on the synthetic odometer; the ratios between methods are the result.

### Fault: biased anchor ranges on one anchored drone (`out/fault_anchor.txt`)

From t = 120 s, +0.02 m/s ramp on the first anchored drone's ranges to anchors 0-2 (the +x
wall), so its multilateration fix walks off (about 0.5 m at +30 s, 1.0-1.2 m at +42 s, 4.5 m at
the end). 30 runs, plus 30 no-fault control runs.

```
method                         target RMSE         others RMSE   det wrong false         latency s
dead-reckoning          2.314 [2.29, 2.36]  0.401 [0.21, 0.82]     0     0     0                 -
central-robust          2.254 [2.19, 2.32]  0.826 [0.30, 1.39]     0     0     0                 -
central-robust+gate     1.364 [0.34, 2.49]  0.677 [0.25, 1.90]     0     0     0                 -
central-robust+ss       0.353 [0.22, 2.42]  0.304 [0.16, 2.39]    30     1     0 42.0 [40.0, 51.0]
ci-robust               2.307 [2.27, 2.36]  1.938 [1.23, 3.85]     0     0     0                 -
ci-robust+gate          2.441 [1.85, 3.61]  2.030 [1.25, 6.19]     0     0     0                 -
ci-robust+vote          3.085 [0.96, 5.68]  4.342 [0.35,14.56]    30    17     0 52.8 [45.5, 70.0]
ci-robust+ss            3.932 [0.76, 7.43]  2.913 [0.80, 7.00]    30     9     0 46.0 [42.5, 94.5]
no-fault control: 0 detections in 30 runs for every monitor; others RMSE 0.167-0.209 m
```

`det` = runs with a detection after onset, `wrong` = first detection names a healthy drone,
`false` = detections before onset. For `ci-robust+ss` with two anchored drones the alarm is
not attributable by design (both fixes are dropped), so `wrong` there only says which drone's
test tripped first.

### Fault: biased inter-drone ranges of the denied drone (`out/fault_peer.txt`)

Same ramp on every range touching the denied drone (a misbehaving UWB peer; the sim does not
model this case).

```
default_3_zigzag_0, peer fault: +0.02 m/s ramp from t=120 s on every inter-drone range of the denied drone
method                         target RMSE         others RMSE   det wrong false         latency s
dead-reckoning          0.550 [0.27, 1.15]  0.155 [0.12, 0.18]     0     0     0                 -
central-robust          2.646 [2.17, 3.30]  0.151 [0.11, 0.18]     0     0     0                 -
central-robust+gate     2.646 [2.17, 3.30]  0.148 [0.11, 0.17]     0     0     0                 -
central-robust+ss       2.639 [2.17, 3.39]  0.173 [0.11, 0.40]     6     6     0  171.2 [158.5,175.0]
ci-robust               6.794 [2.54,20.59]  0.155 [0.12, 0.18]     0     0     0                 -
ci-robust+gate          6.576 [2.53,20.70]  0.151 [0.11, 0.17]     0     0     0                 -
ci-robust+vote         11.008 [2.32,31.58]  0.151 [0.11, 0.17]    19     0     0   87.0 [27.0,154.5]
ci-robust+ss            7.399 [2.53,29.03]  0.381 [0.11, 2.77]     8     8     0  129.0 [51.0,152.0]
no-fault control: 0 detections in 30 runs for every monitor
```

Centralized monitors only watch the fixes, which stay honest, so the denied drone is dragged to
2.6 m RMSE (DR alone: 0.55 m); the 6 late SS alarms blame an anchored drone. Peer votes name
the right drone in 19/30 runs (median 87 s, ~1.7 m of bias) but CI's denied drone is already
far off and stays there (11.0 m mean). Nothing in the shipped filters handles this case well.

## How the sim's conclusions hold on real data

| Sim finding | On MILUV |
|---|---|
| 1. Ranging to anchored agents bounds the denied ones | **Holds.** Denied-drone RMSE 0.484 => 0.198 m centralized (zigzag, 2.4x). Smaller gain on the 81 s flight (0.311 => 0.178), where DR has little time to drift |
| 3. Plain least squares is unusable with NLOS; robust ranging is essential | **Does not hold for this arena.** Plain and robust are within 0.01-0.04 m on real ranges. It holds only with the sim's error model on the same geometry (3.08 m plain vs 0.19 m robust). Robust ranging costs nothing on real data, so keep it, but the sim's NLOS model is far heavier than these LOS flights |
| 4. Naive decentralized fusion double counts and breaks | **Mostly does not reproduce.** NEES 3.2-3.3 (overconfident vs 2.3 centralized) but RMSE is fine. With one denied drone and two strongly anchored peers there are no ranging loops among uncertain agents, which is where the sim's naive filter failed |
| 5. CI is consistent but 2.5-3x worse than centralized, at a fraction of the bandwidth | **Consistent: holds** (NEES 1.6). Accuracy cost 1.4x on zigzag; on the 81 s flight CI-robust is worse than DR (0.398 vs 0.311 m) |
| 6. A faulty anchor is worse than no cooperation | **Holds.** Healthy drones: 0.826 m centralized, 1.94 m CI, vs 0.401 m DR and 0.17 m without the fault |
| 7. Centralized solution separation contains it; a per-fix gate alone is seed-dependent | **Holds.** SS detects 30/30, median 42 s after onset (range bias 0.84 m, fix ~1.1 m off), healthy drones 0.304 m, 0 false alarms in 30 clean runs, 1 of 30 blamed the wrong drone. Gate alone: 0.677 m, spread 0.25-1.90 |
| 8. Decentralized integrity is the hard part | **Holds, more sharply.** Peer votes name the wrong drone first in 17/30 runs and leave healthy drones at 4.3 m. Distributed SS detects in 46 s but, unable to attribute between two sources, drops both fixes and everyone drifts (2.9 m, worse than no monitor) |
| (not in sim) A biased UWB peer | **Gap.** Centralized SS and gate never flag the right drone; the denied drone is dragged to 2.6 m RMSE, worse than its own DR (0.55 m). Peer votes flag it in 19/30 runs at median 87 s, too late for CI (11 m) |

Finding 2 (the odometry bias state) is not tested: the odometry here is synthetic.

## Limits

- Odometry is synthetic, so DR error and every absolute RMSE scale with an assumed odometer.
  Real VIO (the devkit's VINS-Fusion path) or PX4 IMU integration would replace it; not done.
- 2-D filters on 3-D flights: height comes from the downward rangefinder (sd 0.10-0.18 m vs
  mocap z in these runs), lever arms are ignored. Both add symmetric error that the sim does
  not have; the robust gate rejects a few ranges per run because of it.
- One indoor arena, line of sight, 3 drones, 296 s and 81 s flights. MILUV's obstacle runs were
  only used for range statistics, with 317 ranges.
- Filter constants were rescaled by hand for the arena (`adapter.INDOOR`, chosen before
  running the fault scenarios and not tuned per result); R_UWB, gates and windows are the
  sim's. The fault start (120 s) and rate (0.02 m/s) are arbitrary choices.
- Comms are ideal; byte counts are not reported (the sim already covers them).
- UTIL (UWB TDoA) was not used: these filters take two-way ranges, and TDoA would need a
  different measurement model.

## Files

| File | What |
|---|---|
| `fetch_miluv.py` | HTTP-range zip reader: fetches only the needed CSVs of one MILUV experiment |
| `miluv_io.py` | stdlib CSV loader, mocap interpolation, tag lever arms, anchor and height constants |
| `adapter.py` | MILUV => `sim.Epoch` stream: multilateration fixes, horizontal projection, synthetic odometry, faults, indoor constants, synthetic-range control |
| `range_stats.py` | real vs sim range error statistics |
| `run_real.py` | `stats`, `nominal`, `fault` runners |
| `test_real_uwb.py` | geometry, multilateration, truth re-derivation, real-tail check, coop beats DR, sim-model vs real ranges, SS detection with a no-fault control and a monitor-off control |
| `out/` | saved outputs quoted above |
