# GNSS/INS EKF through an outage and a spoofing walk-off

## Goal

Show, in about 250 lines of stdlib Python, what a loosely-coupled GNSS/INS filter buys you
and where it breaks:

- an IMU-only solution drifts to kilometres in minutes;
- an EKF fed with 1 Hz GNSS fixes coasts through a 60 s outage with metre-level error;
- an EKF that blindly trusts GNSS follows a spoofer that walks the position off slowly;
- a chi-square innovation gate catches a fast walk-off but not a slow one.

The last point is the one to take into a hackathon pitch: a gate is a necessary layer,
not a spoofing detector on its own.

## What it simulates

| Item | Value |
|---|---|
| State | `[px, py, vx, vy, psi, bax, bay, bg]` - 2D position, velocity, heading, accel bias (body), gyro bias |
| Trajectory | weaving ground vehicle, 10-20 m/s, yaw rate up to 0.12 rad/s, 400 s |
| IMU | 100 Hz, accel bias (0.06, -0.04) m/s^2, gyro bias 0.03 deg/s, white noise + bias random walk |
| GNSS | 1 Hz position fixes, 2.5 m (1 sigma) per axis |
| Outage | no fixes from 150 s to 210 s |
| Spoofing | from 280 s the fixes carry an offset growing at `--spoof-rate` m/s (default 1.0), heading 30 deg |
| Gate | NIS of the 2D position innovation vs chi-square 99.9 % (13.816); 3 consecutive rejects => alarm |

Four runs on the same random draw:

- `INS-only` - pure strapdown mechanization from the true initial state, biases unknown.
- `EKF` - every fix is fused.
- `EKF+gate` - fixes with NIS above the gate are dropped.
- `EKF+gate+latch` - same, plus after the alarm GNSS is no longer trusted (INS holdover).

Covariance is propagated at 10 Hz (mean at 100 Hz) to keep pure-Python runtime under a second.

## Repos this sample explains

The code is self-contained. These indexed repos are the real tools for the same job:

| Repo | Use it for |
|---|---|
| [Aceinna/gnss-ins-sim](https://github.com/Aceinna/gnss-ins-sim) | realistic IMU/GNSS error models and trajectories instead of the toy generator here |
| [rlabbe/filterpy](https://github.com/rlabbe/filterpy) | tested KF/EKF/UKF classes; `filterpy.kalman.ExtendedKalmanFilter` replaces `Ekf` |
| [i2Nav-WHU/KF-GINS](https://github.com/i2Nav-WHU/KF-GINS) | a full 3D error-state loosely-coupled GNSS/INS in C++ with sample data |
| [borglab/gtsam](https://github.com/borglab/gtsam) | factor-graph smoothing with IMU preintegration; better than an EKF at re-weighting a past spoofed segment |

## Prerequisites

- Python 3.10+ (tested on 3.14.7). No third-party packages.

## Run

```bash
cd samples/gnss-ins-ekf-outage
python3 ekf_outage.py                 # default: seed 7, spoof walk-off 1.0 m/s
python3 ekf_outage.py --sweep         # vary the walk-off rate 0.05 .. 2.0 m/s
python3 ekf_outage.py --seed 1 --spoof-rate 0.5
```

## Expected output (observed, python3.14.7, 2026-11-06)

```
seed=7 spoof_rate=1.0 m/s  IMU 100 Hz, GNSS 1 Hz, outage 150-210 s, spoof from 280 s
Horizontal position error [m]: RMS / max / end-of-segment
segment                      INS-only                        EKF                   EKF+gate             EKF+gate+latch
nominal      299.7 /   675.1 /  675.1     1.9 /     5.7 /    1.8     1.9 /     5.7 /    1.8     1.9 /     5.7 /    1.8
outage       995.2 /  1303.8 / 1303.8     4.9 /     7.7 /    7.7     4.9 /     7.7 /    7.7     4.9 /     7.7 /    7.7
recovery    1820.7 /  2344.4 / 2344.4     1.4 /     2.4 /    0.9     1.4 /     2.4 /    0.9     1.4 /     2.4 /    0.9
spoofing    3562.4 /  4761.7 / 4761.7    70.4 /   122.8 /  122.8    33.7 /    66.3 /   66.3    24.4 /    46.5 /   46.5
gate: rejected 101 fixes (101/119 spoofed); spoofing alarm (3 consecutive rejects) at 300 s (20 s after onset)
final spoof offset 120 m
```

```
End-of-run horizontal error [m] vs spoof walk-off rate
 rate m/s  alarm after s      EKF  EKF+gate   +latch
     0.05          never      6.4       6.4      6.4
      0.1          never     12.5      12.5     12.5
      0.2          never     24.8      24.8     24.8
      0.5          never     61.5      61.7     61.7
      1.0             20    122.8      66.3     46.5
      2.0              7    245.4       4.0      4.0
```

How to read it:

- Outage: the EKF had 150 s to estimate the IMU biases, so 60 s of coasting costs ~8 m,
  against ~1.3 km for unaided INS over the same span.
- Spoofing at 1 m/s: the ungated EKF ends exactly on the spoofer's 120 m offset. The gate
  needs 20 s to alarm because for the first seconds each step is inside the noise and the
  filter absorbs it. The fixes accepted before the alarm already bent the bias estimates,
  so even the latched holdover ends ~46 m off.
- Slow walk-off (<= 0.5 m/s here): never alarms. The filter follows the spoofer and the
  innovation stays small. This is the known weakness of innovation gating.
- Fast walk-off (2 m/s): caught in 7 s, ending error 4 m.

## Extend it in a hackathon

1. Swap the trajectory and IMU for `gnss-ins-sim` output: `sim.run(1)` then
   `sim.results('./data/')` writes the reference and simulated sensor data as files.
2. Add a second, independent check that does not depend on the filter following:
   GNSS-derived velocity vs INS velocity, C/N0 / AGC telemetry (see
   `samples/gnss-interference-monitor`), or a vision/terrain fix.
3. Keep a sliding window of NIS values and run a CUSUM or windowed chi-square test; it
   catches slower ramps than a per-epoch gate.
4. Replace the EKF with a GTSAM fixed-lag smoother and down-weight GNSS factors after an
   alarm instead of only rejecting future fixes.
5. Go 3D with KF-GINS once the 2D logic is clear.

## Pitfalls

- The gate threshold assumes the filter covariance is honest. Over-confident `P` (Q too
  small) rejects real fixes after an outage; over-inflated `P` lets spoofed fixes through.
  Check the "recovery" row after any tuning change.
- After a long outage `P` is large, so the first real fix is accepted even with a large
  innovation. The same mechanism lets a spoofer "capture" a filter that just came out of
  an outage.
- Heading is only observable while the vehicle accelerates or turns. On a straight,
  constant-speed leg, heading and gyro bias errors grow even with GNSS.
- The INS-only column starts from the true state; real dead reckoning starts worse.
- Results depend on the seed. Run a few seeds before quoting a number.

## Files

- `ekf_outage.py` - simulation, EKF, gate, report and sweep.
- `matlite.py` - list-of-lists matrix helpers (multiply, transpose, 2x2 inverse).
