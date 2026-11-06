# Google Smartphone Decimeter Challenge (GSDC 2021-2023) and Android raw GNSS datasets

<!-- about: res:google-gsdc-2023, res:google-gsdc-2022, res:google-android-raw-gnss-datasets, repo:taroz/gsdc2023, repo:stanford-navlab/gnss_lib_py, repo:google/gps-measurement-tools -->

Google's Android GPS team released raw GNSS logs from phones in cars with reference truth (ION GNSS+ 2020 paper), then ran three Kaggle competitions on them: GSDC 2021, 2022 and 2023-2024. This is the biggest public pool of real smartphone raw measurements with truth.

| Field | Value |
|---|---|
| Platform | Android phones mounted in a car (several handset models per drive) |
| Environment | Highways and urban/suburban roads; 2020 release: San Francisco Bay Area highways, summer 2020 (Google Research page) |
| Sensors and rates | Phone raw GNSS (pseudorange, Doppler, ADR/carrier phase where the phone supports it, C/N0, AGC), phone IMU and magnetometer; Kaggle 2022/2023 also ship derived per-epoch corrections. Rates not re-checked this session (Kaggle page needs JS/login) |
| Ground truth | NovAtel SPAN GNSS/INS reference (Google Research page). Accuracy figure not stated on the pages read |
| Size | Not verified for the Kaggle archives (API returns 401 without credentials). Verified: taroz's pre-processed GSDC 2023 bundle `dataset_2023.zip` = 2,761,355,999 bytes (HEAD Content-Length, 2026-11-06) |
| License | Kaggle competition rules (accept on Kaggle). The 2020 paper page states no license |
| Format | Per trace/phone folder: GnssLogger text log, derived CSVs, RINEX, ground-truth CSV (layout per gnss_lib_py parsers `AndroidDerived2021/2022/2023`, `AndroidGroundTruth2021/2022/2023`) |
| Index | [GSDC 2023](../../catalog/resources/google-gsdc-2023.md), [GSDC 2022](../../catalog/resources/google-gsdc-2022.md), [Android raw GNSS datasets paper](../../catalog/resources/google-android-raw-gnss-datasets.md), [taroz gsdc2023](../../catalog/repos/taroz__gsdc2023.md), [gnss_lib_py](../../catalog/repos/stanford-navlab__gnss_lib_py.md), [gps-measurement-tools](../../catalog/repos/google__gps-measurement-tools.md) |

## What's in it

- 2020 release: "60+ datasets" from Bay Area highways with SwiftNav and Verizon corrections (Google Research page).
- GSDC 2021 / 2022 / 2023: train and test drives, many phone models per drive, scored on horizontal error percentiles against truth. The 2023 winning team (taroz) reports public 0.789 m / private 0.928 m with factor-graph GNSS+IMU (repo README).

## Download

```bash
# Kaggle account + accepted competition rules required; kaggle CLI in a venv
uv pip install --python "$VENV/bin/python" kaggle      # needs ~/.kaggle/kaggle.json
kaggle competitions download -c smartphone-decimeter-2023
kaggle competitions download -c smartphone-decimeter-2022
kaggle competitions download -c google-smartphone-decimeter-challenge   # 2021 edition

# No-login alternative: taroz's pre-processed 2023 set (MATLAB-oriented), 2.76 GB
wget http://www.taroz.net/data/dataset_2023.zip
```

## Loading and tooling

```python
import gnss_lib_py as glp   # pip: gnss-lib-py (1.1.0 on PyPI, 2026-11-06)
raw = glp.AndroidRawGnss("trace/phone/supplemental/gnss_log.txt")   # GnssLogger text
der = glp.AndroidDerived2023("trace/phone/device_gnss.csv")
gt  = glp.AndroidGroundTruth2023("trace/phone/ground_truth.csv")
```

File names above follow the 2023 layout as used by gnss_lib_py; check them against your download. `gnss_lib_py.parsers.google_decimeter` also has `solve_kaggle_baseline` and `prepare_kaggle_submission`. [gps-measurement-tools](../../catalog/repos/google__gps-measurement-tools.md) gives the MATLAB pseudorange pipeline; [taroz/gsdc2023](../../catalog/repos/taroz__gsdc2023.md) the winning GTSAM factor graph (MATLAB + custom GTSAM build, heavy for 48 h).

## Hackathon fit

- Idea 4 (Android raw GNSS spoofing detector): clean baseline traces to learn normal C/N0, AGC, clock drift and pseudorange residual behaviour before running on [the spoofing dataset](gnss-spoofing-s7am1na.md).
- Idea 5 (INS holdover budget): cut GNSS out of a drive and measure phone-IMU drift against truth.
- Integrity / RAIM demo: inject synthetic faults into a real trace and show detection.

## Pitfalls

- Kaggle login and rules acceptance cannot be done on venue Wi-Fi at the last minute. Download beforehand.
- File layout and column names changed between 2021, 2022 and 2023; use the matching gnss_lib_py class.
- Carrier phase (ADR) is only usable on some phones and often has cycle slips and resets.
- Test-split truth is withheld (Kaggle); use train drives for any scored demo.

## Sources

- https://research.google/pubs/android-raw-gnss-measurement-datasets-for-precise-positioning/ (2020 release facts)
- https://github.com/taroz/gsdc2023 README (scores, dataset_2023.zip); HEAD on http://www.taroz.net/data/dataset_2023.zip
- gnss_lib_py source: `gnss_lib_py/parsers/google_decimeter.py`, `android.py` (class names)
- Kaggle pages: not readable without JS/login; contents not verified this session
