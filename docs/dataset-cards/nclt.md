# NCLT (Michigan North Campus Long-Term)

<!-- about: res:umich-nclt-dataset -->

University of Michigan PeRL dataset (Carlevaris-Bianco, Ushani, Eustice, IJRR 2016): 27
sessions of a Segway robot on the same campus over 15 months, indoor and outdoor, with
fibre-optic gyro, wheel odometry, consumer and RTK GPS. Unusually rich proprioception for a
long-term dataset and an open license.

| Field | Value |
|---|---|
| Platform | Segway-based wheeled robot (index summary; IJRR paper) |
| Environment | University of Michigan North Campus, indoor and outdoor, Jan 2012 - Apr 2013, varying route and time of day, seasons incl. snow |
| Sensors and rates | Velodyne HDL-32E; Ladybug3 omnidirectional camera; Microstrain GX3 IMU; KVH fibre-optic gyro; wheel odometry; standard and RTK GPS; Hokuyo 2D lidars (download table). Rates are in nclt.pdf, not restated on the web page |
| Ground truth | SLAM graph fusing lidar scan matching, odometry and RTK GPS; graph-node poses interpolated with odometry to about 100 Hz (2019 changelog). Marginal covariances for keyframes provided (2017). Accuracy not stated on the page |
| Size | Web table, summed over 27 sessions: images (lb3) 2558 GB, Velodyne 448 GB, sensors 2.6 GB. HEAD 2026-11-06 for 2012-01-08: sen.tar.gz 119 MB, vel.tar.gz 18.3 GB, groundtruth.csv 116 MB |
| License | Open Database License (ODbL) + Database Contents License; share-alike for public adaptations, commercial use not excluded |
| Format | tar.gz per modality per session; CSV sensor logs; first 40 MB of 2012-01-08_sen.tar.gz lists `gps.csv`, `gps_rtk.csv`, `ms25.csv`, `ms25_euler.csv`, `wheels.csv`, `odometry_mu.csv`, `odometry_mu_100hz.csv`, `odometry_cov.csv`; Velodyne packed binary; Ladybug3 tiff |
| Index | [NCLT](../../catalog/resources/umich-nclt-dataset.md), [evo](../../catalog/repos/michaelgrupp__evo.md) |

## What's in it

27 sessions, average about 1.29 h and 5.5 km each; total 34.9 h and 147.4 km (web page).
Sessions are named by date, `2012-01-08` to `2013-04-05`.

## Download

```bash
B=https://s3.us-east-2.amazonaws.com/nclt.perl.engin.umich.edu
D=2012-01-08
# GNSS / IMU / FOG / odometry + truth: about 235 MB
wget $B/sensor_data/${D}_sen.tar.gz $B/ground_truth/groundtruth_${D}.csv $B/covariance/cov_${D}.csv
# Lidar for the same session: 18.3 GB
wget $B/velodyne_data/${D}_vel.tar.gz
# Official bulk script
wget $B/downloader.py && python3 downloader.py --help
```

All four URLs answered HEAD with 200 on 2026-11-06.

## Loading and tooling

```python
import numpy as np, pandas as pd
gt  = np.genfromtxt('groundtruth_2012-01-08.csv', delimiter=',')  # utime[us], x, y, z, roll, pitch, heading
gt  = gt[~np.isnan(gt).any(axis=1)]                              # first row is NaN
rtk = pd.read_csv('2012-01-08/gps_rtk.csv', header=None)          # check column order in nclt.pdf
```

- The page links a Python script for projecting Velodyne into camera images and one for
  reading only SLAM-graph node poses.
- GT is in a local frame; convert to TUM (`t x y z qx qy qz qw`) for [evo](../../catalog/repos/michaelgrupp__evo.md).

## Hackathon fit

- Idea 5 (INS holdover budget): FOG + IMU + wheel odometry with consumer GPS dropouts
  (indoor passages) and truth; compute dead-reckoning drift per minute of GNSS loss.
  `sen.tar.gz` is small enough to carry on a laptop.
- Reference arch 4.3 (fusion with integrity): consumer GPS vs RTK vs truth in one session,
  ready-made for a residual-based fault detector.

## Pitfalls

- Truth is an interpolated SLAM solution, not a direct RTK track; between graph nodes it is odometry-interpolated.
- Camera intrinsics table in the paper had x/y swapped (changelog); use `cam_params.zip`.
- Images are the bulk (about 2.5 TB); skip them unless you need vision.
- groundtruth CSV starts with a NaN row (checked 2012-01-08); timestamps are microseconds.
- Check sensor CSV column orders in nclt.pdf before parsing (not re-read here).

## Sources

- http://robots.engin.umich.edu/nclt/ (overview, changelog, license, download table), fetched 2026-11-06
- HEAD on the S3 URLs above, 2026-11-06
