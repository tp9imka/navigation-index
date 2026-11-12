# Choose a stack you can run

Start with the [problem decoder](problem-statement-decoder.md), then narrow the candidates
by the resources in the room. The browser at `/site/`, CLI and MCP use the same readiness
fields. The [three starter bundles](starter-bundles.md) cover receiver replay, vehicle
simulation and visual localization; rehearse one before the event.

## Search by constraints

From the repo root:

```sh
python3 tools/query.py search "" --kind sample --compute cpu --hardware none --max-download-mb 100
python3 tools/query.py search "recording replay" --offline verified --platform macos-arm64
python3 tools/query.py concept concept:datasets-benchmarks --compute cpu --validation integrated
```

In MCP `search`, use the same names with underscores: `max_download_mb`,
`max_setup_minutes`; `query: ""` lists candidates matching only the filters. `concept`
and `neighbors` accept the same constraints. The browser's copy buttons preserve them.

Unknown values do not pass a numeric budget or a verified-offline filter. A tested platform
is a host OS/architecture label (for Docker samples it is the tested container platform).
Dataset download MB excludes wheels, images and weights. Setup time is a measured value
only where recorded; do not substitute execution time, a guess, or a zero for an unknown
cold setup. Current shortlist setup times remain unknown.

## What the badges mean

- `compute`: CPU, GPU, optional GPU, or unknown. Optional GPU means the code has a CPU
  path; it does not promise that path meets the demonstrated timing.
- `hardware`: none, optional or required for the documented first command. A replay can
  need no receiver even when collecting equivalent live data would need one.
- `offline`: verified means the cited command ran with networking disabled; cache-required
  means prepare data/dependencies/weights first, and still rehearse. Unknown means no such
  conclusion was established. Read the evidence and the one-host/second-laptop caveat.
- `validation`: integrated means the cited pipeline was executed together; components means
  only individual pieces were checked; unverified means no integration evidence is recorded.
  This is independent of a sample's `ran` status and never means field-qualified.

## Shortlist and its strongest limitations

This table is generated from `data/readiness.json` by `tools/build.py`. Update the source,
including the evidence paths, rather than copying status claims into another hand-kept list.

<!-- BEGIN GENERATED readiness -->

| Sample | Compute | Offline | Dataset MB | Integration | Main limitation |
|---|---|---|---|---|---|
| [Close-area arena: seeded 2.5D A=>B simulator, published drone interface, truth scorer](../catalog/samples/close-area-arena.md) | cpu | verified | 0 | integrated | Synthetic 2.5D point-mass arena on one M3 Max; setup needs network for PyPI wheels (16.5 s cold, interpreter already present); offline checked for the first command only; no SITL, no real drone, Linux not tested. |
| [Close-area benchmark matrix: 21 planners x 8 arena families x 2 range-sensor presets, with replays in the world JSON format](../catalog/samples/close-area-benchmark.md) | cpu | unknown | 0 | integrated | Synthetic 2.5D arena, true pose, exact prior map for the prior-map rows; 20 layouts per cell, seed 0 only. The full matrix wants many cores (timed with 14 worker processes). Setup needs network for PyPI wheels (uv venv + uv pip install, osqp included); cold setup time not measured; no network-denied run, so offline is unknown. README names an Apple M3 Max host (macOS arm64); Linux not tested. |
| [Close-area search for B: frontier, nominal-first, lawnmower and random-walk arms when B is a region or unknown, then A* to the detected B](../catalog/samples/close-area-explore.md) | cpu | unknown | 0 | integrated | Synthetic 2.5D point-mass arena, geometric 2 m omnidirectional detection without false positives, true pose, seed 0 only (partly a tuning seed); offline run not checked; Pyodide not tried; Linux not tested. |
| [Close-area corridor MPC: linear MPC with OSQP in an ESDF half-plane corridor on the arena A*, vs the carrot follower](../catalog/samples/close-area-planner-mpc.md) | cpu | unknown | 0 | integrated | Synthetic 2.5D point-mass arena, known map, truth pose; QP timing is a laptop in Python, not a flight computer. Setup needs network for PyPI wheels (uv venv + uv pip install); cold setup time not measured; no network-denied run, so offline is unknown. README names an Apple M3 Max host (macOS 26.6.2); Linux not tested. |
| [Close-area MPPI: sampling-based MPC (Model Predictive Path Integral) from range returns, alone and on an unknown-map A* path, vs A* on 8 arena families](../catalog/samples/close-area-planner-mppi.md) | cpu | unknown | 0 | integrated | Synthetic 2.5D point-mass arena with true pose on one M3 Max; collides often with a 4-beam sensor; not run in Pyodide; setup needs PyPI wheels and its cold time was not measured. |
| [Close-area reactive planners: APF with wall-follow escape and VFH+, range sensor only, 72-beam vs Crazyflie-like 4-beam fan](../catalog/samples/close-area-planner-reactive.md) | cpu | unknown | 0 | integrated | Synthetic 2.5D arena; 4-beam fan is ideal rays with no beam cone; no Crazyflie or SITL. Setup needs network for PyPI wheels (uv venv + uv pip install); cold setup time not measured; no network-denied run, so offline is unknown. README names an Apple M3 Max host; macOS assumed from the M3 Max host, Linux not tested. |
| [Close-area sampling planners: RRT* and Informed RRT* against A* on narrow gaps 0.4-1.2 m, in the close-area arena](../catalog/samples/close-area-planner-sampling.md) | cpu | unknown | 0 | integrated | Synthetic 2.5D arena, known static map; RRT* not tuned; sweep timings under 14-process load. Setup needs network for PyPI wheels (uv venv + uv pip install); cold setup time not measured; no network-denied run, so offline is unknown. README names an Apple M3 Max host; macOS assumed from the M3 Max host, Linux not tested. |
| [Close-area any-angle planning: Theta* and Lazy Theta* against A* + shortcut on 8 arena families, known and unknown map](../catalog/samples/close-area-planner-thetastar.md) | cpu | unknown | 0 | integrated | Synthetic 2.5D point-mass arena on one shared Apple silicon machine; setup needs PyPI wheels (time not measured); offline not checked; Pyodide not run; Linux not tested. |
| [Close-area relocalization after VIO loss: scan-to-map pose hypotheses, ratio + persistence acceptance, hover until one wins](../catalog/samples/close-area-relocalize.md) | cpu | unknown | 0 | integrated | Synthetic 2.5D arena, exact prior map unless the stale-map ladder is run, perfect hover; yaw is truth except in the yaw-search runs. The headline holds on open layouts only (held-out matrix FAIL on office, warehouse, maze, narrow_gap, glass_office; 4-beam and added-obstacle runs FAIL). Setup needs network for PyPI wheels (uv venv + uv pip install); cold setup time not measured; no network-denied run, so offline is unknown. README names an Apple M3 Max host; macOS assumed from the M3 Max host, Linux not tested. |
| [Close-area safety-filter kill test A: no filter, PX4 Collision Prevention style and PX4-CBF as shipped on A* under VIO faults, with map-only obstacles the range fan cannot see](../catalog/samples/close-area-safety-filter.md) | cpu | unknown | 0 | integrated | Synthetic 2.5D arena, one planner (A* known map); random seeds 0-2 plus u_trap and narrow_gap on seed 1; no PX4 code run (F1 from docs, F2 from doc 05 pseudo-code). Setup needs network for PyPI wheels (uv venv + uv pip install); cold setup time not measured; no network-denied run, so offline is unknown. README names an Apple M3 Max host; macOS assumed from the M3 Max host, Linux not tested. |
| [Dismounted foot-mounted INS: stdlib 15-state ZUPT EKF on the real pyshoe hallway data, cross-checked against pyshoe, with corridor heading, UWB and TAK output](../catalog/samples/dismounted-foot-ins.md) | cpu | cache-required | unknown | integrated | Nominal 95 percent radius covered truth at only 31 percent of markers; UWB aiding is simulated. |
| [End-to-end GNSS-denied visual navigation on one real flight: nadir VO + DINOv2 retrieval + LightGlue fixes + multi-frame voting + altpnt integrity (VPAIR)](../catalog/samples/e2e-visual-nav-vpair.md) | optional-gpu | cache-required | 861.249 | integrated | One flight; map renders share the GNSS/INS reference and the VO error model was fitted on this flight. |
| [AprilTag goal B: detection envelope vs range and view angle, and a tag-relative final approach](../catalog/samples/fiducial-goal-apriltag.md) | cpu | unknown | 0 | integrated | Rendered images and a kinematic point mass; no lens distortion, real camera or SITL. Setup needs network for PyPI wheels (uv venv + uv pip install); cold setup time not measured; no network-denied run, so offline is unknown. README names an Apple M3 Max host; macOS assumed from the M3 Max host, Linux not tested. |
| [License-clean drone frame to orthophoto geolocalization (ALIKED / DISK / SIFT + LightGlue)](../catalog/samples/geoloc-license-clean.md) | cpu | cache-required | unknown | integrated | Only 1 of 5 real eBee frames fixed; synthetic same-map precision does not describe flight performance. |
| [GNSS/INS EKF through a GNSS outage and a spoofing walk-off](../catalog/samples/gnss-ins-ekf-outage.md) | cpu | unknown | 0 | integrated | Fully synthetic two-dimensional sensors; the innovation gate misses slow drags up to 0.5 m/s. |
| [Golden demo: GPS drag (position-only or coherent) on an ArduCopter SITL AUTO mission, integrity monitoring with solution separation + protection level, real visual geolocalization, EKF3 switch to ExternalNav, Monte Carlo, dashboard replay](../catalog/samples/golden-demo.md) | cpu | cache-required | unknown | integrated | Autopilot simulation with recorded/modelled aiding; not field or hardware validation. |
| [Navigation innovation laboratory: active localization, asynchronous fix scheduling and selective model adaptation](../catalog/samples/navigation-innovation-lab.md) | cpu | unknown | 0 | integrated | Primary benchmark uses synthetic descriptor/scalar models; optional replay is one previously studied flight with artificial frame delays, not field validation. |
| [Real attack replay: Jammertest 2024 u-blox logs through the GNSS interference monitor, with RTKLIB SPP](../catalog/samples/real-attack-replay.md) | cpu | cache-required | 63.992 | integrated | One receiver and weak quiet-time labels; dataset redistribution permission is not stated. |
| [Shared pose recording and replay: JSONL plus optional MCAP](../catalog/samples/recording-replay.md) | cpu | verified | 0 | integrated | One macOS laptop, synthetic poses, network-denied replay; cold install and a second laptop were not tested. |
| [UGV GNSS outage on a real log: wheel odometry + IMU, innovation gate, drag detector](../catalog/samples/ugv-gnss-outage-real.md) | cpu | cache-required | 42.3383 | integrated | One low-speed NCLT session; reference SLAM shares wheel odometry, and injected drag is synthetic. |
| [Large-area visual place recognition for lost-GNSS recovery (DINOv2 GeM / VLAD over a 49 km2 NAIP tile DB, chained to LightGlue fine matching)](../catalog/samples/vpr-large-area.md) | optional-gpu | cache-required | unknown | integrated | Retrieval is not a position fix: the fine stage fixed only 1 of 23 real eBee frames. |

<!-- END GENERATED readiness -->

## Rehearse with a teammate

Have someone who did not author the sample start from a fresh clone and choose a bundle
using only the index. Record time to select, missing prerequisites, first successful output
and whether they can explain its main limitation. Move the cache to a second laptop, turn
networking off, and repeat the documented command. Store its exit status, input checksums,
versions and output in the bundle receipt. A missing, failing or online run stays labelled
unverified offline.
