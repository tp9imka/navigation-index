# NTU VIRAL

<!-- about: repo:ntu-aris/ntu_viral_dataset -->

Visual-Inertial-Ranging-Lidar dataset from a research UAV at Nanyang Technological University (Nguyen et al., IJRR 2022). Its distinctive piece is UWB: four nodes on the drone ranging to three anchors, next to two lidars, stereo cameras and IMUs, with laser-tracker ground truth.

| Field | Value |
|---|---|
| Platform | Research multirotor UAV (NTU ARIS) |
| Environment | NTU campus: carparks (eee, rtp), building front squares and facades (sbs, spms), inside an auditorium (nya) and inside a building (tnp); indoor and outdoor |
| Sensors and rates | 2 x 3D lidar (Ouster per the README jitter note), 2 hardware-synced global-shutter cameras, multiple IMUs, 4 UWB nodes on the UAV ranging to 3 anchors. Models and rates not stated on the site; see the IJRR paper |
| Ground truth | "High-accuracy laser tracker" (paper abstract), measured at a prism 0.4 m from the IMU. Device model and accuracy not restated on the site |
| Size | 18 sequences, 4.0-9.4 GB each per the README table; HF dataset usedStorage 88.4 GB total (HF API). HEAD on HF eee_03.zip: 1,995,367,404 bytes, while the README table says 4.3 GB, so treat README sizes as upper bounds |
| License | CC BY-NC-SA 4.0 (site and HF card); commercial use by contacting authors |
| Format | ROS1 bags (zipped per sequence); ground truth in-bag and as CSV |
| Index | [NTU VIRAL repo](../../catalog/repos/ntu-aris__ntu_viral_dataset.md) |

## What's in it

- eee_01..03, nya_01..03, sbs_01..03 (original 9, 181-429 s each).
- rtp_01..03, tnp_01..03, spms_01..03 (added Sep 2022, "more challenging"; 355-583 s).
- calib_stereo (49 MB) and calib_stereo_imu bag (0.96 GB) for Kalibr.
- A baseline catalogue on HF: 63 methods with NTU-specific configs (OpenVINS, VINS-Fusion, ORB-SLAM3, FAST-LIO, LIO-SAM, KISS-ICP, GLIM, ...).

## Download

```bash
HF=https://huggingface.co/datasets/Yuan-Shenghai/NTU-VIRAL-DATASET/resolve/main
# Smallest useful: eee_03 (182 s, carpark, ~2.0 GB per HEAD)
wget -O eee_03.zip "$HF/sequences/eee_03.zip?download=true"
# Ground truth CSVs only (browse first)
#   https://huggingface.co/datasets/Yuan-Shenghai/NTU-VIRAL-DATASET/tree/main/ground_truth
# Whole set with the HF CLI (venv): ~88 GB
huggingface-cli download Yuan-Shenghai/NTU-VIRAL-DATASET --repo-type dataset --local-dir ntu_viral
```

Mirrors: NTU Data Repository (DOI 10.21979/N9/X39LEK) and a OneDrive folder linked in the README.

## Loading and tooling

- Lidar/IMU jitter fix: `utils/restamp.py` in the repo (gh-pages branch) regularizes Ouster cloud and IMU stamps.
- Evaluation tutorial (Jupyter + MATLAB) handles the prism offset: https://ntu-aris.github.io/ntu_viral_dataset/evaluation_tutorial.html
- VIO: [OpenVINS](../../catalog/repos/rpng__open_vins.md), [VINS-Fusion](../../catalog/repos/hkust-aerial-robotics__vins-fusion.md); LIO: [FAST-LIO](../../catalog/repos/hku-mars__fast_lio.md), [LIO-SAM](../../catalog/repos/tixiaoshan__lio-sam.md), [KISS-ICP](../../catalog/repos/prbonn__kiss-icp.md), [GLIM](../../catalog/repos/koide3__glim.md). NTU-specific config links are in the HF BASELINES.md.
- Scoring: [evo](../../catalog/repos/michaelgrupp__evo.md) after the prism offset.

## Hackathon fit

- Idea 13 (radio-ranging return-to-home): real UWB ranges from a flying platform to fixed anchors with truth; fuse UWB + IMU and show bounded error vs VIO drift.
- Idea 19 (cooperative localization for a small team): anchors as "team members" with known positions; ranging-only fusion.
- Idea 10: aerial VIO/LIO baseline outdoors with a laser-tracker reference.

## Pitfalls

- Ground truth is at the prism, 0.4 m from the IMU. Ignoring it inflates ATE; the README says many users forget it.
- Ouster cloud and IMU timestamps jitter; run restamp.py first.
- Only 3 anchors: 3D UWB-only position is poorly constrained vertically; fuse with IMU/baro.
- README sizes and actual HF zip sizes differ (eee_03: 4.3 GB stated vs 2.0 GB served).
- Non-commercial license.

## Sources

- `gh api repos/ntu-aris/ntu_viral_dataset/readme` (sequences, sizes, durations, HF links, restamp, prism offset, baseline list)
- https://ntu-aris.github.io/ntu_viral_dataset/ (license)
- https://arxiv.org/abs/2202.00379 (sensor suite, laser tracker GT)
- HF API datasets/Yuan-Shenghai/NTU-VIRAL-DATASET (usedStorage 88,404,490,942, license); HEAD on sequences/eee_03.zip
