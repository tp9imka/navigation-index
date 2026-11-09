# livox-mid360-slam-evaluation

`repo:harshareddy1611/livox-mid360-slam-evaluation` - <https://github.com/harshareddy1611/livox-mid360-slam-evaluation>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| ? | Python | ? | ? | ? | research-prototype | medium |

Community benchmark of KISS-ICP, DLIO, FAST-LIO2 and GLIM on Livox Mid-360 data (TIERS indoor dataset plus own VICON-tracked UAV flights), run in ROS 2 Humble and scored with evo.

**Why it matters:** One of the few open comparisons of LiDAR-inertial odometry on the sensor small indoor drones actually carry, with the pipeline gotchas (point timestamps, clock offsets) written down.

**Hackathon notes:** License MIT (gh api), last push 2026-09, 12 stars, single author, not peer reviewed. Reported UAV APE RMSE: GLIM (GPU) 0.040 m, DLIO 0.096 m, FAST-LIO2 0.112 m, KISS-ICP 0.123 m; ground truth was the Pixhawk EKF fused with VICON, so it is not raw mocap. Main value: the bag-conversion and timestamp pitfalls.

**Concepts:** [LiDAR odometry and SLAM](../../catalog/concepts/lidar-slam.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md)

**Tags:** `livox-mid360`, `fast-lio2`, `glim`, `dlio`, `kiss-icp`, `benchmark`, `mit`

**Domains:** air

## Related

- evaluated_on: [FAST-LIO / FAST-LIO2](../../catalog/repos/hku-mars__fast_lio.md)
- evaluated_on: [GLIM](../../catalog/repos/koide3__glim.md)
- evaluated_on: [DLIO](../../catalog/repos/vectr-ucla__direct_lidar_inertial_odometry.md)
- evaluated_on: [KISS-ICP](../../catalog/repos/prbonn__kiss-icp.md)
- depends_on: [evo](../../catalog/repos/michaelgrupp__evo.md)

## Referenced by

- [SLAM benchmark on Livox Mid-360: public dataset + our own UAV flight data (KISS-ICP, DLIO, FAST-LIO2, GLIM)](../../catalog/resources/harsha-2026-mid360-slam-benchmark-post.md) (has_code)

_Indexed by lane(s): close-area-localization_
