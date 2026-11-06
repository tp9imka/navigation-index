# Microsoft Indoor Location Competition 2.0 (2020-2021)

<!-- about: repo:location-competition/indoor-location-competition-20 -->

Smartphone indoor positioning data from Microsoft Research's Indoor Location Competition 2.0, later run on Kaggle as "Indoor Location & Navigation". Surveyors walked waypoint-to-waypoint paths inside buildings in Chinese cities carrying a phone that logged IMU, magnetometer, Wi-Fi and BLE.

| Field | Value |
|---|---|
| Platform | Android phone held flat in front of a walking surveyor |
| Environment | "Hundreds of buildings in Chinese cities" (README); multi-floor, with floor-plan images and GeoJSON per floor |
| Sensors and rates | Accelerometer, gyroscope, magnetometer (calibrated and uncalibrated), rotation vector, Wi-Fi scans (SSID, BSSID, RSSI, frequency), iBeacon (UUID, major/minor, RSSI, distance). Rates not stated |
| Ground truth | `TYPE_WAYPOINT` positions labelled by the surveyor on the floor map (x, y in metres); accuracy not stated |
| Size | Full dataset: not verified (Kaggle login required). Repo sample data (2 sites): about 2.19 GB summed from git tree blob sizes; repo download is smaller (GitHub reports 421 MB packed) |
| License | Sample code and data in repo: MIT. Full dataset: Kaggle competition rules; MSR page states no license |
| Format | One `.txt` trace per path (Unix ms timestamp, type, values), floor `floor_info.json`, `geojson_map.json`, raster map |
| Index | [Indoor Location Competition 2.0](../../catalog/repos/location-competition__indoor-location-competition-20.md) |

## Download

```bash
git clone --depth 1 https://github.com/location-competition/indoor-location-competition-20   # sample: site1, site2
# full data (Kaggle account + rules acceptance)
kaggle competitions download -c indoor-location-navigation
```

`aka.ms/location20dataset` redirects to an MSR publication page whose download button points to the Kaggle data page.

## Loading and tooling

```bash
cd indoor-location-competition-20 && python main.py
# outputs path images, step detection, magnetic-strength heatmaps, Wi-Fi/iBeacon RSSI heatmaps under output/
```

`io_f.py` has `read_data_file()` that splits a trace into arrays per sensor type; `compute_f.py` has step detection and step-based PDR.

## Hackathon fit

- Dismounted indoor navigation: PDR + magnetic fingerprint + Wi-Fi fingerprint fusion against waypoint truth.
- Situational awareness: floor-level estimation from Wi-Fi/BLE.
- Not a GNSS dataset; no outdoor segments.

## Pitfalls

- Truth is sparse waypoints, with sensor data in between; interpolate along steps for scoring.
- Wi-Fi scans are throttled on newer Android, so scan timing is irregular.
- Kaggle competition data and the MSR "dataset" are the same source but packaged differently; check which one a baseline assumes.

## Sources

- Repo README and git tree (gh api, 2026-11-06); HEAD on aka.ms link; MSR publication page via WebFetch
