# Flight-Ready LiDAR-Inertial Odometry for Embedded Drone Platforms

`res:gaona-2026-flight-ready-lio` - paper - <https://arxiv.org/abs/2607.22145>

**By:** Alvaro J. Gaona, David Perez-Saura, Francisco J. Anguita, Pascual Campoy - **Year:** 2026 - **Level:** intermediate - **Access:** open

Preprint (Jul 2026). Keeps the FAST-LIO2-style IESKF but fixes five integration problems for flight: output tied to the 10 Hz LiDAR rate, no velocity output, IMU blocking, mutex contention and sync races. Result is 200 Hz IMU-rate odometry with body velocity, kept alive through short LiDAR dropouts, on a Mid-360 + Pixhawk 4 Mini drone with mocap ground truth.

## Key takeaways

- Stock LIO packages are not flight-ready out of the box: rate and velocity matter for the autopilot
- IMU-rate propagation bridges LiDAR gaps

**Concepts:** [LiDAR odometry and SLAM](../../catalog/concepts/lidar-slam.md), [Autopilots and flight control](../../catalog/concepts/autopilot.md)

**Tags:** `fast-lio2`, `livox-mid360`, `px4`, `integration`, `preprint`

## Related

- extends: [FAST-LIO / FAST-LIO2](../../catalog/repos/hku-mars__fast_lio.md)
- cites: [FAST-LIO2: Fast Direct LiDAR-inertial Odometry](../../catalog/resources/fast-lio2-xu-2021.md)

_Indexed by lane(s): close-area-localization_
