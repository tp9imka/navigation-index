# KITTI (odometry, raw) and KITTI-360

<!-- about: res:kitti-odometry-benchmark, res:kitti-360-dataset, repo:utiasstars/pykitti, sample:relative-nav-benchmark -->

Karlsruhe (KIT / MPI) driving datasets. KITTI (2012) is the default stereo / lidar odometry
benchmark; KITTI-360 (2021) re-drives suburbs of Karlsruhe with a 360-degree sensor rig and
dense semantic labels.

| Field | Value |
|---|---|
| Platform | Car (VW Passat wagon per the KITTI IJRR 2013 paper; not re-checked this session) |
| Environment | Karlsruhe city, residential, highway, rural roads; daytime, good weather |
| Sensors and rates | Grey + colour stereo cameras (0.5 MP png), Velodyne lidar (about 100k points / frame), OXTS GPS/IMU (RT3003 per the paper); synced streams at 10 Hz. Raw "extract" archives keep OXTS at its native higher rate. KITTI-360 adds 2 fisheye cameras and a pushbroom SICK lidar |
| Ground truth | OXTS GPS/IMU poses. The odometry page notes the OXTS error on very short sub-sequences was large enough that they changed the metric to 100-800 m segments. Absolute accuracy figure: not restated on the pages checked |
| Size | Odometry: grey 23.2 GB, colour 69.0 GB, velodyne 84.8 GB, poses 1.3 MB, calib 0.6 MB (HEAD Content-Length, 2026-11-06). Raw drive 2011_09_26_drive_0001: sync 459 MB, extract 697 MB; 2011_09_30_drive_0028 sync 21.2 GB (HEAD). KITTI-360 total: not verified (download needs login) |
| License | CC BY-NC-SA 3.0 (stated on cvlibs.net). KITTI-360 also requires registration with intended purpose (GDPR) |
| Format | png images, float32 .bin point clouds, text OXTS / poses (3x4 row-major per line) |
| Index | [KITTI odometry](../../catalog/resources/kitti-odometry-benchmark.md), [KITTI-360](../../catalog/resources/kitti-360-dataset.md), [pykitti](../../catalog/repos/utiasstars__pykitti.md), [evo](../../catalog/repos/michaelgrupp__evo.md) |

## What's in it

- Odometry benchmark: 22 stereo sequences, 00-10 with GT poses (training), 11-21 without
  (scored by the server). Metric: translational % and rotational deg/m over 100-800 m segments.
- Raw data: the drives behind the odometry and object benchmarks, sorted by category (city,
  residential, road, campus, person), synced+rectified and unsynced+unrectified versions.
- KITTI-360: 73.7 km of driving, about 320k images and 100k laser scans, OXTS poses, dense
  2D/3D semantic and instance labels (stated on the KITTI-360 page).

## Download

```bash
B=https://s3.eu-central-1.amazonaws.com/avg-kitti
# smallest useful: GT poses + calib + one raw drive with OXTS (about 1.2 GB)
wget $B/data_odometry_poses.zip $B/data_odometry_calib.zip
wget $B/raw_data/2011_09_26_calib.zip
wget $B/raw_data/2011_09_26_drive_0001/2011_09_26_drive_0001_sync.zip
wget $B/raw_data/2011_09_26_drive_0001/2011_09_26_drive_0001_extract.zip   # high-rate OXTS
# full odometry stereo (grey) for VO
wget $B/data_odometry_gray.zip      # 23.2 GB
# lidar odometry
wget $B/data_odometry_velodyne.zip  # 84.8 GB
```

The S3 URLs answered HEAD without auth on 2026-11-06. KITTI-360 downloads go through
`user_login.php` on cvlibs.net, then their download scripts.

## Used in this repo

[samples/relative-nav-benchmark](../../samples/relative-nav-benchmark/) part 1 (`./run.sh lidar`, `fetch_data.sh lidar`), run 2026-11-06:

| Odometry seq | Raw drive | Download (HEAD) | Status |
|---|---|---|---|
| 04 | `2011_09_30_drive_0016_sync.zip` | 1.13 GB, + `2011_09_30_calib.zip` 4 KB + `data_odometry_poses.zip` 1.3 MB | ran |
| 07 | `2011_09_30_drive_0027_sync.zip` | 4.42 GB | stopped: about 1 MB/s, 2.5 GB after 40 min; mapping is in place, the path never ran |

- The odometry benchmark's velodyne zip is 84.8 GB, so the sample takes the raw drive behind each odometry sequence instead (04 = 2011_09_30_drive_0016, 07 = 2011_09_30_drive_0027) and the 1.3 MB odometry poses.
- KISS-ICP 1.3.0 default config on 04: 271 scans, 393.6 m, ATE 0.23 m, final drift 0.12 % of distance, KITTI t_rel 0.41 % (04 is too short for 400-800 m segments). 12-20 s compute on an M2 Max.
- Frames: odometry poses are in rectified cam0; KISS-ICP runs in the velodyne frame; conjugate with `T_cam0_velo`. Against OXTS the numbers agree within 2 cm.
- Seq 04 is a short, nearly straight road: an easy lidar case. Treat 0.12 % as a best case.
- Download rate from the S3 bucket was 1-2 MB/s per file; pull 07 or bigger well before the event.

## Loading and tooling

- [pykitti](../../catalog/repos/utiasstars__pykitti.md): `pykitti.raw(basedir, '2011_09_26', '0001')`
  gives `.oxts` (packet + T_w_imu), `.get_cam0(i)`, `.get_velo(i)`; `pykitti.odometry(basedir, '00')`
  gives `.poses`.
- [evo](../../catalog/repos/michaelgrupp__evo.md): `evo_ape kitti 00.txt est_00.txt -va --plot`.
- Lidar odometry: [KISS-ICP](../../catalog/repos/prbonn__kiss-icp.md) runs directly on the
  velodyne folder.
- IMU dead reckoning on KITTI raw: [AI-IMU](../../catalog/repos/mbrossar__ai-imu-dr.md).

## Hackathon fit

- Idea 5 (INS holdover budget): take OXTS from a raw "extract" drive, cut GNSS for 30-120 s
  and integrate the IMU, plot drift vs time.
- Idea 10 (VO => GPS-free flight) as a ground-vehicle stand-in: stereo VO on sequence 00/05 scored with evo.
- Idea 18 (geolocalization fused with VO): KITTI-360 poses are geolocated, so tiles from a
  satellite basemap can be matched against them.

## Pitfalls

- Odometry GT poses are in the left camera frame of the first frame, not ENU; use calib to
  go to OXTS / world.
- Synced OXTS is 10 Hz; for real IMU integration use the "extract" archive and its
  timestamps; check them for gaps and non-monotonic steps before integrating.
- Short-segment GT is noisy (the benchmark itself says so); do not quote cm-level drift on
  < 100 m windows.
- Non-commercial license; fine for a hackathon demo, not for a product.

## Sources

- https://www.cvlibs.net/datasets/kitti/eval_odometry.php (sequence split, metric, sizes as "22/65/80 GB")
- https://www.cvlibs.net/datasets/kitti/raw_data.php (10 Hz, sensor list)
- https://www.cvlibs.net/datasets/kitti-360/ (73.7 km, frames, license, registration)
- HEAD requests on the avg-kitti S3 bucket listed above (2026-11-06)
- samples/relative-nav-benchmark/README.md and `fetch_data.sh` (seq 04 / 07 mapping, sizes, run facts)
