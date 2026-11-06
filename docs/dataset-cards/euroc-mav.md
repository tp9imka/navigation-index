# EuRoC MAV

<!-- about: res:ethz-euroc-mav-dataset -->

Stereo + IMU sequences from a hexacopter MAV, ETH Zurich ASL, 2016 (Burri et al., IJRR). The default first test for any VIO pipeline: every major VIO repo ships an EuRoC config.

| Field | Value |
|---|---|
| Platform | Micro aerial vehicle (multirotor), indoor flights; airframe model not restated on the current ASL page |
| Environment | "Machine hall" (industrial hall, 5 sequences) and two Vicon rooms (3 sequences each) |
| Sensors and rates | VI-Sensor: stereo WVGA monochrome 2x20 FPS, MEMS IMU 200 Hz, hardware time alignment (ASL page) |
| Ground truth | Machine hall: Leica MS50 laser tracker (3D position only). Vicon rooms: Vicon motion capture (6D pose). Plus Leica MS50 3D structure scan. Accuracy figure not restated on the current page; page lists "very dynamic motions can deteriorate laser tracker accuracy" as a known issue |
| Size | machine_hall.zip 12.68 GB, vicon_room1.zip 6.04 GB, vicon_room2.zip 6.01 GB, calibration_datasets.zip 4.42 GB; total 29.2 GB. From the ETH Research Collection DSpace API `sizeBytes`, 2026-11-06 (HEAD not possible: host returned HTTP 429) |
| License | Research Collection deposit terms allow download "for personal use and non-commercial purposes"; item-level end-user license not retrieved (rate limited). Treat as non-commercial research use |
| Format | Each sequence as both ROS1 bag and "ASL" zip (CSV + PNG); both inside the per-environment zip |
| Index | [EuRoC MAV](../../catalog/resources/ethz-euroc-mav-dataset.md) |

## What's in it

- MH_01_easy, MH_02_easy, MH_03_medium, MH_04_difficult, MH_05_difficult (machine hall).
- V1_01..V1_03, V2_01..V2_03 (Vicon rooms, easy/medium/difficult).
- Calibration sequences (camera intrinsics, camera-IMU extrinsics), plus the dataset paper PDF.

## Download

The original per-sequence host (`robotics.ethz.ch/~asl-datasets/...`) did not answer on 2026-11-06. Files now live on the ETH Research Collection (DOI 10.3929/ethz-b-000690084) as one zip per environment, so you cannot fetch a single sequence.

```bash
# Vicon room 1 (V1_01..V1_03, smallest real subset, 6.0 GB)
curl -L -o vicon_room1.zip \
  https://www.research-collection.ethz.ch/server/api/core/bitstreams/02ecda9a-298f-498b-970c-b7c44334d880/content
# Machine hall (MH_01..MH_05, 12.7 GB)
curl -L -o machine_hall.zip \
  https://www.research-collection.ethz.ch/server/api/core/bitstreams/7b2419c1-62b5-4714-b7f8-485e5fe3e5fe/content
# Vicon room 2 (6.0 GB) / calibration (4.4 GB)
#   .../bitstreams/ea12bc01-3677-4b4c-853d-87c7870b8c44/content
#   .../bitstreams/5732e864-10f1-49e7-befb-669ee29ff770/content
unzip vicon_room1.zip   # contains V1_0x/V1_0x.bag and V1_0x/V1_0x.zip (ASL format)
```

The server rate-limits aggressively (HTTP 429 seen on metadata calls); retry with backoff and do not parallelize.

## Loading and tooling

- ASL format: `mav0/cam0/data/*.png`, `mav0/cam0/data.csv`, `mav0/imu0/data.csv`, `mav0/state_groundtruth_estimate0/data.csv` (ASL layout, per the dataset paper).
- Every mainstream VIO has an EuRoC config: [OpenVINS](../../catalog/repos/rpng__open_vins.md), [VINS-Fusion](../../catalog/repos/hkust-aerial-robotics__vins-fusion.md), [ORB-SLAM3](../../catalog/repos/uz-slamlab__orb_slam3.md), [Basalt](../../catalog/repos/vladyslavusenko__basalt.md), [OKVIS2](../../catalog/repos/ethz-mrl__okvis2.md), [DPVO](../../catalog/repos/princeton-vl__dpvo.md).
- Scoring: [evo](../../catalog/repos/michaelgrupp__evo.md) reads EuRoC ground-truth CSV directly; [rpg_trajectory_evaluation](../../catalog/repos/uzh-rpg__rpg_trajectory_evaluation.md) for the Zhang and Scaramuzza protocol.

```bash
evo_ape euroc mav0/state_groundtruth_estimate0/data.csv est_tum.txt -va --plot   # SE(3) align
```

## Hackathon fit

- Idea 10 (VIO => PX4 GPS-free flight with measured drift): replay a V1 sequence through the VIO, feed [vio-to-mavlink-bridge](../../samples/vio-to-mavlink-bridge/README.md) and report drift with evo before going near SITL.
- Idea 18 (visual geolocalization fused with VO): the VO half only; EuRoC has no georeference.
- Good warm-up for any team before a custom rig: known-good configs remove calibration as a variable.

## Pitfalls

- Machine-hall ground truth is position only (laser tracker), so rotation error cannot be scored there.
- Per-camera auto-exposure makes left/right brightness differ (ASL known issues).
- Vicon and sensor clocks are separate systems; the page warns synchronization is limited. Use evo `--t_max_diff` and align.
- Indoors only, short (minutes), no GNSS: EuRoC says nothing about outdoor or long-horizon drift.
- Old blog posts and scripts point to the dead `robotics.ethz.ch` URLs.

## Sources

- https://ethz-asl.github.io/datasets/euroc-mav/ (sensors, GT devices, known issues, tools)
- https://projects.asl.ethz.ch/datasets/doku.php?id=kmavvisualinertialdatasets (now a "moved" stub)
- Research Collection DSpace API `items/bcaf173e-.../bundles` (file list and byte sizes), `machine_hall.zip.json` (contents list), `license.txt` (deposit terms)
