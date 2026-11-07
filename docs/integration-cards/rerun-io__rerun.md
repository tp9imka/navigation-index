# Rerun - inspect sensors and navigation on a timeline
<!-- about: repo:rerun-io/rerun -->

| Item | Practical choice |
|---|---|
| Install | Sample-local venv, then `.venv/bin/pip install rerun-sdk`; pin and cache the version tested on the target laptop |
| Inputs | SDK-logged poses, images, points, transforms and scalar signals; supported MCAP messages |
| Outputs | Local viewer and `.rrd` recordings; synchronized plots and spatial views |
| Wiring | Estimated pose, independent reference, frame transforms and monitor state on named timelines |
| Verified | README and license files read 2026-11-07; viewer/SDK not executed here |
| License | Repository offers MIT and Apache-2.0; check [LICENSE-MIT](https://github.com/rerun-io/rerun/blob/main/LICENSE-MIT) and [LICENSE-APACHE](https://github.com/rerun-io/rerun/blob/main/LICENSE-APACHE) |

Start from [the official docs](https://rerun.io/docs/overview/what-is-rerun). For a navigation
demo, place the estimated path beside a reference path and plot health/uncertainty on the
same sensor timeline. The [recording-replay sample](../../samples/recording-replay/README.md)
provides a small explicit pose contract, but does not claim a tested Rerun adapter.

Coordinate frames, timestamp origin and units must be explicit; a visually plausible overlay
is not an accuracy check. Test memory use and graphics support on the actual judging laptop.
MCAP ingestion depends on the message encoding/schema; arbitrary custom JSON may need a
mapping before it becomes a spatial view. Local open-source use and hosted services have
different terms and connectivity requirements.
