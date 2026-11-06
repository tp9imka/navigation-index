# C-UAS classifiers on public data: radar tracks and RF spectra

<!-- about: repo:nrc-cnrc/cuas-sensing-dataset, repo:al-sad/dronerf -->

Two small, defensive drone-detection baselines that run end to end on real, openly
licensed recordings, plus a bridge that reports detections to TAK as Cursor-on-Target.

| Part | Data | Task | Model |
|---|---|---|---|
| `train_radar.py` | NRC UAV vs bird radar tracks (Echodyne EchoGuard, K-band, 10 Hz) | UAV vs bird per track | HistGradientBoosting, RandomForest on 24 track features |
| `train_rf.py` | DroneRF low-band subset (2.4 GHz captures) | drone vs background; 4-class identification | RandomForest, HistGradientBoosting on 69 PSD/burstiness features |
| `cuas_cot.py` | radar session + trained model | UAS detections => CoT `a-u-A-M-H-Q` | reuses `../mavlink-to-tak-cot/cot.py` |

Receive-only. Nothing here transmits, and nothing here goes past detection and reporting.

## Data and licences

| Dataset | Licence | What is downloaded | Size |
|---|---|---|---|
| [nrc-cnrc/CUAS-sensing-dataset](https://github.com/nrc-cnrc/CUAS-sensing-dataset) | CC BY 4.0 (repo `LICENSE`, GitHub API) | 47 labelled `.xlsx` sessions (Demo-0/2/3/5/6) + `metadata/` | 59 MB on disk (du) |
| [DroneRF](https://doi.org/10.17632/f4c2b4n755.1) (Mendeley f4c2b4n755) | CC BY 4.0 (Mendeley API `data_licence`) | 4 of 23 RARs: `00000_L1` background, `10000_L` Bebop, `10100_L` AR Drone, `11000_L1` Phantom | 692 MB RAR, **6.6 GB extracted** CSV text |

Neither licence restricts defence use; attribution is required (cite Mehta, Bolic,
Mantegh, Vidal for the radar data; Al-Sa'd et al. 2019 for DroneRF).

Not used: DroneDetect (Essex) and CardRF both need an IEEE DataPort login, so they fail
the "downloadable without login" bar; their licence terms were not checked. RFUAV
(Apache-2.0) is 299 GB in total, see [the RF dataset card](../../docs/dataset-cards/drone-rf-datasets.md).

## Run

```bash
VENV=/path/to/venv
uv venv "$VENV" --python 3.12 && uv pip install --python "$VENV/bin/python" -r requirements.txt
python3 download_data.py radar        # ~50 s here
python3 download_data.py rf           # ~10 min here, needs bsdtar (macOS built-in; Debian: libarchive-tools)
"$VENV/bin/python" -m pytest -q test_features.py
"$VENV/bin/python" train_radar.py --save-model out/radar_model.pkl
"$VENV/bin/python" train_rf.py --save-model out/rf_model.pkl
"$VENV/bin/python" cuas_cot.py --model out/radar_model.pkl \
    --xlsx data/radar/data/Demo-6/Echodyne_Log_20210318_105543.xlsx \
    --site 45.55 -73.75 30 --boresight 0 --out out/cot_events.xml
```

`data/` and `out/` are git-ignored. Metrics land in `out/radar_metrics.json` and `out/rf_metrics.json`.

## 1. Radar: UAV vs bird from tracks

**Features** (`radar_features.py`, per track, tracks with fewer than 10 updates dropped):
speed mean/std/p90/max and coefficient of variation; vertical speed and climb ratio;
acceleration magnitude from successive tracker velocities; horizontal turn rate;
median 3D curvature `|v x a| / |v|^3`; straightness (net displacement / path length);
duration; RCS mean/std/median/p10/p90/IQR and fraction of updates without RCS.
Range is deliberately left out (UAVs were flown at chosen ranges; it would leak scenario).

Frame facts checked on the data, not taken from docs: `posY` is vertical
(`posY - range*sin(elevation)` median |error| 0.0 m over all 47 files) and `azimuth =
atan2(posX, posZ)` (median error 1.6e-5 deg, checked on one Demo-6 file). The `.xlsx` files have no timestamps, so
dt = 0.1 s from the documented 10 Hz rate; position-difference speed / tracker speed has a
median ratio of 1.10 across files, consistent with that.

**Leakage control.** Labels come from `metadata/track_labels.csv` (normalized), joined on
file + `SystemTrackID`. Splits are by recording session, never by track: Demo-0 recorded
with two radars at once (`-R1`/`-R2`) so both files of a session are one group. 510
tracks (379 BIRD, 131 UAV) in 42 sessions.

**Results** (run 2026-11-06, Apple M2 Max, Python 3.12.14, scikit-learn 1.9.1):

5-fold GroupKFold by session, pooled over folds:

| Model / features | Bal. acc | ROC AUC | UAV P / R | BIRD P / R | Confusion [[B->B, B->U], [U->B, U->U]] |
|---|---|---|---|---|---|
| HistGB, kinematic + RCS | 0.928 | 0.964 | 0.913 / 0.885 | 0.961 / 0.971 | [[368, 11], [15, 116]] |
| RandomForest, kinematic + RCS | 0.908 | 0.966 | 0.924 / 0.840 | 0.946 / 0.976 | [[370, 9], [21, 110]] |
| HistGB, kinematic only | 0.903 | 0.944 | 0.916 / 0.832 | 0.944 / 0.974 | [[369, 10], [22, 109]] |
| HistGB, all minus duration | 0.927 | 0.961 | 0.906 / 0.885 | 0.961 / 0.968 | [[367, 12], [15, 116]] |
| Majority class | 0.500 | 0.500 | 0 / 0 | 0.743 / 1.0 | [[379, 0], [131, 0]] |

Cross-site (train Alma 2019 Demo-0, test Laval 2020-21 Demo-2/3/5/6; 89 test tracks, 22 BIRD / 67 UAV):

| Model | Bal. acc | ROC AUC | UAV P / R | BIRD P / R | Confusion |
|---|---|---|---|---|---|
| HistGB | 0.902 | 0.926 | 0.968 / 0.896 | 0.741 / 0.909 | [[20, 2], [7, 60]] |
| RandomForest | 0.918 | 0.942 | 0.983 / 0.881 | 0.724 / 0.955 | [[21, 1], [8, 59]] |

RandomForest top importances (fit on all 510): accel_std 0.18, rcs_std 0.10,
duration_s 0.09, accel_mean 0.08, speed_mean 0.07. Dropping duration (it partly reflects
how long annotators kept a track) changes nothing material, and RCS adds about 0.02 AUC
over kinematics alone.

Runtime: feature extraction 25 s (openpyxl parsing dominates); RandomForest 5-fold CV 3 s;
HistGB 5-fold CV 47-94 s across two runs (it was sharing the CPU with other jobs, so treat
those timings as loose); whole script 104-329 s.

**CoT demo** (`cuas_cot.py`, model trained on Alma only, run on Laval session
`Echodyne_Log_20210318_105543`): 110 tracks with >= 10 updates, 31 reported at P(UAV) >= 0.5.
Of those 31: 9 labelled UAV, 1 labelled HUMAN, 21 unlabelled. The session's other 5 labelled
UAV tracks (of 14) scored below 0.5. The 21 unlabelled hits have no ground truth (could be UAV track fragments or
clutter); the classifier was never trained on clutter, humans or vehicles, so expect false alarms
on those in a live feed.

## 2. RF: DroneRF detection and identification

Each DroneRF segment file is one CSV line of 10,000,000 real-valued integer samples
(counted). The sample rate is not in the Mendeley description or the repo README and
was not verified here, so features use normalized frequency.

**Features** (`rf_features.py`, per window, 10 windows per segment): Welch PSD (nperseg
2048) pooled into 64 equal bands, log10, minus the window's median band so receiver gain
drops out; spectral flatness; time-envelope burstiness from 1000-sample block power
(p99 over median in dB, std in dB, kurtosis, active fraction).

**Splits.** Windows of a segment never straddle train/test. (a) 5-fold GroupKFold by
segment. (b) Temporal holdout: per class the highest-numbered 30% of segments are test.
73 segments: 21 background, 21 Bebop, 21 AR Drone, 10 Phantom; 730 windows.

| Task / model | Split | Bal. acc | Per-class P / R | Confusion (rows = true) |
|---|---|---|---|---|
| detect, RandomForest | GroupKFold | 0.982 | bg 0.958/0.981, drone 0.992/0.983 | [[206, 4], [9, 511]] |
| detect, RandomForest | temporal | 0.977 | bg 0.958/0.971, drone 0.988/0.982 | [[68, 2], [3, 167]] |
| detect, HistGB | temporal | 0.994 | bg 0.972/1.0, drone 1.0/0.988 | [[70, 0], [2, 168]] |
| identify 4-class, RandomForest | GroupKFold | 0.940 | AR 0.926/0.952, bg 0.933/0.990, Bebop 0.970/0.919, Phantom 0.978/0.900 | see `out/rf_metrics.json` |
| identify 4-class, RandomForest | temporal | 0.852 | AR 0.783/0.929, bg 0.944/0.971, Bebop 0.865/0.643, Phantom 0.788/0.867 | [[65,1,4,0],[0,68,2,0],[16,2,45,7],[2,1,1,26]] (AR, bg, Bebop, Phantom) |
| identify 4-class, HistGB | temporal | 0.856 | Bebop recall 0.643 again | `out/rf_metrics.json` |

Runtime: feature extraction 95 s for 73 segments (CSV text parse about 1 s per segment);
RandomForest fit+predict under 2 s per task; whole script 219 s.

The drop from GroupKFold to temporal holdout for identification (0.94 => 0.85) shows how much
adjacent segments share. Bebop is the weak class: a quarter of its held-out windows read as AR.

## Caveats that matter more than the numbers

- **DroneRF: one recording session per class.** Every class in this subset comes from a single
  archive, so "class" and "session" coincide; the classifier can lean on session artefacts
  (noise floor, interferers that day). No split inside this subset can remove that. Low band
  only, one flight mode per drone (mode 00, on and connected), 2019-era drones. Do not quote
  these numbers as field detection performance.
- **Radar: sessions differ in what was flown.** UAV pilots flew scripted manoeuvres at chosen
  ranges; birds are whatever was there. Cross-site holds up (0.90-0.92 balanced accuracy), but
  the test site has only 22 bird tracks. MIXED (376), HUMAN, VEHICLE tracks are excluded from
  training, so this is a two-class model, not a clutter rejector.
- **CoT placement is illustrative.** The dataset publishes no radar site coordinates, heading or
  tilt. `--site`/`--boresight` are placeholders; the sign of azimuth (left vs right of boresight)
  is assumed clockwise-positive and not verified; `elevation` is relative to the radar horizontal
  so an unknown tilt shows up as wrong height (one demo track came out at -72 m HAE).
- CoT `type` is `a-u-A-M-H-Q` (unknown, Air/Mil/Rotor/Drone per `CoTtypes.xml`), `how` is `m-a`
  ("tracker" in `CoTtypes.xml`) instead of cot.py's GPS `m-g`. `--affiliation s|h` exists for an
  operator decision; the classifier never sets hostile on its own. `ce`/`le` stay "unknown" because
  the data has no position error figures. Not checked: rendering in ATAK/WinTAK.

## Tests

`test_features.py`, 11 tests on synthetic fixtures (no downloads): straight and circular
tracks (curvature 1/R, turn rate v/R, accel v^2/R), vertical axis, RCS NaN handling,
R1/R2 session merge, xlsx + label join with short-track drop, PSD tone placement, gain
invariance, burstiness, DroneRF filename parsing and segment windows, CoT event fields.
Negative control: setting `VERTICAL_AXIS = 2` and disabling the R1/R2 merge fails 4 tests.

## Next steps

- Train the radar model with HUMAN/VEHICLE and the Demo-4 raw logs' clutter tracks as a
  third "other" class, and compare against the radar's own `probUav` in those logs.
- DroneRF: add the H band and the other flight modes (all 23 RARs, 4 GB) and split by flight
  mode, which is closer to a session-held-out test.
- Swap the tabular RF classifier for a small CNN on the band-power spectrogram once a second
  dataset (RFUAV single-device RAR) gives cross-dataset testing.
