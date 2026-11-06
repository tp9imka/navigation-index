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
python3 -m unittest -v                               # 15 tests, ~10 s
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

## Files

- `altpnt_integrity.py` - scenario, sensor simulation, EKF, monitor bank, metrics, CLI.
- `stanford.py` - region classification, ASCII grid, SVG writer.
- `mat.py` - list-of-lists matrix helpers.
- `test_altpnt_integrity.py` - unit and scenario tests (nominal no-alert, no MI in full
  mode, negative control shows HMI, spoof detected and blamed, outputs).
