# Event-camera datasets: DSEC, MVSEC, VECtor

<!-- about: res:uzh-dsec-dataset, res:upenn-mvsec-dataset, res:vector-event-slam-benchmark, repo:uzh-rpg/event-based_vision_resources, repo:neuromorphs/tonic -->

Event cameras report per-pixel brightness changes with microsecond latency and high dynamic range, which helps in night, glare and fast motion. Three widely used datasets with stereo events and some form of ground truth. For an aggressive-drone event set see [UZH-FPV](uzh-fpv.md).

| Field | DSEC (UZH, 2021) | MVSEC (UPenn, 2018) | VECtor (ShanghaiTech MPL, 2022) |
|---|---|---|---|
| Platform | Car | Several: indoor flying, outdoor driving (day/night), motorcycle highway (index: hexacopter and car) | Not stated on site (small- and large-scale sequences) |
| Sensors | Stereo event + stereo frame cameras, lidar, IMU (models not on the download page) | Stereo DAVIS (events + grayscale), VI-Sensor IMU; lidar except motorcycle | Stereo event (Prophesee message type), stereo frame, RGB-D (Azure Kinect projector tool linked), lidar, IMU; hardware-synchronized |
| Ground truth | Disparity, optical flow, semantic masks. **No pose ground truth** on the download page | Per-sequence GT files (poses, depth) and dense flow `.npz`; source not named on download page | Full 6-DoF from "highly accurate external reference devices such as a motion capture system" (site) |
| Size | Page-stated: train events 125 GB, images 216 GB, disparity 12 GB, flow 3.7 GB; test events 27 GB, images 43 GB; lidar+IMU 26 GB. HEAD: interlaken_00_c_events_left.zip 0.86 GB | Page-stated per file, e.g. indoor_flying1_data.bag 1.2G (HEAD 1,278,934,515 bytes), outdoor_day2_data.bag 27G, motorcycle highway1 42G | Not stated; Google Drive / OneDrive hosting, not verified |
| License | CC BY-SA 4.0, commercial use allowed (dsec.ifi.uzh.ch) | Not stated on download page | BSD 3-Clause Clear (data, docs, toolbox) |
| Format | Per-sequence zips per modality (events left/right, rectified images, disparity, flow); see dsec.ifi.uzh.ch/data-format | ROS bags (need rpg_dvs_ros messages) and HDF5 mirrors | ROS bags (Prophesee EventArray), toolbox can merge bags |

Index: [DSEC](../../catalog/resources/uzh-dsec-dataset.md), [MVSEC](../../catalog/resources/upenn-mvsec-dataset.md), [VECtor](../../catalog/resources/vector-event-slam-benchmark.md), [event-based vision resources list](../../catalog/repos/uzh-rpg__event-based_vision_resources.md), [Tonic](../../catalog/repos/neuromorphs__tonic.md).

## What's in it

- **DSEC:** 41 training + 12 test driving sequences (e.g. interlaken_00_c, zurich_city_12_a), including night and difficult illumination; lidar + IMU as rosbags.
- **MVSEC:** indoor_flying 1-4, outdoor_day 1-2, outdoor_night 1-3, motorcycle highway 1.
- **VECtor:** small-scale (mocap) and large-scale sequences, calibration toolbox and results; uploaded 30 June 2022.

## Download

```bash
# DSEC: one sequence's left events (0.86 GB)
wget https://download.ifi.uzh.ch/rpg/DSEC/train/interlaken_00_c/interlaken_00_c_events_left.zip
# MVSEC: smallest indoor flight with GT
wget https://visiondata.cis.upenn.edu/mvsec/indoor_flying/indoor_flying1_data.bag
#   ground truth is a separate file on the download page (2.6G for indoor_flying1, page-stated)
# VECtor: per-sequence Google Drive links on https://star-datasets.github.io/vector/download/
```

The MVSEC HDF5 path I guessed (`indoor_flying1_data.hdf5`) returned 404; take HDF5 links from the download page as listed.

## Loading and tooling

- [Tonic](../../catalog/repos/neuromorphs__tonic.md) has loaders/transforms for many event datasets (check DSEC/MVSEC support in its docs).
- [rpg_dvs_ros](../../catalog/repos/uzh-rpg__rpg_dvs_ros.md) for MVSEC bag message types.
- Event VO: [DEVO](../../catalog/repos/tum-vision__devo.md), [ESVO](../../catalog/repos/hkust-aerial-robotics__esvo.md) (stereo event VO), [HKU event VO/VIO/SLAM index](../../catalog/repos/arclab-hku__event_based_vo-vio-slam.md).
- VECtor toolbox: https://github.com/mgaoling/mpl_dataset_toolbox (bag merger, not in index).
- Scoring: [evo](../../catalog/repos/michaelgrupp__evo.md) for MVSEC and VECtor poses.

## Hackathon fit

- Night / glare / fast-motion navigation where frame VO fails: show an event-based front end holding track on MVSEC outdoor_night or DSEC night where a frame pipeline loses it.
- C-UAS sensing research (event cameras for small fast targets) is adjacent; none of these datasets contains drones as targets.
- Low-priority unless the hackathon provides event hardware.

## Pitfalls

- DSEC has no pose ground truth: use it for flow/depth, not odometry scoring.
- Event data volume is large and needs HDF5/bag-specific readers; budget a few hours just for I/O.
- MVSEC outdoor GT quality differs from indoor mocap GT; read the paper before claiming cm-level accuracy outdoors.
- VECtor hosting is on cloud drives; sizes unknown in advance.

## Sources

- https://dsec.ifi.uzh.ch/dsec-datasets/download/ (sizes, URLs, sequences) and https://dsec.ifi.uzh.ch/ (CC BY-SA 4.0); HEAD on interlaken_00_c_events_left.zip
- https://daniilidis-group.github.io/mvsec/download/ (sequences, URLs, sizes, formats); HEAD on indoor_flying1_data.bag
- https://star-datasets.github.io/vector/ and /download/ (sensors, GT statement, license, toolbox, Drive links)
