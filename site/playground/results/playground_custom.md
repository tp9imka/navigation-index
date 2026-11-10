# Playground loop-75: custom vehicle and sensor in the run message, browser vs native

`node site/playground/results/measure_custom.mjs`, 2026-11-10T07:42:32.793Z. Input: **synthetic** (2.5D point-mass arena, preset worlds, seed 0, truth pose, no filter).
Browser: Chrome/140.0.7339.208, Pyodide 314.0.7 (Python 3.14.2, numpy 2.4.6, scipy 1.18.0), worker.js driven directly by postMessage. Native: 3.12.10, numpy 2.5.4, scipy 1.18.1 ([native_parity_custom.json](native_parity_custom.json)).
Host: 16 CPUs, load average 84.9 / 78.9 / 64.6 at start. Worker ready in 15.5 s. Load errors in the worker: {}.

**3/3 cases identical (browser = native).** Vehicle and sensor flown (result "vehicle", "sensor", radius, beams, max range) = native: yes, every case. Ready env presets = ["ideal","crazyflie","crazyflie_bright","depth_cam_87","lidar_2d"]: yes. Refusals as expected: 3/3.

| world | planner | custom | sensor / yaw policy | vehicle radius m | browser outcome / time to goal s / min clearance m / path m | native | same | browser Python s | native Python s |
|---|---|---|---|---|---|---|---|---|---|
| random_0 | mppi_astar | sensor | custom / look_where_you_go | 0.15 | reached / 20.32 / 0.6225 / 23.998 | reached / 20.32 / 0.6225 / 23.998 | yes | 4.559 | 2.308 |
| office_0 | mppi_astar | sensor | custom / look_where_you_go | 0.15 | reached / 15.88 / 0.2883 / 15.725 | reached / 15.88 / 0.2883 / 15.725 | yes | 2.343 | 1.186 |
| narrow_gap_0 | mppi_astar | vehicle | ideal / off | 0.25 | reached / 21.6 / 0.2652 / 25.194 | reached / 21.6 / 0.2652 / 25.194 | yes | 5.159 | 2.603 |

| refusal case | as expected | worker message |
|---|---|---|
| sensor with unknown key fov | yes |     raise ValueError(f"unknown {what} keys: {', '.join(map(str, unknown))} "                      f"(allowed: {', '.join(list(required) + list(optional))})") ValueError: unknown sensor keys: fov (allowed: beams, fov_deg, max_range_m, min_range_m, noise_sigma_m, cone_deg, dropout) |
| sensor is an array | yes | cfg.sensor must be an object, got array |
| vehicle missing 3 keys | yes |   File "/home/pyodide/close_area_arena/presets.py", line 155, in check_keys     raise ValueError(f"missing {what} keys: {', '.join(missing)}") ValueError: missing vehicle keys: v_max, a_max, tau |

Console errors / warnings: 0
