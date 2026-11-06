# Subterranean datasets: SubT-MRS, DARPA SubT reference, NeBula multi-robot

<!-- about: res:cmu-subt-mrs-dataset, res:darpa-subt-reference-datasets, repo:nebula-autonomy/nebula-multirobot-dataset, res:darpa-subt-challenge -->

Three public data sources born from the DARPA Subterranean Challenge (2018-2021): GNSS-free tunnels, caves, mines and urban underground, often with smoke, dust and darkness. Each serves a different purpose.

| Field | SubT-MRS (CMU) | DARPA SubT reference (ARL for DARPA) | NeBula multi-robot (JPL CoSTAR) |
|---|---|---|---|
| Platform | UGVs, UAV, legged robot, RC cars, handheld | Tunnel: Clearpath Husky. Urban: GVRbot (modified PackBot) | Huskies and Spot robots, 2-4 per dataset |
| Environment | Caves, tunnels, urban, off-road; darkness, smoke, dust, snow, fog | Tunnel circuit (SR and EX courses), Urban circuit (Alpha/Beta courses, 2 floors) | Tunnel, Urban, Finals prelim, Kentucky Underground mine (1.2-6.3 km per dataset) |
| Sensors | 4 RGB cameras, lidar, IMU, thermal (models/rates not listed on page) | Ouster OS1-64, Multisense SL (lidar + stereo), CO2 sensor; thermal IR unusable in Urban | Processed lidar keyed scans + incremental pose graphs (not raw sensors) |
| Ground truth | Separate Google Drive files; method and accuracy not stated on the page | `support.tgz` with GT and artifact annotations (Tunnel); Urban support "being processed" | GT odometry bags, `result.g2o` and GT point cloud per dataset |
| Size | Not stated, not verified (Google Drive) | HEAD 2026-11-06: a_lvl_1.bag 13.85 GB, b_lvl_1.bag 14.68 GB, sr_B_route2.bag 17.46 GB; README: ex_B_route1 33 GB, sr_B_route1 19.6 GB | Not verified (Google Drive) |
| License | Not stated | Not stated (government-released data) | Repo license not set |
| Format | ROS bags + extracted folders; TUM-style GT (`t x y z qx qy qz qw`) | ROS1 bags (lz4-compressed in Urban) | ROS bags + g2o + PCD |

Index: [SubT-MRS](../../catalog/resources/cmu-subt-mrs-dataset.md), [DARPA SubT reference datasets](../../catalog/resources/darpa-subt-reference-datasets.md), [NeBula multi-robot dataset](../../catalog/repos/nebula-autonomy__nebula-multirobot-dataset.md), [DARPA SubT Challenge](../../catalog/resources/darpa-subt-challenge.md), [osrf/subt virtual](../../catalog/repos/osrf__subt.md).

## What's in it

- **SubT-MRS:** primary release (Final_Challenge_UGV1-3, Urban_Challenge_UGV1-2, Laurel_Cavern handheld, plus 3 TartanAir lidar sims), a sensor-fusion extension (Multi_Floor, Long_Corridor, BlockLiDAR, BlockVisual, SmokeRoom, OutdoorNight, FlashLight) and SuperLoc (Cave01-04, Corridor01-02, Floor01-02) with GT maps. Used in ICCV SLAM challenges.
- **DARPA reference:** 4 Urban bags and 3 Tunnel bags, teleoperated, plus a catkin workspace (`subt_reference_datasets`) with message types.
- **NeBula:** multi-robot SLAM inputs as transmitted to the base station (keyed scans + pose graph segments), already converted to g2o/pcd too. Pairs with [LAMP](../../catalog/repos/nebula-autonomy__lamp.md).

## Download

```bash
# DARPA SubT reference, direct S3 (no account)
wget https://subt-data.s3.amazonaws.com/SubT_Urban_Ckt/a_lvl_1.bag        # 13.85 GB, lz4
wget https://subt-data.s3.amazonaws.com/SubT_Tunnel_Ckt/sr_B_route2.bag    # 17.46 GB
wget https://subt-data.s3.amazonaws.com/SubT_Tunnel_Ckt/support.tgz       # GT + annotations, 8 KB
rosbag decompress a_lvl_1.bag      # Urban bags are lz4; README says decompress before playback
# SubT-MRS: Google Drive links on https://superodometry.com/datasets (gdown per file)
# NeBula: Google Drive folders in dataset.md of the repo, e.g. Tunnel
gdown --folder https://drive.google.com/drive/folders/1gcUEDBp_aeGwS059xnK4Xv8qlU3JQUNE
```

Note: Tunnel `support.tgz` is only 8,310 bytes by HEAD, so it is likely a pointer or small annotation set, not dense GT. Open it before relying on it.

## Loading and tooling

- DARPA bags need the message packages in `bitbucket.org/subtchallenge/subt_reference_datasets` (ROS Melodic, Docker option provided).
- NeBula: [LAMP](../../catalog/repos/nebula-autonomy__lamp.md) consumes the pose-graph messages; g2o files open in any pose-graph optimizer (GTSAM, g2o).
- SubT-MRS: [FAST-LIO](../../catalog/repos/hku-mars__fast_lio.md), [KISS-ICP](../../catalog/repos/prbonn__kiss-icp.md) for lidar; thermal VO for smoke rooms.
- Scoring: [evo](../../catalog/repos/michaelgrupp__evo.md).

## Hackathon fit

- Idea 19 (cooperative localization for a small team): NeBula gives multi-robot pose graphs ready for inter-robot loop closure, no raw processing needed.
- Underground / building-interior GNSS-denied navigation: SubT-MRS smoke and darkness sequences for thermal or lidar fallback demos.
- Degraded-sensor switching (camera blinded => lidar/thermal): SubT-MRS BlockVisual / BlockLiDAR sequences are built for it.

## Pitfalls

- DARPA Urban b_lvl_2 has no Ouster data (equipment failure per README); thermal IR unusable in Urban.
- DARPA workspace targets ROS Melodic; use the Docker path.
- SubT-MRS and NeBula live on Google Drive; quotas and no sizes up front.
- NeBula data is already processed by the CoSTAR front-end; you cannot evaluate your own odometry on it.

## Sources

- https://superodometry.com/datasets (SubT-MRS sequences, sensors, GT distribution, formats)
- Bitbucket API `subtchallenge/subt_reference_datasets/src/master/README.md` (platforms, sensors, S3 URLs, compression notes); HEAD on three S3 bags + support.tgz
- `gh api repos/NeBula-Autonomy/nebula-multirobot-dataset/contents/dataset.md` (robots, distances, folders, Drive links)
