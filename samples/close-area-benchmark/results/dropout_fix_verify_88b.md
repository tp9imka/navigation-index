# Arena dropout fix (option B), verification

Input: synthetic (simulated layouts, vehicle and sensors), seed 0, scored on truth. Run on 2026-11-11,
Python 3.12, numpy 2.4.6, scipy 1.17.1, osqp 1.1.3 (the 2026-11-10 dropout-fix study runs used numpy 2.5.4, scipy 1.18.1),
macOS arm64, 4 worker processes, load average 6.6 at the start. No benchmark table was regenerated.

Shipped state: the code landed with `SKIP_DROPPED_BEAMS = False` in `planners/astar_esdf.py`, so the
published tables (matrix_0, matrix_depth_0, advisor, explore, packs) still described the unfixed map.
The runs below set it to True. Update 2026-11-12: the flag is now True and every unknown-map table was
regenerated (item 88c, [upstream-findings section 22](../../../docs/upstream-findings.md#22-close-area-arena-a-dropped-beam-marks-free-space-behind-walls)).

## What changed

- `../../close-area-arena/sensors.py`: new `RangeScanDrops(RangeScan)` with `dropped: list[bool] | None`.
  `RangeFan.scan` returns it. `distances` are unchanged: a dropped beam still reads `math.inf`.
- `../../close-area-arena/sensors_cone.py`: `ConeRangeFan.scan` returns `RangeScanDrops` with its drop mask.
- `../../close-area-arena/planners/astar_esdf.py`: `LogOddsMap.update` skips beams with `dropped[i]` True
  (no free trace, no hit). A beam with no return and no flag is still traced free to `max_range`.
  Named constants: `SKIP_DROPPED_BEAMS = True` (False = shipped behaviour before this fix),
  `NO_RETURN_FREE_TO_MAX_RANGE = True` (False = option A of the dropout-fix study), `NO_TRACE_REACH = -1.0`.
  A `dropped` list whose length differs from `distances` raises `ValueError` instead of misaligning.
  A scan without the field (real drivers, or a scan rebuilt as a plain `RangeScan`) keeps the old behaviour.

The brief described the earlier patch as "NaN for a dropped beam". The patch on file does not do that: it
keeps `inf` and adds a flag. Kept as is, because one consumer breaks on NaN (`apf.py`, see below) and the
flag leaves every published reading bit-identical.

## 1. Sensor stream: identical readings, no NaN, flag = dropout_fix.py mask

Per preset: 8 families x 60 random poses = 480 scans. HEAD sensor (`git show HEAD:...`), patched sensor and
`dropout_fix.DropFlagSensor` around a patched sensor, all with the same rng seed.

| preset | beams | inf | dropped | NaN | readings differ from HEAD | rng state differs | flagged but finite | flag differs from DropFlagSensor replay |
|---|---|---|---|---|---|---|---|---|
| ideal | 34560 | 11455 | 688 | 0 | 0/480 | 0/480 | 0 | 0/480 |
| crazyflie | 1920 | 883 | 110 | 0 | 0/480 | 0/480 | 0 | 0/480 |
| crazyflie_bright | 1920 | 1540 | 203 | 0 | 0/480 | 0/480 | 0 | 0/480 |
| dense | 34560 | 12793 | 691 | 0 | 0/480 | 0/480 | 0 | 0/480 |
| depth_cam_87 | 14400 | 5516 | 758 | 0 | 0/480 | 0/480 | 0 | 0/480 |
| lidar_2d | 172800 | 21914 | 3301 | 0 | 0/480 | 0/480 | 0 | 0/480 |
| ideal_nodrop | 34560 | 10980 | 0 | 0 | 0/480 | 0/480 | 0 | 0/480 |

Wall 4.5 s.

## 2. Option B reproduction: patched arena vs dropout_fix.py `status` arm

108 runs: 6 planners x 3 presets x 6 layouts. Per cell, 3 layouts where the `status` row differs from the
unpatched row (dropout-fix study `before` arm where it exists, else matrix_0.json) and 3 where it does not, drawn
with `np.random.default_rng(88)`. Compared fields: outcome, min_clearance_m, path_length_m, time_to_goal_s
(exact equality).

**Result: identical in 108/108 runs.** The sample is discriminating: 54/108 runs differ from the
unpatched row, 7 of them in outcome.

| planner | preset | runs | identical | reached (status => patched) | collision (status => patched) |
|---|---|---|---|---|---|
| astar_unknown | ideal | 6 | 6 | 5 => 5 | 0 => 0 |
| astar_unknown | crazyflie | 6 | 6 | 4 => 4 | 1 => 1 |
| astar_unknown | crazyflie_bright | 6 | 6 | 1 => 1 | 3 => 3 |
| astar_unknown_f2 | ideal | 6 | 6 | 2 => 2 | 0 => 0 |
| astar_unknown_f2 | crazyflie | 6 | 6 | 4 => 4 | 2 => 2 |
| astar_unknown_f2 | crazyflie_bright | 6 | 6 | 4 => 4 | 2 => 2 |
| dstar_lite | ideal | 6 | 6 | 6 => 6 | 0 => 0 |
| dstar_lite | crazyflie | 6 | 6 | 5 => 5 | 0 => 0 |
| dstar_lite | crazyflie_bright | 6 | 6 | 3 => 3 | 3 => 3 |
| mppi | ideal | 6 | 6 | 1 => 1 | 0 => 0 |
| mppi | crazyflie | 6 | 6 | 1 => 1 | 5 => 5 |
| mppi | crazyflie_bright | 6 | 6 | 1 => 1 | 5 => 5 |
| mppi_astar | ideal | 6 | 6 | 5 => 5 | 0 => 0 |
| mppi_astar | crazyflie | 6 | 6 | 1 => 1 | 5 => 5 |
| mppi_astar | crazyflie_bright | 6 | 6 | 0 => 0 | 6 => 6 |
| hybrid_astar | ideal | 6 | 6 | 5 => 5 | 0 => 0 |
| hybrid_astar | crazyflie | 6 | 6 | 5 => 5 | 0 => 0 |
| hybrid_astar | crazyflie_bright | 6 | 6 | 3 => 3 | 2 => 2 |

Sampled runs whose outcome the fix changes (unpatched => patched, patched = `status` row in every case):

| planner | family | preset | index | unpatched | patched |
|---|---|---|---|---|---|
| astar_unknown | random | crazyflie_bright | 19 | collision | reached |
| astar_unknown | maze | crazyflie_bright | 10 | collision | timeout |
| astar_unknown_f2 | glass_office | crazyflie | 0 | reached | collision |
| astar_unknown_f2 | forest | crazyflie_bright | 11 | collision | reached |
| dstar_lite | office | crazyflie_bright | 2 | collision | reached |
| dstar_lite | glass_office | crazyflie_bright | 9 | stuck | collision |
| hybrid_astar | u_trap | crazyflie_bright | 14 | reached | stuck |

Thetastar_unknown and lazy_thetastar_unknown were not in the dropout-fix study `status` arm, so they are not in this
sample.

## 3. No-dropout identity: before vs after

Preset `ideal_nodrop` (the ideal fan with dropout 0, in memory as in dropout_fix.py). 30 runs: astar_unknown,
mppi, hybrid_astar x 10 layouts (rng 88). Before = the recorded dropout-fix study `before` rows (shipped code); also
re-run here with `SKIP_DROPPED_BEAMS = False`.

**Result: identical in 30/30 runs against the recorded rows and 30/30 against the same-machine re-run**
(outcome, min_clearance_m, path_length_m, time_to_goal_s).

| planner | family | index | outcome before / after | time to goal s before / after | path m before / after |
|---|---|---|---|---|---|
| astar_unknown | random | 1 | reached / reached | 16.76 / 16.76 | 23.974 / 23.974 |
| astar_unknown | glass_office | 11 | reached / reached | 44.32 / 44.32 | 29.123 / 29.123 |
| astar_unknown | u_trap | 15 | reached / reached | 21.32 / 21.32 | 25.935 / 25.935 |
| astar_unknown | office | 6 | reached / reached | 21.36 / 21.36 | 13.343 / 13.343 |
| astar_unknown | random | 19 | reached / reached | 19.74 / 19.74 | 23.885 / 23.885 |
| astar_unknown | narrow_gap | 10 | reached / reached | 34.7 / 34.7 | 37.298 / 37.298 |
| astar_unknown | u_trap | 11 | reached / reached | 22.6 / 22.6 | 26.59 / 26.59 |
| astar_unknown | maze | 4 | reached / reached | 48.9 / 48.9 | 39.179 / 39.179 |
| astar_unknown | maze | 13 | reached / reached | 65.92 / 65.92 | 51.496 / 51.496 |
| astar_unknown | random | 17 | reached / reached | 17.14 / 17.14 | 23.575 / 23.575 |
| mppi | forest | 7 | reached / reached | 20.08 / 20.08 | 23.502 / 23.502 |
| mppi | warehouse | 4 | stuck / stuck | - / - | 25.138 / 25.138 |
| mppi | forest | 10 | reached / reached | 20.58 / 20.58 | 24.248 / 24.248 |
| mppi | u_trap | 18 | stuck / stuck | - / - | 13.186 / 13.186 |
| mppi | random | 17 | reached / reached | 20.0 / 20.0 | 23.584 / 23.584 |
| mppi | office | 5 | stuck / stuck | - / - | 1.837 / 1.837 |
| mppi | narrow_gap | 1 | stuck / stuck | - / - | 20.751 / 20.751 |
| mppi | glass_office | 9 | stuck / stuck | - / - | 2.671 / 2.671 |
| mppi | forest | 17 | reached / reached | 20.3 / 20.3 | 23.984 / 23.984 |
| mppi | maze | 1 | stuck / stuck | - / - | 22.419 / 22.419 |
| hybrid_astar | warehouse | 9 | reached / reached | 46.18 / 46.18 | 26.781 / 26.781 |
| hybrid_astar | forest | 13 | reached / reached | 23.12 / 23.12 | 26.201 / 26.201 |
| hybrid_astar | warehouse | 2 | stuck / stuck | - / - | 26.632 / 26.632 |
| hybrid_astar | random | 11 | reached / reached | 19.2 / 19.2 | 24.549 / 24.549 |
| hybrid_astar | warehouse | 11 | stuck / stuck | - / - | 27.91 / 27.91 |
| hybrid_astar | random | 18 | reached / reached | 16.42 / 16.42 | 23.478 / 23.478 |
| hybrid_astar | random | 16 | reached / reached | 18.64 / 18.64 | 24.891 / 24.891 |
| hybrid_astar | forest | 2 | reached / reached | 21.2 / 21.2 | 24.244 / 24.244 |
| hybrid_astar | forest | 3 | reached / reached | 20.88 / 20.88 | 25.373 / 25.373 |
| hybrid_astar | forest | 11 | reached / reached | 24.46 / 24.46 | 24.468 / 24.468 |

Environment control: 12 of the option B runs re-run with `SKIP_DROPPED_BEAMS = False` match the unpatched
rows (matrix_0.json / dropout-fix study `before`) in 12/12, so the numpy/scipy version gap does not move these runs.
Every worker found exactly one module with `LogOddsMap` (`close_area_arena.planners.astar_esdf`), so the
switch reached every planner.

Sections 2 and 3: 180 runs, wall 65.2 s, 4 workers (fork).

## 4. Smoke tests

| test | result | note |
|---|---|---|
| close-area-arena `test_smoke` | OK, 2 tests, 8.8 s | |
| close-area-benchmark `test_smoke` | **FAIL**, 1 of 3 | pins `astar_unknown_f2 / u_trap / crazyflie / 0` to matrix_0.json. Patched: reached, min clearance 0.5879 m (= dropout-fix study `status` row); `SKIP_DROPPED_BEAMS = False`: 0.6525 m (= matrix_0.json). Expected until matrix_0 is regenerated. |
| close-area-explore `test_smoke` | **FAIL**, 1 of 3 | pins lawnmower / random / 0 / ideal to results/bench_0.json. Path 26.729 => 26.73 m; `SKIP_DROPPED_BEAMS = False` gives 26.729 again. Not in the brief; run for side effects. |
| mppi, dstar, thetastar, hybrid-astar, mpc, relocalize, safety-filter, moving-obstacles, dwa-bug, reactive `test_smoke`; flight-repo `test_flightloop` | OK | benchmark venv, run for side effects |

## 5. Consumers of ranges() / RangeScan.distances

The fix publishes no NaN (section 1: 0 NaN in 294,720 beams), so every consumer gets the same readings as
before. Column "NaN" says what a NaN reading would do, the reason the NaN design was dropped.

| consumer | how it reads a no-return beam | a NaN reading would |
|---|---|---|
| arena `planners/astar_esdf.py` LogOddsMap | `np.isfinite`; reads `dropped` | count as no return: traced free (the bug again) |
| arena `planners/straight.py` | `d < ahead` | be skipped, same as inf |
| arena `run_faults.py` FreestBeam, `score_log.py`, `run*.py` | pass the scan through | - |
| mppi, dstar, thetastar, hybrid-astar, mpc, explore planners | via AStarESDF / LogOddsMap | as LogOddsMap |
| reactive `apf.py` line 74 / `vfh_plus.py` | `math.isfinite` filter | be skipped |
| reactive `apf.py` line 118 | `r = min(d, scan.max_range)` | **break: `min(nan, 6.0)` is nan, the escape term becomes NaN** |
| dwa-bug `dwa.py`, `bug.py` tangents and hold | `np.isfinite` / `math.isfinite` | be skipped |
| dwa-bug `bug.py` line 311 | `d <= R_SENSE` False => free beam | count as free, same as inf |
| moving-obstacles `astar_replan.py`, `predict.py`, `planners_st.py` | `np.isfinite` mask | be skipped |
| relocalize `relocalize.py`, `relocalize_yaw.py`, `mcl.py`, `sparse.py`, `submap.py` | `np.isfinite` (mcl: also `0 < z < max_range`) | be skipped |
| safety-filter `filters.py` points / sectors | `np.isfinite`, sector fill uses `max_range` | be skipped / read as max_range |
| safety-filter `unsensed.py` | subclasses the sensor, inherits the flag | - |
| site/playground `worker.js` Python glue | `_r(d)`: `math.isfinite` => None | be logged as None, same as inf |
| templates/flight-repo `arena_adapter.py` | rebuilds a plain RangeScan | - (drops the flag, see below) |

Scans rebuilt without the flag keep the pre-fix behaviour: `bug.py` `_hold` (`type(scan)(...)`, local use
only), `sparse.py` / `submap.py` (finite returns only, so nothing to flag), flight-repo `arena_adapter.py`
(feeds the team planner: an unknown-map planner there still traces dropped beams free).

## 6. Not verified

- thetastar_unknown, lazy_thetastar_unknown: never run with option B (no dropout-fix study rows); covered only by
  the shared LogOddsMap code path.
- Presets dense, depth_cam_87, lidar_2d: sensor stream checked (section 1), no flights.
- No full-matrix regeneration; the reached / collision deltas in dropout_fix_tables.md stay the dropout-fix study
  numbers until the full regeneration.
- The site playground runs the patched files from its manifest; not run in a browser.

## Commands

From `samples/close-area-benchmark`, venv per the arena install convention
(`uv venv .venv && uv pip install --python .venv -r requirements.txt`). Each script ran as
`.venv/bin/python - <<'EOF' ... EOF`; no script file was added.

Section 1 (sensor check), core loop:

```python
import dropout_fix as DF                      # DropFlagSensor only; nothing flown in this process
B, P = DF.B, DF.B.presets
# HEAD sensors.py / sensors_cone.py exec'd from `git show HEAD:...` as close_area_arena._head_sensors(_cone)
for name in P.SENSOR_PRESETS:                 # 7 presets incl. ideal_nodrop
    for fi, fam in enumerate(B.FAMILIES):     # world index 0, seed 0
        # three sensors from np.random.default_rng([0, fi, 7]): HEAD, patched, DropFlagSensor(patched)
        # 60 poses from np.random.default_rng(fi); compare distances, angles, t, max_range, rng state,
        # count NaN, flagged-but-finite beams, and dropped vs the DropFlagSensor replay mask
```

Sections 2 and 3: keys from `results/dropout_fix_runs.json` and `results/matrix_0.json` as described, then

```python
def task(a):                                  # ProcessPoolExecutor(4, mp_context=fork)
    skip, (p, f, pr, i) = a
    for m in list(sys.modules.values()):
        if hasattr(m, "LogOddsMap") and hasattr(m, "SKIP_DROPPED_BEAMS"):
            m.SKIP_DROPPED_BEAMS = skip
    return a, B.run_one(p, f, pr, i, 0)
# compared fields: outcome, min_clearance_m, path_length_m, time_to_goal_s (==)
```

Section 4: `.venv/bin/python -m unittest test_smoke` in close-area-arena (arena venv) and close-area-benchmark;
the other samples with `../close-area-benchmark/.venv/bin/python -m unittest test_smoke`.
