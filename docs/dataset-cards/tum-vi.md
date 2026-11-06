# TUM-VI

<!-- about: res:tum-vi-benchmark -->

Handheld stereo + IMU benchmark from the TUM Computer Vision Group (Schubert et al., IROS 2018), with photometric calibration and long indoor/outdoor sequences. The standard test for long-horizon VIO drift, because most sequences end where they started.

| Field | Value |
|---|---|
| Platform | Rigid stereo-IMU rig with mocap markers (the page only says "rig"; commonly described as handheld) |
| Environment | Room (mocap hall), corridors, "magistrale" (large university hall), outdoors on campus, "slides" (sequence group name as on the page) |
| Sensors and rates | 2 monochrome global-shutter cameras, 1024x1024 at 20 Hz, 16-bit, linear response, HDR; IMU 200 Hz; hardware time-synchronized (TUM page) |
| Ground truth | Motion capture at 120 Hz. Full trajectory only for `room` sequences; start and end segments only for corridor, magistrale, outdoors, slides. Accuracy figure not stated on the page |
| Size | EuRoC-format export at 512x512: 28 evaluation sequences 172 GB (178 GB with calibration). room1 512 = 1.71 GB (HEAD Content-Length 1707110400). Outdoors1 512 = 16 GB, 1024 = 49 GB. ROS bags at 512: 285 GB. Directory listing sizes on cdn3.vision.in.tum.de, 2026-11-06 |
| License | Data CC BY 4.0, code BSD-2-Clause (TUM page) |
| Format | ROS1 bag (raw and calibrated), or EuRoC/DSO export (tar), each at 512x512 and 1024x1024 |
| Index | [TUM VI benchmark](../../catalog/resources/tum-vi-benchmark.md) |

## What's in it

- Evaluation: room1-6, corridor1-5, magistrale1-6, outdoors1-8, slides1-3 (28 sequences).
- Calibration: calib-cam1-8, calib-imu1-4, vignette sequences, plus 111 h imu-static recording for Allan variance.
- Calibration archives for two camera models (omni-radtan, pinhole-equi) at both resolutions, ~5 MB each.

## Download

```bash
# Smallest useful: one room sequence, full GT, EuRoC layout, 512x512 (1.7 GB)
wget https://cdn3.vision.in.tum.de/tumvi/exported/euroc/512_16/dataset-room1_512_16.tar
wget https://cdn3.vision.in.tum.de/tumvi/exported/euroc/512_16/dataset-room1_512_16.tar.md5
# Drift test: corridor1 at 512 (3.3 GB), ground truth at start/end only
wget https://cdn3.vision.in.tum.de/tumvi/exported/euroc/512_16/dataset-corridor1_512_16.tar
# Mirror a whole folder (page's own pattern)
wget -R "index.*" -m -np -nH --no-check-certificate -e robots=off \
  https://cdn3.vision.in.tum.de/tumvi/exported/euroc/512_16/
```

cdn3 redirects (302) to cdn2.vision.in.tum.de; wget follows it.

## Loading and tooling

- EuRoC export means any EuRoC loader works: [OpenVINS](../../catalog/repos/rpng__open_vins.md), [Basalt](../../catalog/repos/vladyslavusenko__basalt.md) (same group; has TUM-VI configs), [ORB-SLAM3](../../catalog/repos/uz-slamlab__orb_slam3.md), [VINS-Fusion](../../catalog/repos/hkust-aerial-robotics__vins-fusion.md).
- IMU noise from imu-static via [kalibr_allan](../../catalog/repos/rpng__kalibr_allan.md).
- Scoring: [evo](../../catalog/repos/michaelgrupp__evo.md). For start/end-only sequences, compute the loop-closure error (end minus start after aligning the start segment) rather than full ATE.

```bash
evo_ape euroc mav0/mocap0/data.csv est_tum.txt -va
```

## Hackathon fit

- Idea 10 (VIO => PX4 GPS-free flight with measured drift): the corridor/magistrale/outdoors sequences give a "drift after N metres with no external fix" number, which is the figure judges want.
- Idea 5 (INS holdover budget calculator): imu-static (111 h) is real data for Allan variance of a consumer-grade IMU.
- Pedestrian/dismounted demos: handheld walking motion is closer to a soldier-worn camera than any drone dataset.

## Pitfalls

- Ground truth missing in the middle of most sequences: full-trajectory ATE is only possible on `room`.
- 1024x1024 16-bit is heavy; take 512 unless you need resolution.
- Two camera models are provided; use the calibration that matches your VIO (equidistant fisheye vs omni).
- Page notes timestamp offsets per sequence in a table; apply them if you use raw bags.

## Sources

- https://cvg.cit.tum.de/data/datasets/visual-inertial-dataset (sensors, GT policy, license, URL patterns, calibration sizes)
- https://cdn3.vision.in.tum.de/tumvi/exported/euroc/512_16/ , .../1024_16/ , .../calibrated/512_16/ (listing sizes)
- HEAD on dataset-room1_512_16.tar (1,707,110,400 bytes)
