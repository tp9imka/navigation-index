# UZH-FPV Drone Racing

<!-- about: res:uzh-fpv-drone-racing-dataset, repo:uzh-rpg/uzh_fpv_open, sample:relative-nav-benchmark, sample:altpnt-integrity -->

Aggressive FPV quadrotor flights flown by an expert pilot, UZH Robotics and Perception Group (Delmerico et al., ICRA 2019), with frame camera, event camera and IMU. The hard end of VIO benchmarks; also the basis of recurring IROS/ICRA VIO competitions.

| Field | Value |
|---|---|
| Platform | FPV racing quadrotor; Dec 2023 "SplitS" track adds peak speeds up to 100 km/h |
| Environment | Indoor hangar and outdoor field; racetrack laps through gates and free-form flights around obstacles |
| Sensors and rates | Qualcomm Snapdragon Flight board (camera + IMU), mDAVIS 346 event camera (events, frames, IMU), FPV pilot camera; SplitS uses a Realsense T265. Rates and resolutions not stated on the site pages read |
| Ground truth | Leica Nova MS60 laser tracker (position of a prism), turned into 6-DoF by an offline vision-based optimization ([rpg_vision-based_slam](https://github.com/uzh-rpg/rpg_vision-based_slam)). Accuracy not stated; [uzh_fpv_open](../../catalog/repos/uzh-rpg__uzh_fpv_open.md) ships tools to assess GT quality against raw Leica |
| Size | Per sequence 0.25-2.8 GB (download page). Verified by HEAD 2026-11-06: indoor_forward_3_snapdragon_with_gt.bag 1.61 GB, same as .zip 0.84 GB, indoor_forward_3_davis_with_gt.bag 0.88 GB. Total not stated; summing the page table gives about 40 GB of Snapdragon bags plus 25 GB of DAVIS bags (my sum, not a stated figure) |
| License | CC BY-NC-SA 3.0 (data); uzh_fpv_open code GPL-3.0 |
| Format | ROS1 bag (images, IMU, events, GT) and zip (per sequence) |
| Index | [UZH-FPV dataset](../../catalog/resources/uzh-fpv-drone-racing-dataset.md), [uzh_fpv_open](../../catalog/repos/uzh-rpg__uzh_fpv_open.md) |

## What's in it

- Indoor forward-facing 3,5,6,7,9,10 (GT public); 8,11,12 (GT withheld for leaderboard).
- Indoor 45-degree down-facing 2,4,9,12,13,14 (GT); 1,3,11,16 (withheld).
- Outdoor forward 1,3,5 (GT); 2,6,9,10 (withheld). Outdoor 45-degree 1 (GT); 2 (withheld).
- SplitS race_1..3 (T265, GT withheld).
- Calibration YAML and raw Kalibr sequences.

## Download

```bash
B=https://download.ifi.uzh.ch/rpg/web/datasets/uzh-fpv-newer-versions/v3
# Smallest useful with GT: indoor_forward_3 Snapdragon zip (0.84 GB)
wget $B/indoor_forward_3_snapdragon_with_gt.zip
# Same sequence as ROS bag (1.6 GB) and the event camera bag (0.88 GB)
wget $B/indoor_forward_3_snapdragon_with_gt.bag
wget $B/indoor_forward_3_davis_with_gt.bag
# Outdoor with GT
wget $B/outdoor_forward_1_snapdragon_with_gt.bag
```

`http://rpg.ifi.uzh.ch/datasets/uzh-fpv-newer-versions/v3/...` (as linked from the page) 301-redirects to the URL above. Sequences without GT drop the `_with_gt` suffix.

## Used in this repo

[samples/relative-nav-benchmark](../../samples/relative-nav-benchmark/) part 2 (`./run.sh vio`, `fetch_data.sh vio`), run 2026-11-06, on `indoor_forward_3_snapdragon_with_gt.bag` (1.61 GB, HEAD):

- Downloaded at 1-2 MB/s from download.ifi.uzh.ch with `curl -C -` resume.
- OpenVINS v2.7 MSCKF, stereo + IMU, config `uzhfpv_indoor`, in a slim ROS Noetic Docker image (build about 20 min, image 1.7 GB arm64). Run 28.7-81.0 s for the 92 s bag. ATE 0.36 m RMSE over 278.3 m; final drift 0.73 m = 0.26 %.
- **GT covers only 49.5 s of the 92 s bag** and has no geodetic frame; OpenVINS needs about 9.5 s to initialise, so metrics use the overlap.
- The measured heading-error growth fed [altpnt-integrity](../../samples/altpnt-integrity/) as its relative-source error model (`results/altpnt_from_vo.json`).
- colima shares only `$HOME` with containers: a bind mount from `/private/tmp` showed up empty and OpenVINS failed with `BagIOException`; `docker cp` the bag in instead.
- The zip (0.84 GB) holds the same sequence; the sample used the bag because OpenVINS reads bags directly.

## Loading and tooling

- Any ROS1 VIO that reads camera + IMU topics: [OpenVINS](../../catalog/repos/rpng__open_vins.md) ships a `uzhfpv_indoor` config (used by the relative-nav-benchmark sample), [VINS-Fusion](../../catalog/repos/hkust-aerial-robotics__vins-fusion.md) not checked; calibration YAMLs come from the download page.
- Without ROS: `rosbags` (Apache-2.0) reads the bag in Python; the sample's `vio/eval_uzhfpv.py` extracts GT and images that way.
- Event data: [rpg_dvs_ros](../../catalog/repos/uzh-rpg__rpg_dvs_ros.md) message types are needed to read DAVIS bags; [DEVO](../../catalog/repos/tum-vision__devo.md) for learned event VO.
- Scoring: [rpg_trajectory_evaluation](../../catalog/repos/uzh-rpg__rpg_trajectory_evaluation.md) (the protocol the competitions use), or [evo](../../catalog/repos/michaelgrupp__evo.md).

## Hackathon fit

- Idea 10 (VIO => PX4 GPS-free flight): stress-test the VIO you chose on EuRoC; shows where it breaks under fast yaw and motion blur.
- Event-camera or high-dynamics demos: the only common dataset with DAVIS events on an aggressive multirotor.
- Interceptor-style fast flight state estimation (navigation only).

## Pitfalls

- Half the sequences have withheld GT; pick `_with_gt` files for offline scoring.
- Ground truth is reconstructed from a laser tracker plus vision, not mocap; the repo explicitly provides tools to check its quality, so treat it as good but not millimetre.
- Expect many VIO pipelines to diverge; tune IMU noise and feature tracking before concluding a method fails.
- Non-commercial license.

## Sources

- https://fpv.ifi.uzh.ch/ (platform, sensors, GT device, license)
- https://fpv.ifi.uzh.ch/datasets/ (sequence table, sizes, GT availability, URL pattern)
- `gh api repos/uzh-rpg/uzh_fpv_open/readme` (GT quality tools, GPL-3.0)
- HEAD on the three files above, 2026-11-06
- samples/relative-nav-benchmark/README.md and `fetch_data.sh` (measured run facts)
