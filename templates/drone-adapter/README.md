# drone-adapter: one seam between the planner and any drone

Planner code calls three things: `pose()`, `ranges()`, `send_setpoint()`. Today they run on
`MockAdapter` (no simulator). On Day 1 a platform driver implements the same three calls for
Crazyflie, Tello, PX4 or ArduPilot, and the planner does not change.

Stdlib Python only (3.12 and 3.14 tested). Nothing here touches a real vehicle or a SITL.

## Files

| File | What it is |
|---|---|
| `adapter.py` | `Pose`, `RangeScan`, `Setpoint` dataclasses, `Adapter` Protocol, frame helpers (`enu_to_ned`, `ned_to_enu`, `flu_to_frd`, `frd_to_flu`, yaw and yaw-rate versions, `world_to_body`, `body_to_world`) |
| `mock.py` | `MockAdapter`: kinematic point mass, 20 Hz lockstep, one wall segment, 8-beam horizontal range scan, collision flag |
| `example_loop.py` | `fly_to()`: go-to-goal with stop-if-close at 20 Hz, written only against `Adapter` |
| `test_adapter.py` | Frame round-trips, mock satisfies `Adapter`, loop reaches the goal, loop stops before the wall |
| `frames.md` | Frame and unit conventions for PX4, ArduPilot, Crazyflie, Tello, with sources and what is not confirmed |
| `results/` | Raw output of the runs quoted below |

Conventions: world is local ENU (x east, y north, z up, metres, origin at point A); body is FLU
(x forward, y left, z up); yaw rad CCW from +x. Field names are shared with
`samples/close-area-arena`; do not rename them.

## Run it

```sh
cd templates/drone-adapter
python3 -m unittest -v
python3 example_loop.py
```

Output on 2026-11-09, `python3.12` (synthetic input: mock with perfect pose, no noise; copied
from [results/2026-11-09-mock-run.txt](results/2026-11-09-mock-run.txt)):

```
test_known_values (test_adapter.Frames.test_known_values) ... ok
test_round_trips (test_adapter.Frames.test_round_trips) ... ok
test_mock_is_adapter (test_adapter.Loop.test_mock_is_adapter) ... ok
test_reaches_goal (test_adapter.Loop.test_reaches_goal) ... ok
test_stops_before_wall (test_adapter.Loop.test_stops_before_wall) ... ok

----------------------------------------------------------------------
Ran 5 tests in 0.004s

OK

goal=(5.0, 3.0, 1.0) final_distance_m=0.096 t_s=8.00 collided=False min_wall_dist_m=1.20
```

What it shows: from A = (0, 0, 0) the loop reaches (5, 3, 1) within 0.096 m in 8.00 s of simulated
time without touching the wall. With the goal behind the wall at (6, 0, 1) it stops 0.45 m from
the wall and does not collide (same results file). That proves the plumbing, not a planner: the
loop never goes around anything.

## Copy it into a project repo

```sh
cp -r templates/drone-adapter ~/our-project/src/drone_adapter
rm -rf ~/our-project/src/drone_adapter/results          # keep your own results
```

The folder works both ways: as a package (`from drone_adapter import MockAdapter, Setpoint`,
`from drone_adapter.example_loop import fly_to`) or as a flat folder run from inside itself.
Write the planner against `Adapter` only. Never import a platform SDK in planner code.

## Where the drivers go

`drivers/` (not written yet; a follow-up job adds stubs): one file per platform, e.g.
`drivers/px4_mavsdk.py`, `drivers/ardupilot_pymavlink.py`, `drivers/crazyflie_cflib.py`,
`drivers/tello_djitellopy.py`. Each class implements `pose()`, `ranges()`, `send_setpoint()`
and does every frame and unit conversion inside itself, following [frames.md](frames.md). Each one
also owns the keep-alive stream (PX4 Offboard, ArduPilot GUIDED and Tello all stop or land without
fresh commands), arming and mode changes, and storing the pose at A to make it the origin.

## Limits

- The mock is kinematic: no attitude, drag, latency, wind, sensor noise or estimator drift.
  `quality` is always 100 and `reset_counter` 0. Inject jumps and bias yourself before trusting a
  safety claim.
- One wall segment, 2D horizontal scan of 8 beams at 45 degree spacing, max range 4 m. Thin
  obstacles between beams are invisible, as they are on a real Multi-ranger.
- Lockstep time: `send_setpoint()` advances the mock by 0.05 s. A real driver runs on wall time;
  pass `realtime=True` to `fly_to()` or use a proper scheduler. The example loop's `time.sleep`
  ignores compute time.
- Stop-if-close only zeroes horizontal velocity toward a close return. It does not avoid, replan,
  or brake for speed; approaching at the 1 m/s cap it stopped 0.45 m from the wall with a 0.6 m threshold.
- `world_to_body` ignores roll and pitch. Fine for level velocity commands, wrong for tilted
  range sensors.
- Platform conventions in `frames.md` are read from docs and code, not flown. Items marked
  "not confirmed" there (Tello rc units and signs, Crazyflie yaw-rate sign, PX4 yaw-rate with
  velocity-only setpoints) need a bench test.
