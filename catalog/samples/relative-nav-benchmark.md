# Sample: Relative navigation benchmark on real data: KISS-ICP lidar odometry, OpenVINS VIO, mono and nadir VO, scored with evo

`sample:relative-nav-benchmark` - code and walkthrough in [samples/relative-nav-benchmark](../../samples/relative-nav-benchmark/)

One command per part. KISS-ICP (pip) on KITTI odometry 04 from the raw drive, scored against KITTI odometry GT and OXTS; OpenVINS v2.7 stereo-inertial (ROS 1 serial mode, Docker, arm64) and an OpenCV mono VO baseline on UZH-FPV indoor_forward_3; frame-to-frame nadir VO over 9 km of VPAIR light-aircraft imagery at about 320 m AGL, image-only versus attitude-aided with a yaw-bias sensitivity. Every trajectory is written as TUM and navdash/1 JSONL for templates/demo-dashboard, and the fitted scale / heading / noise of each odometry is plugged into the altpnt-integrity sample as its relative source.

**Verification:** Ran on 2026-11-06, Apple M2 Max, python3.12 venv (kiss-icp 1.3.0, evo 1.38.1, opencv 5.0.0.93, rosbags 0.11.9) and OpenVINS v2.7 built from source in a ros:noetic-perception arm64 image under colima (4 vCPU). KITTI 04: KISS-ICP ATE 0.23 m, KITTI t_rel 0.41 %, final drift 0.12 % of 394 m. UZH-FPV indoor_forward_3 (49.5 s GT window, 278 m): OpenVINS ATE 0.36 m, final drift 0.26 %; mono VO with a GT scale oracle ATE 0.80 m. VPAIR (199 frames, 8.98 km): image-only nadir VO 15.5 % final drift, attitude-aided 0.65 %, 3.2 % with a 2 deg yaw bias. altpnt-integrity rerun with each fitted error model. 5 unit tests pass. EuRoC, ORB-SLAM3, cuVSLAM and KITTI 07 were not run (see README).

## Practical readiness

| Compute | Hardware | Offline | Setup | Dataset download | Tested platforms | Validation |
|---|---|---|---|---|---|---|
| unknown | unknown | unknown | unknown | unknown | unknown | unverified |

**Main limitation:** Read the sample verification; readiness has not been curated.

## Deep dives

- [kitti](../../docs/dataset-cards/kitti.md) (dataset-cards)
- [uzh-fpv](../../docs/dataset-cards/uzh-fpv.md) (dataset-cards)
- [vpair](../../docs/dataset-cards/vpair.md) (dataset-cards)

**Concepts:** [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [LiDAR odometry and SLAM](../../catalog/concepts/lidar-slam.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md)

**Tags:** `odometry`, `drift`, `ate`, `rpe`, `evo`, `kiss-icp`, `openvins`, `msckf`, `mono-vo`, `nadir-vo`, `kitti`, `uzh-fpv`, `vpair`, `docker`, `navdash`, `integrity`

## Related

- uses: [KISS-ICP](../../catalog/repos/prbonn__kiss-icp.md)
- uses: [OpenVINS](../../catalog/repos/rpng__open_vins.md)
- uses: [evo](../../catalog/repos/michaelgrupp__evo.md)
- uses: [KITTI Visual Odometry / SLAM Evaluation](../../catalog/resources/kitti-odometry-benchmark.md)
- uses: [The UZH-FPV Drone Racing Dataset](../../catalog/resources/uzh-fpv-drone-racing-dataset.md)
- uses: [VPAIR](../../catalog/repos/aervisloc__vpair.md)
- explains: [ORB-SLAM3](../../catalog/repos/uz-slamlab__orb_slam3.md)
- explains: [cuVSLAM](../../catalog/repos/nvidia-isaac__cuvslam.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Integrity monitoring for navigation and alt-PNT](../../docs/integrity-monitoring.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [Three selective offline starter bundles](../../docs/starter-bundles.md) (mentions)
- [Upstream findings](../../docs/upstream-findings.md) (mentions)
- [Integrity monitoring for alt-PNT: solution-separation FDE, protection levels and a Stanford diagram](../../catalog/samples/altpnt-integrity.md) (uses)
- [End-to-end GNSS-denied visual navigation on one real flight: nadir VO + DINOv2 retrieval + LightGlue fixes + multi-frame voting + altpnt integrity (VPAIR)](../../catalog/samples/e2e-visual-nav-vpair.md) (uses)

_Indexed by lane(s): samples_
