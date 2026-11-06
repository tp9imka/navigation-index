# MILUV - multi-UAV indoor localization with UWB and vision

<!-- about: repo:decargroup/miluv, res:miluv-dataset-2025 -->

McGill DECAR group dataset with three quadcopters flying together, ranging to anchors and to each other over UWB, plus cameras, IMUs and magnetometers, with mocap truth. Paper: Shalaby et al., arXiv 2504.14376 (2025): 36 experiments, 217 min of flight (arXiv abstract).

| Field | Value |
|---|---|
| Platform | Up to 3 Uvify IFO-S quadcopters (Jetson Nano, PX4), each with 2 UWB transceivers, RealSense D435i, downward camera, downward laser rangefinder |
| Environment | About 4 x 4 x 3 m section of an indoor arena, 6 UWB anchors, 3 anchor constellations, AprilTags as visual features; some runs with wood/plastic/foam obstacles |
| Sensors and rates | Decawave DWM1000 UWB: two-way ranging incl. inter-robot, passive listening, channel impulse response (CIR), raw timestamps, RX power; PX4 IMU and D435i IMU; stereo/IR and colour cameras; height; magnetometer. Rates not stated on the pages read |
| Ground truth | Motion capture, 12 cameras (docs). Accuracy not stated |
| Size | figshare API (2026-11-06): 185.7 GB total in 39 zips. Smallest experiment zips: `cirOneTagOneAnchor_1_angular_0.zip` 0.94 GB, `default_1_circular3D_0.zip` 1.67 GB; 3-robot runs 3.2-11.1 GB; calibration zips 5-13 GB |
| License | Data: CC BY 4.0 (figshare). Devkit: MIT |
| Format | Per-experiment folders (CSV per robot/sensor + images, as loaded by the devkit); ROS msg package `uwb_ros` |
| Index | [MILUV devkit](../../catalog/repos/decargroup__miluv.md) |

## What's in it

Experiment names encode setup: `default_3_random_0` (3 robots, random trajectory), `default_1_circular2D_0` (1 robot), `noAprilTags_*`, `obstacles_*`, `cir_*` (with CIR logging), `cirOneTagOneAnchor_1_linear_0`/`_angular_0` (controlled range/angle sweeps). Devkit has SE(3) and SE2(3) EKF benchmarks for 1 and 3 robots, a VINS-Fusion config, LOS/NLOS classification from CIR, AprilTag detection.

## Download

```bash
git clone --depth 1 https://github.com/decargroup/miluv && cd miluv
mkdir -p data && cd data
curl -L -o default_3_random_0.zip https://ndownloader.figshare.com/files/52291625   # 3.2 GB, 3 robots
curl -L -o default_1_circular3D_0.zip https://ndownloader.figshare.com/files/52250702 # 1.7 GB, 1 robot
unzip default_3_random_0.zip    # devkit expects data/<experiment>/
# full list with sizes and URLs
curl -s https://api.figshare.com/v2/articles/28386041 | python3 -c \
 "import json,sys;[print(f['name'],f['size'],f['download_url']) for f in json.load(sys.stdin)['files']]"
```

## Used in this repo

Not downloaded or run by any sample yet (checked 2026-11-06). [samples/swarm-coop-localization](../../samples/swarm-coop-localization/) runs on simulated ranges with a Markov NLOS bias and names MILUV as the drop-in for real inter-robot UWB ranges and ground truth (replace `sim.generate`). Sizes on this card are from the figshare API, not from a download.

## Loading and tooling

```python
from miluv.data import DataLoader
import numpy as np
mv = DataLoader("default_3_random_0", height=False)
d = mv.data_from_timestamps(np.arange(0, 10, 1), ["ifo001", "ifo002"], ["imu_px4", "imu_cam"])
```

Install the devkit into the project venv (`uv pip install --python "$VENV/bin/python" -e .`) or use its Dockerfile / `docker compose up`.

## Hackathon fit

- Idea 19 (cooperative localization for a small team): inter-robot ranging with truth is exactly the data needed; the 3-robot EKF example is a baseline to beat or extend.
- Idea 13 (radio-ranging return-to-home): anchor ranging with NLOS obstacles; CIR enables a learned NLOS flag.

## Pitfalls

- Big: even one 3-robot run is 3-11 GB because of images. Pick 1-2 experiments before the event.
- Unzip location matters: devkit default path is `miluv/data/<experiment>`.
- Indoor mocap arena only; no GNSS or outdoor multipath.
- The devkit README lists no data URL; the figshare DOI (10.25452/figshare.plus.28386041.v1) comes from the arXiv page.

## Sources

- decargroup/miluv README and gh-pages docs (`index.md`, `docs/data.md`, `docs/gettingstarted.md`)
- https://arxiv.org/abs/2504.14376 (counts, DOI); figshare API `api.figshare.com/v2/articles/28386041` (files, sizes, license), 2026-11-06
