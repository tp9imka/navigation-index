# Oxford RobotCar

<!-- about: res:oxford-robotcar-dataset, repo:ori-mrg/robotcar-dataset-sdk -->

Oxford Robotics Institute's year-long driving dataset (Maddern et al., IJRR 2017): over 100
repetitions of one central-Oxford route, May 2014 to Dec 2015, in all weather. The standard
data for long-term, appearance-change localization. RTK ground truth added in 2020.

> **Status (checked 2026-11-06):** the home and downloads pages carry a notice dated
> 2026-10-22: "we are withdrawing the RobotCar Dataset until further notice". The download
> server `mrgdatashare.robots.ox.ac.uk` did not answer a HEAD request. Treat it as
> unavailable unless you already hold a copy.

| Field | Value |
|---|---|
| Platform | Nissan LEAF (Oxford RobotCar) |
| Environment | Central Oxford urban route; rain, night, sun, snow, roadworks, detours |
| Sensors and rates | Bumblebee XB3 trinocular stereo 1280x960 16 Hz; 3x Grasshopper2 fisheye 1024x1024 11.1 Hz; 2x SICK LMS-151 2D lidar 50 Hz; SICK LD-MRS 3D lidar 4-plane 12.5 Hz; NovAtel SPAN-CPT ALIGN GPS/INS 50 Hz, dual antenna (documentation page) |
| Ground truth | Original: SPAN-CPT GPS/INS (plus provided VO). 2020 release: post-processed RTK (raw GPS + IMU + static base) for 72 traversals, described as "globally-consistent centimetre-accurate"; the six RobotCar Seasons runs are excluded |
| Size | Datasets page lists 133 traversals summing to about 20,070 GB (sum of stated per-run sizes, 10-133 GB each). RTK GT archive about 91 MB (stated). Samples: 200 MB and 1 GB (stated). Nothing HEAD-verified (server down) |
| License | CC BY-NC-SA 4.0, non-commercial academic use only; registration required |
| Format | Per-sensor tar chunks per traversal; images png (Bayer), lidar binary, GPS/INS and VO as CSV |
| Index | [Oxford RobotCar](../../catalog/resources/oxford-robotcar-dataset.md), [robotcar-dataset-sdk](../../catalog/repos/ori-mrg__robotcar-dataset-sdk.md), [Oxford Radar RobotCar](oxford-radar-robotcar.md) |

## What's in it

Over 1000 km, almost 20 million images. Traversals are tagged on the Datasets page
(`night`, `snow`, `rain`, `no-gps`, `poor-gps`, `roadworks`, `partial`, ...). The `no-gps`
and `poor-gps` tags make it one of the few driving datasets with labelled GNSS
degradation. RobotCar Seasons (a subset with 6-DoF query poses) is served by the
[Long-Term Visual Localization benchmark](../../catalog/resources/visual-localization-benchmark.md).

## Download

```bash
# Only if the dataset is re-opened. Register first, then (URLs from the downloads page):
wget "http://mrgdatashare.robots.ox.ac.uk:80/download/?filename=rtk.zip" -O rtk.zip   # about 91 MB
wget "http://mrgdatashare.robots.ox.ac.uk:80/download/?filename=camera-models.tar"
# Bulk: the community RobotCarDataset-Scraper script linked from the downloads page.
git clone https://github.com/ori-mrg/robotcar-dataset-sdk
```

## Loading and tooling

- [robotcar-dataset-sdk](../../catalog/repos/ori-mrg__robotcar-dataset-sdk.md) (Python + MATLAB):
  `image.load_image` (demosaic), `camera_model.CameraModel` (undistort),
  `build_pointcloud.py` (lidar + INS/VO poses), `interpolate_poses.py`.
- RTK CSVs follow the documented INS CSV layout and load with the SDK's pose interpolation.

## Hackathon fit

- Idea 18 (visual geolocalization fused with VO): same route under many conditions is the
  classic "match today's image against a map built months ago" test.
- Idea 5 (INS holdover): `no-gps` / `poor-gps` traversals plus RTK truth on others.
- Given the withdrawal, prefer [Boreas](boreas.md) (repeated route, seasons, open S3) for a new build.

## Pitfalls

- Withdrawn as of 2026-10-22; do not plan a hackathon around a fresh download.
- Images are raw Bayer; use the SDK to demosaic and undistort.
- GPS/INS is not RTK in the original release; use `rtk.zip` truth where available.
- Non-commercial license.

## Sources

- https://robotcar-dataset.robots.ox.ac.uk/ (notice, license), /documentation/ (sensors),
  /ground_truth/ (RTK release), /datasets/ (per-run sizes, tags), /downloads/ (links), fetched 2026-11-06
- HEAD on mrgdatashare.robots.ox.ac.uk: no response, 2026-11-06
