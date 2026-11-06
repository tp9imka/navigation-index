# colav-simulator - integration card
<!-- about: repo:ntnu-itk-autonomous-ship-lab/colav-simulator -->
One-line: Python ship collision-avoidance simulator from NTNU - YAML COLREGs scenarios (head-on, crossing, overtaking, AIS-derived) over real Norwegian ENC data, radar/AIS sensors with trackers, a pluggable planner interface and a Gymnasium env.

| | |
|---|---|
| Install | Not on PyPI (404). `git clone https://github.com/ntnu-itk-autonomous-ship-lab/colav-simulator && cd colav-simulator && git lfs pull && uv sync` (README uses `uv sync`; `uv sync --group optional` adds `rrt-star-lib` and `vimmjipda`). Package `colav-simulator` 1.0.0 (pyproject.toml), `requires-python >=3.10,<3.12`. `seacharts` comes from a pinned git fork (`trymte/seacharts`) and needs native GDAL. |
| Runs on | Linux, macOS (README badge; tested "under a Unix-based operating system"). CPU only. Python 3.10 or 3.11 only. |
| Inputs | Scenario YAML (`scenarios/*.yaml`: `utm_zone`, `map_origin_enu`, `map_data_files`, `ship_list` with `csog_state`, `waypoints`, `speed_plan`, guidance, tracker, sensors), simulator config `simulator.yaml`. ENC as ESRI FileGDB (`.gdb`) in UTM 32/33 from kartkatalog.geonorge.no; two are shipped in `data/enc` via Git LFS (`More_og_Romsdal_utm33.gdb`, `Rogaland_utm33.gdb`). Units: North-East metres, m/s, radians. |
| Outputs | List of per-scenario result dicts from `Simulator.run`; live matplotlib plots and saved figures/animations; collision / grounding termination flags; Gymnasium observations and rewards. |
| Key API / entry points | `ScenarioGenerator().generate(config_file=..., new_load_of_map_data=True)` and `.generate_configured_scenarios()`; `Simulator(config=None, config_file=dp.simulator_config, **kwargs)`, `.toggle_liveplot_visibility(bool)`, `.run(scenario_data_list, colav_systems=[(ship_id, colav)], trackers=None, terminate_on_collision_or_grounding=True) -> list[dict]`; planner interface `colav_simulator.core.colav.colav_interface.ICOLAV` with `plan(t, waypoints, speed_plan, ownship_state, do_list, enc=None, goal_state=None, w=None, **kwargs) -> np.ndarray` (9xN references), `reset()`, `get_current_plan()`, `get_colav_data()`, `plot_results(...)`; Gymnasium id `COLAVEnvironment-v0` registered on `import colav_simulator.gym`. Built-in planners: `sbmpc`, `kuwata_vo_alg`; trackers: KF, `god_tracker`, optional VIMMJIPDA. |
| Time to first result | Estimate: 30-60 min to `uv run pytest tests/test_simulator.py` passing, dominated by GDAL/seacharts install; a few hours to plug in your own planner. Assumes Linux/macOS with native GDAL available and Git LFS installed. |
| License | MIT (LICENSE, "Copyright (c) 2025 NTNU TTO"). ENC data from Kartverket/Geonorge has its own terms (not checked). |

## Minimal usage
Not run. Adapted from `examples/dummy_planner.py` (a planner that just runs the built-in LOS guidance).

```python
import colav_simulator.common.paths as dp
from colav_simulator.scenario_generator import ScenarioGenerator
from colav_simulator.simulator import Simulator
from dummy_planner import DummyPlanner, DummyPlannerParams   # examples/dummy_planner.py

scenario = ScenarioGenerator().generate(config_file=dp.scenarios / "head_on.yaml", new_load_of_map_data=True)
sim = Simulator()
sim.toggle_liveplot_visibility(True)
results = sim.run([scenario], colav_systems=[(0, DummyPlanner(DummyPlannerParams()))])
```

Or with uv from the repo root: `uv run python examples/dummy_planner.py`.

## Wiring it into a nav stack
- Planner under test: implement `ICOLAV.plan(...)`; `ownship_state` is `[x, y, psi, u, v, r]` (North, East, yaw, surge, sway, yaw rate) and `do_list` holds tracked dynamic obstacles `(id, state, covariance, length, width)`. Return 9xN references (pose, velocity, acceleration) or, with a `PassThroughInputs` controller, `[X, Y, N]` forces.
- Degraded own-ship nav: the README describes swapping estimators and sensors per ship through the `IShip` subsystem interfaces; feed a noisy or GNSS-denied own-ship estimate to test planner robustness, not just perfect state.
- Target tracking: radar sensor plus KF tracker by default; [VIMMJIPDA](../../catalog/repos/ntnu-itk-autonomous-ship-lab__vimmjipda.md) for multi-target tracking with clutter; compare with [Stone Soup](./dstl__stone-soup.md) trackers on the same scenarios.
- Coordinates: ENC and scenarios are UTM 32/33 North-East; convert to lat/lon with [pymap3d](./geospace-code__pymap3d.md) or pyproj before pushing tracks to [OpenCPN](./opencpn__opencpn.md) (RMC / AIVDM) for an operator view.
- Moving to a deployable runtime: port the planner into a [MOOS-IvP](./moos-ivp__moos-ivp.md) behaviour or an ROS node; the simulator itself has no MAVLink/ROS/MOOS bridge.
- RL: `gymnasium.make("COLAVEnvironment-v0", ...)` after `import colav_simulator.gym`; see `colav_simulator/gym` for action/observation types and `scenarios/rl_scenario*.yaml`.
- Concepts: [maritime-nav](../../catalog/concepts/maritime-nav.md), [obstacle-avoidance](../../catalog/concepts/obstacle-avoidance.md), [simulation](../../catalog/concepts/simulation.md). Catalog page: [catalog/repos/ntnu-itk-autonomous-ship-lab__colav-simulator.md](../../catalog/repos/ntnu-itk-autonomous-ship-lab__colav-simulator.md).

## Gotchas
- ENC files are Git LFS objects (`.gitattributes`: `*.gdb` and `data/enc/**`). Without `git lfs` the `.gdb` folders are pointer stubs and map loading fails.
- Python 3.12+ is excluded (`<3.12`); make sure uv resolves a 3.10/3.11 interpreter.
- GDAL is the usual install blocker (README points to OSGeo/gdal #2166, #2827 and seacharts #4). Install system GDAL first.
- Scenario generation "freezes" if `new_load_of_map_data` is False with wrong/missing map data (README). Random scenario generation is not guaranteed to succeed every time.
- Only UTM zone 32/33 Norwegian GDB charts are supported out of the box (seacharts); other regions need conversion to that format and zone.
- The matplotlib visualiser scales badly with many vessels and leaks memory (README roadmap); turn live plotting off for batch runs.
- Maintenance: classifier "Development Status :: 3 - Alpha"; last commits 2025-12-29; issues are enabled but the tracker has 0 issues, so there is no public bug history to lean on. README CI badge points at `NTNU-TTO/colav-simulator`.

## Alternatives
- [MOOS-IvP](./moos-ivp__moos-ivp.md) - C++ runtime with COLREGs behaviours that also runs on vehicles; prefer when the demo must drive hardware.
- [Aeolus Ocean](../../catalog/repos/aavek__aeolus-ocean.md) - another indexed COLAV environment; compare if you need a different scenario set or RL framing.
- [VRX](../../catalog/repos/osrf__vrx.md) - Gazebo/ROS 2 USV sim with physics and sensors; prefer for perception-in-the-loop rather than planner benchmarking.

Sources: `gh api repos/ntnu-itk-autonomous-ship-lab/colav-simulator` (MIT, no releases), PyPI JSON (404 for `colav-simulator`), README.md, LICENSE, pyproject.toml, .gitattributes, data/enc listing, scenarios listing and scenarios/head_on.yaml, colav_simulator/simulator.py (`Simulator.__init__`, `run`), colav_simulator/gym/__init__.py, colav_simulator/core and core/colav listings, examples/dummy_planner.py, tests/test_simulator.py, commit log (2025-12-29), issue search (0 results).
