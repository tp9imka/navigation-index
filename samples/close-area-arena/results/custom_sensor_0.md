# Forward depth camera vs ideal 360 deg fan (synthetic, seed 0)

`samples/close-area-arena/.venv/bin/python samples/close-area-arena/results/custom_sensor_0.py`
([script](custom_sensor_0.py), [json](custom_sensor_0.json), [generated table](custom_sensor_0.table.md)).
Input: **synthetic**. One preset world per family (`site/playground/presets/{random_0, office_0, maze_0}.json`),
2.5D point-mass vehicle, simulated sensors, truth pose, no filter. Run time limit 60 s, maze 120 s. Python 3.12.10,
numpy 2.5.4, scipy 1.18.1, arm64. Re-run on 2026-11-12 with the dropped-beam fix on
([upstream-findings section 22](../../../docs/upstream-findings.md#22-close-area-arena-a-dropped-beam-marks-free-space-behind-walls)). One layout per family: these are 3 examples, not success rates.

Why: a forward-only depth camera is the likeliest real sensor on a small indoor drone. Every arena number so far
used a 360 deg fan.

## Sensors

| config | what it is |
|---|---|
| ideal | 72 exact rays, 360 deg, 6 m, noise 0.02 m, dropout 2 % (run.DEFAULTS). Yaw stays fixed toward B, as in run.py |
| depth_cam_87 | [presets.py](../presets.py) `depth_cam_87`: 30 beams over 87 deg, 3 deg cones, 0.3-5 m, noise 0.04 m, dropout 5 %, glass and mirror invisible. Look-where-you-go yaw ([worker.js](../../../site/playground/worker.js) `look_where_you_go`: face the commanded velocity, or B when slower than 0.2 m/s, gain 2 /s, cap 1.0 rad/s) |
| depth_cam_87 fixed yaw | the same camera with the yaw policy off: it looks along the initial bearing to B all run |

Camera numbers: 87 deg and the 0.3 m minimum are from the [Intel D435i specifications](https://www.intel.com/content/www/us/en/products/sku/190004/intel-realsense-depth-camera-d435i/specifications.html);
0.04 m is the D400 datasheet accuracy figure of under 2 % at 2 m, held constant over range. The 5 m maximum is a
proposal (Intel quotes about 3 m for its operating range). Beam count, cone, dropout and the yaw gains are proposals.

Planners: `astar_unknown` is the benchmark's geofenced A* unknown map (bench.py `GeofencedAStar`, map corner on the
area bounds, as in [matrix_0.json](../../close-area-benchmark/results/matrix_0.json)). `mppi_astar` is MPPI on the
unknown-map A* path, geofenced (the same in the playground and the benchmark). `astar_unknown_pg` is the playground's
own `astar_unknown` entry. Since the playground geofenced it (2026-11-10) it is the same planner, and its rows equal
the `astar_unknown` rows; it stays in the table as that check.

## Result

Cells: outcome / time to goal s / min clearance m.

| world | planner | ideal | depth_cam_87 | depth_cam_87 fixed yaw |
|---|---|---|---|---|
| random_0 | astar_unknown | reached / 18.7 / 0.6624 | reached / 18.84 / 0.6635 | reached / 19.08 / 0.6496 |
| random_0 | mppi_astar | reached / 20.24 / 0.5813 | reached / 20.34 / 0.6334 | reached / 20.32 / 0.6392 |
| random_0 | astar_unknown_pg | reached / 18.7 / 0.6624 | reached / 18.84 / 0.6635 | reached / 19.08 / 0.6496 |
| office_0 | astar_unknown | reached / 22.76 / 0.2641 | reached / 23.06 / 0.1898 | reached / 23.06 / 0.1885 |
| office_0 | mppi_astar | reached / 12.8 / 0.3193 | reached / 13.8 / 0.3681 | reached / 13.66 / 0.3521 |
| office_0 | astar_unknown_pg | reached / 22.76 / 0.2641 | reached / 23.06 / 0.1898 | reached / 23.06 / 0.1885 |
| maze_0 | astar_unknown | reached / 43.22 / 0.5864 | reached / 44.78 / 0.596 | reached / 44.08 / 0.523 |
| maze_0 | mppi_astar | reached / 31.44 / 0.3757 | reached / 31.7 / 0.3684 | reached / 31.66 / 0.3583 |
| maze_0 | astar_unknown_pg | reached / 43.22 / 0.5864 | reached / 44.78 / 0.596 | reached / 44.08 / 0.523 |

- **The forward camera still reaches B in 6 of 6 geofenced runs**, as the ideal fan does. It costs a little time:
  +0.10 to +0.14 s on random_0, +0.30 to +1.0 s on office_0, +0.26 to +1.56 s on maze_0.
- Clearance drops with the camera on A* unknown map in office_0 (0.2641 => 0.1898 m), still above the 0.15 m vehicle
  radius. On maze_0 it does not drop (0.5864 => 0.596 m). MPPI keeps its clearance (0.3684 m on maze_0 vs 0.3757 m).
- **The look-where-you-go yaw policy did not shorten the room runs.** Fixed yaw toward B was faster in 3 of the 4
  geofenced office_0 and maze_0 runs and tied in the 4th, by at most 0.7 s (A* maze_0 44.08 s fixed vs 44.78 s with the
  policy). On random_0 the policy was 0.24 s faster for A*. The policy kept more clearance on A* maze_0
  (0.596 m vs 0.523 m fixed). With 3 layouts and differences under a second this is an example, not a rule. The policy
  stays in the driver (it is what a real drone with a forward camera does by default) and its effect needs a
  20-layout run per family.
- Before 2026-11-12 this file showed bigger camera costs (up to +9.5 s on maze_0) and a clearance drop on maze_0. The
  dropped-beam fix and the geofenced playground entry removed both; the file's git history has the old table.

Not verified: real hardware (no camera data was flown), the stereo noise growth with distance (the arena noise is
constant), camera dropout rates, and any layout beyond these 3.
