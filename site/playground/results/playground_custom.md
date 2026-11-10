# Playground loop-75 / 75b: custom vehicle, sensor and yaw in the run message, browser vs native

`node site/playground/results/measure_custom.mjs`, 2026-11-10T08:16:35.660Z. Input: **synthetic** (2.5D point-mass arena, preset worlds, seed 0, truth pose, no filter).
Browser: Chrome/140.0.7339.208, Pyodide 314.0.7 (Python 3.14.2, numpy 2.4.6, scipy 1.18.0), worker.js driven directly by postMessage. Native: 3.12.10, numpy 2.5.4, scipy 1.18.1 ([native_parity_custom.json](native_parity_custom.json)).
Host: 16 CPUs, load average 174 / 108.5 / 81.5 at start. Worker ready in 18.2 s. Load errors in the worker: {}.

**7/7 cases identical (browser = native).** Vehicle and sensor flown (result "vehicle", "sensor", radius, beams, max range) = native: yes, every case. Ready env presets = ["ideal","crazyflie","crazyflie_bright","depth_cam_87","lidar_2d"]: yes. Refusals as expected: 4/4.

| world | planner | custom | sensor / yaw | vehicle radius m | browser outcome / time to goal s / min clearance m / path m | native | same | browser Python s | native Python s |
|---|---|---|---|---|---|---|---|---|---|
| random_0 | mppi_astar | sensor | custom / look_where_you_go | 0.15 | reached / 20.32 / 0.6225 / 23.998 | reached / 20.32 / 0.6225 / 23.998 | yes | 4.329 | 2.192 |
| office_0 | mppi_astar | sensor | custom / look_where_you_go | 0.15 | reached / 15.88 / 0.2883 / 15.725 | reached / 15.88 / 0.2883 / 15.725 | yes | 2.077 | 1.174 |
| office_0 | mppi_astar | sensor | custom / fixed | 0.15 | reached / 14.14 / 0.2836 / 14.516 | reached / 14.14 / 0.2836 / 14.516 | yes | 1.761 | 0.985 |
| narrow_gap_0 | mppi_astar | vehicle | ideal / fixed | 0.25 | reached / 40 / 0.3595 / 45.096 | reached / 40 / 0.3595 / 45.096 | yes | 11.571 | 5.632 |
| narrow_gap_0 | mppi_astar | vehicle | ideal / fixed | 0.35 | stuck / - / 0.6173 / 33.293 | stuck / - / 0.6173 / 33.293 | yes | 40.915 | 18.37 |
| narrow_gap_0 | astar_unknown | vehicle | ideal / fixed | 0.25 | reached / 53.24 / 0.3264 / 55.086 | reached / 53.24 / 0.3264 / 55.086 | yes | 13.721 | 6.34 |
| narrow_gap_0 | astar_unknown | vehicle | ideal / fixed | 0.35 | stuck / - / 0.418 / 34.379 | stuck / - / 0.418 / 34.379 | yes | 21.451 | 9.847 |

Vehicle radius in the planners (loop-75b). Before = the same run with the planners at the shipped 0.15 m (native only, `inflate=False`). Free path = BFS on the true grid inflated by the radius.

| world | planner | radius m | free path | before: outcome / time to goal s / min clearance m / path m | after (browser = native) |
|---|---|---|---|---|---|
| narrow_gap_0 | mppi_astar | 0.25 | yes | reached / 21.6 / 0.2652 / 25.194 | reached / 40 / 0.3595 / 45.096 |
| narrow_gap_0 | mppi_astar | 0.35 | no | collision / - / 0.3467 / 12.999 | stuck / - / 0.6173 / 33.293 |
| narrow_gap_0 | astar_unknown | 0.25 | yes | reached / 24.98 / 0.301 / 25.195 | reached / 53.24 / 0.3264 / 55.086 |
| narrow_gap_0 | astar_unknown | 0.35 | no | collision / - / 0.3484 / 12.956 | stuck / - / 0.418 / 34.379 |

| refusal case | as expected | worker message |
|---|---|---|
| sensor with unknown key fov | yes |     raise ValueError(f"unknown {what} keys: {', '.join(map(str, unknown))} "                      f"(allowed: {', '.join(list(required) + list(optional))})") ValueError: unknown sensor keys: fov (allowed: beams, fov_deg, max_range_m, min_range_m, noise_sigma_m, cone_deg, dropout) |
| sensor is an array | yes | cfg.sensor must be an object, got array |
| vehicle missing 3 keys | yes |   File "/home/pyodide/close_area_arena/presets.py", line 155, in check_keys     raise ValueError(f"missing {what} keys: {', '.join(missing)}") ValueError: missing vehicle keys: v_max, a_max, tau |
| cfg.yaw spin | yes |   File "<exec>", line 356, in simulate   File "<exec>", line 402, in _simulate ValueError: cfg.yaw must be fixed or look_where_you_go, got 'spin' |

Page checks (index.html, no Python run): 6/6.

| page check | ok |
|---|---|
| sensor select offers the 5 presets | yes |
| default drone: no vehicle / yaw in readCfg or the link | yes |
| drone panel => readCfg vehicle + yaw | yes |
| link carries radius, v_max, yaw | yes |
| link restores the drone panel (open, same readCfg) | yes |
| radius 9 m clamped to 0.6 m in readCfg | yes |

Console errors / warnings: 0
