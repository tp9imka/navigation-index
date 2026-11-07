# MCAP

`repo:foxglove/mcap` - <https://github.com/foxglove/mcap>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,136 | Rust | MIT | 2026-11-03 | False | production | high |

Open container format and libraries for timestamped, heterogeneous robotics logs, with embedded schemas and indexed access. Message serialization remains an explicit choice separate from the container.

**Why it matters:** Give camera, IMU, pose and navigation-health adapters one portable recording to replay and inspect offline.

**Hackathon notes:** Start with samples/recording-replay: stdlib JSONL main path and a verified mcap 1.3.1 container round trip. The format preserves timestamps but does not fix clock offsets, frames or false ground truth. Code license MIT, read upstream LICENSE. Avoid installing a full robotics framework just to replay this example.

## Deep dives

- [foxglove__mcap](../../docs/integration-cards/foxglove__mcap.md) (integration-cards)

**Concepts:** [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `logging`, `recording`, `replay`, `mcap`, `schemas`, `ros`, `python`

**Domains:** multi

## Related

- integrates_with: [Rosbags](../../catalog/repos/ternaris__rosbags.md)
- integrates_with: [Rerun](../../catalog/repos/rerun-io__rerun.md)

## Referenced by

- [Rerun](../../catalog/repos/rerun-io__rerun.md) (integrates_with)
- [Rosbags](../../catalog/repos/ternaris__rosbags.md) (integrates_with)
- [MCAP guides and format introduction](../../catalog/resources/mcap-guides.md) (explains)
- [Shared pose recording and replay: JSONL plus optional MCAP](../../catalog/samples/recording-replay.md) (uses)

_Indexed by lane(s): recording-debugging_

_GitHub metadata fetched 2026-11-07._
