# KISS-ICP

`repo:prbonn/kiss-icp` - <https://github.com/PRBonn/kiss-icp>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 2,369 | C++ | MIT | 2026-06-09 | False | production | high |

Minimal LiDAR odometry based on point-to-point ICP with adaptive thresholding, working across sensors with few parameters.

**Why it matters:** Works out of the box on almost any LiDAR without IMU; ideal hackathon starting point.

**Hackathon notes:** `pip install kiss-icp` and run on a rosbag or KITTI folder in minutes. Add KISS-SLAM for loop closure.

**Concepts:** [LiDAR odometry and SLAM](../concepts/lidar-slam.md)

**Tags:** `icp`, `python`, `ros2`, `pip`

**Domains:** ground, air, maritime

## Related

- extends: [KISS-SLAM](../repos/prbonn__kiss-slam.md)
- integrates_with: [MapClosures](../repos/prbonn__mapclosures.md)
- evaluated_on: [evo](../repos/michaelgrupp__evo.md)

## Referenced by

- [KISS-SLAM](../repos/prbonn__kiss-slam.md) (extends)
- [MapClosures](../repos/prbonn__mapclosures.md) (integrates_with)
- [RKO-LIO](../repos/prbonn__rko_lio.md) (alternative_to)
- [KISS-ICP: In Defense of Point-to-Point ICP -- Simple, Accurate, and Robust Registration If Done the Right Way](../resources/kiss-icp-vizzo-2022.md) (has_code)
- [LiDAR Odometry Survey: Recent Advancements and Remaining Challenges](../resources/lee-lidar-odometry-survey-2023.md) (cites)

_Indexed by lane(s): slam_

_GitHub metadata fetched 2026-11-06._
