# Multi-frequency GNSS spoofing raw dataset (S7AM1NA)

<!-- about: repo:s7am1na/gnss-spoofing-dataset, repo:stanford-navlab/gnss_lib_py -->

Android GnssLogger raw measurements from four phones and two smartwatches recorded under L1-only, L5-only and simultaneous L1+L5 spoofing, plus clean sessions. Collected 2025-07-30, released by GitHub user S7AM1NA; paper "under review" per README.

| Field | Value |
|---|---|
| Platform | Phones: Google Pixel 6, Huawei Mate 40, Xiaomi MI8, Redmi K60. Watches: Pixel Watch, Pixel Watch 2 |
| Environment | Not stated (spoofer setup, location and power not described) |
| Sensors and rates | GnssLogger `Raw` records only (pseudorange inputs, ADR, Doppler, C/N0, AgcDb, CodeType ...), headers kept; other record types stripped. Epoch rate not stated (sample file shows 1 s epochs) |
| Ground truth | Spoofing on/off windows only, given in README as GPS TOW and UTC: st_L_15 258028-258653 s, st_L1 262228-262860 s, st_L5 265395-265490 s and 266310-267054 s. No position truth |
| Size | README badge and text: full zip about 115 MB. Repo sample file 23,678,435 B (HEAD, 2026-11-06) |
| License | MIT (repo LICENSE) |
| Format | GnssLogger text (v3.x) |
| Index | [repo](../../catalog/repos/s7am1na__gnss-spoofing-dataset.md), [gnss_lib_py](../../catalog/repos/stanford-navlab__gnss_lib_py.md) |

## What's in it

`Scenario/ Session_<local start>_<local end>/ Device/ gnss_log_*.txt` for `st_L1`, `st_L5`, `st_L_15`, `normal`. The session folder names are in local time (UTC+8 by arithmetic: folder `2025.07.30.08.40` vs spoof start 00:50 UTC); the README warns to use its UTC table, not in-file timestamps, as truth.

## Download

```bash
# Repo holds docs + one sample log only
curl -LO https://raw.githubusercontent.com/S7AM1NA/GNSS-Spoofing-Dataset/main/sample/gnss_log_2025_07_30_10_15_12.txt
# Full zip: README links ../../releases/latest, but the repo had NO releases on 2026-11-06
gh api repos/S7AM1NA/GNSS-Spoofing-Dataset/releases --jq '.[].assets[].browser_download_url'
```

## Loading and tooling

```python
import gnss_lib_py as glp
raw = glp.AndroidRawGnss("gnss_log_2025_07_30_10_15_12.txt")
# label: spoofed if gps_millis falls inside the README TOW window for that scenario
```

Features worth plotting first: per-satellite C/N0, `AgcDb` (jamming/power), receiver clock drift (`DriftNanosPerSecond`), L1 vs L5 pseudorange consistency.

## Hackathon fit

Idea 4 (Android raw GNSS spoofing detector) is the direct match; Idea 1 (interference monitor) as a phone-side sensor. Pair with [GSDC](gsdc.md) for clean-baseline statistics.

## Pitfalls

- The full dataset was not downloadable when checked: release missing. Only the 23.7 MB sample is public. Ask the author or treat as unavailable.
- The sample (Pixel 6, first epoch 2025-07-30 02:15 UTC) starts after the last listed spoof window ends (02:10:36 UTC), so it is not a labelled attack sample; which scenario folder it came from is not stated.
- No description of spoofer type, power or spoofed trajectory; detectors can only be scored on on/off timing.
- Small device count; results will not generalize across chipsets without more data.

## Sources

- Repo README and git tree (gh api, 2026-11-06); releases API returned `[]`
- Sample file header and first records (Model Pixel 6, Broadcom BCM4776)
