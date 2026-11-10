# Forward depth camera vs ideal 360 deg fan (loop-75, synthetic, seed 0)

`samples/close-area-arena/.venv/bin/python samples/close-area-arena/results/custom_sensor_0.py`
([script](custom_sensor_0.py), [json](custom_sensor_0.json), [generated table](custom_sensor_0.table.md)).
Input: **synthetic**. One preset world per family (`site/playground/presets/{random_0, office_0, maze_0}.json`),
2.5D point-mass vehicle, simulated sensors, truth pose, no filter. Run time limit 60 s, maze 120 s. Python 3.12.10,
numpy 2.5.4, scipy 1.18.1, arm64. One layout per family: these are 3 examples, not success rates.

Why: a forward-only depth camera is the likeliest real sensor on a hackathon drone. Every arena number so far
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
current `astar_unknown` entry, with the shipped map corner at (-2.5, -2.5).

## Result

Cells: outcome / time to goal s / min clearance m.

| world | planner | ideal | depth_cam_87 | depth_cam_87 fixed yaw |
|---|---|---|---|---|
| random_0 | astar_unknown | reached / 18.7 / 0.6624 | reached / 18.9 / 0.6587 | reached / 19.08 / 0.6485 |
| random_0 | mppi_astar | reached / 20.24 / 0.5812 | reached / 20.32 / 0.6225 | reached / 20.32 / 0.639 |
| random_0 | astar_unknown_pg | reached / 18.68 / 0.6432 | reached / 18.9 / 0.6769 | reached / 18.9 / 0.6037 |
| office_0 | astar_unknown | reached / 21.96 / 0.2892 | reached / 25.4 / 0.224 | reached / 23.14 / 0.191 |
| office_0 | mppi_astar | reached / 12.84 / 0.3131 | reached / 15.88 / 0.2883 | reached / 14.14 / 0.2836 |
| office_0 | astar_unknown_pg | stuck / - / 0.8475 | stuck / - / 0.8475 | stuck / - / 0.8475 |
| maze_0 | astar_unknown | reached / 44.78 / 0.5911 | reached / 54.28 / 0.2642 | reached / 49.82 / 0.5713 |
| maze_0 | mppi_astar | reached / 31.28 / 0.357 | reached / 34.82 / 0.4024 | reached / 31.96 / 0.3598 |
| maze_0 | astar_unknown_pg | reached / 51.9 / 0.5385 | reached / 50.3 / 0.5539 | reached / 47.26 / 0.5875 |

- **The forward camera still reaches B in 6 of 6 geofenced runs**, as the ideal fan does. It costs time:
  +0.08 to +0.2 s on random_0, +3.04 to +3.44 s on office_0, +3.54 to +9.5 s on maze_0.
- Clearance drops with the camera on A* unknown map: maze_0 0.5911 => 0.2642 m, office_0 0.2892 => 0.224 m. Both stay
  above the 0.15 m vehicle radius. MPPI keeps its clearance (0.4024 m on maze_0, more than with the ideal fan).
- **The look-where-you-go yaw policy did not shorten any run here.** Fixed yaw toward B was faster in 4 of the 4 geofenced
  office_0 and maze_0 runs (for example A* maze_0 49.82 s fixed vs 54.28 s with the policy) and within 0.18 s on random_0.
  Fixed yaw also kept more clearance on A* maze_0: 0.5713 m vs 0.2642 m with the policy.
  Unverified explanation: the unknown-map planners treat unseen cells as free and plan toward B, so a camera kept on B
  confirms that corridor sooner. With 3 layouts this is an example, not a rule. The policy stays in the driver (it is
  what a real drone with a forward camera does by default) and its effect needs a 20-layout run per family.
- `astar_unknown_pg` (the playground entry) does not move on office_0 with any sensor (stuck, 0.0 m path): office_0's
  B is at (-6.75, -7.39), outside the shipped map prior that starts at (-2.5, -2.5). The benchmark fixed this with the
  geofenced corner; the playground entry still uses the shipped one.

Not verified: real hardware (no camera data was flown), the stereo noise growth with distance (the arena noise is
constant), camera dropout rates, and any layout beyond these 3.
