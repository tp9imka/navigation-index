# Sample: Shared pose recording and replay: JSONL plus optional MCAP

`sample:recording-replay` - code and walkthrough in [samples/recording-replay](../../samples/recording-replay/)

A deterministic synthetic local-ENU pose stream replayed through JSONL and optional MCAP with an embedded schema. Checks timestamps, coordinate frame, finite metre values and exact round-trip preservation; reports a known 0.5 m offset as an evaluation plumbing check.

**Verification:** Ran 2026-11-07 on macOS arm64: Python 3.14.7 stdlib JSONL and Python 3.12.14 with mcap 1.3.1. Both replayed 101 synthetic epochs over 10 seconds with 0.5 m RMSE and no alignment. MCAP round trip preserved all values exactly, including nanosecond timestamps. Three tests pass with mcap, two pass and one skips with stdlib. MCAP replay also passed under sandbox-exec deny network. Rosbags and Rerun integrations were not executed; no real sensors or independent field truth.

## Practical readiness

| Compute | Hardware | Offline | Setup | Dataset download | Tested platforms | Validation |
|---|---|---|---|---|---|---|
| cpu | none | verified | unknown | 0 MB | macos-arm64 | integrated |

**Main limitation:** One macOS laptop, synthetic poses, network-denied replay; cold install and a second laptop were not tested.

**Readiness evidence:** [samples/recording-replay/README.md](../../samples/recording-replay/README.md), [samples/recording-replay/sample.json](../../samples/recording-replay/sample.json), [samples/recording-replay/results/verification.json](../../samples/recording-replay/results/verification.json)

**Concepts:** [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md), [Geodesy and coordinate frames](../../catalog/concepts/geodesy.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `recording`, `replay`, `mcap`, `jsonl`, `timestamps`, `enu`, `logging`, `stdlib`

## Related

- uses: [MCAP](../../catalog/repos/foxglove__mcap.md)
- explains: [Rosbags](../../catalog/repos/ternaris__rosbags.md)
- explains: [Rerun](../../catalog/repos/rerun-io__rerun.md)

## Referenced by

- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Choose a stack you can run](../../docs/practical-readiness.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)

_Indexed by lane(s): samples_
