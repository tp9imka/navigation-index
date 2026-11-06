# Boreas and Boreas Road Trip

<!-- about: repo:utiasasrl/pyboreas, repo:utiasasrl/steam_icp, repo:dan11003/cfear_radarodometry -->

University of Toronto ASRL driving datasets: Boreas (Burnett et al., IJRR 2023), repeated
Toronto routes over a year in all weather including snow; Boreas Road Trip (Boreas-RT,
arXiv 2602.16870, 2026) adds more routes plus an FMCW lidar and a standalone IMU. Open on
public S3, CC BY 4.0: the most usable radar + lidar + camera + cm truth dataset in the index.

| Field | Value |
|---|---|
| Platform | Car with roof sensor rack (vehicle model not stated in the devkit docs read) |
| Environment | Toronto: Glen Shields loop and St George (downtown) routes, repeated across seasons; snow, rain, night. Boreas-RT: additional "challenging roads" routes |
| Sensors and rates | Velodyne Alpha Prime 128-beam lidar; FLIR Blackfly S 2448x2048 camera, extracted at 10 Hz; Navtech CIR204-H radar, 4 Hz, 400 azimuths, 0.0596 m bins to 200 m; Applanix POS LV with wheel encoder. Boreas-RT adds Aeva Aeries II FMCW lidar and a Silicon Sensing DMU41 IMU (README) |
| Ground truth | Applanix POS LV + RTX corrections, post-processed in POSPac (batch RTS smoother). DATA_REFERENCE states RMS position error typically 2-4 cm, 200 Hz. Per-sensor poses (`lidar_poses.csv`, `radar_poses.csv`, `camera_poses.csv`) in a fixed ENU frame anchored at the first pose of `boreas-2020-11-26-13-58`. Test-set sequences have GT withheld |
| Size | S3 listing, 2026-11-06: `boreas-2020-11-26-13-58` = 118.2 GB (camera 63.5, lidar 50.3, radar 2.75, applanix 0.29 GB; 43,065 objects). Bucket has 125 sequence prefixes (48 from 2020-2022, 77 from 2024-2025) plus `boreas-objects-v1/`. Whole-bucket total not computed |
| License | CC BY 4.0 (DATA_LICENSE.md) - commercial use allowed with attribution |
| Format | Per-sequence folder: `camera/<ts>.png`, `lidar/<ts>.bin`, `radar/<ts>.png` (polar, Oxford-style), `applanix/*.csv`, `calib/*` |
| Index | [pyboreas](../../catalog/repos/utiasasrl__pyboreas.md), [STEAM-ICP](../../catalog/repos/utiasasrl__steam_icp.md), [CFEAR](../../catalog/repos/dan11003__cfear_radarodometry.md), [Oxford Radar RobotCar](oxford-radar-robotcar.md) |

## What's in it

Sequences are named `boreas-YYYY-MM-DD-HH-MM`. The 2020-2022 set is Boreas; 2024-2025
prefixes appear to be Boreas-RT (inferred from dates; check the website table). Leaderboards
for odometry, localization and 3D detection at boreas.utias.utoronto.ca.

## Download

```bash
# No AWS account needed. Radar + GT + calib for one sequence: about 3 GB
S=boreas-2020-11-26-13-58
aws s3 sync s3://boreas/$S ./boreas/$S --no-sign-request \
  --exclude "*" --include "radar/*" --include "applanix/*" --include "calib/*"
# Add lidar (about 50 GB for this sequence): --include "lidar/*"
# Without the AWS CLI, single files over HTTPS work:
curl -O https://boreas.s3.amazonaws.com/$S/applanix/gps_post_process.csv   # 77.6 MB (HEAD)
```

The AWS CLI was not installed on this machine, so the `aws` commands are from the README,
not run; the HTTPS listing and HEAD were run.

## Loading and tooling

```python
from pyboreas import BoreasDataset          # pip install asrl-pyboreas
bd = BoreasDataset('/data/boreas/')
seq = bd.sequences[0]
r = seq.get_radar(0)                          # r.load_data(); r.polar, r.azimuths, r.timestamps; r.pose = T_enu_radar
l = bd.get_lidar(0); pts = l.points           # x,y,z,i,r,t
```

- [pyboreas](../../catalog/repos/utiasasrl__pyboreas.md) also has odometry / localization evaluation scripts matching the leaderboard.
- Radar odometry: [CFEAR](../../catalog/repos/dan11003__cfear_radarodometry.md); lidar / radar
  continuous-time odometry: [STEAM-ICP](../../catalog/repos/utiasasrl__steam_icp.md) (same lab).

## Hackathon fit

- Reference arch 4.3 (fusion with integrity) with radar as the bad-weather sensor: radar
  odometry on a snow sequence vs truth, GNSS cut artificially.
- Idea 18 (map-based localization): localize a winter run against a lidar or radar map
  from a summer run on the same route; poses share one ENU frame, so no alignment fuss.
- Best open replacement for Oxford RobotCar (withdrawn 2026-10-22).

## Pitfalls

- Sensors are not synchronous; each frame has its own timestamp and pose (README).
- GT poses are float64; casting to float32 in PyTorch loses cm-level precision (README warns).
- Camera folder dominates size; exclude it unless you need vision.
- Test sequences have no GT; pick from the training split for self-scoring.

## Sources

- https://github.com/utiasASRL/pyboreas: README, DATA_REFERENCE.md, DATA_LICENSE.md via `gh api`, 2026-11-06
- S3 REST listing `https://boreas.s3.amazonaws.com/?list-type=2` (sizes, prefixes) and HEAD on gps_post_process.csv, 2026-11-06
