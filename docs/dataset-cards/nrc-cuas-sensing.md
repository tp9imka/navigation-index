# NRC UAV vs bird radar tracks (CUAS-sensing-dataset)

<!-- about: repo:nrc-cnrc/cuas-sensing-dataset, sample:cuas-classifiers -->

Real radar tracks of small drones, birds, people and vehicles from an Echodyne EchoGuard (MESA, K-band) radar, recorded by the National Research Council Canada in eight field trials in Quebec, October 2019 to March 2021. Track-level data, not raw radar returns, so it suits kinematic UAV-vs-bird classification at ranges where micro-Doppler is not available.

| Field | Value |
|---|---|
| Platform | Ground radar, Echodyne EchoGuard; co-located Bosch PTZ camera used by annotators |
| Environment | 3 sites (Alma, Laval, QC), several seasons and weather; DJI Phantom 2, Phantom 4, Inspire, Mavic at 100-1,200 m range, roughly 9-36 m altitude (README) |
| Sensors and rates | Track updates at 10 Hz: 3D position, 3D velocity, azimuth / elevation / range, RCS. Raw logs add about 40 columns incl. timestamps and the radar's own `probUav` (README) |
| Ground truth | Expert labels per track: BIRD 492, MIXED 376, UAV 167, HUMAN 65, VEHICLE 14, UNKNOWN 3 = 1,117 labelled tracks (README). Demo-4 raw logs add about 8,000 unlabelled radar tracks |
| Size | 201.6 MB in 91 files (sum of GitHub tree blob sizes, 2026-11-06): Demo-4 98.7 MB, Demo-7 39.5 MB, Demo-0 26.8 MB, Demo-3 15.1 MB, Demo-6 11.8 MB, rest under 6 MB. The labelled `.xlsx` subset the sample uses came to 59 MB on disk |
| License | CC BY 4.0 (repo `LICENSE`, GitHub API). Cite Mehta, Bolic, Mantegh, Vidal |
| Format | Annotated `.xlsx` (11 columns per update, second sheet maps `SystemTrackID` to label); raw log `.csv` / `.csv.gz` (`;`-delimited). Column reference in `docs/DATA_DICTIONARY.md` |
| Index | [CUAS-sensing-dataset](../../catalog/repos/nrc-cnrc__cuas-sensing-dataset.md), [cuas-classifiers sample](../../samples/cuas-classifiers/) |

## What's in it

| Folder | Date | Content |
|---|---|---|
| Demo-0 | 2019-10 Alma | 29 sessions from two radars at once (`-R1` / `-R2`), 946 labelled tracks |
| Demo-1, Demo-7 | 2020-11 to 2021-03 Laval | curated single-UAV extracts (raw-log CSV) |
| Demo-2, 3, 5, 6 | 2020-11 to 2021-03 Laval | 2-10 sessions each, 4-88 labelled tracks each |
| Demo-4 | 2021-02 Laval | 3 full raw logs (about 1.27 M rows, gzip) + 8 UAV / truck extracts |

`metadata/track_labels.csv` indexes every labelled track; `metadata/file_manifest.csv` lists rows and sizes per file.

## Download

```bash
# whole repo (about 200 MB, plain git, no LFS)
git clone --depth 1 https://github.com/nrc-cnrc/CUAS-sensing-dataset
# labelled xlsx only (what the sample does, about 50 s here): GitHub tree API + raw.githubusercontent.com
python3 samples/cuas-classifiers/download_data.py radar
```

## Used in this repo

[samples/cuas-classifiers](../../samples/cuas-classifiers/) (`download_data.py radar`, `train_radar.py`, `cuas_cot.py`), run 2026-11-06:

- Downloads the 47 labelled `.xlsx` sessions of Demo-0/2/3/5/6 plus `metadata/`; 59 MB on disk, about 50 s.
- 510 usable tracks (379 BIRD, 131 UAV, at least 10 updates) in 42 sessions. HistGradientBoosting on 24 kinematic + RCS features: balanced accuracy 0.928, ROC AUC 0.964 with 5-fold GroupKFold by session; cross-site (train Alma, test Laval) 0.90-0.92.
- Frame facts checked on the data by that sample: `posY` is vertical, `azimuth = atan2(posX, posZ)`. The `.xlsx` files carry no timestamps, so dt = 0.1 s comes from the documented 10 Hz.
- Demo-0 recorded two radars at once: both `-R1` / `-R2` files of a session must sit in the same CV fold, or the score leaks.

## Loading and tooling

- `examples/load_tracks.py` in the repo; openpyxl or pandas for the `.xlsx`. Parsing dominates runtime (25 s for 47 files in the sample).
- Feature code and leakage-safe splits: `samples/cuas-classifiers/radar_features.py`, `train_radar.py`.
- CoT output for TAK: `samples/cuas-classifiers/cuas_cot.py` (type `a-u-A-M-H-Q`).

## Hackathon fit

- C-UAS situational awareness: classify radar tracks UAV vs bird, push UAV tracks to a TAK / C2 picture (playbook section 4.2 pattern). Detection and reporting only.
- Clutter rejection: train a third "other" class on HUMAN / VEHICLE tracks and the Demo-4 raw logs, compare against the radar's own `probUav`.

## Pitfalls

- No radar site coordinates, heading or tilt are published. Any map placement is illustrative; elevation is relative to the radar horizontal, so an unknown tilt shows up as wrong height.
- UAVs flew scripted manoeuvres at chosen ranges; leave range out of the features or the model learns the scenario.
- Only 22 bird tracks in the Laval cross-site test set; cross-site numbers are noisy.
- Track duration partly reflects how long annotators kept a track; check that it does not carry the result.

## Sources

- nrc-cnrc/CUAS-sensing-dataset README, `LICENSE`, git tree API (file count and sizes), 2026-11-06
- samples/cuas-classifiers/README.md and `download_data.py` (measured facts above)
