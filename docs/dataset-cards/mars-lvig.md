# MARS-LVIG

<!-- about: res:hku-mars-lvig-dataset -->

Aerial lidar-visual-inertial-GNSS dataset from HKU MARS Lab, flown on a DJI M300 RTK at 80-130 m over airfields, islands, towns and valleys (sequence prefixes HK and AM; exact sites not stated on the page). The only dataset in this group with **raw GNSS observations from an aerial platform**, so it supports tightly coupled GNSS fusion and GNSS-outage experiments at real survey altitudes.

| Field | Value |
|---|---|
| Platform | DJI Matrice 300 RTK with custom payload |
| Environment | Aero-model airfield, islands, rural towns, valleys, featureless airfield; altitudes 80-130 m, plus manual ~20 m flights in Featureless_GNSS01 |
| Sensors and rates | Livox Avia lidar, Hikvision CA-050 RGB camera, u-blox ZED-F9P raw GNSS receiver; IMU model and all rates not listed on the dataset page |
| Ground truth | Position: M300 RTK. Mapping: DJI Zenmuse L1 survey lidar. Accuracy figures not stated on the page |
| Size | Not stated and not verified (Google Drive hosting; HEAD not possible) |
| License | CC BY-NC-SA 4.0, academic use only |
| Format | ROS1 bag per sequence |
| Index | [MARS-LVIG](../../catalog/resources/hku-mars-lvig-dataset.md) |

## What's in it

| Scenario | Sequences | Altitude | Speeds (m/s) | Notes |
|---|---|---|---|---|
| Aero-model airfield | HKairport01-03, HKairport_GNSS01-03, HKairport_GNSS_Evening | 80 m | 3/6/9 | Evening = lighting change |
| Islands | HKisland01-03, HKisland_GNSS01-03, HKisland_GNSS_Evening | 90 m | 3/6/9 | |
| Rural towns | AMtown01-03 | 80 m | 4/8/12 | |
| Valleys | AMvalley01-03 | 130 m | 4/8/12 | Camera and lidar degeneration |
| Featureless airfield | Featureless_GNSS01-03 | 80 m | 6/6/high | Camera and lidar degeneration |

The `_GNSS` suffix suggests these carry the raw GNSS stream; the page does not say so explicitly, so check topics with `rosbag info`.

## Download

All bags are on Google Drive: folder https://drive.google.com/drive/folders/1aG21le4QZl9LhSLE1O0vuVDQ8YgAwdas (plus per-sequence links on https://mars.hku.hk/dataset.html).

```bash
# venv; gdown handles large-file confirmation pages
pip install gdown
gdown --folder https://drive.google.com/drive/folders/1aG21le4QZl9LhSLE1O0vuVDQ8YgAwdas
```

Drive quotas often block bulk folder downloads; fetch single files by id from the per-sequence links. A third-party HF upload of one sequence exists (`swd123456/HKisland_GNSS03_Dataset_from_MARS-LVIG`), not checked for integrity.

## Loading and tooling

- Lidar is Livox (custom message `livox_ros_driver/CustomMsg`, as for other Livox bags); [FAST-LIO](../../catalog/repos/hku-mars__fast_lio.md) from the same lab reads it natively.
- Raw GNSS: export to RINEX or parse u-blox RXM-RAWX; fuse with GVINS-style or factor-graph code. Check bag topics with `rosbag info` first.
- Scoring vs RTK: [evo](../../catalog/repos/michaelgrupp__evo.md) without alignment for absolute (GNSS-fused) solutions.

## Hackathon fit

- Idea 10 / 18 at altitude: down-looking camera over real terrain with RTK truth; blank GNSS mid-flight and show visual/lidar holdover.
- GNSS integrity / tightly coupled fusion demos: raw F9P observations in flight, rare in public aerial data.
- Idea 11 (terrain-relative navigation over a real DEM): lidar returns over valleys and towns can be matched against a public DEM.

## Pitfalls

- Google Drive hosting: quotas, no checksums, no HEAD sizes. Budget time.
- Featureless and valley sequences intentionally break lidar and camera odometry.
- RTK ground truth is position only from the aircraft's RTK; orientation truth not described.
- Non-commercial, academic-only license.

## Sources

- https://mars.hku.hk/dataset.html (platform, sensors, sequences, altitudes, GT sources, license, Drive links)
- HF search API for "lvig" (third-party mirror)
