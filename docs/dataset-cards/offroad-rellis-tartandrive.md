# Off-road: RELLIS-3D and TartanDrive

<!-- about: repo:unmannedlab/rellis-3d, res:rellis3d-paper, repo:castacks/tartan_drive -->

Two off-road ground-vehicle datasets. RELLIS-3D (Texas A&M + US Army CCDC ARL, 2020):
Clearpath Warthog on the RELLIS campus with lidar and camera semantic labels. TartanDrive
(CMU AirLab, ICRA 2022): instrumented ATV driven aggressively off-road, aimed at learning
vehicle dynamics. Neither is a precision-navigation benchmark; both are the go-to real data
for off-road autonomy and traversability.

| Field | RELLIS-3D | TartanDrive |
|---|---|---|
| Platform | Clearpath Warthog UGV | ATV (all-terrain vehicle) |
| Environment | Off-road trails, grass, mud, puddles, concrete at Texas A&M RELLIS campus | Off-road trails, slopes, vegetation |
| Sensors and rates | Ouster OS1-64, Velodyne Ultra Puck 32, Nerian Karmin2 stereo, Basler acA1920-50gc RGB, VectorNav VN-300 dual-antenna GNSS/INS, Warthog IMU + wheel odometry (topic table; rates not listed) | Multisense stereo (RGB 1024x512 at 20 Hz), IMU 200 Hz, state `/odometry/filtered_odom` 50 Hz, commands 100 Hz, shock position / wheel RPM / pedals 50 Hz, local RGB and height maps 501x501 at 20 Hz |
| Ground truth | Per-scan `poses.txt` in the annotated release (source and accuracy not stated; README notes a 2021 "fix wrong poses"). Main GT is semantic labels | No positioning GT; state is the vehicle's own filtered odometry (GPS-based, per the converter's `--zero_pose_init` note). Accuracy not stated |
| Size | README: synced bags 7-14 GB per sequence (5 sequences), full-stack merged 14-28 GB; 60 s samples 2-4.3 GB; Ouster SemanticKITTI 14 GB; full images 11 GB. Not HEAD-verified (Google Drive) | HEAD on all 23 files in `azfiles.txt`, 2026-11-06: 69-127 GB each, total 2063 GB |
| License | CC BY-NC-SA 3.0 (README) | Repo is MIT (GitHub API); a separate data license is not stated in the README |
| Format | ROS1 bags; SemanticKITTI-format `.bin` + `.label`; PLY | tar.gz of ROS1 bags (custom `racepak` msgs); converter to torch trajectories |
| Index | [RELLIS-3D](../../catalog/repos/unmannedlab__rellis-3d.md), [paper](../../catalog/resources/rellis3d-paper.md) | [TartanDrive](../../catalog/repos/castacks__tartan_drive.md) |

## Download

```bash
# RELLIS-3D: Google Drive links in the README; 60 s full-stack sample (4.2 GB):
#   https://drive.google.com/file/d/1qSeOoY6xbQGjcrZycgPM8Ty37eKDjpJL/view
gdown 1qSeOoY6xbQGjcrZycgPM8Ty37eKDjpJL        # in the project venv; not run here
# Baidu mirror (README): https://pan.baidu.com/s/1akqSm7mpIMyUJhn_qwg3-w?pwd=4gk3

# TartanDrive: public S3-compatible endpoint, no auth (HEAD verified)
E=https://airlab-cloud.andrew.cmu.edu:8080/swift/v1/AUTH_ac8533a83cff4d48bc8c608ad222d330
curl -O $E/tartandrive/20210828_heightmaps_1.tar.gz   # smallest, 69.1 GB
# or: python download_files.py --download-dir ./tartandrive   (boto3, unsigned)
```

## Loading and tooling

- RELLIS-3D: SemanticKITTI tools (their `point_labeler` fork), any KITTI `.bin` reader
  (`np.fromfile(f, np.float32).reshape(-1, 4)`); bags via ROS1 or `rosbags`.
- TartanDrive: `rosbag_to_dataset` + `multi_convert_bag.py --config_spec specs/2021_atv_3.yaml`
  produce torch trajectories at `dt: 0.1`; needs `racepak` msgs built in catkin.

## Hackathon fit

- Reference arch 4.1 for ground robots: RELLIS-3D gives GNSS/INS + wheel odometry + lidar on
  a UGV for a "lidar odometry with GNSS outage" demo on rough terrain, using the 4.2 GB sample.
- TartanDrive suits learned dynamics / traversability (IMU + wheel + shock data), not PNT
  scoring; too large to pre-download except one file.

## Pitfalls

- RELLIS-3D Google Drive quota limits (README asks to wait 24 h or email for access).
- RELLIS-3D poses' provenance is not documented in the README; do not treat them as survey truth.
- TartanDrive files are about 90 GB each; one file is a multi-hour download even on good links.
- TartanDrive needs ROS Melodic-era tooling and custom messages.
- Non-commercial license for RELLIS-3D.

## Sources

- https://github.com/unmannedlab/RELLIS-3D README via `gh api`, 2026-11-06
- https://github.com/castacks/tartan_drive README, download_files.py, azfiles.txt via `gh api`; HEAD on all azfiles, 2026-11-06
