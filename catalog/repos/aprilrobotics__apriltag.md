# AprilTag 3

`repo:aprilrobotics/apriltag` - <https://github.com/AprilRobotics/apriltag>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 2,621 | C | NOASSERTION | 2026-08-07 | False | production | high |

C library for detecting AprilTag fiducial markers and estimating the 6-DoF pose of each tag relative to a calibrated camera. Ships several tag families and Python bindings.

**Why it matters:** The cheapest way to define goal B or anchor a drift-prone estimator in a close area: print tags, place them at A, B or on walls, and get a camera-relative pose with no map.

**Build notes:** License BSD-2-Clause (LICENSE.md read via gh api; GitHub reports NOASSERTION). Last push 2026-08. Builds with CMake in minutes, Python bindings available. Needs camera intrinsics, so calibrate on the actual camera first. Pose ambiguity on small or far tags at near-frontal views is the known gotcha; use tag bundles or larger tags for the goal marker.

**Concepts:** [Feature detection and matching](../../catalog/concepts/feature-matching.md), [Visual SLAM](../../catalog/concepts/visual-slam.md), [Sensor calibration](../../catalog/concepts/calibration.md)

**Tags:** `fiducial`, `apriltag`, `marker`, `pose-estimation`, `c`, `bsd-2-clause`

**Domains:** air

## Related

- integrates_with: [apriltag_ros (ROS 2)](../../catalog/repos/christianrauch__apriltag_ros.md)
- alternative_to: [vision_landing](../../catalog/repos/goodrobots__vision_landing.md)
- alternative_to: [COEX Clover](../../catalog/repos/copterexpress__clover.md)

## Referenced by

- [First-day intake: close-area A=>B, answers => stack](../../docs/first-day-intake.md) (mentions)
- [Brief decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Close-area talk scaffold: A to B through obstacles](../../templates/presenting/close-area-story.md) (mentions)
- [apriltag_ros (ROS 2)](../../catalog/repos/christianrauch__apriltag_ros.md) (depends_on)
- [AprilTag 2: Efficient and robust fiducial detection](../../catalog/resources/wang-olson-2016-apriltag2.md) (has_code)
- [AprilTag goal B: detection envelope vs range and view angle, and a tag-relative final approach](../../catalog/samples/fiducial-goal-apriltag.md) (explains)

_Indexed by lane(s): close-area-localization_

_GitHub metadata fetched 2026-11-16._
