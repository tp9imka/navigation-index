# SLAM benchmark on Livox Mid-360: public dataset + our own UAV flight data (KISS-ICP, DLIO, FAST-LIO2, GLIM)

`res:harsha-2026-mid360-slam-benchmark-post` - blog - <https://discourse.openrobotics.org/t/slam-benchmark-on-livox-mid-360-public-dataset-our-own-uav-flight-data-kiss-icp-dlio-fast-lio2-glim/57912>

**By:** Harsha Reddy - **Year:** 2026 - **Level:** intermediate - **Access:** open

Open Robotics Discourse post (Sep 2026) with seven VICON-arena UAV flights on Jetson Orin NX + Mid-360 + Pixhawk. Average APE RMSE: GLIM (GPU) 0.040 m, DLIO 0.096 m, FAST-LIO2 0.112 m, KISS-ICP 0.123 m. Notes that GLIM's edge likely comes from loop closure in a small revisited arena.

## Key takeaways

- In a small arena, LIO lands around 0.1 m APE
- Loop closure helps most where the drone revisits the same space
- Community result, not peer reviewed

**Concepts:** [LiDAR odometry and SLAM](../../catalog/concepts/lidar-slam.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md)

**Tags:** `livox-mid360`, `uav`, `benchmark`, `community`

## Related

- has_code: [livox-mid360-slam-evaluation](../../catalog/repos/harshareddy1611__livox-mid360-slam-evaluation.md)

_Indexed by lane(s): close-area-localization_
