# MulRan and HeLiPR

<!-- about: res:snu-mulran-dataset, res:snu-helipr-dataset, repo:url-kaist/outlier-robust-radar-odometry, repo:mttgdd/open-radvlad -->

Two place-recognition datasets from SNU RPM Robotics Lab (Korea). MulRan (Kim et al., ICRA
2020): radar + lidar on repeated urban routes with month-level gaps and reverse revisits.
HeLiPR (Jung et al., IJRR 2024): the same kind of routes with four different lidars
(spinning, solid-state, FMCW) for cross-lidar place recognition, with sequences aligned to
MulRan routes 4 years later.

| Field | MulRan | HeLiPR |
|---|---|---|
| Platform | Car | Car |
| Environment | Daejeon (DCC, KAIST, Riverside) and Sejong city, Korea; 2019 | Roundabout, Town, Bridge (2023) plus KAIST / DCC / Riverside revisits (2023-2024, incl. night) |
| Sensors and rates | Ouster OS1-64 lidar, Navtech scanning radar; IMU and GPS added 2020-11 (site). Rates not stated on pages read | Ouster OS2-128, Velodyne VLP-16, Livox Avia, Aeva Aeries II (FMCW, radial velocity), all 10 Hz, asynchronous; Xsens MTi-300 IMU; NovAtel SPAN-CPT7 INS with dual antenna |
| Ground truth | "Baseline" SE3 trajectory with time, CSV, referenced to the rear-axle centre on the ground; method in the IJRR paper (not on the site). Accuracy not stated | 6-DoF per-lidar GT `[t x y z qx qy qz qw]` from the INS via extrinsics and B-spline interpolation; global UTM version for MulRan correspondence. Accuracy not stated |
| Size | Download page, unzipped: per sequence lidar 5.4-30.2 GB, radar polar 2.8-15.5 GB, radar ray 6.5-34.8 GB; sum for 12 sequences about 161 GB lidar + 82 GB radar polar (sum of stated sizes). ParkingLot sample: lidar 1.2 GB, radar polar 0.6 GB | Download page, unzipped: per sequence Ouster 34-79 GB, Aeva 25-63 GB, Velodyne 4.4-12 GB, Avia 3.6-8.9 GB; Roundabout01 1-minute sample 3.2 GB total. Calibration bags 33 / 40 GB |
| License | CC BY-NC-SA 4.0 (Citation tab) | Not stated on the pages read |
| Access | Google Form request, link emailed | Google Form request, link emailed |
| Format | Lidar `.bin` (KITTI layout), radar polar `.png`, radar per-ray `.csv`, Oxford-compatible polar zip on request; ROS file player | Per-lidar `.bin` + `stamp.csv`, `inertial_data/xsens_imu.csv`, GT txt; ROS file player |
| Index | [MulRan](../../catalog/resources/snu-mulran-dataset.md) | [HeLiPR](../../catalog/resources/snu-helipr-dataset.md) |

## What's in it

- MulRan sequences: DCC 01-03, KAIST 01-03, Riverside 01-03 (03 reverse), Sejong 01-03
  (03 reverse), plus ParkingLot sample. Same route weeks apart, reverse direction, lane shifts.
- HeLiPR sequences: Roundabout 01-03, Town 01-03, Bridge 01-04, KAIST 04-06, DCC 04-06,
  Riverside 04-06 (06 sequences added Jan 2024 for temporal gap).

## Download

```bash
# Both datasets: fill the Google Form linked on the Download page; links arrive by email.
#   https://sites.google.com/view/mulran-pr/download
#   https://sites.google.com/view/heliprdataset/download
# Smallest useful: MulRan KAIST 02 radar-polar (zipped 1.5 GB) + its baseline CSV,
#   or HeLiPR Roundabout01 sample (Aeva + Ouster about 1.5 GB zipped).
```

No direct URLs, so sizes are the page's statements, not HEAD checks. Allow a day for the
form-to-email turnaround.

## Loading and tooling

- Lidar `.bin`: `np.fromfile(f, np.float32).reshape(-1, 4)` for MulRan Ouster (KITTI layout per site);
  HeLiPR per-lidar layouts differ (Aeva has radial velocity) - read the System page struct.
- Radar polar PNG: parse like Oxford Radar RobotCar; the Oxford-compatible variant works with
  [robotcar-dataset-sdk](../../catalog/repos/ori-mrg__robotcar-dataset-sdk.md) `radar.load_radar`.
- Radar odometry: [outlier-robust radar odometry](../../catalog/repos/url-kaist__outlier-robust-radar-odometry.md)
  (KAIST, evaluated on MulRan); radar place recognition: [Open-RadVLAD](../../catalog/repos/mttgdd__open-radvlad.md).
- Lab tools linked from the sites (Scan Context, file_player_mulran) are not indexed.

## Hackathon fit

- Idea 18 / map-based relocalization with range sensors: "I came back weeks later from the
  other direction, where am I?" is exactly MulRan's design.
- HeLiPR: show a place-recognition descriptor that survives a sensor swap (Ouster map,
  Livox query), relevant when the deployed platform differs from the mapping platform.

## Pitfalls

- Request-form access; not something to start on hackathon day.
- MulRan file player needs IMU/GPS folders present even if unused (site note).
- Non-commercial license (MulRan); HeLiPR license not found on the pages read.
- HeLiPR lidars are asynchronous; use per-lidar GT, not a shared frame index.

## Sources

- https://sites.google.com/view/mulran-pr (+ /dataset, /download, /citation), fetched 2026-11-06
- https://sites.google.com/view/heliprdataset (+ /system, /sequence, /download), fetched 2026-11-06
