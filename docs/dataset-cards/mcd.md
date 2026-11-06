# MCD: Multi-Campus Dataset

<!-- about: res:mcd-multi-campus-dataset, repo:mcdviral/mcdviral.github.io -->

Campus-scale dataset (Nguyen et al., CVPR 2024) from NTU Singapore, KTH Stockholm and TUHH
Hamburg, day and night, with spinning + non-repetitive lidar, stereo, several IMUs, UWB
ranging and survey-grade prior maps that drive a continuous-time ground truth.

| Field | Value |
|---|---|
| Platform | All-terrain vehicle (ntu_ sequences); handheld rig (kth_, tuhh_ sequences) |
| Environment | Three university campuses in Asia and Europe, day and night, different seasons |
| Sensors and rates | Ouster OS1 lidar 10 Hz (128 ch on ATV, 64 ch handheld); Livox Mid-70 non-repetitive lidar 10 Hz; RealSense D435i (ATV), D455 bottom (both), D455 top (handheld) at 30 Hz, 640x480; IMUs: VN100 400 Hz (ATV), VN200 400 Hz, RealSense IMUs 400 Hz, Ouster IMU 100 Hz; UWB Nooploop LinkTrack P 20 Hz (two tags); VN200 GPS fix (ATV only) |
| Ground truth | Lidar registration against survey-grade prior maps, delivered as a B-spline (`spline.csv`, Dt 0.025 s, order 6) and as discrete poses sampled at 0.1 s (`pose_inW.csv`). Accuracy figure: not stated on the pages checked |
| Size | Stated per sequence on the Download page: 18 sequences, 3.5-51.3 GB each, sum 438.8 GB. Split per sensor: e.g. ntu_day_01 is d435i 13.3 GB, d455b 13.8 GB, os1_128 13.8 GB, mid70 542 MB, UWB 1 MB, vn100 32 MB, vn200 54 MB. Not HEAD-verified (Google Drive) |
| License | CC BY-NC-SA 4.0, non-commercial academic use (site README) |
| Format | ROS1 bags, bz2-compressed, one bag per sensor per sequence; GT as CSV |
| Index | [MCD (resource)](../../catalog/resources/mcd-multi-campus-dataset.md), [MCD site repo](../../catalog/repos/mcdviral__mcdviral.github.io.md), [evo](../../catalog/repos/michaelgrupp__evo.md) |

## What's in it

| Campus | Sequences (duration) |
|---|---|
| NTU (ATV) | ntu_day_01 (10m02s), day_02 (3m49s), day_10 (5m25s), night_04 (4m57s), night_08 (7m47s), night_13 (3m54s) |
| KTH (handheld) | kth_day_06 (14m51s), day_09, day_10, night_01 (16m09s), night_04, night_05 |
| TUHH (handheld) | tuhh_day_02, day_03 (13m59s), day_04 (3m08s), night_07, night_08, night_09 (3m05s, 3.5 GB) |

Extras: the prior-map point clouds (CloudCompare format) with annotations, semantic labels
for Livox scans, calibration YAMLs per rig.

## Download

```bash
# All links are Google Drive. Example sequence folder (ntu_day_02, 14.8 GB):
#   https://drive.google.com/drive/folders/1Nt_khn7u8y3d1TIjY8Lyht2vI8qCG6Sy
# With gdown (in the project venv), pick only the bags you need:
gdown --folder https://drive.google.com/drive/folders/1Nt_khn7u8y3d1TIjY8Lyht2vI8qCG6Sy
# Calibration: ATV
gdown https://drive.google.com/uc?id=1zVTBqh4cA1DciWBj5n7BGiexbfan1BBL
bunzip2 -k *.bag.bz2   # or `rosbag decompress`; site says about 3x larger uncompressed
```

Smallest useful UWB + IMU subset: the per-sequence UWB (about 1 MB) and VN100/VN200 bags
(tens of MB) plus `pose_inW.csv`: under 100 MB per NTU sequence. The `gdown` command was not
run here; Google Drive quota limits often hit large files.

## Loading and tooling

- ROS1 bags; UWB uses `nlink_parser/LinktrackNodeframe3` (custom msg), Livox uses
  `livox_ros_driver/CustomMsg`, both need their message packages (or `rosbags` with registered .msg).
- `mcdviral/ceva` (not indexed) wraps basalt splines in Python to query GT pose / velocity at any time.
- `pose_inW.csv` columns `num t x y z qx qy qz qw` drop straight into
  [evo](../../catalog/repos/michaelgrupp__evo.md) after removing the `num` column.

## Hackathon fit

- Idea 19 (cooperative localization) and idea 13 (radio-ranging return-to-home): UWB
  ranges + IMU + continuous-time truth in a few MB per sequence. Cheapest real UWB data in the index besides UTIL.
- Idea 10 (VIO without GNSS) on night sequences, and lidar odometry against a survey map.

## Pitfalls

- Google Drive downloads are throttled; pre-fetch before the event.
- Body frame is VN100 on NTU but VN200 on KTH/TUHH (User Manual).
- Ouster header stamp is the end of the sweep, Livox header stamp is the start (User Manual);
  deskew accordingly.
- GPS only on the ATV (NTU), so there is no GNSS story for the handheld campuses.
- UWB anchor positions: check the site before relying on them; not confirmed in the pages read.

## Sources

- https://github.com/mcdviral/mcdviral.github.io: README.md (license, features), Download.md (sizes, links),
  UserManual.md (topics, rates, frames), Groundtruth.md (GT formats), read via `gh api` 2026-11-06
