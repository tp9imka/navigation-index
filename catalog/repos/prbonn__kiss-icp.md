# KISS-ICP

`repo:prbonn/kiss-icp` - <https://github.com/PRBonn/kiss-icp>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 2,369 | C++ | MIT | 2026-06-09 | False | production | high |

Minimal LiDAR odometry based on point-to-point ICP with adaptive thresholding, working across sensors with few parameters.

**Why it matters:** Works out of the box on almost any LiDAR without IMU; ideal hackathon starting point.

**Hackathon notes:** `pip install kiss-icp` and run on a rosbag or KITTI folder in minutes. Add KISS-SLAM for loop closure.

## Deep dives

- [_index-perception-altnav](../../docs/integration-cards/_index-perception-altnav.md) (integration-cards)
- [prbonn__kiss-icp](../../docs/integration-cards/prbonn__kiss-icp.md) (integration-cards)
- [kiss-icp-vizzo-2022](../../docs/paper-digests/kiss-icp-vizzo-2022.md) (paper-digests)

**Concepts:** [LiDAR odometry and SLAM](../../catalog/concepts/lidar-slam.md)

**Tags:** `icp`, `python`, `ros2`, `pip`

**Domains:** ground, air, maritime

## Related

- extends: [KISS-SLAM](../../catalog/repos/prbonn__kiss-slam.md)
- integrates_with: [MapClosures](../../catalog/repos/prbonn__mapclosures.md)
- evaluated_on: [evo](../../catalog/repos/michaelgrupp__evo.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Learning paths](../../docs/learning-paths.md) (mentions)
- [4. Vision, LiDAR and radar odometry](../../docs/primer/04-vision-lidar-radar-odometry.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [KISS-SLAM](../../catalog/repos/prbonn__kiss-slam.md) (extends)
- [MapClosures](../../catalog/repos/prbonn__mapclosures.md) (integrates_with)
- [RKO-LIO](../../catalog/repos/prbonn__rko_lio.md) (alternative_to)
- [KISS-ICP: In Defense of Point-to-Point ICP -- Simple, Accurate, and Robust Registration If Done the Right Way](../../catalog/resources/kiss-icp-vizzo-2022.md) (has_code)
- [LiDAR Odometry Survey: Recent Advancements and Remaining Challenges](../../catalog/resources/lee-lidar-odometry-survey-2023.md) (cites)
- [Relative navigation benchmark on real data: KISS-ICP lidar odometry, OpenVINS VIO, mono and nadir VO, scored with evo](../../catalog/samples/relative-nav-benchmark.md) (uses)

_Indexed by lane(s): slam_

_GitHub metadata fetched 2026-11-06._
