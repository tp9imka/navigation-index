# Close-area A=>B: planning and mapping for a small multirotor

Written 2026-11-09 for a close-area A=>B task ([full-brief routing](../../problem-statement-decoder.md#route-a-full-brief-to-rows-and-first-pages)). Working
assumption: "fly a drone from A to B in a close area, maybe with obstacles". Platform, sensors,
indoor or outdoor, sim or real are unknown until the task is announced.

Scope: the vehicle's own path through obstacles. No targeting, homing or intercept.

Companion to [guidance-planning.md](../../guidance-planning.md), which covers the wider GNC chain.
New records: [data/repos/close-area-planning.json](../../../data/repos/close-area-planning.json)
(15 repos), [data/resources/close-area-planning.json](../../../data/resources/close-area-planning.json)
(23 resources).

How facts were checked: licenses, languages and last-push dates come from `gh api` on 2026-11-09,
or from the LICENSE file when GitHub reports none or NOASSERTION. ROS versions come from README
text and branch lists. PyPI wheel availability comes from the PyPI JSON API. **Nothing on this page
was built or run when it was written.** Recipe 5a has since been built and run on synthetic inputs
(section 5, [close-area-arena](../../../samples/close-area-arena/README.md)); the setup times for
the external stacks below are still estimates from README build steps, not measurements.

Source labels: **[peer]** peer-reviewed, **[preprint]** arXiv only, **[code]** repository,
**[docs]** official documentation.

## 1. Recommendation in one paragraph

Build one planner in Python and run it in two harnesses. Map = dense 3D numpy occupancy grid
with three states (unknown, free, occupied), inflated by drone radius plus a tracking margin, with
`scipy.ndimage.distance_transform_edt` as the ESDF. Global = A* (26-connected, octile heuristic)
with a clearance cost from the ESDF. Smoothing = shortcut the path, then fit a min-snap trajectory
(RotorPy `MinSnap`) and check it against the ESDF. Local = replan the whole thing at 2-5 Hz
from the current state whenever new cells become occupied or the committed segment touches unknown
space. Harness (a) is RotorPy or gym-pybullet-drones. Harness (b) is the hub's headless SITL
([samples/sitl-docker](../../../samples/sitl-docker/)) with the obstacles living in the companion's
map and setpoints going out through MAVSDK Offboard (PX4) or GUIDED position targets (ArduPilot).
That stands up in hours, runs on an Apple Silicon laptop, is commercially licensable, and every
piece can later be swapped for a C++ component (OctoMap, jps3d, DecompUtil, acados) without changing
the architecture. EGO-Planner and friends are the "what good looks like" reference, not the first-day
build.

## 2. Global path options

| Method | What it gives | Good for close area? | Reference code | License | Runs without ROS | Notes |
|---|---|---|---|---|---|---|
| A* on a 3D grid | Optimal grid path; easy to add clearance cost | Yes: small volumes make 3D A* cheap | [zhm-real/PathPlanning](https://github.com/zhm-real/PathPlanning) Search_3D, [PythonRobotics](../../../catalog/repos/atsushisakai__pythonrobotics.md) | MIT / MIT | Yes (Python) | Default choice. Grid-aligned, jagged: needs shortcutting and smoothing |
| JPS (Jump Point Search) | Same optimal path as A* on uniform grids, far fewer expansions | Worth it on big 3D grids only | [jps3d](https://github.com/KumarRobotics/jps3d) | BSD-3 | Yes (plain CMake) | Last push 2021-02-18. Uniform cost only: a clearance-weighted grid breaks the pruning assumption |
| RRT / RRT* / Informed RRT* | Feasible (RRT) or asymptotically optimal (RRT*) paths in continuous space | Fine; narrow gaps are slow to find | [OMPL](../../../catalog/repos/ompl__ompl.md) (pip `ompl` 2.0.1 has macOS arm64 wheels), zhm-real rrt_3D | BSD-3 / MIT | Yes | Random output differs run to run, which hurts a demo. Narrow passages are its classic weakness |
| PRM | Roadmap built once, queried many times | Good if the map is known and static | OMPL | BSD-3 | Yes | Pre-build on the first day from a known floor plan |
| Hybrid A* | A* with continuous state per node and feasible motions | Built for curvature-limited cars; overkill for a multirotor | Nav2 Smac planner (ground) | Apache-2.0 (not checked) | No (ROS 2) | For drones the analogue is kinodynamic search |
| Kinodynamic search (motion primitives) | Dynamically feasible path directly | Only if aggressive flight is the pitch | [mpl_ros](https://github.com/sikang/mpl_ros); Fast-Planner front end | Apache-2.0 / GPL-3.0 | No (ROS 1) | Slow in Python in 3D |

Sources: [peer] Harabor and Grastien 2011 (JPS); [peer] Karaman and Frazzoli 2011 (RRT*, PRM*);
[peer] Kavraki et al. 1996 (PRM); [peer] Dolgov et al. 2010 (Hybrid A*); [peer] Liu et al. IROS 2017
(motion primitives); [code] repos above.

## 3. Local replanners and autopilot-native avoidance

"Setup" is an estimate from the README build steps. "Sensor" is what the stack expects as input.

| Stack | Method | License | ROS | Lang | Without ROS? | Map | Sensor input | Last push | Setup (est.) |
|---|---|---|---|---|---|---|---|---|---|
| [EGO-Planner](../../../catalog/repos/zju-fast-lab__ego-planner.md) | Gradient B-spline optimisation, ESDF-free (collision term from local guide paths) | GPL-3.0 | ROS 1 | C++ | No | Own local grid | Depth image or point cloud + odometry | 2025-03-08 | 1-3 h in a Noetic Docker |
| [EGO-Swarm](../../../catalog/repos/zju-fast-lab__ego-planner-swarm.md) | EGO + swarm terms | GPL-3.0 | ROS 1; `ros2_version` branch | C++ | No | Own local grid | Depth + odometry | 2025-03-08 | 1-3 h |
| [EGO-Planner-v2](../../../catalog/repos/zju-fast-lab__ego-planner-v2.md) | MINCO trajectory + gradient optimisation | GPL-3.0 | ROS 1 | C++ | No | Own local grid | Depth + odometry | 2023-10-16 | 2-4 h |
| [Fast-Planner](../../../catalog/repos/hkust-aerial-robotics__fast-planner.md) | Kinodynamic A* + B-spline optimisation on ESDF | GPL-3.0 | ROS 1 | C++ | No | ESDF (own sdf_map) | Depth + pose | 2024-10-24 | 2-4 h, NLopt friction |
| [FASTER](https://github.com/mit-acl/faster) | JPS + convex corridors + MIQP, fast plan through unknown plus safe backup in known free | BSD-3 | ROS 1 (Kinetic/Melodic) | C++ | No | Voxel map | Depth + pose | 2025-03-10 | Blocked without a Gurobi license |
| Bubble Planner | Sphere corridors from point cloud, receding horizon | No official code found | n/a | n/a | n/a | KD-tree on points | LiDAR point cloud | n/a | Not buildable from an official source |
| [GCOPTER](../../../catalog/repos/zju-fast-lab__gcopter.md) (MINCO) | Corridor + MINCO trajectory optimisation | MIT | ROS 1 | C++ | Not checked | Point cloud => corridors | Known map | 2023-10-15 | 1-2 h for the example |
| [SUPER](https://github.com/hku-mars/SUPER) | Exploratory + backup trajectory on raw point cloud | None (read-only) | ROS 1 Noetic; ROS 2 Foxy preview | C++ | No | ROG-Map | 3D LiDAR + LIO | 2025-06-04 | Half a day+; needs LiDAR for real flight |
| [IPC](https://github.com/hku-mars/IPC) | Corridor + 100 Hz linear MPC that outputs rates and thrust | None (read-only) | ROS 1 | C++ | No | Grid + corridor | LiDAR point cloud | 2024-07-19 | Half a day |
| [MADER](../../../catalog/repos/mit-acl__mader.md) / [PANTHER](../../../catalog/repos/mit-acl__panther.md) | Dynamic obstacles and multi-agent | BSD-3 | ROS 1 | C++ | No | Convex hulls of tracked obstacles | Tracked obstacles | 2022 | Skip (Gurobi, ROS 1) |
| FAST-LIO + planner | LIO odometry feeding any planner above | GPL-2.0 ([FAST_LIO](../../../catalog/repos/hku-mars__fast_lio.md)) | ROS 1; ROS2 branch | C++ | No | Point cloud | 3D LiDAR + IMU | 2026-10-25 | Only if a LiDAR is on the airframe |
| MPC with obstacle constraints | Corridor half-planes or ESDF distance as constraints | acados BSD-2, OSQP Apache-2.0 | Any | C / Python | Yes | Corridor or ESDF | Any | n/a | 4-8 h to write well |
| APF (potential fields) | Attractive goal + repulsive obstacles, follow gradient | Write it | Any | Any | Yes | ESDF or range rays | Range / depth | n/a | 1 h |
| VFH+ | Polar histogram of obstacle density, pick free sector near goal heading | Write it | Any | Any | Yes | None (range histogram) | 2D range scan | n/a | 2 h |
| PX4 Collision Prevention | Velocity limit toward obstacles, can bend direction up to `CP_GUIDE_ANG` | BSD-3 (in PX4) | n/a | n/a | Yes | None | Distance sensors or `OBSTACLE_DISTANCE` MAVLink | n/a | Params only |
| PX4 obstacle avoidance ([PX4-Avoidance](../../../catalog/repos/px4__px4-avoidance.md)) | Old companion planner + path-planning interface | BSD-3 | ROS 1 | C++ | No | Point cloud | Depth | Archived | Do not use: interface removed from PX4 |
| ArduPilot BendyRuler | Probes bearings ahead against an object database; type 2 also searches vertically | GPL-3.0 (in ArduPilot) | n/a | n/a | Yes | Object DB from proximity + fences | Proximity sensors, fences | n/a | Params only |
| ArduPilot Dijkstra's | Shortest path around fence polygons and stay-out zones | GPL-3.0 (in ArduPilot) | n/a | n/a | Yes | Polygon fences | None (no sensed obstacles) | n/a | Params + fence upload |

Autopilot-native details, from [docs]:

- PX4 Collision Prevention only works in acceleration-based Position mode. It blocks motion
  into directions with no sensor data by default (`CP_GO_NO_DATA` = 0). Missing range data for
  0.5 s zeroes xy motion; after 5 s the vehicle goes to Hold. It never plans a route.
- PX4's companion obstacle-avoidance interface (`COM_OBS_AVOID`, trajectory waypoint messages)
  is marked removed on the main docs and unsupported on v1.16. A companion planner now talks to
  PX4 through Offboard mode or ROS 2 external modes.
- ArduPilot BendyRuler and Dijkstra's run in Auto, Guided and RTL (Dijkstra's in Guided needs
  `GUID_OPTIONS` bit 6). BendyRuler handles sensed obstacles; Dijkstra's handles only fences and
  stay-out zones. A combined mode exists.

Practical reading: ArduPilot gives a team onboard avoidance with zero companion code, which is a
good fallback layer under a companion planner. PX4 gives only a stop-before-wall layer.

Sources: [peer] Zhou et al. Science Robotics 2022 (EGO-Planner-v2); [peer] Tordesillas et al.
T-RO 2022 (FASTER); [preprint] Ren et al. 2022 (Bubble Planner); [peer] Ren et al. Science
Robotics 2025 (SUPER); [peer] Liu, Ren, Zhang RA-L 2024 (IPC); [peer] Liu et al. RA-L 2017
(safe flight corridors); [peer] Khatib 1986 (APF); [peer] Ulrich and Borenstein 1998 (VFH+);
[docs] PX4 Collision Prevention, PX4 Path Planning Interface, ArduPilot BendyRuler, ArduPilot
Dijkstra's; [code] repos linked above.

## 4. Mapping

| Map | Representation | ESDF? | Unknown space | CPU laptop (Apple Silicon) | Needs GPU | ROS | License | Last push |
|---|---|---|---|---|---|---|---|---|
| numpy grid + `scipy.ndimage.distance_transform_edt` | Dense 3D array | Yes, full recompute | If you add a third state | Yes | No | None | BSD (scipy) | n/a |
| [OctoMap](https://github.com/OctoMap/octomap) | Probabilistic octree | Via bundled dynamicEDT3D | Yes (explicit) | Yes; `octomap-python` has macOS arm64 wheels | No | ROS 2 server in `octomap_mapping` (ros2 branch) | BSD (library) | 2026-09-26 |
| [voxblox](https://github.com/ethz-asl/voxblox) | TSDF => ESDF voxels | Yes, incremental | Partial (unobserved voxels) | Yes in Docker; native mac build not attempted | No | ROS 1 | BSD-3 | 2024-07-01 |
| nvblox ([isaac_ros_nvblox](../../../catalog/repos/nvidia-isaac-ros__isaac_ros_nvblox.md)) | TSDF => ESDF on GPU | Yes | Partial | No | Yes, CUDA (Jetson or NVIDIA dGPU) | ROS 2 (Isaac ROS) | Apache-2.0 | 2026-09-22 |
| [UFOMap](https://github.com/UnknownFreeOccupied/ufomap) | Octree with explicit unknown indexing | No (build one) | Yes, first-class | Yes | No | ROS 1 wrapper | BSD-2 | 2025-06-27 |
| [wavemap](https://github.com/ethz-asl/wavemap) | Wavelet-compressed multi-resolution octree | No | Yes | Yes (tested on ARM CPUs per README) | No | ROS 1; ROS 2 on unmerged branch | BSD-3 | 2024-12-30 |
| [Bonxai](https://github.com/facontidavide/Bonxai) | Sparse hierarchical voxel grid | No | Via occupancy layer | Yes | No | None required | MPL-2.0 | 2026-09-29 |
| [ROG-Map](https://github.com/hku-mars/ROG-Map) | Robocentric sliding occupancy grid with inflation | No | Yes | Linux + ROS 1 | No | ROS 1 | GPL-3.0 | 2025-03-13 |

Laptop sizing (arithmetic, not measured): a 20 m x 20 m x 5 m volume at 0.1 m is 200 x 200 x 50
= 2 million cells. As uint8 that is 2 MB; a float32 ESDF is 8 MB. A full scipy EDT on that size
is a sub-second operation on a laptop CPU in typical use, which is fast enough to recompute at a
few Hz. Measured since: 182.95 ms median over 7 calls on 200 x 200 x 50 cells, 5 % random
occupancy, Apple M3 Max (synthetic grid, laptop timing;
[arena results](../../../samples/close-area-arena/README.md#results-ran-2026-11-09-apple-m3-max-cpython-31210-numpy-254-scipy-1181)).
Re-time it on the machine you will fly from.

GPU summary: only nvblox needs CUDA. Everything else on this table runs on an Apple Silicon CPU,
either natively (numpy/scipy, octomap-python) or inside a Linux Docker image (voxblox, UFOMap,
wavemap, ROG-Map). If the actual platform carries a Jetson and a depth camera, nvblox is the
natural map on the vehicle.

Sources: [peer] Hornung et al. 2013 (OctoMap); [preprint, published IROS 2017] Oleynikova et al.
(voxblox); [preprint] Millane et al. 2023 (nvblox); [peer] Duberg and Jensfelt RA-L 2020 (UFOMap);
[peer] Reijgwart et al. RSS 2023 (wavemap); [preprint] ROG-Map arXiv 2302.14819; [code] repos.

## 5. Fastest credible baseline

**Built and measured since this was written (2026-11-09, synthetic only).** Recipe 5a exists as
[close-area-arena](../../../samples/close-area-arena/README.md) (2.5D, plus a 3D `window_bar`
family). Its baseline comparison (step 9) grew into
[close-area-benchmark](../../../samples/close-area-benchmark/README.md): 14 planners x 8 room
families x 2 range sensors, 20 layouts per cell. With a prior map, A* reached 100 % with 0 %
collisions in every family on both sensors. Without a map, A* on a grid built from range returns
(step 5) reached 55-100 % with 72 beams, but only 0-35 % in office, warehouse and glass_office
with 4 Crazyflie-like beams. APF and the other reactive planners reached 0-40 % in office,
warehouse and maze with 72 beams. Pick from the benchmark first
([cheat sheet section 3](../../cheatsheets/close-area-a-to-b.md#3-which-planner-first)); the
innovation decision is in the [research README](../README.md#decision-2026-11-09-evening-what-the-close-area-innovation-claim-is).
Min-snap (step 6) and RotorPy or gym-pybullet-drones (step 8) were not used: the arena flies a
carrot follower (or the corridor MPC) on a point mass.

### 5a. Pure-Python sim (target: flying A=>B through obstacles by hour 4-6)

1. World: boxes and cylinders in a config file. Rasterise into a 3D occupancy grid at 0.1-0.2 m.
2. Sensor model: raycast a fake depth or range fan from the current pose into the true world,
   write hits as occupied and rays as free. Everything else starts unknown. This makes the
   "unknown space" failure mode visible from the start.
3. Inflate occupied cells by drone radius + tracking margin (start at radius + 0.2 m, then set
   the margin from measured tracking error, section 6).
4. ESDF: `scipy.ndimage.distance_transform_edt` on the free mask.
5. Global: A* over known-free plus unknown cells (unknown at a cost penalty), clearance cost
   `w / max(d, eps)` from the ESDF. Shortcut with line-of-sight checks.
6. Trajectory: RotorPy `MinSnap` through the shortcut waypoints. Check samples against the ESDF;
   if a sample violates clearance, insert a midpoint waypoint and refit (classic Richter-Bry-Roy
   fix).
7. Replan loop at 2-5 Hz: replan when the committed segment hits new occupied cells or enters
   unknown space within the stopping distance. Keep a stop trajectory available at all times
   (FASTER and SUPER idea, simplified to "brake to hover along the current path").
8. Sim: [RotorPy](../../../catalog/repos/spencerfolk__rotorpy.md) (MIT, includes the
   trajectory and controller) or [gym-pybullet-drones](../../../catalog/repos/learnsyslab__gym-pybullet-drones.md)
   (MIT, PyBullet collision checks). Both pip-install.
9. Baselines for the comparison table: straight line, APF, and the A*+min-snap planner.
   An APF stuck in a U-shaped trap is a cheap, convincing slide.

Why this one: no ROS, no C++ build, MIT/BSD dependencies, and every step maps to a C++
equivalent (OctoMap, jps3d, DecompUtil/GCOPTER, acados) for the product story.

### 5b. PX4 / ArduPilot SITL (target: same planner flying the SITL vehicle by hour 8-12)

1. Start the hub's headless SITL ([samples/sitl-docker](../../../samples/sitl-docker/): ArduCopter
   4.6.3 and PX4 v1.17.0 SIH, verified on Apple Silicon per that README). No Gazebo, so no
   simulated depth camera.
2. Keep the obstacle world in the companion. Raycast the fake sensor from the SITL-reported
   pose (LOCAL_POSITION_NED) exactly as in 5a. The planner code does not change.
3. Output:
   - PX4: MAVSDK Offboard position or velocity setpoints at 10-20 Hz from the trajectory. Keep
     the setpoint stream alive or PX4 drops out of Offboard.
   - ArduPilot: GUIDED mode `SET_POSITION_TARGET_LOCAL_NED` with position + velocity.
4. Safety layer on ArduPilot: enter known static obstacles as stay-out polygons and set
   `OA_TYPE` to Dijkstra's or BendyRuler. If the companion plan fails, the autopilot still
   avoids the fence-defined obstacles. Not tested in this hub.
5. Log planned vs flown path and minimum ESDF distance along the flown path. That one plot is
   the core evidence for reviewers.

If the actual platform runs ROS 1 with a depth camera and the team has a Linux box, EGO-Swarm
in its bundled simulator is the fastest way to show a state-of-the-art local planner. Its GPL-3.0
license is fine for the demo; say so in the pitch.

## 6. Failure modes and what to do about each

| Failure | Why it happens | What to do in 48h | Source |
|---|---|---|---|
| Narrow gaps not found | Inflation closes the gap on the grid; RRT samples miss it; APF repulsion from both walls cancels the goal pull | Grid resolution at most half the gap clearance; inflate by radius + measured margin, not a guess; show the minimum passable gap in the results | [peer] Koren and Borenstein 1991; [peer] Karaman and Frazzoli 2011 |
| Dead ends / local minima | Reactive methods (APF, VFH+, BendyRuler, gradient-only local optimisers) only see locally | Always keep a global search (A*) in the loop; local optimiser starts from the global path, not from the straight line | [peer] Koren and Borenstein 1991; [docs] ArduPilot BendyRuler |
| Unknown space treated as free | Map initialised as free, or collision checks only test "occupied" | Three-state map; commit only to segments with a stop inside known free space; cost penalty on unknown in the global search | [peer] Tordesillas et al. 2022; [peer] Ren et al. 2025; [peer] Duberg and Jensfelt 2020 |
| Dynamic obstacles | Static maps keep stale occupied cells or miss movers between scans | For 48h: replan fast, decay occupancy (log-odds clamping or expiry, like ArduPilot `OA_DB_EXPIRE`); full dynamic planning (MADER/PANTHER) is out of reach. **Refuted since for "replan fast" (synthetic):** A* replanning at 5 Hz hit walking people in 12 / 36 % of runs (0.5 / 1.0 m/s) vs 14 / 36 % at 2.5 Hz; a PX4-CBF-style range filter under A* gave 0 %, at 16 % stuck ([close-area-moving-obstacles](../../../samples/close-area-moving-obstacles/README.md#results-ran-2026-11-09-apple-m3-max-cpython-31210-numpy-254-scipy-1181)) | [peer] Hornung et al. 2013; [peer] Liu, Ren, Zhang 2024; [docs] ArduPilot BendyRuler |
| Tracking error larger than planned margin | Plan is feasible on paper, controller lags or overshoots in turns, wind or ground effect | Measure max cross-track error in sim on the actual trajectory profile; set inflation = radius + that error + sensor noise; cap speed and jerk near obstacles | [peer] Liu, Ren, Zhang 2024 (motivation for integrated MPC) |
| PX4 Collision Prevention freezing the vehicle | No sensor data in a direction => motion blocked; data gap => Hold | Do not combine it with an Offboard planner unless sensor coverage is full | [docs] PX4 Collision Prevention |
| Corner cutting by smoothing | Min-snap through waypoints bulges outside the safe path | Check trajectory samples against the ESDF; insert waypoints or use corridor constraints | [peer] Liu et al. RA-L 2017 |

## 7. Not verified

Reconciled 2026-11-09 against the samples that ran after this page was written. Still open:

- The external stacks in sections 2-4 (EGO-Planner, FASTER, OctoMap, voxblox and the rest) were
  not built or run. Their setup times are estimates from README steps.
- Min-snap smoothing (5a step 6) and RotorPy / gym-pybullet-drones (5a step 8) were not used:
  the arena flies a carrot follower or a corridor MPC on a point mass (section 5).
- Bubble Planner: no official code found. The third-party Robot-Nav/Bubble-Planner repo was
  seen in search but not inspected. The IROS 2022 venue is from the authors, not checked.
- IPC and SUPER have no LICENSE file per `gh api`. Code there is all rights reserved by default.
- OctoMap: only the octomap library's BSD license was read. octovis and dynamicEDT3D license
  files were not opened.
- OMPL macOS arm64 wheels and octomap-python wheels were seen on PyPI, not installed.
- ArduPilot BendyRuler/Dijkstra's behaviour in SITL with fence-defined obstacles is from docs,
  not tested. The docs page does not mention SITL.
- PX4: the docs mark the path-planning interface removed; whether every trace is gone from
  v1.17.0 source was not checked.
- FASTER's need for Gurobi is from its README. Whether an open solver fork exists was not checked.
- python_motion_planning 3D support was not checked.

### Verified since

All synthetic (2.5D or 3D point-mass arena), not SITL or flight.

- Recipe 5a (grid, ESDF, A* with clearance cost, shortcut, 2-5 Hz replan) was built and run: A*
  with a known map reached 100 % on random, u_trap and narrow_gap (50 layouts each, seed 0)
  ([arena A* + ESDF](../../../samples/close-area-arena/README.md#a--esdf-grid-planner-ran-2026-11-09-synthetic)).
  Arena venv setup took 16.5 s wall
  ([readiness](../../../samples/close-area-arena/README.md#readiness-measured-2026-11-09-apple-m3-max-macos-2662-arm64)).
- Sub-second scipy EDT on 2 million cells: 182.95 ms median (min 178.42, max 188.0 ms, 7 calls),
  Apple M3 Max, synthetic 5 % occupancy grid, laptop timing
  ([arena results](../../../samples/close-area-arena/README.md#results-ran-2026-11-09-apple-m3-max-cpython-31210-numpy-254-scipy-1181)).

## 8. Sources

| Label | Source |
|---|---|
| [peer] | Hornung et al., "OctoMap", Autonomous Robots 2013, doi 10.1007/s10514-012-9321-0 |
| [preprint] (IROS 2017) | Oleynikova et al., "Voxblox", arXiv 1611.03631 |
| [peer] | Duberg and Jensfelt, "UFOMap", RA-L 2020, arXiv 2003.04749 |
| [peer] | Reijgwart et al., wavemap, RSS 2023, doi 10.15607/RSS.2023.XIX.065 |
| [preprint] | Millane et al., "nvblox", arXiv 2311.00626 |
| [peer] | Tordesillas et al., "FASTER", T-RO, doi 10.1109/TRO.2021.3100142 |
| [preprint] | Ren et al., "Bubble Planner", arXiv 2202.12177 |
| [peer] | Liu, Ren, Zhang, IPC, RA-L, doi 10.1109/LRA.2023.3311358 |
| [peer] | Ren et al., "Safety-assured high-speed navigation for MAVs", Science Robotics 2025, doi 10.1126/scirobotics.ado6187 |
| [peer] | Zhou et al., "Swarm of micro flying robots in the wild", Science Robotics 2022, doi 10.1126/scirobotics.abm5954 |
| [peer] | Liu et al., safe flight corridors, RA-L 2017, doi 10.1109/LRA.2017.2663526 |
| [peer] | Liu et al., search-based planning with LQMT, IROS 2017, doi 10.1109/IROS.2017.8206119 |
| [peer] | Harabor and Grastien, JPS, AAAI 2011, doi 10.1609/aaai.v25i1.7994 |
| [peer] | Karaman and Frazzoli, RRT*/PRM*, IJRR 2011, arXiv 1105.1186 |
| [peer] | Kavraki et al., PRM, IEEE T-RA 1996, doi 10.1109/70.508439 |
| [peer] | Dolgov et al., Hybrid A*, IJRR 2010, doi 10.1177/0278364909359210 |
| [peer] | Khatib, potential fields, IJRR 1986, doi 10.1177/027836498600500106 |
| [peer] | Koren and Borenstein, potential field limitations, ICRA 1991, doi 10.1109/ROBOT.1991.131810 |
| [peer] | Ulrich and Borenstein, VFH+, ICRA 1998, doi 10.1109/ROBOT.1998.677362 |
| [docs] | PX4 Collision Prevention: https://docs.px4.io/main/en/computer_vision/collision_prevention.html |
| [docs] | PX4 Path Planning Interface (removed): https://docs.px4.io/main/en/computer_vision/path_planning_interface |
| [docs] | ArduPilot BendyRuler: https://ardupilot.org/copter/docs/common-oa-bendyruler.html |
| [docs] | ArduPilot Dijkstra's: https://ardupilot.org/copter/docs/common-oa-dijkstras.html |
| [code] | All GitHub repos linked in sections 2-4; metadata from `gh api` 2026-11-09 |
