# MCAP - recording and replay card
<!-- about: repo:foxglove/mcap -->

| Item | Practical choice |
|---|---|
| Install | A sample-local venv with `mcap==1.3.1`; the stdlib JSONL path needs no install |
| Inputs | Timestamped serialized bytes, a topic/channel and an explicit payload schema |
| Outputs | Indexed `.mcap` file, preserving nanosecond log/publish times |
| First result | [recording-replay](../../samples/recording-replay/README.md): 101 synthetic poses through JSONL and MCAP |
| Verified | Python 3.12.14, mcap 1.3.1, macOS arm64, 2026-11-07; exact round trip and network-denied replay |
| License | MIT, checked in [upstream LICENSE](https://github.com/foxglove/mcap/blob/main/LICENSE) |

Use `mcap.writer.Writer`, register a schema and channel, then add messages with integer
nanosecond timestamps. `mcap.reader.make_reader(...).iter_messages()` returns the schema,
channel and raw message. The sample uses uncompressed JSON, so the replay itself does not
need a ROS installation or a message decoder plugin.

MCAP does not synchronize sensors or infer coordinate frames. A JSON payload in an MCAP
container is not automatically a ROS message. Preserve source time and receive time when
they differ, and document units and ENU/NED/ECEF conventions alongside the schema.

Sources checked 2026-11-07: [guides](https://mcap.dev/guides),
[Python API](https://mcap.dev/docs/python/), upstream Python `writer.py` / `reader.py`.
