# UZH-FPV Drone Racing

<!-- about: res:uzh-fpv-drone-racing-dataset, repo:uzh-rpg/uzh_fpv_open -->

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

## Loading and tooling

- Any ROS1 VIO that reads camera + IMU topics: [OpenVINS](../../catalog/repos/rpng__open_vins.md), [VINS-Fusion](../../catalog/repos/hkust-aerial-robotics__vins-fusion.md). Whether a ready UZH-FPV config ships in each repo was not checked; calibration YAMLs come from the download page.
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
