# ORB-SLAM3

`repo:uz-slamlab/orb_slam3` - <https://github.com/UZ-SLAMLab/ORB_SLAM3>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 9,223 | C++ | GPL-3.0 | 2024-07-24 | False | research-prototype | high |

Visual, visual-inertial and multi-map SLAM supporting monocular, stereo and RGB-D cameras with pinhole and fisheye models, using a map atlas to survive tracking loss.

**Why it matters:** Still the most cited open VI-SLAM system; a solid GNSS-denied drift baseline for drones and ground robots.

**Hackathon notes:** Build against Pangolin, OpenCV and Eigen; expect a few compile fixes. Run on EuRoC or TUM-VI first, then your own camera after Kalibr calibration. Upstream sees little activity.

## Deep dives

- [_index-perception-altnav](../../docs/integration-cards/_index-perception-altnav.md) (integration-cards)
- [uz-slamlab__orb_slam3](../../docs/integration-cards/uz-slamlab__orb_slam3.md) (integration-cards)
- [orb-slam3-campos-2020](../../docs/paper-digests/orb-slam3-campos-2020.md) (paper-digests)

**Concepts:** [Visual SLAM](../../catalog/concepts/visual-slam.md), [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Place recognition and loop closure](../../catalog/concepts/place-recognition.md)

**Tags:** `orb`, `imu`, `multi-map`, `fisheye`, `c++`

**Domains:** air, ground, dismounted

## Related

- extends: [ORB-SLAM2](../../catalog/repos/raulmur__orb_slam2.md)
- integrates_with: [ORB_SLAM3_ROS2](../../catalog/repos/zang09__orb_slam3_ros2.md)
- integrates_with: [Kalibr](../../catalog/repos/ethz-asl__kalibr.md)
- evaluated_on: [evo](../../catalog/repos/michaelgrupp__evo.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [4. Vision, LiDAR and radar odometry](../../docs/primer/04-vision-lidar-radar-odometry.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [Kalibr](../../catalog/repos/ethz-asl__kalibr.md) (integrates_with)
- [Photo-SLAM](../../catalog/repos/huajianup__photo-slam.md) (depends_on)
- [ORB-SLAM2](../../catalog/repos/raulmur__orb_slam2.md) (alternative_to)
- [AirSLAM](../../catalog/repos/sair-lab__airslam.md) (alternative_to)
- [ORB_SLAM3_system_local](../../catalog/repos/sasha-lobov__orb_slam3_system_local.md) (depends_on)
- [ORB_SLAM3_ROS2](../../catalog/repos/zang09__orb_slam3_ros2.md) (integrates_with)
- [ORB-SLAM3: An Accurate Open-Source Library for Visual, Visual-Inertial and Multi-Map SLAM](../../catalog/resources/orb-slam3-campos-2020.md) (has_code)
- [Relative navigation benchmark on real data: KISS-ICP lidar odometry, OpenVINS VIO, mono and nadir VO, scored with evo](../../catalog/samples/relative-nav-benchmark.md) (explains)

_Indexed by lane(s): slam_

_GitHub metadata fetched 2026-11-06._
