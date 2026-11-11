# cuVSLAM

`repo:nvidia-isaac/cuvslam` - <https://github.com/nvidia-isaac/cuVSLAM>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 1,900 | C++ | NOASSERTION | 2026-11-07 | False | production | high |

NVIDIA's CUDA-accelerated visual odometry and SLAM library supporting mono to multi-camera rigs with optional IMU, with Python bindings.

**Why it matters:** The engine behind Isaac ROS Visual SLAM, now usable directly from Python.

**Build notes:** Download the prebuilt wheel (cuvslam-cu12 or -cu13) from the GitHub releases page, not PyPI; wheels cover x86_64, Jetson Orin (JetPack 6) and Jetson Thor with Python 3.10+, other combos need a source build. Needs CUDA Toolkit libraries; examples include EuRoC and KITTI.

## Deep dives

- [_index-perception-altnav](../../docs/integration-cards/_index-perception-altnav.md) (integration-cards)
- [nvidia-isaac-ros__isaac_ros_visual_slam](../../docs/integration-cards/nvidia-isaac-ros__isaac_ros_visual_slam.md) (integration-cards)
- [nvidia-isaac__cuvslam](../../docs/integration-cards/nvidia-isaac__cuvslam.md) (integration-cards)
- [cuvslam-2025](../../docs/paper-digests/cuvslam-2025.md) (paper-digests)

**Concepts:** [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Visual SLAM](../../catalog/concepts/visual-slam.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md)

**Tags:** `cuda`, `jetson`, `visual-odometry`, `python`

**Domains:** air, ground

## Related

- integrates_with: [Isaac ROS Visual SLAM](../../catalog/repos/nvidia-isaac-ros__isaac_ros_visual_slam.md)
- integrates_with: [cuVSLAM: CUDA accelerated visual odometry and mapping](../../catalog/resources/cuvslam-2025.md)

## Referenced by

- [Competition playbook: navigation and PNT under GNSS denial](../../docs/competition-playbook.md) (mentions)
- [First-day intake: close-area A=>B, answers => stack](../../docs/first-day-intake.md) (mentions)
- [Integration cards](../../docs/integration-cards/README.md) (mentions)
- [Model weights licenses: code vs weights vs training data](../../docs/model-weights-licenses.md) (mentions)
- [Paper digests](../../docs/paper-digests/README.md) (mentions)
- [Brief decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [Isaac ROS Visual SLAM](../../catalog/repos/nvidia-isaac-ros__isaac_ros_visual_slam.md) (depends_on)
- [cuVSLAM: CUDA accelerated visual odometry and mapping](../../catalog/resources/cuvslam-2025.md) (has_code)
- [Shield AI Hivemind autonomy stack](../../catalog/resources/shield-ai-hivemind.md) (alternative_to)
- [Spleenlab VISIONAIRY perception and GNSS-free navigation software](../../catalog/resources/spleenlab-visionairy.md) (alternative_to)
- [Relative navigation benchmark on real data: KISS-ICP lidar odometry, OpenVINS VIO, mono and nadir VO, scored with evo](../../catalog/samples/relative-nav-benchmark.md) (explains)

_Indexed by lane(s): gap-fill_

_GitHub metadata fetched 2026-11-09._
