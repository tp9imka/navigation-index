# apriltag_ros (ROS 2)

`repo:christianrauch/apriltag_ros` - <https://github.com/christianrauch/apriltag_ros>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| ? | C++ | ? | ? | ? | active-research | high |

ROS 2 node that wraps the AprilTag library, subscribes to a rectified image and camera info, and publishes tag detections and TF transforms.

**Why it matters:** Gets fiducial poses into a ROS 2 graph in one launch file, so a planner can treat 'tag id N in view' as goal B or feed tag-relative pose to the autopilot.

**Hackathon notes:** License MIT (gh api), last push 2026-11. Use this for ROS 2; AprilRobotics/apriltag_ros is the older ROS 1 wrapper (last push 2024-06). Publish the tag TF, then convert to LANDING_TARGET or to a local-frame goal. Frame conventions (camera optical vs body) are the usual time sink.

**Concepts:** [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md), [Feature detection and matching](../../catalog/concepts/feature-matching.md)

**Tags:** `fiducial`, `apriltag`, `ros2`, `mit`

**Domains:** air

## Related

- depends_on: [AprilTag 3](../../catalog/repos/aprilrobotics__apriltag.md)
- integrates_with: [MAVROS](../../catalog/repos/mavlink__mavros.md)

## Referenced by

- [AprilTag 3](../../catalog/repos/aprilrobotics__apriltag.md) (integrates_with)

_Indexed by lane(s): close-area-localization_
