# Rerun

`repo:rerun-io/rerun` - <https://github.com/rerun-io/rerun>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 11,855 | Rust | Apache-2.0 | 2026-11-21 | False | production | high |

SDKs and viewer for recording and inspecting multimodal robotics data on synchronized timelines, including images, point clouds, transforms, trajectories and scalar signals; supports MCAP ingestion.

**Why it matters:** Inspect the estimator trajectory beside sensor frames and navigation-health signals when a map alone cannot explain a failure.

**Build notes:** Prototype with the Python SDK and local viewer. Define coordinate frames and clock domains before comparing tracks. Cache the viewer/package and test the actual target laptop offline. README and MIT/Apache license files checked 2026-11-07; viewer not run in this hub. Keep hosted-service terms separate from the open-source SDK licenses.

## Deep dives

- [rerun-io__rerun](../../docs/integration-cards/rerun-io__rerun.md) (integration-cards)

**Concepts:** [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md), [Geodesy and coordinate frames](../../catalog/concepts/geodesy.md), [Situational awareness and C2 interop](../../catalog/concepts/situational-awareness.md)

**Tags:** `visualization`, `debugging`, `timeline`, `recording`, `mcap`, `python`, `3d`

**Domains:** multi

## Related

- integrates_with: [MCAP](../../catalog/repos/foxglove__mcap.md)
- integrates_with: [evo](../../catalog/repos/michaelgrupp__evo.md)

## Referenced by

- [Integration cards](../../docs/integration-cards/README.md) (mentions)
- [MCAP](../../catalog/repos/foxglove__mcap.md) (integrates_with)
- [Rerun overview and multimodal robotics data guide](../../catalog/resources/rerun-overview.md) (explains)
- [Shared pose recording and replay: JSONL plus optional MCAP](../../catalog/samples/recording-replay.md) (explains)

_Indexed by lane(s): recording-debugging_

_GitHub metadata fetched 2026-11-23._
