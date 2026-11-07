# Rosbags

`repo:ternaris/rosbags` - <https://github.com/ternaris/rosbags>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 12 | Python | NOASSERTION | 2026-10-20 | False | production | high |

Pure Python ROS 1 and ROS 2 bag readers, writers, converters and type system. The official source is on GitLab; this GitHub repository is its official mirror. It can operate without a ROS installation.

**Why it matters:** Extract organiser-provided IMU and pose recordings into a small evaluation pipeline without first setting up ROS.

**Hackathon notes:** Use AnyReader to deserialize known pose/IMU topics, retaining message time, log time and frame ids. Missing custom message definitions need the right typestore; a bag conversion does not transform coordinate frames. Docs and Apache-2.0 LICENSE.txt checked 2026-11-07; not run in this hub. GitHub's NOASSERTION metadata is not a substitute for reading the license.

## Deep dives

- [ternaris__rosbags](../../docs/integration-cards/ternaris__rosbags.md) (integration-cards)

**Concepts:** [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `rosbag`, `rosbags`, `ros1`, `ros2`, `conversion`, `recording`, `replay`

**Domains:** multi

## Related

- integrates_with: [MCAP](../../catalog/repos/foxglove__mcap.md)
- integrates_with: [evo](../../catalog/repos/michaelgrupp__evo.md)

## Referenced by

- [MCAP](../../catalog/repos/foxglove__mcap.md) (integrates_with)
- [Rosbags documentation: read and convert ROS bags without ROS](../../catalog/resources/rosbags-documentation.md) (explains)
- [Shared pose recording and replay: JSONL plus optional MCAP](../../catalog/samples/recording-replay.md) (explains)

_Indexed by lane(s): recording-debugging_

_GitHub metadata fetched 2026-11-07._
