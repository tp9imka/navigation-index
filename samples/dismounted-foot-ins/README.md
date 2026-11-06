<!-- about: repo:utiasstars/pyshoe, repo:hcarlsso/zupt-aided-ins, repo:pajaraca/iez, res:openshoe-foot-mounted-ins-2012 -->
# Dismounted foot-mounted INS (ZUPT) on real data

A soldier or first responder inside a building or underground has no GNSS. The standard
answer is an IMU on the boot: between steps the foot is still, so a zero-velocity update
(ZUPT) resets the velocity error every stride and drift grows with distance walked, not with
time cubed. This sample is a stdlib-only 15-state error-state EKF for that, run on **36 real
foot-mounted IMU trials** with surveyed ground truth. It is checked against pyshoe's INS on the
same trials, then gets aiding (corridor heading, floor height, simulated UWB with NLOS), a
look at why the magnetometer fails indoors, and blue-force output as CoT and `navdash/1`.

All numbers below come from runs on 2026-11-06 (Python 3.14.7 stdlib for this code; pyshoe
under Python 3.11.16, numpy 1.23.5, scipy 1.10.1). Raw outputs:
[results/run_hallway_output.md](results/run_hallway_output.md),
[results/mag_indoor_output.md](results/mag_indoor_output.md), per-trial metrics in
[results/hallway.json](results/hallway.json).

## Data: pyshoe hallway set (real)

[utiasSTARS/pyshoe](https://github.com/utiasSTARS/pyshoe) (Wagstaff, Peretroukhin, Kelly,
IEEE Sensors J. 2019) ships a foot-mounted IMU dataset. Its hallway part:

- 36 trials on the UTIAS FTP (pyshoe's README says 39), modes `walk` (9), `run` (13), `comb`
  (14, mixed walk/run/...), 5 subjects. IMU at 200 Hz (mean rate per trial 199.95 to 200.06 Hz).
  pyshoe's script labels the sensor "microstrain"; the exact model is not stated in what I read.
- Truth: the foot position at surveyed floor markers (`gt`) at known IMU indices (`gt_idx`).
  Every trial walks the same L-shaped out-and-back route, 214.6 m along the markers, start =
  end. walk/comb trials hit 15 markers, run trials 7. The true path between markers is not
  recorded.
- `processed_data.mat` (~2 MB each) per trial; raw ROS CSVs (IMU, magnetometer, pressure) next to it.

`sh fetch_data.sh` downloads all 36 `.mat` files (~85 MB) and the magnetometer logs of 6 walk
trials (~37 MB) into `data/` (git-ignored). Source: the FTP that pyshoe's `download_data.sh`
uses, `ftp://128.100.201.179/2019-pyshoe/`; also on
[IEEE DataPort](https://ieee-dataport.org/open-access/university-toronto-foot-mounted-inertial-navigation-dataset).
pyshoe's repo has no license file, so none of its code is vendored here; the dataset's terms
were not checked beyond "open access" on DataPort.

## Files

| File | What |
|---|---|
| `foot_ins.py` | `FootINS`: 15-state ES-EKF (p, v, attitude, accel bias, gyro bias), ZUPT, ZARU, yaw, height and range (NIS-gated) updates. Stdlib. |
| `detectors.py` | SHOE, ARED, AMVD, MBGTD stance detectors, same definitions and thresholds as pyshoe. |
| `matfile.py` | 60-line stdlib reader for MATLAB v5 numeric matrices (plain and zlib-compressed). |
| `run_hallway.py` | All 36 trials: filter variants, detector sweep, aiding table. `multiprocessing`, stdlib. |
| `pyshoe_compare.py` | Runs pyshoe's own `INS.baseline` (SHOE) on the same trials, dumps marker estimates. Needs numpy<1.24 + scipy. |
| `mag_indoor.py` | Real magnetometer logs: hard-iron sphere fit, heading residual, mag-aided vs corridor-aided EKF. |
| `export_tak.py` | One trial => `cot.xml` (via `../mavlink-to-tak-cot/cot.py`, optional UDP) + `navdash/1` tracks. |
| `test_foot_ins.py` | 18 stdlib unit tests (detectors, strapdown, EKF updates, gate, MAT reader). |
| `dash/walk1/` | Shipped export of walk/1/2018-04-11-10-39-53 for `templates/demo-dashboard`. |

## Run

```sh
cd samples/dismounted-foot-ins
python3 -m unittest -v test_foot_ins            # 18 tests, <1 s
sh fetch_data.sh                                 # ~120 MB from the UTIAS FTP
python3 run_hallway.py data/hallway --tables filter,detectors,aiding --jobs 8
python3 mag_indoor.py data/hallway
python3 export_tak.py data/hallway/walk/1/2018-04-11-10-39-53 --out dash/walk1 [--udp 127.0.0.1:4242]
```

`run_hallway.py` with all three tables took ~12 min wall on 11 workers of a heavily shared
12-core machine (one 40k-sample, 204 s trial through the 15-state filter is ~3 s CPU, so about
65x real time in pure Python).
`--only walk/0` restricts trials.

Cross-check against pyshoe (optional):

```sh
git clone --depth 1 https://github.com/utiasSTARS/pyshoe.git /tmp/pyshoe   # tested at 6bbc4df
uv venv --python 3.11 .venv && uv pip install --python .venv/bin/python numpy==1.23.5 scipy==1.10.1
.venv/bin/python pyshoe_compare.py /tmp/pyshoe data/hallway results/pyshoe_markers.json   # ~4 min
python3 run_hallway.py data/hallway --tables filter --pyshoe results/pyshoe_markers.json
```

pyshoe needs numpy<1.24 (`np.int`, `np.float`, `np.maximum_sctype`); its LSTM/SVM detectors
(torch, old sklearn) and the `liegroups` import are stubbed, so only the classical path runs.

Dashboard:

```sh
cd ../.. && python3 -m http.server 8000      # serve from the repo root
# http://localhost:8000/templates/demo-dashboard/?manifest=/samples/dismounted-foot-ins/dash/walk1/manifest.json
```

## Metrics

Same alignment as pyshoe's `process_error_hallway.py`: the initial yaw is unknown, so the
estimate is rotated about the start until its position at marker 1 points at marker 1. For the
aided runs that angle is used as the initial yaw ("known entry heading"), so corridor
directions and anchors live in one frame. Cells in the tables are:

**mean ARMSE at markers (m) / mean final horizontal error as % of the 214.6 m route / mean max
horizontal marker error (m)**, averaged over trials. The last column is how often the
filter's own 95 % radius (2.45 sigma_h) contains the true horizontal error at the markers.

Final error % is the number the task asked for, but read it with care: on an out-and-back
route a constant heading error rotates the outbound and the return leg the same way and
largely cancels at the start point. Max marker error (usually at the far end, 77 m out) is the
more honest drift number.

## Result 1: stdlib filter vs pyshoe (SHOE, G = 8.5e7, W = 5, all 36 trials)

| config | walk | run | comb | all | r95 covers |
|---|---|---|---|---|---|
| **pyshoe** (its own code, T = 1/200) | 2.47 / 1.60% / 4.25 | 2.03 / 1.33% / 3.79 | 2.99 / 1.56% / 3.83 | 2.51 / 1.49% / 3.92 | - |
| pyshoe, dt from ROS timestamps | 2.79 / 1.69% / 5.44 | 7.87 / 5.42% / 15.93 | 3.75 / 2.32% / 6.00 | 5.00 / 3.28% / 9.45 | - |
| stdlib `pyshoe9` (9 states, pyshoe step order) | 2.47 / 1.60% / 4.25 | 2.03 / 1.33% / 3.79 | 2.99 / 1.56% / 3.83 | 2.51 / 1.49% / 3.92 | 23% |
| stdlib `ins9` (9 states, textbook step order) | 2.97 / 1.61% / 4.76 | 2.36 / 1.08% / 3.14 | 3.55 / 1.59% / 4.41 | 2.98 / 1.41% / 4.04 | 19% |
| `ins9_bg` (+ gyro bias from first 1 s) | 3.41 / 2.27% / 6.13 | 7.27 / 5.50% / 14.00 | 8.04 / 7.45% / 16.78 | 6.61 / 5.45% / 13.11 | 10% |
| `ins15` (15 states, textbook order) | 2.91 / 1.57% / 4.73 | 2.33 / 1.07% / 3.11 | 3.42 / 1.34% / 4.24 | 2.90 / 1.30% / 3.95 | 22% |
| `ins15_bg` | 3.36 / 2.28% / 6.15 | 6.75 / 5.35% / 12.81 | 7.36 / 6.62% / 15.30 | 6.14 / 5.08% / 12.11 | 14% |
| `ins15_zaru` (+ ZARU when \|w\| < 0.02 rad/s) | 3.05 / 1.89% / 4.64 | 2.49 / 1.11% / 3.51 | 4.37 / 3.20% / 7.41 | 3.36 / 2.12% / 5.31 | 20% |
| **`ins15_py`** (15 states, pyshoe order; default) | 2.33 / 1.53% / 4.03 | 1.93 / 1.29% / 3.57 | 2.76 / 1.17% / 3.42 | **2.35 / 1.30% / 3.63** | 31% |
| `ins15_py_zaru` | 2.51 / 1.86% / 4.29 | 2.04 / 1.29% / 3.96 | 3.85 / 3.22% / 7.23 | 2.86 / 2.18% / 5.31 | 29% |
| `ins15_py_yrw` (+ yaw random walk 0.15 deg/sqrt s) | 2.30 / 1.52% / 3.73 | 1.95 / 1.36% / 3.77 | 2.77 / 1.38% / 3.52 | 2.36 / 1.41% / 3.66 | 60% |

- **Reproduction.** The stdlib SHOE detector gives stance labels identical to pyshoe's on
  100.0000 % of samples in all 36 trials. With pyshoe's step order and frozen bias states, the
  stdlib filter lands within 2.7 mm of pyshoe's estimate at every marker of every trial
  (unaligned). So `foot_ins.py` is pyshoe's INS when configured as such.
- **15-state default vs pyshoe: 2.35 vs 2.51 m ARMSE, 1.30 % vs 1.49 % final, 3.63 vs 3.92 m
  max** (mean of 36 trials). A modest gain; the bias states mostly help through slightly
  different gains, not through bias estimates that mean much.
- **Two downloads, two results.** The table is on the author's download (re-run on that data
  2026-11-06: identical). A fresh `fetch_data.sh` download in review round 2, same code, gave
  **2.21 m / 1.33 % / 3.68 m** for `ins15_py` (`pyshoe9` 2.37 m, `ins15` 2.76 m): every config
  about 0.14 m lower. Cause not found. Quote "2.2-2.35 m" or name the download, as the
  [evidence matrix](../../docs/evidence-matrix.md) does.
- **Step order matters more than I expected**: pyshoe's `nav_eq` rotates the specific force
  with the already-updated attitude and integrates position from the new velocity. That beats
  the textbook order (previous attitude, old velocity) by ~0.5 m ARMSE here. Not explained, just
  measured; `FootINS(pyshoe_order=...)` switches it.
- **Do not use the per-sample ROS timestamps.** They are bunched (4.6 % of intervals < 1 ms on
  walk/0, median 5.18 ms) although the mean rate is exactly 200 Hz. Integrating with them
  doubles the error (5.00 vs 2.51 m); run trials suffer most.
- **Gyro bias from the start standstill hurts** (2.35 => 6.14 m). The subjects' "standing
  still" first second has gyro std of 1 to 10 mrad/s and means up to 8 mrad/s; that is foot
  fidget, not bias. Bias states with a tight prior and no init are harmless.
- **ZARU hurts** with SHOE stance: at G = 8.5e7 the detector accepts stance with |w| up to
  ~0.8 rad/s (median |w| in stance on walk/0 is 0.28 rad/s), so "zero angular rate" is false.
  Even gated to |w| < 0.02 rad/s it adds error.
- **The ZUPT filter is overconfident**: its 95 % radius contains the true error at only 31 % of
  markers. This decides how any absolute aiding must be gated (Result 3).

## Result 2: stance detectors (`ins15_py`, all 36 trials)

| detector, threshold | walk | run | comb | all | r95 covers |
|---|---|---|---|---|---|
| SHOE 3e7 | 1.85 / 1.65% / 3.70 | 2.55 / 1.73% / 5.71 | 2.57 / 1.49% / 3.59 | 2.38 / 1.62% / 4.38 | 59% |
| **SHOE 8.5e7** | 2.33 / 1.53% / 4.03 | 1.93 / 1.29% / 3.57 | 2.76 / 1.17% / 3.42 | 2.35 / 1.30% / 3.63 | 31% |
| SHOE 2e8 | 3.81 / 1.79% / 5.79 | 2.02 / 0.97% / 2.97 | 3.17 / 1.28% / 4.48 | 2.91 / 1.30% / 4.26 | 12% |
| ARED 0.3 | 2.18 / 1.58% / 4.00 | 2.34 / 1.67% / 4.48 | 2.75 / 1.32% / 3.29 | 2.46 / 1.51% / 3.89 | 46% |
| ARED 0.55 | 3.42 / 1.92% / 5.60 | 5.67 / 3.71% / 9.53 | 3.25 / 1.19% / 3.92 | 4.17 / 2.28% / 6.37 | 23% |
| ARED 0.8 | 4.37 / 1.83% / 7.01 | 7.17 / 4.83% / 11.80 | 4.01 / 1.51% / 5.06 | 5.24 / 2.79% / 7.98 | 8% |
| AMVD 0.02 | 2.99 / 1.75% / 5.45 | 11.83 / 3.61% / 17.97 | 3.96 / 2.08% / 5.44 | 6.56 / 2.55% / 9.97 | 41% |
| AMVD 0.05 | 4.82 / 1.91% / 8.18 | 7.17 / 4.85% / 14.32 | 5.62 / 2.42% / 8.99 | 5.98 / 3.17% / 10.71 | 23% |
| AMVD 0.1 | 10.90 / 2.50% / 20.25 | 9.44 / 5.49% / 15.95 | 11.23 / 4.29% / 20.05 | 10.50 / 4.28% / 18.62 | 9% |
| MBGTD 0.5 | 3.74 / 1.94% / 6.74 | 9.46 / 5.36% / 16.36 | 4.33 / 2.04% / 6.69 | 6.03 / 3.22% / 10.19 | 30% |
| MBGTD 0.75 | 6.81 / 2.34% / 12.24 | 8.59 / 6.32% / 16.05 | 7.73 / 3.78% / 13.52 | 7.81 / 4.34% / 14.11 | 17% |
| MBGTD 1.0 | 13.05 / 3.01% / 25.02 | 16.03 / 8.92% / 29.16 | 12.44 / 4.85% / 22.48 | 13.89 / 5.86% / 25.52 | 6% |

SHOE and ARED thresholds are pyshoe's hallway values; AMVD and MBGTD have none in pyshoe, so I
picked thresholds that give about SHOE's stance share on walk/0 and swept around them. That is
one trial's tuning, then evaluated on all, so their rows are indicative only. The trade-off is
visible: a strict threshold (SHOE 3e7) is best for walking, a loose one (SHOE 2e8) for running,
because running stance is short and noisy. That is the problem pyshoe's adaptive and LSTM
detectors address (not run here). Accelerometer-only detectors (AMVD, MBGTD) do clearly worse
than detectors that use the gyro.

## Result 3: aiding (`ins15_py` + SHOE 8.5e7, all 36 trials)

Simulated UWB: 4 anchors at 2.5 m height set back from the corridor centre lines (invented
positions, see `ANCHORS`), max range 25 m, sigma 0.15 m, 30 % of ranges NLOS with +1 to +5 m
excess. Ranges exist **only at odd marker epochs** (the only times the true position is known),
so every row is scored on the **even markers only** (held out from the ranges). Cells use
horizontal ARMSE.

| aiding | walk | run | comb | all | r95 covers |
|---|---|---|---|---|---|
| none | 1.72 / 1.53% / 4.03 | 1.30 / 1.29% / 3.57 | 1.69 / 1.17% / 3.42 | 1.56 / 1.30% / 3.63 | 37% |
| corridor heading (HDE) | 1.34 / 0.67% / 2.56 | 1.26 / 1.21% / 3.49 | 1.37 / 0.59% / 2.68 | 1.32 / 0.83% / 2.94 | 38% |
| floor height | 1.71 / 1.53% / 3.98 | 1.30 / 1.27% / 3.51 | 1.65 / 1.12% / 3.36 | 1.54 / 1.28% / 3.57 | 37% |
| floor + UWB, no gate | 1.86 / 1.55% / 4.21 | 2.84 / 2.94% / 7.49 | 1.52 / 1.21% / 3.78 | 2.08 / 1.92% / 5.23 | 16% |
| floor + UWB, NIS gate | 1.60 / 1.29% / 3.70 | 1.26 / 1.12% / 3.62 | 1.68 / 1.20% / 3.26 | 1.51 / 1.19% / 3.50 | 30% |
| floor + UWB, inflate + gate | 1.25 / 1.39% / 3.23 | 1.70 / 1.50% / 4.79 | 0.96 / 0.80% / 2.34 | 1.30 / 1.20% / 3.45 | 72% |
| HDE + floor | 1.33 / 0.67% / 2.54 | 1.25 / 1.20% / 3.44 | 1.36 / 0.57% / 2.65 | 1.31 / 0.82% / 2.91 | 37% |
| HDE + floor + UWB, NIS gate | 1.33 / 0.70% / 2.66 | 1.23 / 1.06% / 3.55 | 1.47 / 0.79% / 2.75 | 1.35 / 0.87% / 3.02 | 29% |
| **HDE + floor + UWB, inflate + gate** | 0.86 / 0.66% / 1.95 | 1.66 / 1.46% / 4.67 | 0.65 / 0.35% / 1.60 | **1.07 / 0.83% / 2.80** | 80% |

Range bookkeeping over all trials: NIS gate alone used 129 ranges and rejected 245, including
93 of the 98 NLOS ranges **and ~150 good ones**. With inflation: 275 used, 99 rejected, 77 of
98 NLOS rejected.

- **Corridor heading (heuristic drift elimination)** is the cheapest win: when the last 3
  strides are straight within 8 deg and within 15 deg of a building axis, a yaw update snaps the
  walking direction to that axis (sigma 5 deg). Max error 3.63 => 2.94 m, final 1.30 => 0.83 %;
  walking trials 4.03 => 2.56 m max. It needs the building axes (a floor plan or two corridor
  walls) and fails in open or diagonal spaces.
- **UWB without a gate is worse than no UWB** (NLOS biases pull the track). A plain 99 % NIS
  gate (6.63) rejects the outliers but also most good ranges, because the ZUPT covariance is
  overconfident (see r95 coverage). The fix that worked: before each ranging epoch, add
  (0.02 x distance walked since the last ranging epoch)^2 to the horizontal variance, the
  measured unaided drift rate, then gate. That is a heuristic covariance floor, not a tuned
  noise model.
- **Floor height** (z = floor at each stance onset, sigma 5 cm; a stand-in for a barometer on
  one storey) barely moves horizontal error, but it stops the vertical drift (up to 3 m on
  walk/1 without it) from corrupting ranges to ceiling-height anchors.
- **Run trials do not benefit from UWB** here: they have only 3 ranging epochs (markers 1, 3, 5)
  and the far one sees 1 to 2 anchors.

## Result 4: the magnetometer indoors (real logs, 6 walk trials)

`mag_indoor.py` aligns the raw `imumagnetic_field.csv` (Gauss) to the processed IMU samples by
the ROS sequence number, removes hard iron with a sphere fit, and at each stance onset compares
the tilt-compensated horizontal field direction with its direction at the start. In a uniform
field this residual is 0 everywhere. It then runs the EKF with that heading as a 5 deg yaw
update, and with the corridor heading instead.

| trial | \|B\| after cal (uT) | heading residual median / p95 / max abs (deg) | horiz. ARMSE none / mag / corridor (m) | max err none / mag / corridor (m) |
|---|---|---|---|---|
| walk/0 15-39-07 | 37.2 - 55.2 | 39.5 / 76.2 / 81.2 | 1.08 / 9.60 / 1.13 | 2.02 / 28.44 / 1.93 |
| walk/0 15-42-42 | 37.3 - 54.5 | 19.3 / 48.1 / 60.1 | 1.85 / 5.28 / 1.88 | 3.22 / 15.31 / 3.19 |
| walk/0 14-04-36 | 38.0 - 55.5 | 34.0 / 65.1 / 68.8 | 2.55 / 9.37 / 2.55 | 3.96 / 27.89 / 3.88 |
| walk/1 10-39-53 | 26.8 - 54.8 | 14.9 / 38.1 / 48.1 | 1.15 / 2.71 / 0.88 | 2.44 / 10.85 / 1.62 |
| walk/2 19-42-05 | 35.0 - 55.8 | 13.6 / 36.9 / 47.9 | 3.89 / 7.38 / 2.21 | 11.85 / 22.01 / 4.61 |
| walk/4 15-20-30 | 24.8 - 52.1 | 25.7 / 59.3 / 69.7 | 1.01 / 7.72 / 0.70 | 2.56 / 24.44 / 1.41 |

The field magnitude swings 25 to 56 uT along one corridor walk and the field direction is off
by a median 14 to 40 deg. Trusting it as a compass makes every trial 2 to 9x worse (max error up
to 28 m on a 214 m walk). The residual includes the unaided INS's own yaw error, which is a few
degrees, an order smaller. Soft iron is not modelled. Takeaway: indoors, take heading from the
building (corridors), not from the compass; a magnetometer is still useful as a fingerprint
(magnetic map matching), which is a different algorithm.

## Result 5: blue-force output

`export_tak.py` runs the unaided and the best aided configuration on one trial and writes:

- `cot.xml`: one CoT event per second, type `a-f-G-U-C-I` (friendly ground infantry), `how`
  `m-f` (fused), `ce` = 95 % radius, callsign `DISMOUNT-1`, built with
  `samples/mavlink-to-tak-cot/cot.py`'s `build_event` (its `how` is fixed to `m-g`, GPS, so it is
  rewritten). `--udp host:port` also sends each event as a datagram (not tested against a live
  TAK server).
- `truth.jsonl`, `fused.jsonl`, `ins.jsonl`, `zones.geojson` (UWB anchor reach), `manifest.json`
  in `navdash/1`.

`ce` / `r95_m` = max(2.45 sigma_h, 0.02 x distance walked since the last ranging epoch),
because the filter's sigma alone covers the true error too rarely (Result 1).

The building is **not georeferenced**: the export places the building frame at an illustrative
anchor (43.7825, -79.4660, near UTIAS) with x => east, y => north. The map position and
orientation are not the real building. The shipped `dash/walk1` export (walk/1/2018-04-11-10-39-53):
unaided max 2.44 m / final 1.14 %; aided final 0.60 % but max 2.91 m (aiding does not win on
every trial). The JSONL was checked for parseability and schema fields, **not rendered in a
browser**.

## Extending it in a hackathon

- Real UWB: replace `uwb_at` in `run()` with logged ranges (DW1000/DW3000 TWR); keep the
  inflation + gate. Anchors dropped by the team at entry points are the realistic case.
- Map matching: the corridor constraint only uses axis directions. A particle filter over a
  floor-plan polygon (walls as hard constraints) is the next step and fits this filter as the
  motion model.
- Barometer: the raw logs have `imufluid_pressure.csv`; swap the floor constraint for
  `height_update()` from pressure for stairs and multi-storey.
- Stance detection for running / crawling: pyshoe's adaptive (SVM) and LSTM detectors, or a
  per-mode threshold from Result 2.
- Two feet or foot + body IMU: inter-foot range constraint.

## Pitfalls

- The route is out-and-back with start = end: final-error % flatters heading drift; quote max error.
- Use the nominal 200 Hz, not the ROS stamps.
- Truth only at markers: UWB ranges are simulated only there and scoring is on held-out markers.
  Anchors, noise and NLOS rates are invented.
- AMVD/MBGTD thresholds are tuned on one trial; the aiding parameters (HDE tolerances, 2 %
  drift floor, gate) were tuned while looking at an 18-trial subset (the 2018-04-11 sessions) of the same data. No separate
  test set.
- `ins15_py` beats pyshoe by ~6 % on the mean; that is one tuning on one dataset, not a general claim.
- Vertical drift is large without a height aid (several metres per trial on a flat floor).

## Verification status

Ran: everything above, on 2026-11-06. Not run: pyshoe's LSTM / adaptive detectors, the
VICON and stairs parts of the dataset, a live TAK server, the dashboard in a browser. Unit
tests: 18 pass; four planted mutations (range Jacobian sign, ZARU residual sign, the
attitude-to-velocity coupling sign, SHOE gyro term removed) each make at least one test fail.
