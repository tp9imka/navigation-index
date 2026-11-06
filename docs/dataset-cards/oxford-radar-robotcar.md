# Oxford Radar RobotCar

<!-- about: res:oxford-radar-robotcar-dataset, repo:ori-mrg/robotcar-dataset-sdk, repo:dan11003/cfear_radarodometry, repo:keenan-burnett/yeti_radar_odometry, repo:mttgdd/open-radvlad -->

Radar extension of [Oxford RobotCar](oxford-robotcar.md) (Barnes et al., ICRA 2020): 32
traversals of the RobotCar route in January 2019, 280 km, with a Navtech scanning FMCW radar,
two Velodynes and the original camera / GPS-INS suite. The reference dataset for radar
odometry and radar place recognition.

| Field | Value |
|---|---|
| Platform | Nissan LEAF (Oxford RobotCar) |
| Environment | Central Oxford urban route, Jan 2019, varied traffic, weather, light |
| Sensors and rates | Navtech CTS350-X 360-degree FMCW radar (4.38 cm range bins, 0.9 deg azimuth, 163 m range in this config, 400 azimuths x 3768 bins per sweep); 2x Velodyne HDL-32E; Bumblebee XB3 stereo; 3x Grasshopper2; 2x SICK LMS-151; NovAtel SPAN-CPT GPS/INS (LD-MRS dropped). Radar sweep rate not stated on the pages read |
| Ground truth | SE(2) radar odometry from a large Ceres optimisation over robust VO, visual loop closures and GPS/INS constraints (`gt/radar_odometry.csv`). Relative poses between consecutive scans, not global. Accuracy not stated |
| Size | Datasets page: 32 traversals, 36.6-143.2 GB each, sum 3831.5 GB (stated). Samples stated as Tiny 200 MB, Small 1 GB, Medium 5 GB, Large 10 GB. Not HEAD-verified (Google Drive) |
| License | Not restated on the radar pages read; the parent RobotCar license is CC BY-NC-SA 4.0 non-commercial. Registration required |
| Format | Polar radar scans as lossless PNG (first 11 columns hold timestamp, sweep counter, valid flag); Velodyne binary + raw PNG; one zip per sensor per traversal |
| Index | [Oxford Radar RobotCar](../../catalog/resources/oxford-radar-robotcar-dataset.md), [robotcar-dataset-sdk](../../catalog/repos/ori-mrg__robotcar-dataset-sdk.md), [CFEAR](../../catalog/repos/dan11003__cfear_radarodometry.md), [Yeti](../../catalog/repos/keenan-burnett__yeti_radar_odometry.md), [Open-RadVLAD](../../catalog/repos/mttgdd__open-radvlad.md) |

## What's in it

32 traversals named `yyyy-mm-dd-HH-MM-SS-radar-oxford-10k` (about 9 km, about 35 min each),
two of them `-partial`. Each has `gt/radar_odometry.csv`, `radar/<ts>.png`,
`velodyne_left|right/<ts>.bin|png`, per-sensor `.timestamps`, plus the classic RobotCar
sensors.

## Download

```bash
# 1. Register your Google account on the registration page (grants Drive read access).
# 2. Sample first (from the downloads page; Google Drive):
#    Tiny  200 MB: https://drive.google.com/file/d/1C5b2w1DMpSFlAkyVah8Om5IdokJrlcgs
# 3. Scripted, per sensor (uses rclone against Google Drive; install inside the venv/docker):
pip install git+https://github.com/dbarnes/radar-robotcar-dataset-sdk.git
python -m radar_robotcar_dataset_sdk.downloader.download --sample_dataset Small --download_folder ./rrc
python -m radar_robotcar_dataset_sdk.downloader.download \
  --datasets 2019-01-10-11-46-21-radar-oxford-10k --sensors Navtech_CTS350-X_Radar,Radar_Odometry --download_folder ./rrc
```

The sensor names in `--sensors` are illustrative; run `--help` without `--download_folder`
to list matching files before downloading. The Google Drive sample links were not
HEAD-checked; whether the 2026-10-22 RobotCar withdrawal also covers these Drive files was
not determined.

## Loading and tooling

- [robotcar-dataset-sdk](../../catalog/repos/ori-mrg__robotcar-dataset-sdk.md):
  `radar.load_radar(path)` => timestamps, azimuths, valid, fft_data, radar_resolution;
  `radar.radar_polar_to_cartesian(...)`; `velodyne.load_velodyne_binary`.
- Radar odometry baselines: [CFEAR](../../catalog/repos/dan11003__cfear_radarodometry.md),
  [Yeti](../../catalog/repos/keenan-burnett__yeti_radar_odometry.md),
  [TBV radar SLAM](../../catalog/repos/dan11003__tbv_slam_public.md); place recognition:
  [Open-RadVLAD](../../catalog/repos/mttgdd__open-radvlad.md).

## Hackathon fit

- Reference arch 4.1 / 4.3 with radar as the weather-proof odometry source: run CFEAR on one
  traversal, chain the SE(2) GT, show drift per km.
- Maritime angle (reference arch 4.4): the CTS350-X is a Navtech scanning radar similar in
  principle to marine radar; polar PNG handling transfers to OpenCPN radar_pi style data.

## Pitfalls

- Full traversals are 37-143 GB; take one traversal and only the radar + GT sensors.
- GT is relative SE(2), not a global trajectory; integrate it yourself, or use GPS/INS for absolute.
- Drop azimuth rows with valid flag 0 if you need raw (dropped packets are interpolated).
- Google Drive quotas; the downloader matches files by name in your Drive.
- Parent dataset was marked withdrawn on 2026-10-22; check availability early.

## Sources

- https://oxford-robotics-institute.github.io/radar-robotcar-dataset/ (+ /documentation, /downloads, /datasets), fetched 2026-11-06
- https://github.com/oxford-robotics-institute/radar-robotcar-dataset-sdk README via `gh api`, 2026-11-06
