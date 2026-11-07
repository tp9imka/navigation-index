# Rosbags - ROS recordings without a ROS install
<!-- about: repo:ternaris/rosbags -->

| Item | Practical choice |
|---|---|
| Install | `python3 -m venv .venv`, then `.venv/bin/pip install rosbags`; pin the resolved version before caching |
| Inputs | ROS 1 bags or ROS 2 bag directories and their message definitions |
| Outputs | Deserialized messages; ROS 1/ROS 2 conversion with `rosbags-convert` |
| Key API | `rosbags.highlevel.AnyReader`, `reader.connections`, `reader.messages()`, `reader.deserialize()` |
| Verified | Primary docs and LICENSE.txt read 2026-11-07; library execution not verified here |
| License | Apache-2.0 in [LICENSE.txt](https://github.com/ternaris/rosbags/blob/master/LICENSE.txt); GitHub API reports NOASSERTION |

Start with the [official AnyReader example](https://ternaris.gitlab.io/rosbags/index.html).
Filter to the needed IMU/pose topics before deserializing. Bags without embedded definitions
need a matching typestore; custom messages may need explicit registration. ROS distributions
can carry different message definitions, so select the one that produced the recording.

For the [shared replay contract](../../samples/recording-replay/README.md), retain log time,
message time and frame id as separate fields until their relationship is established. Convert
to metre-valued local ENU explicitly. Conversion between bag containers does not perform that
transform or create independent ground truth.

Canonical development: [GitLab](https://gitlab.com/ternaris/rosbags).
[GitHub mirror](https://github.com/ternaris/rosbags).
