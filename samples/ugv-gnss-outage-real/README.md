# UGV GNSS outage on a real log: wheel odometry + IMU, innovation gate, drag detector

<!-- about: res:umich-nclt-dataset, sample:gnss-ins-ekf-outage -->

## Goal

[gnss-ins-ekf-outage](../gnss-ins-ekf-outage/README.md) shows the hold-and-correct pattern on a
simulated vehicle. This sample runs the same pattern on a recorded ground-vehicle log, stdlib
only, from a 42 MB download:

- position error growth through GNSS outages of 10 / 30 / 60 / 120 s, with and without wheel speed;
- one real GNSS gap in the log (39.6 s) bridged the same way;
- what a chi-square innovation gate does with real consumer-GPS multipath;
- a coherent drag injected on the real fixes (labelled synthetic attack), detection time for the
  gate and for an odometry-vs-GNSS displacement test, and their false alarms on the clean log.

## Run

```bash
python3 fetch_nclt.py      # 42.3 MB (GT csv 20.7 MB + sensor tarball 21.7 MB), sha256-checked, ~30 s
python3 ugv_loop.py        # all four reports, ~26 s
python3 ugv_loop.py stats|outage|multipath|spoof
python3 -m unittest -v     # 11 tests, ~4 s with data; 4 skip without data
```

Python 3.10+, stdlib only (no numpy). The 8-state INS and the matrix helpers are imported from
`../gnss-ins-ekf-outage/` (`ekf_outage.Ekf.mechanize` / `update`, `matlite`, gate constant
`CHI2_2DOF_999 = 13.816`, `ALARM_CONSECUTIVE = 3`); nothing there is edited. Data lands in
`data/` (gitignored); `fetch_nclt.py` extracts only the six sensor CSVs by name and deletes the
tarball. The output quoted below is saved in `results/all-2013-01-10.txt`.

## Data used

[NCLT](../../docs/dataset-cards/nclt.md), session 2013-01-10: University of Michigan Segway robot
on North Campus, 1022 s, 1139 m of truth path, top speed about 1.4 m/s.

| File | Size | Use |
|---|---|---|
| `groundtruth_2013-01-10.csv` | 20,669,309 B, sha256 `4301c74f...` | truth (SLAM + RTK, ~100 Hz) |
| `2013-01-10_sen.tar.gz` | 21,669,014 B, sha256 `3ec1a5ac...` | `gps.csv` (consumer GPS, ~7 Hz), `gps_rtk.csv`, `ms25.csv` (Microstrain GX3 IMU, 47 Hz), `ms25_euler.csv`, `wheels.csv` (41 Hz), `kvh.csv` (KVH FOG heading, 95 Hz) |

Sizes from HEAD and the fetch on 2026-11-06. This was the smallest of the 27 sessions (the
others need 108-280 MB for the same two files). License: ODbL 1.0, contents under DbCL 1.0 (NCLT page "License" section, fetched 2026-11-06), share-alike for public adaptations;
attribution to Carlevaris-Bianco, Ushani, Eustice, IJRR 2016.

Conventions checked against truth before use (`ugv_loop.py stats` and exploration, 2026-11-06):
truth x = north, y = east, z down; MS25 gyro z vs truth yaw rate correlation 0.998, slope 0.994;
KVH heading rate = minus truth yaw rate (slope -0.999); wheel speed = 1.07 x truth speed (the
filter estimates this scale online). Consumer GPS lat/lon are mapped to the truth frame by a 2-D
rigid fit on RTK 3-D fixes vs truth (rotation -0.12 deg, residual median 0.84 m, p95 2.33 m); the
consumer GPS under test is not used in that fit.

## What runs

| Config | Propagation between fixes | Filter |
|---|---|---|
| `ins` | MEMS accel + gyro strapdown, accel levelled with the GX3's own roll/pitch; no wheels | `ekf_outage.Ekf` (8 states), local Q/R |
| `odo-mems` | wheel speed + MEMS z gyro | 5 states `[n, e, psi, gyro bias, wheel scale]` |
| `odo-fog` | wheel speed + KVH fibre-optic gyro | same 5 states |

GNSS: consumer `gps.csv` fixes, decimated to 1 Hz, R = 4 m (3-D fix) / 8 m (2-D fix) per axis,
set a priori. Gate: NIS > 13.816 rejects the fix, 3 consecutive rejects = gate alarm. Filters
start from the truth pose at the first sample, biases zero, scale 1.

Drag test: every 1 Hz fix, |GNSS displacement - odometry displacement| over the last 30 s, where
the odometry track is a free-running wheel + gyro integration whose heading is re-anchored to the
filter heading at the window start. Alarm if > 15 m on 3 consecutive fixes. Window, threshold and
persistence were fixed before the clean log was evaluated.

## Results

Ran 2026-11-06, /opt/homebrew/bin/python3 3.14.7, stdlib.

### Error growth vs outage length

Injected outages start every 20 s from 60 s; before the start the filter runs gated on real
fixes, after it dead-reckons. drift = error of the dead-reckoned displacement since the outage
start; abs = absolute error vs truth (adds the GNSS-aided error at the start, typically ~5 m
because the filter follows a ~5 m consumer receiver). Median / p95 / max over start times.

| Config | 10 s | 30 s | 60 s | 120 s |
|---|---|---|---|---|
| `ins` drift | 4.7 / 12.1 / 16.5 | 20.1 / 49.3 / 57.6 | 57.1 / 109.1 / 116.2 | 163.1 / 270.8 / 384.9 |
| `odo-mems` drift | 0.6 / 2.5 / 3.1 | 2.2 / 7.4 / 9.0 | 3.9 / 14.7 / 19.5 | 6.6 / 34.5 / 44.9 |
| `odo-fog` drift | 0.4 / 1.4 / 2.2 | 1.1 / 3.9 / 6.2 | 2.5 / 8.5 / 12.9 | 4.2 / 16.7 / 28.7 |
| `ins` abs | 7.9 / 53.8 / 98.1 | 18.6 / 73.2 / 141.0 | 54.1 / 126.9 / 182.8 | 159.3 / 261.6 / 381.3 |
| `odo-mems` abs | 5.5 / 17.9 / 18.6 | 5.9 / 17.9 / 19.2 | 7.2 / 18.7 / 22.0 | 9.4 / 33.1 / 43.8 |
| `odo-fog` abs | 5.4 / 16.6 / 18.1 | 5.2 / 16.8 / 18.1 | 5.7 / 16.9 / 17.7 | 6.8 / 21.1 / 27.1 |
| windows | 48 | 47 | 46 | 43 |
| truth path in window, median | 13 m | 39 m | 71 m | 140 m |

Real GNSS gap, 792.9-833.5 s (40.6 s between 1 Hz fixes, 30 m travelled; cause not verified):
error at gap start => at gap end, before the first new fix: `ins` 54.4 => 104.1 m, `odo-mems`
16.8 => 18.5 m, `odo-fog` 16.7 => 18.0 m. The high starting error is the multipath episode just
before the gap (next section).

### Gate vs real multipath

Consumer fix error vs truth over the log: 3-D fixes median 4.8 m / p95 11.3 m / max 23.7 m;
2-D fixes median 5.1 / p95 45.1 / max 54.6 m. The bad fixes cluster at 740-800 s, right before
the real gap. Classes below use truth: bad > 15 m, good < 10 m (1 Hz fixes).

| Config | Bad fixes rejected | Good fixes rejected | Gate alarms | Filter RMS gate / no gate | Filter max gate / no gate |
|---|---|---|---|---|---|
| `ins` | 0 / 40 | 0 / 800 | 0 | 9.8 / 9.8 m | 54.4 / 54.4 m |
| `odo-mems` | 16 / 40 | 0 / 800 | 1 (780 s) | 6.2 / 7.1 m | 18.5 / 33.7 m |
| `odo-fog` | 16 / 40 | 0 / 800 | 1 (780 s) | 6.1 / 6.7 m | 18.0 / 26.5 m |

### Injected drag on real fixes (synthetic attack)

Offset added to the real 1 Hz fixes, growing at r m/s from each of 8 start times (100-800 s),
direction 30 deg, for up to 200 s. An attack-run alarm counts only inside the attack window and
not within 10 s of a clean-log alarm of the same detector. Delay is the (upper) median over
detected runs; offset = r x delay.

| Config | r [m/s] | Gate: detected | delay | offset | Drag test: detected | delay | offset |
|---|---|---|---|---|---|---|---|
| `odo-mems` | 0.1 | 1/8 | 144 s | 14 m | 2/8 | 165 s | 16 m |
| `odo-mems` | 0.3 | 1/8 | 136 s | 41 m | 6/8 | 67 s | 20 m |
| `odo-mems` | 1.0 | 8/8 | 44 s | 44 m | 8/8 | 16 s | 16 m |
| `odo-fog` | 0.1 | 1/8 | 144 s | 14 m | 0/8 | - | - |
| `odo-fog` | 0.3 | 2/8 | 143 s | 43 m | 6/8 | 67 s | 20 m |
| `odo-fog` | 1.0 | 7/8 | 30 s | 30 m | 8/8 | 18 s | 18 m |

Clean log (1022 s, no injection), both configs: 1 gate alarm episode (780 s) and 1 drag-test
episode (762 s), both inside the real multipath episode where consumer fixes were 46-55 m off.
They are alarms on a real GNSS fault, not on spoofing; there were none elsewhere. Drag statistic
on the clean log: median 4.2 m (`odo-mems`) / 4.0 m (`odo-fog`), p99 39.3 / 37.9 m (the multipath
episode).

## What this shows

- Wheel speed is the difference between usable and useless here. MEMS-only strapdown on a
  pitching Segway drifts 57 m (median) in 60 s; wheel speed + the same MEMS gyro drifts 3.9 m,
  with the FOG 2.5 m. At 120 s the tail matters: p95 34.5 m (MEMS gyro) vs 16.7 m (FOG); a gyro
  heading error grows the position error linearly with distance.
- The gate needs a tight prior to work. With wheel odometry it rejected 16 of 40 truth-bad fixes
  and none of 800 good ones, and cut the worst filter error from 33.7 to 18.5 m. The INS filter's
  covariance was so wide that it rejected nothing.
- Same conclusion as the simulated sample, now on real noise: the gate catches a 1 m/s drag
  (30-44 s) but a 0.1-0.3 m/s drag passes. The displacement test catches 1 m/s in 16-18 s and
  0.3 m/s in 6 of 8 runs, but a 30 s window only sees r x 30 m of drag (3 m at 0.1 m/s), below
  real consumer-GPS noise. Slow drags need a longer baseline, and odometry drift over that
  baseline (table above) sets the floor.
- Real multipath and a drag look alike to both detectors over 30 s. The one clean-log alarm per
  detector was a real 46-55 m GNSS error, which is the alarm you want, but a spoofing claim needs
  more than these two tests.

## Limits

- Truth is NCLT's SLAM solution, which fuses lidar scan matching, odometry and RTK and is
  odometry-interpolated between graph nodes (dataset card). It is not independent of the wheel
  odometry being evaluated, which flatters the `odo-*` rows at short horizons.
- One session, one winter day, a campus Segway at <= 1.4 m/s. No road tunnel or city canyon; the
  "urban canyon" here is buildings on a campus, and the cause of the 39.6 s gap was not checked.
  Car speeds and wheel slip on a road vehicle are not covered.
- Outage windows overlap (120 s windows every 20 s), so the 43-48 windows are not independent.
- The drag is a position offset added to recorded fixes, not an RF spoof: the receiver's own
  velocity, clock and C/N0 do not change, so velocity- or clock-based detectors cannot be tested
  here.
- 2-D only; antenna lever arm ignored; frame alignment uses truth (on RTK fixes); initial pose from
  truth.
- Two choices were made after seeing a first run and are stated here: an alarm-attribution
  window of 10 s against clean-log alarms, and ending a drag-alarm episode when evaluation pauses
  > 5 s (a pre-attack multipath alarm was being carried across the 40 s gap into the 800 s attack
  window). Noise parameters, gate, and drag window / threshold / persistence were not tuned.
- Not run: robot_localization, DRIFT, Nav2 or any ROS stack.

## Tests

`test_ugv_loop.py`: 7 tests on inline synthetic NCLT-format fixtures (rigid fit, frame alignment,
gravity levelling, odometry dead reckoning with perfect sensors < 0.1 m in 60 s, gate rejects a
60 m jump and nothing on clean fixes, drag test fires on 1 m/s and not on clean, drag injection)
always run; 4 real-data tests (alignment residual, wheels beat IMU-only over 60 s, gate spares
good fixes, 1 m/s drag detected within 60 s) skip without `data/`. Mutations checked on a
scratch copy: an inert gate (`CHI2_GATE = 1e9`) fails the gate test; a zero injected drag fails
the drag and injection tests.
