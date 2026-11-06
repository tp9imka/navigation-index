# KAIST Complex Urban

<!-- about: res:kaist-complex-urban-dataset -->

KAIST IRAP / Naver Labs driving dataset (Jeong et al., IJRR 2019) targeting dense Korean
city centres where GPS reception collapses between high-rises. Strong point for navigation
work: a full proprioceptive suite (FOG, IMU, wheel encoders, altimeter) next to consumer
and VRS GPS, all as plain CSV.

| Field | Value |
|---|---|
| Platform | Toyota Prius |
| Environment | Seoul, Gangnam, Yeouido, Pangyo/Seongnam, Dongtan and others: metropolis, complex buildings, residential; complexity rated 1-4 stars per sequence |
| Sensors and rates | 2x 3D lidar `VLP_left` / `VLP_right` (Velodyne, tilted 45 deg); 2x SICK 2D lidar (rear down, middle up, 190 deg FOV); stereo camera 10 Hz, externally triggered, Bayer RGGB PNG (Ver 2 sequences only); consumer GPS; VRS GPS; IMU; fibre-optic gyro; wheel encoders; altimeter. Sensor-specific rates are in the paper and format page, not all restated here |
| Ground truth | "Baseline" SE(3) trajectory from graph SLAM using the onboard sensors (site warns it is not accurate enough for exact lidar-to-image projection). VRS GPS (UTM, fix/float flags, std) is a separate raw stream. Accuracy not stated on pages read |
| Size | Not stated on the pages read; download links are emailed after a request form. Not verified |
| License | CC BY-NC-SA 4.0 (KAIST and Naver Labs), non-commercial |
| Format | tar per sequence; `sensor_data/*.csv` (gps, vrs_gps, imu, fog, encoder, altimeter, stamps), lidar float binaries named by timestamp, stereo PNG; LAS map per session; ROS file_player |
| Index | [Complex Urban](../../catalog/resources/kaist-complex-urban-dataset.md), [evo](../../catalog/repos/michaelgrupp__evo.md) |

## What's in it

Sequences urban00 - urban39. Ver 1 ("LiDAR" tab, about 20 sequences, urban00-17 style):
lidar + navigation. Ver 2 ("LiDAR + Stereo", urban26-39 and others): adds stereo, updated
IMU and VRS. Path lengths roughly 3-12 km each (e.g. urban39 11.06 km Pangyo, urban35
3.2 km Seoul). urban28 / 38 / 39 overlap the same Pangyo area for revisit tests.

## Download

```bash
# Request links via the form on either download tab; links arrive by email:
#   https://sites.google.com/view/complex-urban-dataset/download-lidar-stereo
#   https://sites.google.com/view/complex-urban-dataset/download-lidar
# Development tools (ROS file_player, etc.) from the Development Tool tab.
```

## Loading and tooling

```python
import pandas as pd
vrs = pd.read_csv('sensor_data/vrs_gps.csv', header=None)   # t, lat, lon, x_utm, y_utm, alt, fix(4=fix,5=float,1=normal), ...
gps = pd.read_csv('sensor_data/gps.csv', header=None)       # t, lat, lon, alt, 9x cov
```

- 3D lidar bins are `[x, y, z, R]` float32; 2D SICK bins are `[r, R]` with -5 to 185 deg at 0.666 deg steps (format page).
- Timestamps are ROS time throughout (format page); check units in the first rows.

## Hackathon fit

- Idea 5 (INS holdover budget): FOG + wheel encoder dead reckoning through urban canyon
  GPS gaps, scored against VRS-fixed epochs and the SLAM baseline. CSV only, no ROS needed.
- Reference arch 4.3 (fusion with integrity): consumer GPS vs VRS fix-state gives labelled
  "trustworthy vs not" epochs for a residual monitor.

## Pitfalls

- Request-form access and no published sizes; ask early.
- Baseline is SLAM output, not independent truth; do not use it to score a SLAM method from the same sensors without saying so.
- VRS CSV columns differ between Ver 1 and Ver 2 (extra orthometric altitude).
- Old irap.kaist.ac.kr links are deprecated (moved 2021).

## Sources

- https://sites.google.com/view/complex-urban-dataset (home, /system, /format, /download-lidar-stereo, /download-lidar), fetched 2026-11-06
