# Flight log format `close-area-log/1` (JSONL)

One format for the arena, SITL and a real drone, so reviewers get the same numbers and the same
plot from each. Score it with [score_log.py](score_log.py), which imports only numpy and
matplotlib (no arena code):

```sh
.venv/bin/python score_log.py flight.jsonl --plot flight.png --json flight_score.json
```

## Lines

Line 1 is a header. Every other line is one step of the control loop, written once per
`send_setpoint()` call. Frame: local ENU, metres, seconds, radians, origin at A (the same frame
as `Pose` in [adapter.py](adapter.py) and [templates/drone-adapter](../../templates/drone-adapter/adapter.py)).

### Header

| Field | Required | Meaning |
|---|---|---|
| `type` | yes | `"header"` |
| `format` | no | `"close-area-log/1"` |
| `input` | yes | `"real"`, `"sitl"` or `"synthetic"`. Printed with every score |
| `A`, `B` | yes | `[x, y]` start and goal, m. A is normally `[0, 0]` |
| `goal_tol` | no | Reached radius around B, m. Default 0.3 (arena value) |
| `radius` | no | Vehicle radius, m. Clearance below it counts as a collision. Default 0.15 |
| `world.area` | no | `[xmin, ymin, xmax, ymax]` walls, m. Omit for an open field (no wall clearance) |
| `world.boxes` | no | List of `[cx, cy, hx, hy]` or `[cx, cy, hx, hy, yaw]`: centre, half sizes, rotation rad |
| `world.cylinders` | no | List of `[cx, cy, r]` |
| `t0` | no | Time the A=>B leg started. Default: `t` of the first step |
| `manual_modes` | no | Mode strings that count as a pilot takeover. Default: PX4 and ArduPilot pilot modes (`MANUAL`, `POSCTL`, `POSITION`, `ALTCTL`, `STABILIZED`, `ACRO`, `STABILIZE`, `ALT_HOLD`, `POSHOLD`, `RATTITUDE`) |
| `source`, `notes`, `frame` | no | Free text, shown in the plot title |

Obstacles are 2.5D vertical prisms, as in the arena. Measure them in the A frame before the
flight (tape or mocap). With no obstacles and no area, min clearance prints `-`.

### Step

| Field | Required | Meaning |
|---|---|---|
| `t`, `x`, `y`, `z`, `vx`, `vy`, `vz`, `yaw`, `quality`, `reset_counter`, `sigma_xy` | `t`, `x`, `y` | The `Pose` dataclass fields, as the planner saw them |
| `sp` | no | Setpoint sent: `{"vx", "vy", "vz", "yaw_rate"}` |
| `filter_intervened` | no | `true` when the safety filter changed the planner's setpoint this step. Default false |
| `mode` | no | Flight mode string (`"OFFBOARD"`, `"GUIDED"`, `"POSCTL"`, ...) |
| `planned` | no | `[[x, y], ...]` current planned path. Write it only when it changes; each new one is a replan |
| `truth` | no | `{"x", "y", "z"}` from sim truth or mocap. If every step has it, scoring uses it |

Without `truth`, scoring uses the logged pose, which is the drone's own estimate. The output
says `positions from pose (onboard estimate)` so nobody reads it as ground truth. A drifting
estimate can show a clean run that hit something.

## Writer (stdlib, about 10 lines)

```python
import json
class FlightLog:
    def __init__(self, path, A, B, boxes=(), cylinders=(), area=None, goal_tol=0.3, input="real"):
        self.f = open(path, "w", buffering=1)            # line-buffered: a crash keeps the lines so far
        self._w({"type": "header", "format": "close-area-log/1", "input": input, "A": A, "B": B,
                 "goal_tol": goal_tol, "world": {"area": area, "boxes": list(boxes), "cylinders": list(cylinders)}})
    def _w(self, d): self.f.write(json.dumps(d) + "\n")
    def step(self, pose, sp, filter_intervened=False, mode="OFFBOARD", planned=None, truth=None):
        d = dict(vars(pose), sp=vars(sp), filter_intervened=bool(filter_intervened), mode=mode)
        if planned is not None: d["planned"] = [[float(p[0]), float(p[1])] for p in planned]
        if truth is not None: d["truth"] = {"x": truth[0], "y": truth[1], "z": truth[2]}
        self._w(d)
```

Use: `log = FlightLog("flight.jsonl", [0, 0], [5, 0], boxes=[[2.5, 0.3, 0.4, 0.4]])`, then
`log.step(adapter.pose(), sp, intervened, mode)` right after each `send_setpoint(sp)`. `pose`
and `sp` are the `Pose` and `Setpoint` dataclasses. A torn last line (power cut mid-write) is
skipped with a warning.

## What the scorer computes

Same definitions as [scorer.py](scorer.py) where they overlap. The first event in time ends
the run: `reached`, `collision`, `stuck` (< 0.2 m moved in 10 s) or `log_ended`.

- **reached / time to goal**: first logged position within `goal_tol` of B; time from `t0`.
  Samples only, so a sparse log can miss a brief pass through the goal disc.
- **min clearance**: centre to nearest declared surface, on the path between samples
  interpolated every 0.05 m, up to the end event. **Collision** uses the same points.
- **path length**: sum of logged segments up to the end event.
- **interventions**: number of times `filter_intervened` turns on; **fraction**: share of
  logged steps with it on (log at a fixed rate for this to mean share of time).
- **manual mode entries**: times `mode` enters a `manual_modes` value.

Plot: walls, obstacles, every logged plan (earlier ones faint), flown path, A and B discs of
`goal_tol` radius, closest approach marked with a circle of the min-clearance radius, end event.

## Checked on (2026-11-09, CPython 3.11.15, numpy 2.4.6, matplotlib 3.11.2)

Both inputs are **synthetic**. No real or SITL log has been scored yet.

| Log | Outcome | Time to goal s | Min clearance m | Path m | Interventions (fraction) |
|---|---|---|---|---|---|
| [arena random seed 0 index 2, 10 Hz](results/log_arena_random_0_2.jsonl) ([score](results/log_arena_random_0_2_score.txt), [plot](results/log_arena_random_0_2.png)) | reached | 17.76 | 0.3792 | 23.936 | 2 (0.1732) |
| [hand-written, 20 lines, 2 Hz](results/log_hand_20line.jsonl) ([score](results/log_hand_20line_score.txt), [plot](results/log_hand_20line.png)) | reached | 8.5 | 0.2779 | 5.022 | 2 (0.1667) |

Cross-check: the arena's own `scorer.py` on its 50 Hz truth trace of the same run gives reached,
17.76 s, 0.3789 m, 23.936 m ([reference](results/log_arena_random_0_2_reference.txt), same as
run 2 in [straight_random_0.md](results/straight_random_0.md)). The 10 Hz log differs by 0.0003 m
in min clearance. In the arena log `filter_intervened` marks the straight planner's slow-down
(commanded speed below 99 % of nominal), since the arena has no safety filter yet. The hand
log's closest approach (0.2779 m) falls between two samples, found by the 0.05 m interpolation.
