# Close-area A=>B: simulators, platforms, competition formats

Lane 2 of the close-area research pass (2026-11-09). Task assumption: move a small drone
from A to B in a confined space, possibly with obstacles. Platform, sensors, indoor vs
outdoor and sim vs real are unknown until Day 1. Team laptop: Apple Silicon Mac, `uv`
and `docker` present, no numpy/pybullet in system python.

Source labels: **[code]** = read in the repo via `gh api` on 2026-11-09, **[docs]** =
vendor or project documentation, **[peer]** = peer-reviewed, **[preprint]** = arXiv,
**[rules]** = official competition rulebook, **[news]** = press or third-party tracker.
Nothing in this file was installed or run. "First flight" times are estimates, not
measurements.

## TL;DR

- **Primary lightweight sim: gym-pybullet-drones** (already in the hub,
  `repo:learnsyslab/gym-pybullet-drones`). README says tested on Apple Silicon/macOS 26.
  Has obstacles and an RGB/depth/segmentation camera out of the box, Crazyflie models,
  gymnasium API. One risk: `pybullet` has no macOS arm64 wheel, so it compiles from
  source. Fallback with zero compile: **RotorPy** (pure-Python wheel) or
  **crazyflow + lsy_drone_racing** (pure-Python wheel, MuJoCo rendering, gates and
  obstacles already modelled).
- **Product-credible sim: PX4 SITL + Gazebo Harmonic (gz)**, run natively on the Mac.
  PX4 docs say macOS setup works on Apple Silicon and CI runs on Apple Silicon only.
  Ships `x500_depth` (OAK-D Lite), `x500_lidar_2d`, `x500_lidar_front`, `x500_flow`
  models and `walls`, `forest`, `baylands` worlds. The same offboard code (MAVSDK or
  ROS 2) flies a real PX4 airframe.
- **Most likely platforms** for a 48h close-area event: Crazyflie 2.1 (Flow + Multi-ranger
  decks), DJI Tello / RoboMaster TT, or a PX4 quad (Holybro X500 class, maybe ModalAI
  VOXL 2). Write the planner against a thin "setpoint + range scan + pose" interface so
  it ports across all three.
- **What judges score** (IMAV 2026 rules are the closest public analogue): completion
  first, then onboard autonomy (off-board compute or beacons => 0.7x, any manual
  intervention => 0.4x), then risk-graded choices (smaller window, harder bar), mass,
  and a precision landing bonus.

## 1. Simulators

### 1.1 Comparison table

| Sim | Apple Silicon | Install path, size | Depth / camera / range | Spawn obstacles | Python API | License | First flight (est.) |
|---|---|---|---|---|---|---|---|
| gym-pybullet-drones | Native. README: "Tested on ... Apple Silicon/macOS 26" [code] | `pip install -e .`; pybullet built from source with `CFLAGS="-Dfdopen=fdopen"` [code]. PyPI has no macOS arm64 pybullet wheel (checked) | `getCameraImage` => rgb, depth, seg per drone [code]. Range via Bullet ray casts, write it yourself | `obstacles=True` flag, any URDF via `p.loadURDF` [code] | gymnasium envs, PID examples, SB3 RL, Betaflight SITL | MIT | 20-40 min incl. pybullet compile |
| RotorPy | Native, pure-Python wheel `rotorpy-3.0.0-py3-none-any` (PyPI) | `pip install rotorpy` (+ `[learning]`, `[px4]` extras) [code] | IMU, mocap, v3.0 pinhole camera projecting world feature points (not photoreal) [code] | World files with blocks (`rotorpy/worlds/`) [code] | Plain Python sim loop, gymnasium env, batched env | MIT | 10 min |
| crazyflow + lsy_drone_racing | Native. `crazyflow` CPU wheel is py3-none-any; GPU extra is Linux x86-64 only [code] | `pip install crazyflow`; lsy_drone_racing via pixi or pip [code] | MuJoCo render (FPV cam, track cam), raycasting via MJX [code] | Gates + pole obstacles in TOML, randomized at levels 2-3 [code] | gymnasium `DroneRacing-v0`, state or attitude control | MIT | 15-30 min |
| MuJoCo + mujoco_menagerie | Native (`mujoco` wheel on PyPI) | `pip install mujoco`; clone menagerie for `skydio_x2` and `bitcraze_crazyflie_2` models [code] | MuJoCo camera render, rangefinder sensor element (not verified for drones) | Edit MJCF XML | Low-level; you write controller and loop | Apache-2.0 engine; menagerie per-model licenses (NOASSERTION at repo level) | 1-2 h (no drone controller included) |
| Genesis (genesis-world) | Compiler targets Apple Metal and ARM64 [code] | `pip install genesis-world` | Depth camera and lidar sensor examples [code] | Python scene API | `examples/drone/` has `hover_env.py`, `fly_route.py`, `quadcopter_controller.py` [code] | Apache-2.0 | 30-60 min; young, fast-moving API |
| PX4 SITL + gz Harmonic | Native. "works on both Intel and Apple Silicon Macs", CI on Apple Silicon only [docs] | `Tools/setup/macos.sh --sim-tools`: Homebrew taps, XQuartz, gz from a locked conda-forge env via pixi. Size not measured | `x500_depth` (OakD-Lite), `x500_lidar_2d`, `x500_lidar_front`, `x500_lidar_down`, `x500_flow`, `x500_mono_cam` [code: PX4-gazebo-models] | SDF worlds `walls`, `forest`, `baylands`, `aruco`, etc. [code]; add boxes by editing SDF | MAVSDK-Python, pymavlink, ROS 2 via uXRCE-DDS | BSD-3 (PX4), Apache-2.0 (gz) | 1-2 h first build (password prompt, XQuartz may need re-login) |
| PX4 SIH headless (hub `samples/sitl-docker`) | Verified on Apple Silicon linux/arm64 docker 2026-11-06 (hub sample) | `docker compose up -d px4` | None (physics inside PX4, no world) | No | MAVSDK / pymavlink | BSD-3 | 10 min if images built |
| ArduPilot SITL + ardupilot_gazebo | SITL headless verified in hub docker. Native gz plugin on macOS: not verified | Hub docker for SITL; plugin build against gz Harmonic | gz sensors as above; ArduPilot proximity + BendyRuler/Dijkstra avoidance (docs, not re-read) | SDF worlds | pymavlink, MAVSDK, DroneKit-era scripts | GPL-3.0 (ArduPilot) | 30 min headless; gz part unknown |
| Webots | Native arm64 reported from R2023b [news: third-party trackers]; not confirmed in release notes | DMG installer, ~GB-scale | Camera, RangeFinder (depth), Lidar, DistanceSensor nodes | Drag-and-drop in GUI or `.wbt` file | Python controllers | Apache-2.0 | 30-60 min |
| crazyflie-simulation | Webots path inherits Webots; Gazebo path inherits gz | Clone repo, open world | Webots Crazyflie with range sensors used in a wall-following demo [docs] | Webots/gz worlds | Python controllers, cflib-style | MIT | 30-60 min |
| Flightmare | No. Linux + Unity renderer | ROS 1 catkin | RGB, depth, seg (Unity) | Unity scenes | Python bindings for RL | NOASSERTION | Not practical on Mac |
| AirSim / Colosseum / Project AirSim | Not practical. Unreal; AirSim wound down, Colosseum archived (hub records) | Prebuilt Linux/Windows binaries | Camera, depth, lidar | Unreal editor | Python RPC | MIT / NOASSERTION | Not on Mac |
| Isaac Sim / Pegasus / Aerial Gym | No. Linux or Windows + NVIDIA RTX | Large (tens of GB) | Full RTX sensors | USD | Python | Pegasus BSD-3, Isaac Sim NVIDIA terms | Only if a Linux GPU box is provided |
| Parrot Sphinx (+ Olympe) | No. Sphinx: Ubuntu 20.04/22.04/24.04, NVIDIA GPU (min 2 GB) [docs]. Olympe wheel is `manylinux_2_31_x86_64` only (PyPI) | apt repo, "several GBytes" per app [docs] | ANAFI camera models | Unreal-based worlds | Olympe | BSD-3 (Olympe) | Only on an x86 Linux + NVIDIA box |
| Tello sims | No official sim found. djitellopy has no simulator mode | - | - | - | - | - | Mock the UDP text protocol yourself |
| aerial-autonomy-stack | No. Needs nvidia-driver + nvidia-container-toolkit [code] | `./sim_build.sh`, first build ~45 min [code] | YOLO + 3D lidar, KISS-ICP | gz worlds | ROS 2 | MIT | Linux GPU only |

### 1.2 Recommendation

**Primary lightweight: gym-pybullet-drones.** Reasons: it is already indexed in the hub,
the maintainers claim Apple Silicon testing, it has real rigid-body collisions (so a
crash is a crash, not a silent overlap), it gives depth images for free, and its
Crazyflie models match the most likely hackathon hardware. The A* / RRT / potential-field
planner lives in plain Python next to it. If the pybullet compile fails, switch to
RotorPy (no compile) and accept a kinematic world without contact physics, or to
crazyflow + lsy_drone_racing if the task looks like gates.

**Product-credible: PX4 SITL + gz Harmonic, native on macOS.** Reasons: same autopilot,
same MAVLink / ROS 2 offboard interface and same EKF as a real X500 or VOXL 2 build; ships
depth-camera and lidar airframes and an obstacle world (`walls`); PX4 Collision
Prevention can sit under our planner as a safety layer. This is the sim a judge from an
autonomy product company recognises. Keep the hub's headless SIH docker for fast
control-loop tests when gz is not needed.

### 1.3 First-hour recipes (not run)

**A. gym-pybullet-drones with uv**

```sh
git clone https://github.com/learnsyslab/gym-pybullet-drones.git
cd gym-pybullet-drones
uv venv --python 3.12 .venv && source .venv/bin/activate
CFLAGS="-Dfdopen=fdopen" uv pip install pybullet --no-cache   # compiles; expect minutes
uv pip install -e .
cd gym_pybullet_drones/examples && python pid.py               # smoke test, GUI window
```

Then: subclass `CtrlAviary` with `obstacles=True`, add box URDFs with
`p.loadURDF("cube.urdf", ...)`, read depth from `_getDroneImages`, feed waypoints from
your planner to `DSLPIDControl.computeControlFromState`.

Fallback if the compile breaks:

```sh
uv venv --python 3.12 .venv-rp && source .venv-rp/bin/activate
uv pip install "rotorpy[all]"
python -c "import rotorpy; print(rotorpy.__file__)"   # then run examples/ from the repo
```

**B. PX4 SITL + gz Harmonic, native**

```sh
xcode-select --install
echo "ulimit -S -n 2048" >> ~/.zshrc && exec zsh          # avoids "too many open files"
git clone https://github.com/PX4/PX4-Autopilot.git && cd PX4-Autopilot
git submodule update --init --recursive --force
./Tools/setup/macos.sh --sim-tools                          # asks for password, installs XQuartz
source .venv/bin/activate                                   # every new terminal
make px4_sitl gz_x500                                       # smoke test
PX4_GZ_WORLD=walls make px4_sitl gz_x500_depth              # obstacle world + depth cam
```

Second terminal: `uv pip install mavsdk` and fly an offboard position/velocity loop; or
ROS 2 offboard with `TrajectorySetpoint` (hub: `res:px4-ros2-offboard-control`). The
`PX4_GZ_WORLD` variable and the `gz_x500_depth` target name follow the PX4 gz docs
pattern; confirm on Day 0.

Sanity note: the `--sim-tools` script trusts third-party Homebrew taps and installs
XQuartz. That is an install; get the go-ahead before running it on the team laptop.

## 2. Platform cheat table

| Platform | Obstacle sensing | Indoor localization | How you command motion | Compute | Latency notes |
|---|---|---|---|---|---|
| DJI Tello / RoboMaster TT | None forward on Tello. TT adds an expansion board with a forward ToF (not verified) | Downward VPS (optical flow + IR); mission pads on EDU/TT [docs] | UDP text SDK: `go x y z speed` (cm, +-500, 10-100 cm/s), `curve`, `rc a b c d` (-100..100, no ack) [docs]. Python: `djitellopy` | Off-board only (laptop over WiFi). 720p/480p video stream | Auto-lands after 15 s without a command [docs]. Command and video latency: no numbers found |
| Crazyflie 2.1 | Multi-ranger deck: 5 x VL53L1x, front/back/left/right/up, up to 4 m [docs] | Flow deck v2 (PMW3901 flow + VL53L1x height, fused in onboard EKF; matte floors) [docs]; Lighthouse or Loco (UWB) for absolute position | `cflib`: high-level commander `go_to` / uploaded trajectories, or streamed position/velocity setpoints over Crazyradio. Crazyswarm2 for ROS 2 | STM32 onboard estimator + controller; planning usually on laptop; AI deck (GAP8 + grey camera) for onboard CNN | Radio link round trip: not measured. 27 g class, fits a net cage |
| PX4 quad (Holybro X500 class) | What you bolt on: OAK-D depth, 2D lidar, rangefinders. PX4 Collision Prevention consumes `OBSTACLE_DISTANCE` / distance sensors [docs] | Optical flow + rangefinder, external vision (VIO / mocap) into EKF2 | Offboard mode: MAVSDK or ROS 2 `TrajectorySetpoint` at a steady rate, else PX4 falls back [docs] | Companion (Pi, Jetson) + FC | Collision Prevention only works in acceleration-based Position mode; it zeroes velocity after 0.5 s without range data and goes to Hold after 5 s [docs] |
| ModalAI VOXL 2 (PX4 onboard) | Stereo depth => `voxl-vision-hub` VOA => `OBSTACLE_DISTANCE` to PX4; ToF path is community-only [docs, forum] | VIO (QVIO / OpenVINS) on board (hub `res:px4-modalai-voxl-2-docs`) | Same PX4 offboard paths; MAVLink or ROS 2 | Onboard QRB5165, flight + companion on one SoC | VOA off by default; needs `en_voa` + DFS server + PX4 CP params [docs] |
| ArduPilot copter | Proximity sensors; built-in BendyRuler / Dijkstra object avoidance (docs, not re-read this pass) | Optical flow, external nav (`VISION_POSITION_ESTIMATE`), beacons | Guided mode: position / velocity / acceleration setpoints via pymavlink or MAVROS | Companion + FC | Hub sample `vio-to-mavlink-bridge` already feeds external nav |
| DJI consumer (MSDK v5) | Onboard APAS, limited exposure to SDK | Onboard VPS | Android app, virtual stick; advanced mode needs `setVirtualStickAdvancedModeEnabled`, then `sendVirtualStickAdvancedParam` at 5-25 Hz (forum) [docs] | Phone/tablet off-board; PSDK for enterprise payload compute | Mini 4 Pro needs the RC-N2 controller for MSDK [news]. Android-only build path costs hours |
| Parrot ANAFI (Olympe) | ANAFI Ai has stereo obstacle avoidance (not verified) | Onboard vision + GNSS | Olympe Python over WiFi: `moveBy`, `moveTo`, piloting commands | Off-board laptop; Ai supports onboard Air SDK (not verified) | Olympe only ships Linux x86-64 wheels => not on the Mac without x86 emulation |

**Design rule from this table:** every platform reduces to three ports: `pose()`,
`ranges()` or `depth()`, and `send_setpoint(pos | vel)`. Write the planner against that
interface on Day 0, back it with gym-pybullet-drones and PX4 SITL, and swap in the real
driver once the platform is known.

## 3. Competition formats and lessons

| Event | Format | What scoring rewarded | What winners used | What broke | Source |
|---|---|---|---|---|---|
| IMAV 2026 indoor | 14 x 7 x 4 m net arena; mission 1 = obstacle course: two window types, over a red bar, under two blue bars, a pipe passage | Per-mission max 20: completion up to 7, x autonomy factor (1.0 onboard, 0.7 off-board compute or beacons such as UWB, 0.4 any manual intervention), x mass factor 1.13 (3 kg) to 2.0 (0.1 kg); smaller red window 1 pt vs blue 0.5 pt; bar height choice 0.25-0.75 pt; landing on ArUco platform +1 static / +2 moving; multi-mission bonus; self-made drone bonus | - | Organisers add textured floor wallpaper "to improve navigation" => they expect optical flow to fail on plain floors | [rules] IMAV 2026 rulebook V3 |
| LSY Autonomous Drone Racing (TUM) | Crazyflie gates + obstacles; sim levels 0-3 then sim2real with Vicon | Fastest completion; competition always runs level 2 (randomized inertia and gate/obstacle positions) | Planning + replanning; exact obstacle positions only revealed within `sensor_range = 0.7` m | Controllers tuned on nominal track fail when positions shift | [code] |
| IROS Autonomous Drone Racing 2016-2018 | Indoor gate course, onboard sensing | Gates passed, then time | Modified ORB-SLAM, waypoint alignment, sensor fusion, CNN and stereo gate detection | Few full-track completions (from memory, not verified) | [peer] Moon et al. 2019 |
| AlphaPilot 2019 (Lockheed Martin / DRL) | Standard drone with Jetson Xavier, camera + IMU, gate course | Time through gates | MAVLab (winner): light onboard estimation; UZH (2nd): learned gate detection + filtering + time-optimal planning | State estimation drift at speed (hub records) | [news] MAVLab post, [preprint] UZH |
| NeurIPS 2019 Game of Drones | Sim-only (AirSim), tiers: perception, planning/control, head-to-head | Race completion and time vs an opponent | Classic planning + control stacks | 117 teams registered, 16 unique entries made it to submission | [peer] Madaan et al. PMLR 2020 |
| A2RL x DCL 2025 (Abu Dhabi) | Standardized drone, camera-only | Race time, head-to-head incl. vs humans | MAVLab won ahead of TII Racing and KAIST; one finalist on open Aerostack2 + MPCC | - | hub `res:a2rl-2025-season`, `res:cvar-upm-a2rl-team` |
| DARPA SubT (aerial part) | Underground, no GNSS, degraded comms | Artifacts reported within an error radius, not coverage | Multi-sensor odometry, heterogeneous robots | Comms loss, dust, drift | hub `res:darpa-subt-challenge`, `res:cerberus-subt-final-paper` |
| MBZIRC (maritime) | UAV + USV, GNSS-denied | Task completion | - | - | hub `repo:osrf/mbzirc` |
| Learning High-Speed Flight in the Wild | Not a competition; reference for sim-trained obstacle flight | - | Sim-trained imitation policy from depth to trajectories | Research code, Ubuntu 20.04 + ROS Noetic only | [peer] Loquercio et al. Science Robotics 2021 |

### 3.1 What this tells us a judge scores

1. **Completion beats speed.** Every format scores "reached the goal / passed the gate"
   before time. A slow, sure A=>B outranks a fast crash.
2. **Onboard autonomy is a multiplier.** IMAV discounts off-board compute and installed
   beacons to 0.7 and any human touch to 0.4. Expect a judge to ask "where does the
   planner run" and "did anyone touch the sticks".
3. **Randomized layouts are the norm.** LSY level 2 and IMAV adjustable bar heights both
   punish a hard-coded path. Show replanning on a moved obstacle.
4. **Graded risk options.** IMAV pays more for the smaller window. Expose a "safety
   margin" knob and show the trade-off.
5. **Estimation is the usual failure.** AlphaPilot, IROS ADR and SubT all broke on state
   estimation, not on the planner. Log estimator health and show what happens when flow
   or VIO degrades.
6. **Precision landing at B is cheap points.** An ArUco pad at B is an easy, visible
   "arrived" signal.

## 4. Not verified

Reconciled 2026-11-09 (loop-28): no sample installed or ran any simulator or platform SDK named
here. The hub compares planners in its own numpy arena instead
([close-area-arena](../../../samples/close-area-arena/README.md), synthetic), and the drone-adapter
drivers are unrun stubs ([drivers](../../../templates/drone-adapter/drivers/README.md)). Every
bullet below is still open.

- Install sizes and real first-flight times for every sim; none were installed.
- Whether `pybullet` compiles cleanly on the team Mac's macOS and Python 3.12.
- RotorPy obstacle collision behaviour (contact vs kinematic check).
- MuJoCo rangefinder usage on the menagerie drone models.
- Exact PX4 `PX4_GZ_WORLD` usage and the `gz_x500_depth` make target name on current
  `main`.
- ArduPilot SITL + `ardupilot_gazebo` native on macOS.
- Webots native arm64: only third-party trackers, not Cyberbotics release notes.
- RoboMaster TT forward ToF sensor; RoboMaster SDK support for TT.
- Tello command and video latency; Crazyflie radio round trip.
- ANAFI Ai obstacle avoidance and Air SDK onboard compute.
- DJI Mini 4 Pro virtual stick advanced mode support.
- IROS ADR completion statistics and AlphaPilot failure modes beyond the hub records.
- IMAV 2026 text was extracted from the PDF with a crude stream parser; numbers match
  across sections but the weight-factor formula did not extract cleanly.

## 5. Records added

- `data/repos/close-area-sims.json`: djitellopy, olympe, mujoco_menagerie,
  Mobile-SDK-Android-V5, lsy_drone_racing, crazyflow, aerial-autonomy-stack,
  genesis-world, AirSim-Drone-Racing-Lab, agile_autonomy,
  aideck-gap8-examples.
- `data/resources/close-area-sims.json`: PX4 gz worlds,
  PX4 macOS dev env, ModalAI VOA, Parrot Sphinx requirements, LSY racing docs,
  Bitcraze Multi-ranger, Bitcraze Flow deck v2, DJI MSDK virtual stick, Tello SDK 2.0,
  Moon 2019 ADR paper, Madaan 2020 Game of Drones, IMAV 2026 rulebook, Loquercio 2021,
  crazyflie-simulation docs.
