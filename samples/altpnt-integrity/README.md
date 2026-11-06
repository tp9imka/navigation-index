# Integrity monitoring for alt-PNT

## Goal

Camera-to-map navigation is sold on accuracy. Nobody publishes how often it is wrong
without saying so. This sample shows, in stdlib Python, the machinery that answers that
question for a fused GNSS-denied navigator:

- an EKF that fuses INS, VIO-like velocity, intermittent visual-geolocalization fixes,
  an optional coarse MagNav-like fix and a GNSS that gets jammed and then spoofed;
- chi-square innovation gating per measurement;
- a solution-separation (SS) bank of sub-filters for fault detection and exclusion (FDE);
- a horizontal protection level (HPL) per epoch, an alert limit (AL) and alert logic;
- metrics: position error, HPL, misleading information (MI), hazardously misleading
  information (HMI), availability, time-to-alert (TTA), detection and attribution latency;
- a Stanford diagram as an ASCII tally and an optional SVG;
- a negative control: the same flight with the monitor off.

Background and references: [docs/integrity-monitoring.md](../../docs/integrity-monitoring.md).

**v2** ([below](#v2-calibrated-on-measured-error-models)) re-runs everything with error models
measured in sibling samples. v1's zero-MI result does not survive them; heading/scale states
and measured R restore zero MI at 13-26 % availability instead of 41.7 %.

## What it simulates

| Item | Value |
|---|---|
| Vehicle | 2D, 30 m/s, weaving heading, 600 s |
| Filter state | `[px, py, vx, vy, bax, bay, bvx, bvy]`: position, velocity, accel bias, VIO velocity bias (Gauss-Markov, 0.3 m/s, 300 s) |
| INS | 10 Hz accelerometer, bias (0.03, -0.02) m/s^2, 0.05 m/s^2 noise; mean at 10 Hz, covariance at 1 Hz |
| VIO | 1 Hz velocity; true error = 0.5 % scale + 0.004 rad yaw + white noise; noisier over water |
| Visual geoloc (`vgeo`) | every 5 s, 5 m noise (filter assumes 8 m); random dropouts 15 % |
| `vgeo` failure modes | repetitive texture at 60-200 s and 450-540 s: 30 % of fixes are 60-250 m outliers; water at 200-290 s: no fixes; map misregistration at 300-380 s: (25, -25) m bias |
| GNSS | 1 Hz, 2 m noise (filter assumes 2.5 m); jammed 150-330 s; spoofed from 420 s, walk-off 1.5 m/s at 60 deg |
| MagNav (`--magnav`) | every 10 s, 20 m noise (filter assumes 25 m), no faults; a stand-in for any coarse independent absolute fix |

Three monitor modes run on the same random draw:

- `none` - no gate, no FDE. HPL = fault-free term only. This is the negative control.
- `gate` - chi-square gate (2 dof, 99.9 %, 13.816) on every measurement, no FDE.
- `full` - gate + SS bank + exclusion / alert + protection level with fault terms.

## Monitor design (full mode)

- Main filter fuses every admitted source. One sub-filter per monitored absolute source
  (GNSS, vgeo, MagNav) fuses everything except that source. VIO is not a monitored fault
  hypothesis; its correlated error is overbounded by the bias state instead.
- Test per sub-filter j: `d_j = |x_main - x_j|` (horizontal) vs
  `T_j = K_fa * sqrt(lambda_max(P_j - P_main))`, `K_fa = Q^-1(P_FA / (2 N))`.
- `HPL = max(K_ff * sigma_main, max_j(T_j + K_md * sigma_j))` with `P_FA = 1e-5`,
  `P_MD = 1e-3`, fault-free risk `1e-7`. `sigma` = largest eigenvalue of the 2x2 position
  covariance (worst direction).
- Available iff `HPL < AL` and no unresolved alert. AL defaults to 50 m.
- On detection, the number of recently active monitored sources decides what happens:
  - 1 active source: its branch is inconsistent with INS + VIO dead reckoning, so exclude it.
  - 3 or more: exclude the source whose branch has the largest normalised separation.
    After an exclusion the PL keeps the spread between candidate branches for 30 s, so a
    wrong exclusion still leaves the error bounded.
  - exactly 2: each branch keeps one of the two, so the fault is detectable but not
    identifiable. Raise an alert (unavailable), drop both, rewind the main filter to a
    snapshot 30 s old and replay INS + VIO only, then re-admit whichever source stays
    consistent with that dead-reckoning solution for 45 s of probation. The other one is
    blamed.
- Excluded sources stay out at least 30 s, then need 45 s of passing innovations against
  the main filter (one isolated failure allowed) before re-admission.

## Prerequisites

Python 3.10+ (tested on 3.14.7). No third-party packages.

## Run

```bash
cd samples/altpnt-integrity
python3 altpnt_integrity.py                          # seed 1, three modes, ASCII Stanford diagrams
python3 altpnt_integrity.py --csv run.csv --svg stanford.svg
python3 altpnt_integrity.py --magnav                 # add a third, independent absolute source
python3 altpnt_integrity.py --no-gnss                # alt-PNT only
python3 altpnt_integrity.py --al-sweep               # availability / MI / HMI vs alert limit
python3 altpnt_integrity.py --runs 20                # Monte Carlo over seeds 1..20 (~20 s)
python3 altpnt_integrity.py --no-faults              # nominal flight, should never alert
python3 -m unittest -v                               # v1 15 tests + v2 10 tests, ~15 s
```

## Observed output (python3.14.7, 2026-11-06)

Default run, seed 1:

```
seed=1 duration=600s AL=50 m  gnss=on faults=on magnav=off
P_FA=1e-05/epoch  P_MD=0.001  IR_ff=1e-07  gate=chi2(2) 13.816
                                              none                  gate                  full
HPE rms / p95 / max [m]       90.0 / 222.1 / 262.9    24.8 / 59.7 / 74.5      5.7 / 7.8 / 32.5
HPL median [m]                                 4.8                  22.3                  47.2
availability (HPL<AL)                       90.3 %                82.2 %                45.8 %
nominal epochs                                 302                   339                   275
unavailable epochs                               0                    96                   325
MI epochs (PE>PL, PL<AL)                        71                   145                     0
HMI epochs (PE>AL, PL<AL)                      169                     9                     0
unavail+MI (PE>PL>=AL)                          58                    11                     0
hazard episodes (PE>=AL)                         2                     1                     0
  missed (no alert)                              1                     0                     0
  max TTA [s] / >10s                        24 / 1                 9 / 0                 - / 0
detections / attributions                    0 / 0                 0 / 0                 2 / 2
  wrong attributions                             0                     0                     0
spoof detect / blame [s]                     - / -                 - / -               15 / 65
misreg detect / blame [s]                    - / -                 - / -               30 / 30

monitor log (full): 330s vgeo, 390s readmit vgeo, 435s ambiguous, 485s blame gnss, 485s readmit vgeo
MI/HMI epochs by condition (none): {'gnss jammed, texture zone': 20, 'gnss jammed, over water': 90, 'gnss jammed, map misregistered': 15, 'gnss spoofed': 83, 'gnss spoofed, texture zone': 90}
MI/HMI epochs by condition (full): none

Stanford diagram, mode=none
PL>= 500 |    .    .    .    .    .    .    .    .    .    .    .    \
PL>= 250 |    .    .    .    .    .    .    .    .    .    .    \    .
PL>= 150 |    .    .    .    .    .    .    .    .    .    \    .    .
PL>= 100 |    .    .    .    .    .    .    .    .    3    .    .    .
PL>=  75 |    .    .    .    .    .    .    .   16   10    .    .    .
PL>=  50 |    .    .    .    .    .    .    4   25    .    .    .    .
PL>=  40 |    .    .    3    .    .    \   12    .    .    .    .    . <AL
PL>=  30 |    .    2    4    .    \    1   12    .    .    .    .    .
PL>=  20 |    .    3    8   12   12   14    .    .    .    .    .    .
PL>=  10 |   19    1    \    .    2    7    .    .    .    .    .    .
PL>=   5 |   61    1    .    .    .    .    .    .    .    .    .    .
PL>=   0 |  195    4    6    6    6    6   16   16   35   68   10    .
         +------------------------------------------------------------
   PE>=       0    5   10   20   30   40   50   75  100  150  250  500  [m]
   nominal=302  unavailable=0  MI=71  HMI=169  unavail_MI=58

Stanford diagram, mode=full
PL>= 500 |    .    .    .    .    .    .    .    .    .    .    .    \
PL>= 250 |    .    .    .    .    .    .    .    .    .    .    \    .
PL>= 150 |   72   10    6   10    9    .    .    .    .    \    .    .
PL>= 100 |   47    .    .    .    .    .    .    .    \    .    .    .
PL>=  75 |   46    2    .    .    .    .    .    \    .    .    .    .
PL>=  50 |   86    .    .    .    .    .    \    .    .    .    .    .
PL>=  40 |   77    .    .    .    .    \    .    .    .    .    .    . <AL
PL>=  30 |  186    2    2    .    \    .    .    .    .    .    .    .
PL>=  20 |   41    3    .    \    .    .    .    .    .    .    .    .
PL>=  10 |    1    .    \    .    .    .    .    .    .    .    .    .
PL>=   5 |    .    \    .    .    .    .    .    .    .    .    .    .
PL>=   0 |    \    .    .    .    .    .    .    .    .    .    .    .
         +------------------------------------------------------------
   PE>=       0    5   10   20   30   40   50   75  100  150  250  500  [m]
   nominal=275  unavailable=325  MI=0  HMI=0  unavail_MI=0
```

The grid counts epochs per (PE, PL) bin; `\` marks the diagonal bin. Epochs right of the
diagonal are MI; right of 50 m with PL below 50 m they are HMI. The region tally under each
grid is computed per epoch, not per bin. In the SVG, a few `unavailable` points sit below
the AL line: those are epochs under an unresolved two-source alert.

Alert-limit sweep (seed 1), availability % / MI / HMI epochs:

```
seed=1 magnav=off: availability % / MI / HMI epochs vs alert limit
 AL [m]                none                gate                full
     25    82.5 /  14 / 194    60.7 /  27 /  70     1.3 /   0 /   0
     50    90.3 /  71 / 169    82.2 / 145 /   9    45.8 /   0 /   0
     75    95.2 / 115 / 154    91.5 / 165 /   0    58.0 /   0 /   0
    100    99.5 / 172 / 123    98.2 / 165 /   0    66.0 /   0 /   0
    150   100.0 / 220 /  78   100.0 / 165 /   0    73.8 /   0 /   0
    250   100.0 / 288 /  10   100.0 / 165 /   0    91.7 /   0 /   0
seed=1 magnav=on: availability % / MI / HMI epochs vs alert limit
 AL [m]                none                gate                full
     25    83.3 /  18 / 192    70.3 /  32 /  72     5.3 /   0 /   0
     50    92.5 /  84 / 166    91.2 / 146 /   0    50.8 /   0 /   0
     75   100.0 / 121 / 129   100.0 / 146 /   0    63.0 /   0 /   0
    100   100.0 / 137 / 113   100.0 / 146 /   0    85.8 /   0 /   0
    150   100.0 / 172 /  78   100.0 / 146 /   0    90.8 /   0 /   0
    250   100.0 / 241 /   9   100.0 / 146 /   0    90.8 /   0 /   0
```

Monte Carlo, 20 seeds x 600 epochs per configuration, AL = 50 m. `MI*` counts MI + HMI +
unavailable-and-MI epochs; "wrong blame" counts exclusions or blames of a source that was
not faulty in the preceding window.

| Configuration | Mode | Avail % | MI* | HMI | Missed hazards | Wrong blame |
|---|---|---|---|---|---|---|
| default | none | 90.9 | 5127 | 3217 | 25 | 0 |
| default | gate | 89.0 | 4614 | 2371 | 16 | 0 |
| default | full | 41.7 | 0 | 0 | 0 | 0 |
| `--magnav` | none | 93.0 | 4762 | 3236 | 29 | 0 |
| `--magnav` | gate | 92.2 | 3962 | 1912 | 15 | 0 |
| `--magnav` | full | 49.5 | 0 | 0 | 0 | 0 |
| `--no-gnss` | none | 90.8 | 5193 | 1173 | 80 | 0 |
| `--no-gnss` | gate | 89.7 | 1721 | 10 | 0 | 0 |
| `--no-gnss` | full | 5.0 | 0 | 0 | 0 | 0 |
| `--no-gnss --magnav` | none | 92.8 | 4840 | 1031 | 76 | 0 |
| `--no-gnss --magnav` | gate | 92.0 | 1552 | 0 | 0 | 0 |
| `--no-gnss --magnav` | full | 5.4 | 8 | 0 | 0 | 11 |
| `--no-faults` (with or without `--magnav`) | all three | 100.0 | 0 | 0 | 0 | 0 |
| `--spoof-rate 0.3` | none | 90.9 | 4883 | 498 | 28 | 0 |
| `--spoof-rate 0.3` | gate | 90.1 | 4767 | 266 | 20 | 0 |
| `--spoof-rate 0.3` | full | 48.6 | 0 | 0 | 0 | 0 |
| `--spoof-rate 0.3 --magnav` | full | 57.1 | 0 | 0 | 0 | 0 |

The 8 `MI*` epochs in `--no-gnss --magnav full` are all unavailable-and-MI (PE > PL >= AL):
the system had already declared itself unusable.

## How to read it

- **Negative control.** With the monitor off, the filter reports a small HPL (4.8 m
  median) while following the spoofer to 263 m of error: 169 HMI epochs on seed 1, 3217
  over 20 seeds. Every one of those epochs looked healthy to a downstream consumer.
- **A gate is not a monitor.** The gate removes the repetitive-texture outliers when the
  filter is confident, but it lets them through when the filter is uncertain (GNSS jammed),
  absorbs the slowly growing misregistration bias, then *rejects the healthy GNSS* when
  it returns at 330 s (61 consecutive `gate:gnss` rejections, 330-390 s, with 30-37 m
  error and a PL that claims less). That is why `gate` has more
  MI epochs than `none` on seed 1. The spoofer walks it off too.
- **Full monitor: zero MI/HMI in every configuration above with GNSS, at a cost in
  availability.** With one absolute alt-PNT source the fault-protection term of the PL is
  the drift of INS + VIO, so it grows without bound between independent checks; that is
  most of the 325 unavailable epochs on seed 1 and the 5 % availability without GNSS.
- **Two sources detect, three identify.** At 435 s the spoof is detected (15 s after
  onset) but the GNSS and vgeo branches each contain one of the two suspects, so the monitor
  alerts, rewinds, and needs 50 s of dead-reckoning consistency to blame GNSS. With
  `--magnav` the spoof is excluded directly (28 s after onset).
- **Wrong blame without a third source.** In `--no-gnss --magnav`, the 35 m map
  misregistration is small against 45 s of VIO drift, so either source can pass probation
  first; there were 11 wrong blames over 20 seeds. Integrity held (the alert was raised); continuity
  did not. The fix is a better-characterised reference (better VIO, a third independent
  source), not a tighter threshold.
- **Slow spoof.** At 0.3 m/s walk-off the full monitor still had zero MI over 20 seeds,
  but only because the PL grows while GNSS and vgeo disagree. Probation needs the spoof
  offset to outgrow the dead-reckoning bound within 45 s; slower spoofers win that race.

## Extend it in a hackathon

1. Replace the synthetic vgeo fixes with real matcher output from
   [samples/visual-geolocalization-lightglue](../visual-geolocalization-lightglue/) and
   derive R per fix from match statistics (inliers, reprojection error) instead of a constant.
2. Replace the single-Gaussian overbound with a mixture or an uncertainty-aware matcher
   (UASTHN outputs a homography uncertainty) and see how the PL changes.
3. Plug a TRN fix from [samples/terrain-relative-nav-pf](../terrain-relative-nav-pf/) or a
   MagNav fix from [samples/magnav-quickstart](../magnav-quickstart/) in as a third
   absolute source via `MEAS` and `_available_sources`.
4. Feed the per-epoch CSV into a dashboard: HPL vs HPE over time, monitor log as markers.
5. Port the bank to `filterpy` or a GTSAM fixed-lag smoother; the SS test only needs the
   main and sub-solution means and covariances.

## Pitfalls

- PLs are only as honest as the noise models. Here the filter assumes larger noise than
  the truth (2.5 vs 2 m, 8 vs 5 m, 25 vs 20 m) and a VIO bias state that covers the true
  scale and yaw error. Make the filter optimistic and MI appears; check that before
  quoting numbers.
- `P_j - P_main` as the separation covariance assumes optimal, consistent filters. With
  gating the sub-filters accept different measurement sets and that assumption is only
  approximate; the code floors the separation sigma at 0.5 m.
- Map misregistration is a common-mode fault if two "independent" sources share the same
  orthophoto or DEM. The SS bank cannot see it then.
- The 2D model has no attitude error. A real INS has heading error that makes the drift
  terms larger and the PL wider.
- Thresholds (AL, P_FA, P_MD, probation times) are illustrative choices for this sample,
  not values taken from a standard.
- Results depend on the seed. Quote the Monte Carlo table, not one run.

## v2: calibrated on measured error models

v1 above reports zero MI with error models I chose. Four sibling samples have since measured
those errors on real data, and the measurements disagree with v1's choices. v2 keeps the same
flight, fault timeline (jam, spoof, texture outliers, water, 35 m misregistration) and SS
monitor, replaces the nominal error models with measured ones, and adds the filter changes
the measurements call for. `altpnt_integrity.py` is unchanged: the v1 numbers above still
reproduce, and the v2 Monte Carlo re-runs them as its `assumed` rows (identical to the table
above: 90.9 / 5127 / 3217 for `none`, 41.7 / 0 / 0 for `full`, 5.0 % without GNSS).

Ran 2026-11-06 with python3.14.7 (and 3.12.14), stdlib only.

### 1. Measured error models (`calibration.py` => `calibration.json`)

`calibration.py` reads committed result files from the sibling samples and writes every
number below into `calibration.json` with its source path. `python3 calibration.py --check`
recomputes and compares.

| Model | Measured value | Source file | v1 assumed |
|---|---|---|---|
| Relative-source heading error, OpenVINS (UZH-FPV indoor, 50 s) | 3.58 deg whole-run fit; per >= 50 m window 0.57 => 5.23 deg, monotonic (+0.17 deg/s over 48 s) | `relative-nav-benchmark/results/altpnt_from_vo.json`, `results/vio/uzhfpv_indoor_forward_3_{gt,openvins}.tum` | 0.23 deg constant |
| Heading error, KISS-ICP (KITTI 04, 28 s) | -0.13 deg fit; windows within 0.53 deg | `results/lidar/kitti04_{gt,kiss_icp}.tum` | same |
| Heading error, nadir VO + attitude (VPAIR, 8.9 km) | -0.03 deg fit; windows within 2.77 deg | `results/aerial/vpair_{gt,attitude_aided_yaw_bias_0deg}.tum` | same |
| Scale error | OpenVINS -0.13 +- 0.36 %, KISS-ICP +0.12 +- 0.72 %, VPAIR -0.61 +- 3.27 % (windowed; VPAIR wanders -4.9 % to +7.4 %) | same TUM pairs | 0.5 % constant |
| Velocity white noise | 2.96 % (OpenVINS), 0.87 % (KISS-ICP), 2.56 % (VPAIR) of speed => 0.89 / 0.26 / 0.77 m/s at 30 m/s | `altpnt_from_vo.json` | 0.08 m/s |
| Visual geoloc availability | 246 / 425 fixes (58 %), real ALIKED + LightGlue, cross-season NAIP; mean no-fix run 4.4 s, mean fix run 5.1 s at 30 m/s, longest gap 17 nodes (340 m) | `golden-demo/data/vgeo_table.json` | 85 % (15 % dropouts) |
| Visual geoloc error | 2D median 3.3 m, p95 6.3 m, max 9.9 m, with a consistent (+3.41, -0.79) m registration bias | same | zero-mean 5 m |
| Real UAV frames | 1 fix in 50 frame x config attempts (best: 1 / 5 frames, ALIKED vs NAIP 2019, tight prior), error 11.0 m | `geoloc-license-clean/out/results.json`, `out/results_real_tight.json` | - |
| Wrong geoloc fixes (> 20 m) | 0 of 296 accepted fixes (golden table, synthetic cross-season, real; same-map synthetic excluded) => rate <= 1.0e-2 (95 %, exact binomial) | same three files | 30 % in texture zones |
| TRN error vs its own particle spread | true error < 1x / 2x / 3x spread on 82 / 99 / 100 % of 4720 updates; worst region (hilly) 61 / 97 / 100 % | `terrain-heightmap-pf/out/v2_results.json` | - |
| TRN spread distribution | log-normal through P(spread <= 50 m) = 0.513 and P(<= 100 m) = 0.672 => median 47 m | same | - |
| TRN fault rate (error > 3x spread) | 0 of 4720 => <= 6.3e-4 per update (95 %) | same | - |
| SS detection with real geoloc (cross-check, not a model input) | SS TTD 22.5 s at 1 m/s position drag; chi-square detector 4/4 false alarms on no-spoof flights from the 3-5 m registration bias | `golden-demo/data/mc_summary.json` | - |

### 2. What v2 adds (`altpnt_v2.py`)

- **Heading and scale states.** `Ekf2` state `[px, py, vx, vy, bax, bay, s, psi]`; VIO is
  `z = (1 + s) R(psi) v` with an analytic Jacobian (checked against finite differences in the
  tests). s and psi are Gauss-Markov with the measured envelope as sigma (5.23 deg, 3.27 %) and
  a 300 s correlation time. The correlation time is assumed: the measured runs are 27-197 s long.
- **Overbounding.** Folded-CDF Gaussian overbound of the golden-table per-axis errors in the
  style of DeCleene (2000): the smallest zero-mean sigma whose two-sided tail lies above the
  empirical tail, using a 95 % Wilson upper bound on each tail fraction beyond the median.
  Result: 5.38 m per axis, binding at the bias. The Rife et al. (2006) paired form splits it
  into a 3.5 m bias bound plus a 2.7 m core sigma. v2 puts sigma into R and adds the bias to
  the PL and to each SS threshold, because a Kalman filter averages fixes as if independent
  and a registration bias does not average out. DeCleene's guarantee needs symmetric unimodal
  errors; the measured errors are biased, which is the case paired overbounding was made for.
- **Fault priors per source.** `K_md_j = Q^-1(IR_F / (N P_j))` with IR_F = 1e-5 per epoch
  (illustrative): vgeo 1.0e-2 per fix and TRN 6.3e-4 per update from the bounds above; GNSS
  1e-2 per epoch is an assumption (nothing measured a spoofing rate).
- **TRN as a third source with R from its own confidence.** Per-axis sigma = 1.07 x spread /
  sqrt(2), the inflation that makes the Rayleigh coverage match the worst measured region at
  1x and 2x spread. The TRN source rides in v1's `magnav` slot so v1 code can consume it too.
- **Measured world.** `simulate()` reuses v1's truth, IMU and GNSS draws per seed, then
  replaces VIO (fitted heading and scale with random sign, GM evolution, white as a fraction
  of speed), vgeo (two-state Markov availability with the measured run lengths, errors
  bootstrapped from the 246 real residuals and rotated per seed as a different map tile,
  outliers at the 1.0e-2 bound everywhere plus v1's 30 % in texture zones) and adds TRN.

Ladder (each step keeps the previous ones): `L1` heading + scale states; `L2` + measured VIO
R, folded overbound R + bias term (`L2p`: paired sigma R + bias term, `L2n`: no bias term);
`L3` + fault priors; `L3o/k/v` tuned to one relative source instead of the envelope; `L4` +
TRN with R from spread (`L4c`: TRN with constant 25 m R).

### 3. Monte Carlo (`python3 altpnt_v2.py --runs 20`, 182 s, `results/v2_mc.json`)

20 seeds x 600 epochs per row (12 000 epochs), AL = 50 m unless stated. MI* = MI + HMI +
unavailable-and-MI. "Wrong" = exclusions or blames of a source not faulty in the preceding
window.

| World | Filter | Avail % | MI* | HMI | Wrong | HPE max m | Avail % at AL 100 | HMI at AL 100 |
|---|---|---|---|---|---|---|---|---|
| assumed (v1) | v1 full | **41.7** | **0** | **0** | 0 | 40 | 60.2 | 0 |
| measured: OpenVINS + real geoloc | v1 none | 89.9 | 6767 | 3279 | 0 | 350 | 99.0 | 2700 |
| measured | v1 full | **8.3** | **8901** | **18** | 5 | 31 920 | 9.8 | 50 |
| measured | L1 states | 6.8 | 26 | 0 | 7 | 661 | 32.5 | 0 |
| measured | L2 measured R + folded overbound + bias | 13.9 | 0 | 0 | 3 | 271 | 33.9 | 0 |
| measured | L2p paired sigma + bias | **26.1** | 0 | 0 | 1 | 272 | 35.3 | 0 |
| measured | L2n folded, no bias term | 19.6 | 0 | 0 | 3 | 271 | 34.3 | 0 |
| measured | L3 + fault priors | 12.9 | 0 | 0 | 3 | 271 | 33.6 | 0 |
| measured | L3o tuned to OpenVINS only | 12.9 | 0 | 0 | 0 | 203 | 33.5 | 0 |
| measured + TRN | v1 full (TRN as constant-R magnav) | 12.3 | 6809 | 102 | 34 | 31 426 | 20.7 | 264 |
| measured + TRN | L4c TRN constant R | 12.7 | 103 | 0 | 22 | 271 | 34.4 | 0 |
| measured + TRN | L4 TRN R from spread | 16.7 | 221 | 0 | 13 | 272 | 41.1 | 0 |
| measured: KISS-ICP + real geoloc | v1 full | 38.8 | 0 | 0 | 0 | 70 | 62.0 | 0 |
| measured: KISS-ICP | L3 (envelope) | 13.1 | 0 | 0 | 2 | 271 | 33.9 | 0 |
| measured: KISS-ICP | L3k tuned to KISS-ICP | 37.9 | 0 | 0 | 11 | 101 | 58.1 | 0 |
| measured: nadir VO (VPAIR) | v1 full | 19.0 | 6180 | 3 | 9 | 1684 | 25.1 | 126 |
| measured: nadir VO | L3v tuned to VPAIR | 15.5 | 0 | 0 | 1 | 271 | 36.0 | 0 |
| map-age stress (20 % availability, +11 m bias) | v1 full | 5.1 | 8802 | 14 | 9 | 31 920 | 9.8 | 77 |
| map-age stress | L3 | 4.9 | **374** | 0 | 7 | 761 | 19.1 | **2** |
| assumed, GNSS off | v1 full | 5.0 | 0 | 0 | 0 | 55 | 9.8 | 0 |
| measured, GNSS off | v1 full | 5.1 | 7516 | 31 | 11 | 31 818 | 10.8 | 139 |
| measured, GNSS off | L3 | 2.3 | 0 | 0 | 0 | 260 | 3.9 | 0 |
| assumed (v1) | L3 (v2 tuning in v1's world) | 21.3 | 0 | 0 | 0 | 272 | 34.4 | 0 |

Region breakdown of the non-zero v2 MI* cells (`results/v2_mc.json` has every row; breakdown
re-run separately over the same 20 seeds): `L1` 26 = 26 unavailable-and-MI, 21 of them during
a two-source ambiguity alert; `L4` 221 = 221 unavailable-and-MI, 220 during an alert; `L4c`
103 = 10 MI with the system **claiming availability** + 93 unavailable-and-MI; stress `L3` 374
= 374 unavailable-and-MI, none during an alert (PE > PL >= AL: the system said "unusable",
but its PL was still too small).

Seed 1 (`python3 altpnt_v2.py`):

```
seed=1 AL=50 m gnss=on
world     filter mode   avail %   MI*   HMI  HPE rms  HPE max  HPL med  monitor log
assumed   v1     none      90.3   298   169     90.0    262.9      4.8
assumed   v1     full      45.8     0     0      5.7     32.5     47.2  330s vgeo, 435s ambiguous, 485s blame gnss
measured  v1     none      89.7   372   205    124.9    349.5      4.8
measured  v1     full      33.0   329     0    499.2   1099.8    138.8
assumed   L3     full      20.2     0     0      8.4     45.4    226.6  330s vgeo, 434s gnss
measured  L1     full       7.7     0     0     26.0     85.1    180.9  330s vgeo, 445s ambiguous, 535s blame gnss
measured  L2     full      15.5     0     0     13.2     72.8    222.1  330s vgeo, 438s gnss
measured  L3     full      14.3     0     0     13.2     72.8    224.6  330s vgeo, 438s gnss
```

### 4. What changed vs v1, honestly

- **v1's zero-MI result does not survive measured errors.** Same monitor, same faults,
  measured heading and geoloc: MI* goes from 0 to 8901 epochs (74 %) and HMI from 0 to 18;
  without GNSS MI* is 7516 of 12 000 (63 %), in line with the 60 % that
  relative-nav-benchmark found with a constant 3.6 deg heading. The v1 filter diverges (HPE up
  to 32 km) because a 3.6-5 deg heading error at 30 m/s is a 1.9-2.7 m/s velocity bias against
  a 0.3 m/s bias prior. Which fixes the gate rejected on the way was not inspected per seed.
- **Where v1's assumptions held: KISS-ICP-grade heading.** With the LiDAR odometry model
  (0.5 deg) and real geoloc, v1 full stays at 0 MI and 38.8 % availability. The geoloc
  measurements alone (58 % availability, 3.5 m bias, 5.4 m overbound vs v1's 8 m R) did not
  break v1. The heading model did.
- **The fix that removes MI: heading/scale states plus measured R.** L1 alone cuts MI* from
  8901 to 26 (all unavailable) at 6.8 % availability. L2 reaches 0 MI* at 13.9 %; the paired
  overbound L2p at 26.1 %. In this Monte Carlo the bias term did not change MI (L2n is also 0),
  so its necessity is not shown here; it costs about 6 points of availability.
- **The price: availability at AL 50 m is 13-26 %, not 41.7 %.** At AL 100 m it is 34-41 %.
  A filter that is honest about a 5 deg heading uncertainty is also a weaker referee: a
  1.5 m/s spoof walk-off at 30 m/s looks like a 2.9 deg heading error, inside the prior, so
  probation can re-admit a spoofer and blame vgeo (seen in the `assumed` / L3 runs, seeds 2-4:
  `readmit:gnss blame:vgeo`). Integrity held (the PL grew past the AL); continuity did not.
- **TRN confidence as R is worth it; constant R is not.** With TRN as a third source, R from
  the particle spread raised availability from 12.9 % to 16.7 % (AL 50) and 33.6 % to 41.1 %
  (AL 100) with no available-MI epochs. The same TRN with a constant 25 m R gave 10 epochs of
  MI with the system claiming availability.
- **Fault priors** cost about one point of availability and removed nothing in this run;
  their value is that K_md is now traceable to a measured rate, not that the numbers moved.
- **The biggest lever is the heading reference, not the monitor.** Tuned to the source it
  actually flies (L3k, KISS-ICP-grade heading), v2 is at 37.9 % availability with 0 MI, but
  11 wrong blames over 20 seeds (not diagnosed; L3 with the envelope had 2).
  With the OpenVINS-grade envelope, the same filter is at 13 %.
- **Overbounds do not transfer across conditions.** Under map-age stress (20 % fix
  availability and an extra 11 m bias, the one real eBee fix) the 3.5 m bias overbound from
  the golden table is exceeded: 374 epochs with PE > PL, all while flagged unavailable at AL
  50 m, but 2 HMI epochs at AL 100 m. An overbound is only as good as the conditions of the
  data it came from.
- **v2 tuning in v1's world costs half the availability** (21.3 % vs 41.7 %): if the world
  really were as v1 assumed, v2 would be needlessly pessimistic. That is the trade being made.

### v2 limits

- Measured runs are short (OpenVINS 48 s, KISS-ICP 27 s, VPAIR 197 s) and replayed for 600 s
  at 30 m/s. Magnitudes are measured; the 300 s correlation time and the random sign are
  assumptions.
- The heading model is the OpenVINS indoor FPV run. An outdoor fixed-wing VIO may be closer to
  KISS-ICP or worse; nobody measured it here.
- Geoloc residuals come from one park, one season pair, rendered frames (no tilt, no real
  camera). The real-frame evidence is 1 fix.
- TRN spread distribution is fitted to two published shares, not to the full sample; the
  per-region coverage numbers are point estimates (per-region counts are not stated in the
  source JSON).
- Multi-fault hypotheses (spoof + vgeo outlier) are not monitored although their joint prior
  (1e-4) exceeds IR_F; the ARAIM recipe would monitor them.
- 12 000 epochs per row cannot validate integrity risks below about 1e-4.

Run v2:

```bash
python3 calibration.py --check        # recompute calibration.json from sibling samples, compare
python3 altpnt_v2.py                  # seed 1, v1 vs v2 filter in assumed and measured worlds
python3 altpnt_v2.py --no-gnss
python3 altpnt_v2.py --runs 20        # full matrix, ~3 min, writes results/v2_mc.json
python3 -m unittest -v test_altpnt_v2 # 10 tests, ~1.5 s
```

## Files

- `altpnt_integrity.py` - scenario, sensor simulation, EKF, monitor bank, metrics, CLI.
- `stanford.py` - region classification, ASCII grid, SVG writer.
- `mat.py` - list-of-lists matrix helpers.
- `test_altpnt_integrity.py` - unit and scenario tests (nominal no-alert, no MI in full
  mode, negative control shows HMI, spoof detected and blamed, outputs).
- `calibration.py` - v2: extracts measured error models from sibling samples into `calibration.json`.
- `altpnt_v2.py` - v2: measured world, heading/scale-state EKF, overbound + bias term, fault
  priors, TRN R from spread, Monte Carlo matrix.
- `results/v2_mc.json` - v2 Monte Carlo output (20 seeds, AL 50 and 100 m).
- `test_altpnt_v2.py` - v2 tests: calibration reproduces from source files, overbound, Jacobian,
  heading state converges, v1 misleads and v2 bounds the measured world on seed 1.
