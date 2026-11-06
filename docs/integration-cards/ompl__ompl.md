# OMPL - integration card
<!-- about: repo:ompl/ompl -->
Sampling-based motion planning library (RRT-Connect, RRT*, PRM, KPIECE, SST and 40+ more) with Python wheels on PyPI, so a geometric path planner over SE(2)/SE(3) with your own collision check is a few dozen lines.

| | |
|---|---|
| Install | Python: `pip install ompl` (PyPI 2.0.1, `requires-python >=3.9`; wheels for CPython 3.10-3.13 on manylinux x86_64/aarch64 and macOS 15 x86_64/arm64, per the PyPI file list). From source (README): `git submodule update --init --recursive && mkdir -p build/Release && cd build/Release && cmake ../.. && make -j <n>`; bindings from source: `pip install ./py-bindings`. Latest GitHub release 2.0.2 (2026-08-14), one patch ahead of PyPI. ROS: rosdistro lists OMPL 1.7.0 for Humble and Jazzy (not 2.x), pulled in by MoveIt. |
| Runs on | CPU only. Linux, macOS, Windows (README). Required deps: Boost >= 1.68, CMake >= 3.12, Eigen >= 3.3. VAMP SIMD collision checking is an optional dep, "enabled by default" in source builds. |
| Inputs | A state space (`ob.SE2StateSpace`, `ob.SE3StateSpace`, `ob.RealVectorStateSpace(n)`, Dubins/Reeds-Shepp, compound spaces), bounds, a state validity callback `isStateValid(state) -> bool` that you write against your map (occupancy grid, ESDF, grid_map layer), start and goal states. Control-based planning adds a control space and a state propagator. Units are whatever your callback assumes. |
| Outputs | `PathGeometric` / `PathControl` (list of states; `printAsMatrix()` text), `PlannerData` graph, benchmark logs that `ompl_benchmark_statistics` turns into an SQLite DB. |
| Key API / entry points | Python modules `from ompl import base as ob, geometric as og, control as oc`. `og.SimpleSetup(space)` with `.setStateValidityChecker(fn)`, `.setStartAndGoalStates(s, g)`, `.setPlanner(og.RRTstar(si))`, `.solve(t_sec)`, `.simplifySolution()`, `.getSolutionPath()`. Lower level: `ob.SpaceInformation`, `ob.ProblemDefinition`, `og.RRTConnect(si)`. CLI `ompl_benchmark_statistics` (`py-bindings/pyproject.toml` `[project.scripts]`). C++ demos in `demos/` (e.g. `RigidBodyPlanning`, `DubinsAirplane`, `multicopter/MulticopterPlanning.cpp`). |
| Time to first result | Estimate: 10 min with `pip install ompl` and `demos/RigidBodyPlanning.py`; 30-60 min for a C++ source build. |
| License | `LICENSE`: BSD 3-Clause (Rice University). GitHub metadata reads NOASSERTION because of the custom header text. Python package metadata declares `BSD-3-Clause`. No weights or data. |

## Minimal usage
Not run. Adapted from `demos/RigidBodyPlanning.py`.

```python
from ompl import base as ob, geometric as og

space = ob.SE2StateSpace()
b = ob.RealVectorBounds(2); b.setLow(-50); b.setHigh(50)
space.setBounds(b)

def is_valid(s):                      # plug your occupancy / ESDF lookup here
    return not (abs(s.getX()) < 5 and abs(s.getY()) < 20)

ss = og.SimpleSetup(space)
ss.setStateValidityChecker(is_valid)
start = space.allocState(); start.setX(-30); start.setY(0); start.setYaw(0)
goal = space.allocState();  goal.setX(30);  goal.setY(0);  goal.setYaw(0)
ss.setStartAndGoalStates(start, goal)
ss.setPlanner(og.RRTConnect(ss.getSpaceInformation()))
if ss.solve(1.0):
    ss.simplifySolution()
    print(ss.getSolutionPath())
```

## Wiring it into a nav stack
- Validity checker is the integration point: query a [grid_map](./anybotics__grid_map.md) layer, an [elevation_mapping_cupy](./leggedrobotics__elevation_mapping_cupy.md) traversability map, or an occupancy grid built from SLAM ([RTAB-Map](./introlab__rtabmap.md)).
- Output waypoints => [MAVROS](./mavlink__mavros.md) setpoints / MAVLink `SET_POSITION_TARGET_LOCAL_NED`, or => a Nav2 path for ground robots ([Navigation2](./ros-navigation__navigation2.md) uses its own planners, OMPL is not a Nav2 plugin out of the box).
- Arm planning in ROS 2 goes through [MoveIt 2](../../catalog/repos/moveit__moveit2.md), which wraps OMPL.
- For a fast UAV local planner instead of global sampling, see [EGO-Swarm](./zju-fast-lab__ego-planner-swarm.md).

## Gotchas
- 2.0 moved the Python bindings to nanobind. Not every 1.7 planner is bound yet: open issues #1419 ("planners exposed in 1.7.0 are missing in 2.0.0"), #1142 (no QRRT), #1088 (multilevel planning), #1087 (no ConstraintIntersection), #1482 (SST constructor missing).
- #1420: AORRTC returns a zero-length path on `RealVectorStateSpace` in the 2.0.0 Python bindings. Stick to RRTConnect/RRT*/PRM for a demo.
- Python validity callbacks run under the GIL per sample; for tight time budgets use the C++ API or VAMP.
- `py-bindings/README.md`: building bindings on ARM (Apple M-series) "can sometimes fail"; use gcc, or just use the PyPI wheel.
- ROS 2 apt OMPL is 1.7.0, so code written for 2.x Python bindings will not match the ROS-packaged library.
- It is a planner library only: no map, no controller, no ROS node.

## Alternatives
- [EGO-Swarm](./zju-fast-lab__ego-planner-swarm.md) / [EGO-Planner](../../catalog/repos/zju-fast-lab__ego-planner.md) - gradient-based local replanning for quadrotors with mapping built in.
- [TARE](./caochao39__tare_planner.md) - when the task is exploration coverage rather than start-to-goal.
- [MoveIt 2](../../catalog/repos/moveit__moveit2.md) - when you are planning for a manipulator in ROS 2.

Sources: `README.md`, `LICENSE`, `package.xml`, `py-bindings/pyproject.toml`, `py-bindings/README.md`, `demos/` listing, `demos/RigidBodyPlanning.py`, release 2.0.2, issues #860 #1087 #1088 #1142 #1419 #1420 #1482 (github.com/ompl/ompl); https://pypi.org/pypi/ompl/json; rosdistro `humble/distribution.yaml`, `jazzy/distribution.yaml`.
