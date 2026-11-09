# flight-repo: close-area A=>B flight loop starter

Use this when the task is "fly from A to B in a close area, maybe with obstacles": clone it at
H+0 as the team repo. Platform drivers: [../drone-adapter/drivers/](../drone-adapter/drivers/README.md).
Planners and measured baselines (synthetic): [close-area-arena](../../samples/close-area-arena/README.md).
For a GNSS / PNT-integrity brief use [../project-repo/](../project-repo/README.md) instead.

It is the loop skeleton, runnable today on a mock with no dependencies:

```
Adapter.pose() + ranges() => NavHealth => Planner.step() => SafetyFilter.filter() => Adapter.send_setpoint()   at 20 Hz
```

Stdlib Python only (runs below on 3.14.6; unit tests also pass on 3.12). Nothing here has touched a real vehicle or a SITL.
Status: hackathon starter, not flight-tested, not for operational use.

## Run it

```sh
make test    # 6 unit tests on the mock
make sim     # 4 mock flights, one score line each, JSONL logs in runs/
make arena   # the hub's arena "straight" planner flown through this loop (needs the hub checkout)
python3 main.py --mock          # A=(0,0,1) => B=(5,3,1), one-line score
```

## Files

| Path | What |
|---|---|
| `flightloop/adapter.py` | `Pose`, `RangeScan`, `Setpoint`, `Adapter` Protocol, frame helpers. Copied from the hub's `templates/drone-adapter/adapter.py` |
| `flightloop/mock.py` | `MockAdapter`: kinematic point mass, one wall from (4, -1) to (4, 1), 8 beams, 4 m range, lockstep 0.05 s per `send_setpoint()`. Copied from `templates/drone-adapter/mock.py` |
| `flightloop/health.py` | `NavHealth.update(pose)` => `ok` / `degraded` / `lost` from `quality`, `reset_counter` jumps, `sigma_xy`, stale pose. Thresholds are named constants at the top |
| `flightloop/planner.py` | `Planner` Protocol (`step(pose, scan, goal, grid, dt) -> Setpoint`, same as the arena) and `GoToGoal` (stops if a return ahead is closer than `STOP_DIST_M` = 0.6 m) |
| `flightloop/safety.py` | `SafetyFilter` Protocol (`filter(setpoint, pose, scan, health) -> (setpoint, intervened)`), `PassThrough`, `RangeStop` |
| `flightloop/loop.py` | `run()`: 20 Hz loop, planner in a worker thread with a 30 ms budget, keep-alive, degraded => 0.3 m/s cap, lost => hover, one JSONL line per tick |
| `main.py` | CLI: `--mock`, `--scenario open|blocked`, `--planner go_to_goal|blind|arena:<module>`, `--safety range_stop|pass_through`, `--realtime` |
| `test_flightloop.py` | Protocols, reach, filter vs blind planner, keep-alive, degraded cap, lost hover, reset counting |
| `results/2026-11-09-mock-run.txt` | Raw output quoted below |

## Loop rules (flightloop/loop.py)

| Situation | What is sent |
|---|---|
| Health `ok`, planner answered within `PLAN_BUDGET_S` (30 ms) | Planner setpoint, then safety filter. `mode=nominal` |
| Planner still running at the budget | Last planner setpoint again, re-filtered on the fresh scan. `source=keepalive`. The overrunning result is used on the tick it arrives (`source=late`) |
| Health `degraded` | Planner setpoint capped to `DEGRADED_SPEED_CAP_MS` (0.3 m/s horizontal). `mode=capped`. `RangeStop` adds 0.2 m margin |
| Health `lost` | Zero velocity (hover), planner not called. `mode=hover` |
| Planner raised | Hover for that tick, `mode=planner_error`, next tick tries again |
| Estimated distance to B under `GOAL_TOL_M` (0.2 m), or `timeout_s` | One hover setpoint, then `run()` returns. `mode=arrived` / `timeout` |

Each JSONL line has `t`, `pose`, `setpoint` (the one actually sent), `intervened`, `health`,
`mode`, plus `source`, `reasons` (why health is not ok) and `plan_ms`.

## Results (2026-11-09, synthetic: mock with perfect pose, no noise)

From [results/2026-11-09-mock-run.txt](results/2026-11-09-mock-run.txt), Python 3.14.6, macOS arm64:

```
$ make test
python3 -m unittest -v test_flightloop
test_degraded_caps_speed_and_lost_hovers (test_flightloop.FlightLoop.test_degraded_caps_speed_and_lost_hovers) ... ok
test_health_reset_jumps (test_flightloop.FlightLoop.test_health_reset_jumps) ... ok
test_keepalive_when_planner_overruns (test_flightloop.FlightLoop.test_keepalive_when_planner_overruns) ... ok
test_open_reaches_and_logs_every_tick (test_flightloop.FlightLoop.test_open_reaches_and_logs_every_tick) ... ok
test_protocols (test_flightloop.FlightLoop.test_protocols) ... ok
test_safety_filter_catches_blind_planner (test_flightloop.FlightLoop.test_safety_filter_catches_blind_planner) ... ok

----------------------------------------------------------------------
Ran 6 tests in 1.661s

OK
$ make sim
python3 main.py --mock --scenario open --log runs/open.jsonl
score scenario=open planner=go_to_goal safety=range_stop reached=True final_dist_m=0.194 t_s=7.00 collided=False min_wall_dist_m=1.20 ticks=141 intervened=0 keepalive=0 overruns=0 modes=arrived:1,nominal:140 log=runs/open.jsonl
python3 main.py --mock --scenario blocked --timeout 10 --log runs/blocked.jsonl
score scenario=blocked planner=go_to_goal safety=range_stop reached=False final_dist_m=2.450 t_s=10.00 collided=False min_wall_dist_m=0.45 ticks=201 intervened=0 keepalive=0 overruns=0 modes=nominal:200,timeout:1 log=runs/blocked.jsonl
python3 main.py --mock --scenario blocked --timeout 10 --planner blind --log runs/blocked-blind.jsonl
score scenario=blocked planner=blind safety=range_stop reached=False final_dist_m=2.450 t_s=10.00 collided=False min_wall_dist_m=0.45 ticks=201 intervened=129 keepalive=0 overruns=0 modes=nominal:200,timeout:1 log=runs/blocked-blind.jsonl
python3 main.py --mock --scenario blocked --timeout 10 --planner blind --safety pass_through --log runs/blocked-blind-nofilter.jsonl
score scenario=blocked planner=blind safety=pass_through reached=False final_dist_m=2.143 t_s=10.00 collided=True min_wall_dist_m=0.14 ticks=201 intervened=0 keepalive=0 overruns=0 modes=nominal:200,timeout:1 log=runs/blocked-blind-nofilter.jsonl
```

What it shows:

- **open:** A=>B reached, 0.194 m from B at 7.00 s simulated time, 1.20 m from the wall at closest.
- **blocked** (B behind the wall): `GoToGoal` stops 0.45 m from the wall and times out. It does not
  go around: that is the planner's job, not this skeleton's.
- **blind planner** (never stops): with `RangeStop` it stops 0.45 m from the wall, filter active on
  129 of 201 ticks. With `PassThrough` it hits the wall (0.14 m, under the 0.15 m radius). This is
  the one run where the safety filter is the only thing between the planner and a crash.
- **arena planner:** `make arena` flew the arena's `straight` planner, unchanged, through this loop:
  reached B, 0.192 m, 5.10 s. Same results file.
- **realtime:** `python3 main.py --mock --realtime` paced 141 ticks in 7.40 s wall time with 0
  overruns (same results file). On the mock that only proves the scheduler, not a driver.
- **keep-alive and health** are covered by unit tests only (a 100 ms planner against the 30 ms
  budget; quality forced to 40 and 5 after 1 s; reset_counter jumps). No mock flight injects them.

## Swap the mock for a real driver

1. Write `drivers/<platform>.py` with a class that has `pose()`, `ranges()`, `send_setpoint(sp)`.
   Do every frame and unit conversion inside it (local ENU, origin at A; body FLU; yaw CCW from
   +x). Conventions per platform: hub [templates/drone-adapter/frames.md](../drone-adapter/frames.md).
2. Map the estimator flags into `Pose`: `quality` (PX4 / ArduPilot `ODOMETRY.quality`),
   `reset_counter`, `sigma_xy`. If the platform has no quality field it stays -1, which
   `NavHealth` treats as `degraded` (0.3 m/s cap) until you change `UNKNOWN_QUALITY_STATE`.
3. In `main.py`, build the driver instead of `MockAdapter` and call
   `run(driver, planner, safety, goal, realtime=True)`. Lockstep mode is for the mock only.
4. The driver owns arming, mode changes (PX4 Offboard, ArduPilot GUIDED), takeoff to the start
   altitude, and what happens after `run()` returns: the loop sends one hover setpoint, then
   stops streaming. Land or switch to a hold mode right after, or the autopilot fails safe.
5. Fly it first with `--safety range_stop` and a low `V_MAX_MS` in `flightloop/planner.py`.

## Where the arena planners plug in

The hub's [close-area-arena](../../samples/close-area-arena/CONTRACT.md) planners have the same
`step(pose, scan, goal, grid, dt)` signature and return a `Setpoint` with the same fields, so
they pass straight to `run()`:

```sh
python3 main.py --mock --planner arena:straight --arena /path/to/navigation-index/samples/close-area-arena
```

- `main.load_arena_planner()` loads the arena as package `close_area_arena`, the recipe in its
  CONTRACT.md, then calls `planners/<name>.py: make()`.
- Planners with `uses_grid = True` get `run(..., grid=...)`. The mock has no grid; build an
  `OccGrid` from the arena (numpy) or your own map.
- Arena planners that import numpy or scipy need the arena's venv:
  `.venv/bin/python main.py ...` from a venv with the arena's `requirements.txt`. `straight` is stdlib.
- The arena plans at 10 Hz (`dt` = 0.1 s); this loop calls the planner every tick with
  `dt` = 0.05 s. A planner that integrates over `dt` sees half the step.
- Or write your own: a class with `name`, `uses_grid`, `reset()`, `step(...)` in `flightloop/`.
  The integrity-aware safety filter from the hub research goes in `flightloop/safety.py`.

## Limits

- The mock is kinematic with perfect pose: no attitude, drag, latency, noise or estimator drift.
  Health faults reach the loop only through the test wrapper `FaultyPose`.
- 8 beams at 45 degree spacing: thin obstacles between beams are invisible to both `GoToGoal`
  and `RangeStop`. A blind spot is not a pass.
- `RangeStop` removes velocity toward close returns using an assumed 2.0 m/s^2 braking rate and
  0.35 m margin. Not tuned, not a CBF, no guarantee between beams or for moving obstacles.
- `NavHealth` thresholds (quality 50 / 20, sigma 0.30 / 1.00 m, 3 resets in 10 s) are guesses,
  not fitted to any estimator. The stale-pose check only runs with `realtime=True`.
- The planner thread cannot be killed: a planner that hangs forever keeps the keep-alive going
  (correct) but also keeps the process alive on exit.
- Links to `../drone-adapter/` and `../../samples/` work inside the hub only. After copying the
  folder into a project repo, use the hub paths in `AGENTS.md`.
