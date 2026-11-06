# Newer College

<!-- about: res:ori-newer-college-dataset -->

Handheld lidar + camera + IMU sequences around New College and the Maths Institute in Oxford, plus an underground mine, from the Oxford Dynamic Robot Systems group (2020 original, 2021 multi-camera extension). Ground truth comes from registering each lidar scan to a survey-grade prior map, so truth is dense 6-DoF over the whole run.

| Field | Value |
|---|---|
| Platform | Handheld rig carried at walking speed (~6.7 km total) |
| Environment | College quads, cloister, park, Maths Institute (indoor/outdoor), an underground mine (2021 collection 4) |
| Sensors and rates | 2020: Intel Realsense D435i stereo-inertial + Ouster OS1-64 (Gen 1) with IMU. 2021: Sevensense Alphasense Core (4 cameras + IMU) + Ouster OS0-128 with IMU. Rates not stated on the site |
| Ground truth | Leica BLK360 tripod scans => mm-accurate prior map (290 M points); per-scan 6-DoF poses by registration to the map, stated as "centimetre accurate" |
| Size | HF usedStorage 610.6 GB total. 2020: short experiment bags 98.5 GB, long 171.0 GB, quad_with_dynamics 25.6 GB, dynamic_spinning 7.7 GB, parkland_mound 32.2 GB. 2021: per bag 1.8-11 GB, e.g. math-easy part 1 1.84 GB, mine easy 7.99 GB (HF tree API, 2026-11-06) |
| License | CC BY-NC-SA 4.0 (HF card); not stated on the site |
| Format | ROS1 bags; ground truth CSV per sequence; prior map as PLY/E57 |
| Index | [Newer College](../../catalog/resources/ori-newer-college-dataset.md) |

## What's in it

- 2020 (`2020-ouster-os1-64-realsense/`): 01_short_experiment (also raw format), 02_long_experiment, 05_quad_with_dynamics, 06_dynamic_spinning, 07_parkland_mound; prior map at 1 cm and 5 cm resolution; calibration bags.
- 2021 (`2021-ouster-os0-128-alphasense/`): collection 1 quad easy/medium/hard + stairs; collection 2 park and cloister; collection 3 maths institute easy/medium/hard; collection 4 underground mine easy/medium/hard; per-collection camera calibration and ground truth; prior maps.

## Download

```bash
HF=https://huggingface.co/datasets/ori-drs/newer_college_dataset/resolve/main
# Smallest useful 2021 pair: math-easy part 1 (1.84 GB) + its ground truth folder
wget "$HF/2021-ouster-os0-128-alphasense/collection%203%20-%20maths%20institute/2021-04-07-13-52-31_1-math-easy.bag"
# Directory pulls with the HF CLI (venv); quote paths with spaces
huggingface-cli download ori-drs/newer_college_dataset --repo-type dataset --local-dir ncd \
  --include "2021-ouster-os0-128-alphasense/collection 3 - maths institute/*" \
            "2021-ouster-os0-128-alphasense/os_imu_lidar_transforms.yaml"
```

The dataset is not gated on HF (API `gated: false`).

## Loading and tooling

- LIO: [FAST-LIO](../../catalog/repos/hku-mars__fast_lio.md), [KISS-ICP](../../catalog/repos/prbonn__kiss-icp.md), [LIO-SAM](../../catalog/repos/tixiaoshan__lio-sam.md), [GLIM](../../catalog/repos/koide3__glim.md). VIO on Alphasense: [OpenVINS](../../catalog/repos/rpng__open_vins.md), [OKVIS2](../../catalog/repos/ethz-mrl__okvis2.md).
- Lidar-IMU extrinsics: `os_imu_lidar_transforms.yaml`; Ouster beam intrinsics JSON per sensor.
- Scoring: [evo](../../catalog/repos/michaelgrupp__evo.md) (GT CSV => TUM).
- Prior map: usable for map-based localization (register live scans to the PLY), which is a real "known-map, no GNSS" scenario.

## Hackathon fit

- Map-based relocalization without GNSS: localize against the provided survey map, a stand-in for a pre-surveyed base or facility.
- Underground mine sequences: tunnel/subterranean navigation demos (compare [SubT datasets](subt-datasets.md)).
- Idea 10 handheld VIO/LIO with dense truth.

## Pitfalls

- Folder names contain spaces; URL-encode or use the HF CLI.
- 2020 long experiment is 171 GB; do not grab the whole 2020 tree.
- 2020 uses a Realsense D435i (consumer stereo-inertial); for VIO prefer the 2021 Alphasense set, which was built for visual-inertial use.
- License only stated on the HF card (CC BY-NC-SA 4.0).

## Sources

- https://ori-drs.github.io/newer-college-dataset/ (sensors, GT method, HF location)
- HF API datasets/ori-drs/newer_college_dataset (license, usedStorage 610,602,574,863, gated false) and tree listings (per-folder sizes)
