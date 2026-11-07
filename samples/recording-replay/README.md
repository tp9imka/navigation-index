# Recording and replay: one pose stream in JSONL and MCAP

<!-- about: repo:foxglove/mcap, repo:ternaris/rosbags, repo:rerun-io/rerun, concept:datasets-benchmarks, concept:geodesy -->

A small shared recording contract for adapters and visual debugging: integer nanoseconds,
metres, an explicit local ENU frame, estimated position and separate synthetic truth. The
same 101 epochs go through JSONL replay and, optionally, MCAP with an embedded JSON Schema.
It rejects nonfinite values, ambiguous frames and repeated/backwards timestamps.

## Run

From this sample folder, the main path needs only Python 3.10+:

```sh
python3 recording.py
python3 recording.py --input out/poses.jsonl
python3 -m unittest discover -q
```

Optional MCAP container round trip, in an isolated environment:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python recording.py --mcap
.venv/bin/python recording.py --input out/poses.mcap
.venv/bin/python -m unittest discover -q
```

Both formats produce `out/summary.json`. Expected values: 101 epochs, 10 seconds, 0.5 m
position RMSE, `alignment: none`, `input: synthetic`. The offset is deliberately 0.3 m east
and 0.4 m north. This verifies preservation and evaluation, not localization accuracy.

## Verification

Ran 2026-11-07 on macOS arm64, Python 3.14.7 (stdlib) and Python 3.12.14 with mcap 1.3.1.
Both paths produced the expected metrics. Three tests pass with MCAP installed; one optional
test skips in the stdlib environment. The MCAP path also ran under macOS `sandbox-exec` with
`(deny network*)`, so this one-host replay did not require a network connection.
[Verification receipt](results/verification.json). This does not certify another laptop or
a cold offline install; cache the optional wheels before the event.

## Integrate

- Replace `demo_records()` with an adapter that emits the same fields. Never substitute a
  vehicle's reported position for independent truth when measuring accuracy.
- MCAP's topic is `/navigation/pose`, message encoding `json`, schema name `NavigationPose`.
  The embedded schema describes the payload; log and publish times equal `t_ns` in this demo.
  Arbitrary JSON poses do not become ROS messages merely by saving them in MCAP.
- [Rosbags](../../docs/integration-cards/ternaris__rosbags.md) can extract ROS pose messages
  without installing ROS. Convert units, timestamps and frames explicitly before replay.
- [Rerun](../../docs/integration-cards/rerun-io__rerun.md) can display the resulting positions
  on a timeline. Its viewer and Rosbags were read from primary sources, not executed here.
- Keep sensor time, receipt time, coordinate transforms and estimator output separate in a
  real recording. This synthetic example has one clock and one frame only.

Sources: [MCAP guides](https://mcap.dev/guides), [Python API](https://mcap.dev/docs/python/),
[Rosbags docs](https://ternaris.gitlab.io/rosbags/), [Rerun docs](https://rerun.io/docs/overview/what-is-rerun).
