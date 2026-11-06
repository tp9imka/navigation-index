# RoNIN - Robust Neural Inertial Navigation dataset

<!-- about: repo:sachini/ronin, res:ronin-paper, repo:higerra/ridi_imu -->

Smartphone IMU dataset for learned pedestrian dead reckoning (Yan, Herath, Furukawa, ICRA 2020). A body-mounted Tango phone gives the trajectory while a second phone is carried naturally and records IMU.

| Field | Value |
|---|---|
| Platform | Pedestrians, two phones: harness-mounted 3D-tracking phone (Google Tango) + a second Android phone the subject handles freely (project page) |
| Environment | 100 human subjects (project page); venues not stated on the pages read |
| Sensors and rates | Android gyro, accel, magnetometer, rotation vectors, gravity, linear accel, step counter, pressure; optional Wi-Fi scans every 3 s and GPS. `synced` group resampled at 200 Hz (README.txt) |
| Ground truth | Tango visual SLAM pose (`tango_pos`, `tango_ori`) of the harness phone; accuracy not stated. Truth is for the body, not the IMU phone |
| Size | Not verified. Project page says more than 42.7 h of data; README.txt lists 327 sequences; about 50% withheld "due to security concerns" |
| License | Research use only (project page); FRDR lists a custom non-commercial license. Code: GPL-3.0 |
| Format | Per sequence `data.hdf5` (`raw`, `synced`, `pose` groups) + `info.json` |
| Index | [RoNIN code](../../catalog/repos/sachini__ronin.md), [RoNIN paper](../../catalog/resources/ronin-paper.md), [RIDI](../../catalog/repos/higerra__ridi_imu.md) |

## Download

```bash
# Data and pretrained models via FRDR (Canada); DOI redirect checked 2026-11-06
open https://doi.org/10.20383/102.0543
# => https://www.frdr-dfdr.ca/repo/dataset/816d1e8c-1fc3-47ff-b8ea-a36ff51d682a
# Options on that page: "Download as Zip" or Globus. Format spec:
curl -LO https://ronin.cs.sfu.ca/README.txt
```

When fetched on 2026-11-06 the FRDR page showed "No files uploaded" and "files ... are currently being backed up". Treat availability as uncertain and try early.

## Loading and tooling

```python
import h5py
with h5py.File("seq/data.hdf5") as f:
    t   = f["synced/time"][:]
    gyr = f["synced/gyro"][:]; acc = f["synced/acce"][:]
    ori = f["synced/game_rv"][:]
    pos = f["pose/tango_pos"][:]
```

Baselines: `source/ronin_resnet.py` (ResNet), `source/ronin_lstm_tcn.py` (LSTM/TCN), `source/ronin_body_heading.py`. RIDI (indexed) is the earlier SVR-based method.

## Hackathon fit

- Dismounted GNSS-free navigation demo: learned PDR on a phone, scored against Tango truth with ATE/RTE.
- Idea 5 (INS holdover budget) for pedestrians: compare naive double integration vs learned velocity.

## Pitfalls

- Half the data is not public; the public split differs from the paper's.
- Do not use `ekf_ori` at test time (README.txt says so).
- Trajectory truth belongs to the harness phone, so a body-vs-device heading offset is part of the task.
- FRDR download state was flaky when checked.

## Sources

- Sachini/ronin README; http://ronin.cs.sfu.ca/ and https://ronin.cs.sfu.ca/README.txt; FRDR landing page (via WebFetch), 2026-11-06
