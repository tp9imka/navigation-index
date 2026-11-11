# First-day intake: close-area A=>B, answers => stack

**Next action when the task arrives:** ask questions 1-3 of [section 1](#1-questions-in-the-order-to-ask), then
open [section 2](#2-if-you-only-get-3-answers) for the stack. The rest of the page refines it.

Use this page in the first 20 minutes after the brief arrives, when the task is "fly a drone from
A to B in a close area, potentially with obstacles" (decoder rows 31, 32, 33 in
[problem-statement-decoder.md](problem-statement-decoder.md)). It routes each answer from whoever set
the task to an adapter driver, a sim, samples and docs. It does not repeat the research; it points into
[research/close-area-nav](research/close-area-nav/README.md).

Status, 2026-11-09: this page is a routing table, not a measured result. Nothing on it was run
for this page. Numbers are quoted from the hub files they link to, with the input type of each.
"Estimate" means a setup time read from READMEs, not timed. "gap:" marks what the hub does not
have yet. Gap notes refreshed 2026-11-09 after the safety-filter kill test (held-out verdict
FAIL), relocalization, moving obstacles, sensor presets, complex arenas and the flight-repo first
flight landed; refreshed again later that day after the planner benchmark, the 3D window_bar family, the
relocalization held-out runs and the first cold-start run ([cold-start drill](cold-start-drill.md#blockers)).
The Q5 and Q7 defaults were changed in that refresh so that together they lead to a stack the hub has
measured (see [why these defaults](#why-these-defaults)).

## 0. The 20-minute clock

| Clock | Who | Do | Output |
|---|---|---|---|
| 0:00-0:05 | Lead | Ask Q1-Q3. Write the answers in the [intake card](#6-intake-card). | 3 answers |
| 0:05-0:10 | Lead | Ask Q4-Q10. "Don't know yet" is an answer: take the default in the card. | 10 answers or defaults |
| 0:05-0:10 | Platform | Run the two smoke tests in [section 2](#2-if-you-only-get-3-answers) on the team laptop. | Both green or a named failure |
| 0:10-0:15 | Lead + Nav | Walk [section 3](#3-decision-tree) branch by branch. Circle one path per question. | Stack, driver, sim, first sample |
| 0:15-0:20 | Lead | Read [section 4](#4-scoring-rule-implications) for the stated scoring. Write ADR-001 ([adr](../templates/adr.md)). Hand over to the [first-three-hours guide](first-three-hours.md) at its 0:25 row. | ADR-001 |

## 1. Questions, in the order to ask

Q1-Q3 decide most of the stack. Q4 decides what to optimise. Ask them first even if time runs out.

| # | Ask whoever set the task | Why it is this early | Default if no answer |
|---|---|---|---|
| Q1 | Which drone, and which autopilot or SDK do we command it through (PX4, ArduPilot, Crazyflie cflib, Tello SDK, DJI MSDK, other)? | Picks the adapter driver, the sim and the keep-alive rules | PX4-class quad over MAVSDK; write against the [adapter](../templates/drone-adapter/README.md) so it ports |
| Q2 | Is the judged run in sim, on a real drone, or both? If real: how many flight slots, when, with a net or a safety pilot? If sim: do you provide the sim and world? | Sim-only lets us skip hardware work; real flight makes estimation and safety the main risk | Both: sim first, real port in the last 24 h |
| Q3 | How is B given: offset from A, coordinates in a venue frame (mocap / UWB), a GPS point, or a marker / pad / object we must find? What tolerance counts as "at B"? | Picks the goal pipeline and the localization source | Offset from A in metres, tolerance unknown => assume 0.3 m, as the [arena](../samples/close-area-arena/README.md) scorer does |
| Q4 | How is it scored: completion, time, collisions, manual interventions, off-board compute, precision at B, number of attempts? | Decides speed vs safety, see [section 4](#4-scoring-rule-implications) | IMAV-like: completion first, interventions and off-board compute multiply the score down |
| Q5 | Which sensors does the airframe carry: stereo / depth camera, 2D or 3D lidar, ToF rangers, optical flow, downward rangefinder, GNSS, RTK? | Decides obstacle sensing and the backup velocity source | 4-beam ToF range fan (Crazyflie Multi-ranger class) + downward flow + rangefinder |
| Q6 | Indoor or outdoor? Does the venue have mocap, Lighthouse or UWB anchors we may use? | Mocap ends the localization problem; outdoor brings GNSS | Indoor, no venue positioning |
| Q7 | Are obstacles known in advance (map or layout file), unknown, or moved between runs? Any thin poles, nets or glass? | Known map => plan once; unknown => sensed map and replanning | Unknown and moved between runs, no floor plan given (ask for one: see [why](#why-these-defaults)) |
| Q8 | Where may our code run: an onboard companion (which board), a ground laptop over a link, or a provided Linux / GPU box? | Picks VIO and mapping options; off-board may cost score | Ground laptop only |
| Q9 | May we add things: AprilTags at A and B, extra sensors, firmware or parameter changes? | A tag at A fixes the frame; a tag at B is a precise goal | Tags allowed, firmware locked |
| Q10 | What is handed in and judged: live runs, video, code, a slide deck? How many runs count? | Sets how much goes into reliability vs demo polish | Live run plus deck, best of 2 runs |

### Why these defaults

The old pair (Q5 "no obstacle sensor" + Q7 "unknown and moved") was the hard gate in
[3.4](#34-q5-and-q6-sensors-and-venue-localization): no planner can avoid obstacles it cannot
sense or look up, and no benchmark row covers it ([cold-start drill blocker 5](cold-start-drill.md#blockers)).
The new Q5 default is the cheapest obstacle sensor a small indoor drone usually carries, and the
arena's `crazyflie` preset models it, so every number below has a measured row. With it, the
defaults lead to a working stack: **`astar_unknown` + F2 range filter** from
[close-area-benchmark](../samples/close-area-benchmark/README.md#results-ran-2026-11-09-synthetic)
(4-beam preset, 20 layouts, seed 0, true pose, synthetic): random 100 / 0, u_trap 100 / 0,
office 50 / 5, maze 55 / 0 reached / collision %. It does not work in warehouses (0 %) or glass
rooms (5 % reached, 45 % collision), so ask for a floor plan as part of Q7: with a prior map,
`astar_known` reached 100 % with 0 % collisions in every family on both sensors. If Q5 turns out
to be "no obstacle sensor" after all, the gate in 3.4 still applies.

## 2. If you only get 3 answers

Run these two smoke tests while the Lead asks (synthetic input; about 2 s each once warm on the
laptop that produced the quoted results). The first run on a fresh venv can take minutes of
waiting: 75.69 s wall for 1.78 s CPU in the [dry run](cold-start-drill.md#4-smoke-tests-and-sample-venv-0-extra-hops-commands-are-in-intake-section-2),
205.89 s for a cold `make first-flight`
([flight-repo](../templates/flight-repo/README.md#brief-to-first-flight)). Run long commands with
stdin closed (`< /dev/null`) or in the background so an agent shell does not hang:

```sh
(cd templates/drone-adapter && python3 -m unittest -v && python3 example_loop.py)
# expect: 10 tests OK (5 adapter + 5 driver smoke); goal=(5.0, 3.0, 1.0) final_distance_m=0.096 collided=False
(cd samples/close-area-arena && uv venv .venv && uv pip install --python .venv -r requirements.txt \
  && .venv/bin/python run.py --planner straight --layouts 20 --seed 0 --out /tmp/arena < /dev/null)
# expect: straight baseline reached 40 %, collision 0 %, stuck 60 %
```

Keep `--out /tmp/arena`: without it the run overwrites the sample's committed
`results/straight_random_0.*`.

Both numbers are synthetic, from [drone-adapter results](../templates/drone-adapter/results/2026-11-09-mock-run.txt),
[driver smoke run](../templates/drone-adapter/drivers/results/2026-11-09-smoke-run.txt)
and [straight_random_0.md](../samples/close-area-arena/results/straight_random_0.md).

Then pick one cell per row. Everything not asked takes the default in [section 1](#1-questions-in-the-order-to-ask).

| Q1 drone + SDK | Driver to write | Light sim (planner work) | Product sim (credibility) |
|---|---|---|---|
| PX4 quad (X500, VOXL 2, other PX4) | [`drivers/px4_mavsdk.py`](../templates/drone-adapter/drivers/README.md) (stub, unrun), rules in [frames.md PX4](../templates/drone-adapter/frames.md#px4) | [close-area-arena](../samples/close-area-arena/) | [sitl-docker](../samples/sitl-docker/) PX4 SIH (ran, headless, no obstacles); PX4 SITL + gz `walls` world (not run) |
| ArduPilot copter | [`drivers/ardupilot_pymavlink.py`](../templates/drone-adapter/drivers/README.md) (stub, unrun), [frames.md ArduPilot](../templates/drone-adapter/frames.md#ardupilot) | close-area-arena | [sitl-docker](../samples/sitl-docker/) ArduCopter 4.6.3 (ran, headless) |
| Crazyflie | [`drivers/crazyflie_cflib.py`](../templates/drone-adapter/drivers/README.md) (stub, unrun), [frames.md Crazyflie](../templates/drone-adapter/frames.md#crazyflie) | close-area-arena | [crazyflie-simulation](../catalog/repos/bitcraze__crazyflie-simulation.md) or [gym-pybullet-drones](integration-cards/learnsyslab__gym-pybullet-drones.md) (both not run) |
| Tello / RoboMaster TT | [`drivers/tello_djitellopy.py`](../templates/drone-adapter/drivers/README.md) (stub, unrun), [frames.md Tello](../templates/drone-adapter/frames.md#tello) | close-area-arena | gap: no Tello sim exists; `MockAdapter` in [drone-adapter](../templates/drone-adapter/) stands in |
| Anything else | gap: no driver; see [3.1](#31-q1-drone-and-sdk) | close-area-arena | ask for the vendor sim |

| Q2 sim or real | Do |
|---|---|
| Sim only | Planner + safety filter in close-area-arena, repeat the best arm in SITL. Real-flight items in [frames.md](../templates/drone-adapter/frames.md) marked "not confirmed" do not matter |
| Real only | Driver first, bench-test the "not confirmed" sign and unit items in frames.md before the first flight. Planner still developed in the arena |
| Both | Arena by hour 6, SITL by hour 12 (targets from [01 section 5](research/close-area-nav/01-planning-and-mapping.md#5-fastest-credible-baseline)), real port after that |

| Q3 how B is given | Goal pipeline | Decoder row |
|---|---|---|
| Offset from A | Odometry started at A; origin = pose at A (driver stores it) | 31 |
| Venue-frame coordinates | Use the venue system ([vrpn_mocap](../catalog/repos/alvinsunyixiao__vrpn_mocap.md)) or an AprilTag at A to align | 31, 33 |
| GPS point | GNSS to get close, marker for the last metres ([03 section 5b](research/close-area-nav/03-close-area-localization.md#b-outdoor-gnss-available)) | 31, 32 |
| Marker / pad / object | Bring it into view, then fiducial or detector as the goal | 32 |

Fast-path stack in one line: **planner against `pose()` / `ranges()` / `send_setpoint()`, picked
from the [close-area-benchmark](../samples/close-area-benchmark/README.md) row for the room and
sensor (`astar_known` with a map; `astar_unknown`, plus F2 on a 4-beam fan, without), developed in
close-area-arena, ported through the Q1 driver, with the Q3 goal pipeline.** For the innovation
story, pitch the measured toolkit plus the narrow claim that fits the brief
([decision](research/README.md#decision-2026-11-09-evening-what-the-close-area-innovation-claim-is)):
relocalization after VIO loss in an open room with a dense sensor
([close-area-relocalize](../samples/close-area-relocalize/README.md)), or the range filter when
people move. The integrity-aware safety filter failed its held-out kill test
([Part e](../samples/close-area-safety-filter/README.md#part-e-held-out-seeds-and-families-ran-2026-11-09-synthetic)).

### Answers that map to a tool

Added 2026-11-10. All tools run on synthetic input; the full flow is in the
[cheat sheet](cheatsheets/close-area-a-to-b.md#first-day-flow-with-the-browser-tools).

| Answer | Tool | First command or click |
|---|---|---|
| Q7: "here is the floor plan" (image, PDF screenshot, whiteboard photo) | [world_from_image.py](../samples/close-area-arena/README.md#your-room-in-the-arena-ran-2026-11-10-synthetic) | `world_from_image.py <plan>.png --ref X1 Y1 X2 Y2 D --a-m X Y --b-m X Y -o room.world.json --preview room.png`; a measured room without a drawing: `world_from_room.py <room>.json` |
| Q1 / Q5: drone size, top speed, sensor specs | Solver **Your drone** panel ([site/solver](../site/solver/README.md)) | Set radius, v_max, a_max and a sensor preset or Custom (beams, FoV, range), then **Quick**; **Recommend** gives the flight-repo command |
| Q7: "people walk through" | VO gate in [close-area-moving-obstacles](../samples/close-area-moving-obstacles/README.md#prediction-arms-constant-velocity-tracks-space-time-a-vo-gate-ran-2026-11-10) | `run_predict.py --layouts 50 --seeds 0,1 --workers 14`. A* + VO gate reached B in 100 of 100 held-out runs with 0 collisions vs 92 % for A* + F2; the sim people walk straight lines |
| Q3: "B is a marker" and its position is not given | [close-area-explore](../samples/close-area-explore/README.md) to find it, then [fiducial-goal-apriltag](../samples/fiducial-goal-apriltag/README.md) for the last metres | `bench.py --layouts 20 --seed 0 --jobs 14`. With B unknown nearest-frontier found it in 43.3 % [31.6, 55.9]; with a nominal within 2 m every arm found it in 88.3-100 %. Ask for a nominal B |
| Any answer, before tuning | Scenario pack in [close-area-benchmark](../samples/close-area-benchmark/README.md#scenario-packs) | `pack.py run packs/<name>.json`: our room + our drone + the bar, re-run after each change |

## 3. Decision tree

Each leaf names the hub paths to open. Status words come from
[samples/README.md](../samples/README.md): `ran`, `partial`, `sketch`.

### 3.1 Q1: drone and SDK

- **PX4 quad** (Holybro X500 class, ModalAI VOXL 2, any PX4 airframe)
  - Driver: `drivers/px4_mavsdk.py` (`Px4MavsdkAdapter`, unrun stub written from docs; see
    [drivers README](../templates/drone-adapter/drivers/README.md) for the 3 bench checks before any planner flight).
    Convert ENU => NED with `adapter.enu_to_ned`; `VelocityNedYaw` takes an absolute heading in
    degrees, not a yaw rate ([frames.md PX4](../templates/drone-adapter/frames.md#px4)).
  - Keep-alive: at least 2 Hz setpoints before and during Offboard ([frames.md](../templates/drone-adapter/frames.md#px4), docs).
  - Avoidance: PX4 does not plan around obstacles any more. Collision Prevention only stops, only
    in Position mode, zeroes xy motion after 0.5 s without range data and goes to Hold after 5 s
    ([01 section 3](research/close-area-nav/01-planning-and-mapping.md#3-local-replanners-and-autopilot-native-avoidance), docs).
    Do not combine it with an Offboard planner.
  - Sims: [sitl-docker](../samples/sitl-docker/) PX4 v1.17.0 SIH (`ran`, headless, about 10 min if
    images are built, estimate from doc 02). PX4 SITL + gz Harmonic `x500_depth` in `walls`
    (not run; first build 1-2 h estimate; the setup script installs Homebrew taps and XQuartz, so
    get approval first; [02 section 1.3 B](research/close-area-nav/02-sims-platforms-competitions.md#13-first-hour-recipes-not-run)).
  - Cards: [PX4](integration-cards/px4__px4-autopilot.md), [MAVSDK-Python](integration-cards/mavlink__mavsdk-python.md),
    [px4_ros_com](integration-cards/px4__px4_ros_com.md) if ROS 2. Safety-filter baseline:
    [PX4-CBF](../catalog/repos/ntnu-arl__px4-cbf.md).
  - Samples: [vio-to-mavlink-bridge](../samples/vio-to-mavlink-bridge/) (`partial`, pose into EKF2),
    [px4-sitl-gps-denial](../samples/px4-sitl-gps-denial/) (`ran`, MAVSDK flight on SIH),
    [llm-mission-agent](../samples/llm-mission-agent/) `mav_mcp_server.py` (`partial`, geofenced
    vehicle tools, SITL only).
  - VOXL 2: VIO and depth avoidance on board ([VOXL 2 docs](../catalog/resources/px4-modalai-voxl-2-docs.md),
    [VOA docs](../catalog/resources/modalai-voxl-voa-docs.md), [OpenVINS server](../catalog/resources/modalai-voxl-open-vins-server-docs.md)).
- **ArduPilot copter**
  - Driver: `drivers/ardupilot_pymavlink.py` (`ArduPilotPymavlinkAdapter`, unrun stub). GUIDED, `SET_POSITION_TARGET_LOCAL_NED`,
    velocity mask 3527, yaw rate in rad/s CW ([frames.md ArduPilot](../templates/drone-adapter/frames.md#ardupilot)).
  - Keep-alive: re-send at least every second; the vehicle stops after 3 s without a command (same file, docs).
  - Zero-code fallback: BendyRuler (sensed obstacles) and Dijkstra's (fences, stay-out zones) in
    GUIDED ([01 section 3](research/close-area-nav/01-planning-and-mapping.md#3-local-replanners-and-autopilot-native-avoidance); not tested in the hub).
  - Sims: [sitl-docker](../samples/sitl-docker/) ArduCopter 4.6.3 (`ran`, headless). gz plugin on macOS: not verified.
  - Cards: [ArduPilot](integration-cards/ardupilot__ardupilot.md), [pymavlink](integration-cards/ardupilot__pymavlink.md),
    [MAVROS](integration-cards/mavlink__mavros.md) if ROS.
  - Samples: [ardupilot-ekf3-source-switch](../samples/ardupilot-ekf3-source-switch/) (`ran`, EKF3
    source sets), [vio-to-mavlink-bridge](../samples/vio-to-mavlink-bridge/) (ExternalNav).
  - License: firmware is GPL-3.0; companion code over MAVLink is separate ([path-to-product section 5](path-to-product.md#5-license-traps-for-a-shipped-product)).
- **Crazyflie 2.1** (likely with Flow deck v2 and Multi-ranger)
  - Driver: `drivers/crazyflie_cflib.py` (`CrazyflieCflibAdapter`, unrun stub). `send_velocity_world_setpoint`, yaw rate in deg/s,
    sign on current firmware not confirmed; check +x on the bench ([frames.md Crazyflie](../templates/drone-adapter/frames.md#crazyflie)).
  - Ranges: Multi-ranger, 5 ToF beams (front, back, left, right, up), up to 4 m
    ([Multi-ranger](../catalog/resources/bitcraze-multi-ranger-deck.md), docs). Thin obstacles between beams are invisible.
  - Pose: Flow deck dead reckoning ([Flow deck v2](../catalog/resources/bitcraze-flow-deck-v2.md)), or
    Lighthouse / Loco if the venue has it ([3.4](#34-q5-and-q6-sensors-and-venue-localization)).
  - Sims: [crazyflie-simulation](../catalog/repos/bitcraze__crazyflie-simulation.md) (Webots, 30-60 min
    estimate), [crazyflow](../catalog/repos/learnsyslab__crazyflow.md) + [lsy_drone_racing](../catalog/repos/learnsyslab__lsy_drone_racing.md)
    if the task looks like gates (15-30 min estimate), [gym-pybullet-drones](integration-cards/learnsyslab__gym-pybullet-drones.md)
    (pybullet compiles from source on Apple Silicon). All not run.
  - Cards: [Crazyflie firmware](integration-cards/bitcraze__crazyflie-firmware.md), [cflib](../catalog/repos/bitcraze__crazyflie-lib-python.md).
  - Compute: planning usually runs on the laptop over Crazyradio, see [3.6](#36-q8-compute).
- **DJI Tello / RoboMaster TT**
  - Driver: `drivers/tello_djitellopy.py` (`TelloDjitellopyAdapter`, unrun stub; refuses to fly until the stick scales are set). `send_rc_control` values are stick deflection
    -100..100, not cm/s; calibrate a per-axis scale on the bench ([frames.md Tello](../templates/drone-adapter/frames.md#tello)).
  - Keep-alive: auto-lands after 15 s without a command ([Tello SDK 2.0](../catalog/resources/tello-sdk-2-user-guide.md), via doc 02).
  - No obstacle sensor on Tello: the driver's `ranges()` returns an empty scan (no beams), never "clear". Only a known map works; see [3.5](#35-q7-obstacles).
  - No position: mission pads (EDU / TT), an external system, or dead reckoning.
  - Sim: gap: no Tello sim. Use `MockAdapter` from [drone-adapter](../templates/drone-adapter/) and the arena.
  - Code: [djitellopy](../catalog/repos/damiafuentes__djitellopy.md). Compute is off-board only.
- **DJI consumer (MSDK v5)**
  - Android app + virtual stick at 5-25 Hz ([MSDK virtual stick](../catalog/resources/dji-msdk-v5-virtual-stick-tutorial.md), via doc 02).
    The Android build path costs hours (doc 02 estimate).
  - gap: no hub driver, sample or sim. Ask for a different airframe or a laptop bridge before committing.
- **Parrot ANAFI (Olympe)**
  - Olympe ships Linux x86-64 wheels only; Sphinx needs Ubuntu + NVIDIA
    ([Sphinx requirements](../catalog/resources/parrot-sphinx-system-requirements.md)).
  - gap: no hub driver; not runnable on the Mac. Needs an x86 Linux box from whoever set the task.
- **Custom or unknown airframe**
  - Speaks MAVLink => treat as PX4 or ArduPilot above, after reading its heartbeat autopilot type.
  - Anything else => gap: no driver. Keep the planner on `MockAdapter` and ask for SDK docs today.

### 3.2 Q2: sim, real or both

- **Sim only, our choice of sim**
  - Planner and filter work: [close-area-arena](../samples/close-area-arena/) (`ran`, synthetic,
    2.5D point mass). Faults go in through the `pose_source` hook ([CONTRACT.md](../samples/close-area-arena/CONTRACT.md)).
  - Credibility repeat: the Q1 SITL from [3.1](#31-q1-drone-and-sdk).
  - Planners that exist (synthetic): straight baseline (0 % reached on `u_trap` and `narrow_gap`),
    `planners/astar_esdf.py` (known map 100 % on all three families, unknown map 80 % on
    `narrow_gap`, [README](../samples/close-area-arena/README.md#a--esdf-grid-planner-ran-2026-11-09-synthetic)),
    APF and VFH+ in [close-area-planner-reactive](../samples/close-area-planner-reactive/).
    Estimator faults: `run_faults.py`. Safety-filter arms F0-F5 (PX4 CP style, PX4-CBF,
    Belief-CBF, MR-CBF, ours) in [close-area-safety-filter](../samples/close-area-safety-filter/README.md);
    use F2 (PX4-CBF) under the planner. Complex rooms: `--family office / warehouse / forest /
    maze / glass_office` (known-map A* 100 % on all five, 20 layouts,
    [complex arenas](../samples/close-area-arena/README.md#complex-arenas-ran-2026-11-09-synthetic)).
    Which planner per room and sensor: [close-area-benchmark](../samples/close-area-benchmark/README.md)
    (14 planners incl. D* Lite, DWA, Bug2, TangentBug; table in the
    [cheat sheet](cheatsheets/close-area-a-to-b.md#3-which-planner-first)). Windows and bars:
    `run_z.py` and `planners/astar_esdf_3d.py` (3D A* 100 % vs 2.5D 14 %,
    [window_bar](../samples/close-area-arena/README.md#altitude-windows-and-bars-ran-2026-11-09-synthetic)).
  - Loop to fly them: [flight-repo](../templates/flight-repo/README.md) (`make sim` on the mock,
    `--planner arena:<name>` loads an arena planner unchanged; `make first-flight` flies arena A* +
    F2 and scores the log: reached in 19.76 s, synthetic,
    [Brief to first flight](../templates/flight-repo/README.md#brief-to-first-flight)).
- **Sim only, the task provides the sim and world**
  - gz / Gazebo => [Gazebo card](integration-cards/gazebosim__gz-sim.md), PX4 or ArduPilot driver from 3.1.
  - AirSim / Colosseum, Isaac Sim, Flightmare => not practical on the Mac
    ([02 section 1.1](research/close-area-nav/02-sims-platforms-competitions.md#11-comparison-table)); ask for their Linux box.
  - gap: no driver for a provided sim. Write one more `Adapter` class against their API.
- **Real only**
  - Driver plus a bench session before any flight: check every "not confirmed" item in
    [frames.md](../templates/drone-adapter/frames.md) (command +x, watch which way it moves).
  - Log every run: [recording-replay](../samples/recording-replay/) (`ran`, stdlib) writes JSONL / MCAP;
    flight-repo writes one JSONL line per tick. Score real and sim logs the same way with the arena's
    `score_log.py` ([log_format.md](../samples/close-area-arena/log_format.md); synthetic logs only so far).
  - Safety: [demo-script-close-area](../templates/demo-script-close-area.md) setup list (safety pilot, net, geofence).
- **Both**
  - Order: arena => SITL => real. One planner, three `Adapter` backends. Real flight never
    debugs planner logic.

### 3.3 Q3: how B is given

| B given as | Localization needed | Open | Decoder row |
|---|---|---|---|
| Offset from A ("5 m forward, 3 m left") | Any local odometry started at A; drift small vs the tolerance | [03 section 3](research/close-area-nav/03-close-area-localization.md#3-how-b-is-specified-and-what-it-implies), [drone-adapter](../templates/drone-adapter/README.md) origin rule | 31 |
| Venue-frame coordinates (mocap, UWB, Lighthouse frame) | The venue system, or one known pose (AprilTag at A) to align VIO | [vrpn_mocap](../catalog/repos/alvinsunyixiao__vrpn_mocap.md), [Loco](../catalog/resources/bitcraze-loco-positioning.md) | 31, 33 |
| GPS point | GNSS (RTK if offered) to get close, a relative cue for the last metres | [03 section 5b](research/close-area-nav/03-close-area-localization.md#b-outdoor-gnss-available) | 31, 32 |
| Marker, pad, tag or object | Odometry only has to bring it into view; fiducial or detector gives the goal | [AprilTag](../catalog/repos/aprilrobotics__apriltag.md), [apriltag_ros](../catalog/repos/christianrauch__apriltag_ros.md), [PX4 precision landing](../catalog/resources/px4-precision-landing-docs.md), [Clover card](integration-cards/copterexpress__clover.md) | 32 |
| "Somewhere behind the obstacles" (search) | Exploration + detection | [close-area-explore](../samples/close-area-explore/README.md) (frontier 43.3 % found with B unknown, synthetic; a frontier of the map is not a search for B), [01 planning](research/close-area-nav/01-planning-and-mapping.md) | 31, 32 |

Marker branch details:

- Fiducials allowed (Q9 yes) => AprilTag next to the official marker. PX4 precision landing via
  LANDING_TARGET, `PLD_HACC_RAD` default 0.2 m (docs, not run); the docs say it needs a valid
  global position, untested indoors ([03 section 3](research/close-area-nav/03-close-area-localization.md#3-how-b-is-specified-and-what-it-implies)).
- Tag size and hand-over range: [fiducial-goal-apriltag](../samples/fiducial-goal-apriltag/README.md)
  (synthetic: 0.16 m tag36h11 detected at >= 90 % to 5 m frontal, 2 m at 70 deg; tag-relative
  final approach within 0.1 m in 50/50 seeds; a 0.40 m pad tag fails at 0.5 m, so nest a small tag).
- Fiducials forbidden => learned detector trained on frames of the real marker, recorded as soon as it is available.
  gap: no marker-approach dataset and no learned-detector sample in the hub.

### 3.4 Q5 and Q6: sensors and venue localization

Localization source, first match wins:

- **Venue mocap** => it is the pose. [vrpn_mocap](../catalog/repos/alvinsunyixiao__vrpn_mocap.md) =>
  MAVROS `vision_pose` => EKF2 / EKF3 ([03 section 2](research/close-area-nav/03-close-area-localization.md#2-sensor-options)).
  Score note: IMAV counts beacons as off-board help (0.7x, [section 4](#4-scoring-rule-implications)).
- **Lighthouse** (Crazyflie) => native in the firmware; 2-4 cm mean / median vs mocap
  (Taffanel 2021, preprint, [record](../catalog/resources/taffanel-2021-lighthouse-positioning-accuracy.md)).
- **UWB anchors** => Loco on Crazyflie, ArduPilot Beacon source; dm-class per vendor
  ([Loco](../catalog/resources/bitcraze-loco-positioning.md), [LPS precision wiki](../catalog/resources/bitcraze-lps-precision-wiki.md)).
- **Stereo / depth camera + IMU, no venue system** => VIO into EKF2 / EKF3 as ODOMETRY; decoder row 33.
  - CPU companion => [OpenVINS](integration-cards/rpng__open_vins.md). Reference: ATE 0.36 m over
    278 m on UZH-FPV indoor_forward_3 (real dataset, [relative-nav-benchmark](../samples/relative-nav-benchmark/)).
  - Jetson => [Isaac ROS Visual SLAM](integration-cards/nvidia-isaac-ros__isaac_ros_visual_slam.md).
  - Bridge: [vio-to-mavlink-bridge](../samples/vio-to-mavlink-bridge/) or [vision_to_mavros](integration-cards/thien94__vision_to_mavros.md).
  - Gate on ODOMETRY `quality`, `reset_counter` and EV innovation rejects, not on covariance
    ([03 section 4](research/close-area-nav/03-close-area-localization.md#4-estimator-health-signals-a-planner-can-consume)).
  - On VIO loss with a map or a first pass of the room => hover, scan-to-map relocalization and
    a short disambiguating move ([close-area-relocalize](../samples/close-area-relocalize/README.md):
    99-100 % reached, 0 wrong commits, against 36-64 % with the estimator alone; synthetic, known map).
    Limits from the held-out runs: it holds on random and u_trap layouts only; office 94.4 %,
    glass_office 83.3 %, narrow_gap 85.6 %, warehouse 33 wrong commits per 180 runs; 48-64 % on a
    4-beam fan even with a yaw-spin; 7 % collisions with unmapped added obstacles
    ([held-out matrix](../samples/close-area-relocalize/README.md),
    [4-beam](../samples/close-area-relocalize/README.md),
    [stale map](../samples/close-area-relocalize/README.md)).
- **Optical flow + downward rangefinder only** => position is integrated velocity and drifts;
  fine for short offsets from A, weak for venue coordinates. Needs textured floors.
- **Outdoor with GNSS** => [03 section 5b](research/close-area-nav/03-close-area-localization.md#b-outdoor-gnss-available); VIO as fallback.
- **Nothing (Tello without pads)** => dead reckoning only; set `quality` low and keep the route short.

Obstacle sensing:

- **Depth / stereo camera** => raycast into the 3D occupancy grid, ESDF with scipy, A* + replan
  ([01 section 1](research/close-area-nav/01-planning-and-mapping.md#1-recommendation-in-one-paragraph)). Jetson + depth => [nvblox](../catalog/repos/nvidia-isaac-ros__isaac_ros_nvblox.md) is the map.
- **2D or 3D lidar** => same grid; FAST-LIO2 only if a 3D lidar is on board ([03 section 5a](research/close-area-nav/03-close-area-localization.md#a-indoor-no-gnss)).
- **ToF rangers (Multi-ranger)** => sparse range fan; the arena's `RangeFan` can be set to 4-5
  beams to match ([sensors.py](../samples/close-area-arena/sensors.py)). On a 4-beam fan the
  memoryless reactive planners collide often (VFH+ 72-98 %, APF 8-54 %, synthetic,
  [close-area-planner-reactive](../samples/close-area-planner-reactive/README.md)): keep a scan
  memory or a map, or slow down hard. The arena's `crazyflie` preset (4 x 27 deg cones, 3.0 m)
  hits glass in 90-100 % of glass-family runs
  ([sensor realism](../samples/close-area-arena/README.md#sensor-realism-crazyflie-presets-and-glass-ran-2026-11-09-synthetic)).
  This is the Q5 default. Without a map the benchmark's best 4-beam stack is `astar_unknown` + F2:
  office 50 % reached / 5 % collision, maze 55 / 0, warehouse 0 / 0
  ([close-area-benchmark](../samples/close-area-benchmark/README.md#preset-crazyflie)); with a map
  `astar_known` 100 / 0.
- **None** => known-map planning only. Unknown obstacles + no sensor is a hard gate: ask
  whoever set the task again before committing (first-three-hours [hard gates](first-three-hours.md#2-pick-the-idea-scoring-rubric)).

### 3.5 Q7: obstacles

- **Known in advance, static** => plan once on the given map (A* or PRM, [OMPL card](integration-cards/ompl__ompl.md));
  ArduPilot: enter them as stay-out polygons for Dijkstra's as a fallback layer.
- **Unknown** (the default) => three-state map (unknown / free / occupied), unknown at a cost penalty, replan at
  2-5 Hz, keep a brake-to-hover trajectory; `astar_unknown` in the benchmark, + F2 on a 4-beam fan
  ([cheat sheet table](cheatsheets/close-area-a-to-b.md#3-which-planner-first)) ([01 section 5a](research/close-area-nav/01-planning-and-mapping.md#5a-pure-python-sim-target-flying-ab-through-obstacles-by-hour-4-6)).
  Replan cost: a 200 x 200 x 50 scipy EDT took 183 ms median on an M3 Max (synthetic grid,
  [edt_timing.json](../samples/close-area-arena/results/edt_timing.json)).
- **Moved between runs** => never hard-code a path; show a replan on a moved obstacle
  ([02 section 3.1](research/close-area-nav/02-sims-platforms-competitions.md#31-what-this-tells-us-a-judge-scores)).
- **Narrow gaps or doorways** => grid resolution at most half the gap clearance; inflate by radius +
  measured tracking error ([01 section 6](research/close-area-nav/01-planning-and-mapping.md#6-failure-modes-and-what-to-do-about-each)).
  Arena family `narrow_gap` exercises it.
- **Thin poles, nets, glass** => range sensors miss them; put them in the map as map-only
  obstacles, and give map obstacles a margin for position error. In the kill test a fixed 0.2 m
  margin (MR-CBF) kept A* at 1.0 % or less collisions with unsensed obstacles under VIO faults;
  the protection-level margin did no better (synthetic,
  [close-area-safety-filter](../samples/close-area-safety-filter/README.md#part-e-held-out-seeds-and-families-ran-2026-11-09-synthetic)).
- **Dynamic (people, other drones)** => A* replanning on the latest scan is not enough: in the
  arena it collided in 14 % (0.5 m/s people) and 36 % (1.0 m/s) of runs, 5 Hz replans did not
  help. Put a range-only CBF filter (PX4-CBF style) under the planner: 0 % collisions, at 16 %
  stuck. APF also held 0-2 %. Synthetic, no motion prediction
  ([close-area-moving-obstacles](../samples/close-area-moving-obstacles/README.md)).
  With constant-velocity tracks, a VO gate on A* (`run_predict.py`) reached B in 100 of 100
  held-out runs with 0 collisions vs 92 % for A* + F2 (exact sign test p = 0.0078); the gain is
  reaching B where F2 deadlocks. Synthetic, people walk straight lines at constant speed.

### 3.6 Q8: compute

- **Onboard Jetson** => Isaac ROS Visual SLAM + nvblox; the numpy planner still runs on its CPU.
  Budget and latency table: [path-to-product section 1](path-to-product.md#1-onboard-compute-what-fits-where).
- **Onboard CPU companion (Pi, NUC, VOXL 2)** => numpy / scipy planner, OpenVINS on 1-2 cores
  ([03 section 2](research/close-area-nav/03-close-area-localization.md#2-sensor-options)). Measure loop time p99 on the board.
- **Ground laptop only** (Crazyflie, Tello, DJI) => fine technically; if scored like IMAV it costs
  0.7x. Keep the setpoint keep-alive inside the driver so a laptop stall does not land the drone.
- **Provided Linux GPU box** => Isaac Sim / Pegasus or aerial-autonomy-stack become possible
  ([02 section 1.1](research/close-area-nav/02-sims-platforms-competitions.md#11-comparison-table)); do not move the planner there unless asked.

### 3.7 Q9 and Q10: additions and deliverable

- **Tags allowed** => AprilTag at A (frame) and B (goal), 2-3 on walls for drift resets (decoder rows 32, 33).
- **Firmware locked** => everything stays in the companion; PX4-CBF-style in-firmware filtering is off the table, so the filter runs on setpoints.
- **Few counted runs** => reliability over peak speed; rehearse the [fallback plan](../templates/demo-script-close-area.md#fallback-plan).
- **Video or deck judged** => [close-area pitch](../templates/pitch/close-area-story.md) and its [kill test gate](../templates/pitch/close-area-story.md#2-kill-test-gate-decide-the-story-at-h24).

## 4. Scoring-rule implications

The closest public rules are IMAV 2026 indoor ([rulebook record](../catalog/resources/imav-2026-rulebook.md),
summarised in [02 section 3](research/close-area-nav/02-sims-platforms-competitions.md#3-competition-formats-and-lessons)):
completion up to 7 of 20 points per mission, times an autonomy factor of 1.0 onboard, 0.7 with
off-board compute or beacons, 0.4 with any manual intervention; ArUco landing +1 static, +2 moving.
These are another event's rules; replace them with Q4's answer.

| If the scoring says... | Then this matters more | And this matters less | Open |
|---|---|---|---|
| Manual intervention multiplies the score down (IMAV: 0.4x) | Safety filter, hover fallback on nav-health loss, driver keep-alive, geofence. One safety-pilot touch costs more than any time saving | Top speed | [synthesis](research/close-area-nav/README.md#recommended-direction), [04 section 3](research/close-area-nav/04-innovation-prior-art.md#3-idea-c-safety-filter-around-any-planner) |
| Off-board compute or beacons are discounted (IMAV: 0.7x) | Planner and VIO onboard; mocap only as ground truth, not as the pose | Ground-laptop convenience | [path-to-product section 1](path-to-product.md#1-onboard-compute-what-fits-where), row 33 |
| Completion first, time second | A slow, sure A=>B; speed cap by stopping distance | Trajectory optimisation | [02 section 3.1](research/close-area-nav/02-sims-platforms-competitions.md#31-what-this-tells-us-a-judge-scores) |
| Time only, crashes allowed | Min-snap smoothing, higher speed cap, fewer replans; tune only after the arena shows 100 % reached | Margins beyond radius + tracking error | [01 section 5a](research/close-area-nav/01-planning-and-mapping.md#5a-pure-python-sim-target-flying-ab-through-obstacles-by-hour-4-6) |
| A collision ends the run or zeroes it | Inflation = radius + measured tracking error + sensor noise; treat unknown space as unsafe | Shortest path | [01 section 6](research/close-area-nav/01-planning-and-mapping.md#6-failure-modes-and-what-to-do-about-each) |
| Precision at B or a landing bonus | AprilTag at B, precision landing, final-error metric | Mid-route accuracy | row 32, [3.3](#33-q3-how-b-is-given) |
| Randomized or moved layouts | Replanning shown live; no hard-coded path | Pre-computed optimal routes | arena families `random`, `u_trap`, `narrow_gap` |
| Mass factor (IMAV: 1.13x at 3 kg to 2.0x at 0.1 kg) | If we may choose: the lightest airframe (Crazyflie class) | Payload | [02 section 2](research/close-area-nav/02-sims-platforms-competitions.md#2-platform-cheat-table) |
| Innovation or "real-world implementation" judged | Relocalization after VIO loss (the headline); the range filter and the kill-test result as the honest supporting story; runtime-assurance product story | Polish on the baseline planner | [close-area-relocalize](../samples/close-area-relocalize/README.md), [close-area story H1](../templates/pitch/close-area-story.md#3-alternative-hooks-if-the-kill-test-fails), [path-to-product section 4](path-to-product.md#4-runtime-assurance-ship-the-new-algorithm-next-to-a-trusted-baseline) |
| Best of N attempts | Peak performance on one good run is fine; still record the backup | Variance | [demo-script-close-area](../templates/demo-script-close-area.md#recording-the-backup) |
| All N attempts averaged | Reliability; run the arena on 200 layouts, not 20 | Peak speed | [arena](../samples/close-area-arena/README.md#run) |

Headline kill test, whatever the scoring: 200 layouts with injected VIO jump and bias faults; pass
at breaches 1 % or less, at least 3x lower than Belief-CBF on fault cases, goal reach at least
90 % of PX4-CBF ([synthesis](research/close-area-nav/README.md#recommended-direction)). It ran
(synthetic, 100 layouts per seed, held-out seeds 1-2): **FAIL**. Ours collided in 2.5 % [1.1, 5.7]
of held-out jump runs and reached 0.55 of PX4-CBF's jump reach; a fixed 0.2 m bound stayed at
1.0 % or less on seeds 0-2
([Part e](../samples/close-area-safety-filter/README.md#part-e-held-out-seeds-and-families-ran-2026-11-09-synthetic)).
The pitch switches to H1, relocalization after VIO loss
([close-area-story section 3](../templates/pitch/close-area-story.md#3-alternative-hooks-if-the-kill-test-fails)).

## 5. Gaps this tree exposed

- gap: the [drivers](../templates/drone-adapter/drivers/README.md) (PX4 MAVSDK, ArduPilot pymavlink, cflib, djitellopy) exist as unrun
  stubs: no SDK was installed and no SITL or vehicle touched. Every Q1 branch starts with their
  bench checks.
- Filled 2026-11-09: A* + ESDF, APF and VFH+ planners and estimator faults in the arena (synthetic),
  and the [flight-repo](../templates/flight-repo/README.md) loop template (mock only).
- Filled 2026-11-09: the safety-filter kill test
  ([close-area-safety-filter](../samples/close-area-safety-filter/README.md), parts a-e, held-out
  verdict FAIL), relocalization after VIO loss
  ([close-area-relocalize](../samples/close-area-relocalize/README.md)), walking people
  ([close-area-moving-obstacles](../samples/close-area-moving-obstacles/README.md)), Crazyflie
  sensor presets, glass and five complex families in the arena, and the flight-repo
  `make first-flight` chain. All synthetic.
- gap: no marker-approach dataset (row 32); the marker-goal sample
  [fiducial-goal-apriltag](../samples/fiducial-goal-apriltag/) is synthetic only.
- gap: no close-area starter bundle in [starter-bundles.md](starter-bundles.md) or the offline kit.
- gap: no Tello sim, no DJI MSDK or Olympe path on the Mac, no driver for a sim provided with the task.
- Filled 2026-11-09 (second refresh): planner benchmark (14 planners x 8 families x 2 sensors), 3D
  `window_bar` family with a 3D A* on a prior map, D* Lite, DWA and Bug planners, browser playground. All synthetic.
- gap: no 3D unknown-map planner, no up / down sensing in the arena, and no recorded close-area obstacle flight.
- gap: the question order above was written before
  [06-task-phrasing-survey.md](research/close-area-nav/06-task-phrasing-survey.md) landed and is not
  yet checked against its revised question list (section 4).

## 6. Intake card

Copy into the team repo's `docs/` and fill during 0:00-0:10.

| # | Answer | Branch taken | Hub path opened |
|---|---|---|---|
| Q1 drone + SDK | | | |
| Q2 sim / real | | | |
| Q3 how B is given, tolerance | | | |
| Q4 scoring | | | |
| Q5 sensors | | | |
| Q6 indoor / outdoor, venue positioning | | | |
| Q7 obstacles | | | |
| Q8 compute | | | |
| Q9 additions allowed | | | |
| Q10 deliverable, counted runs | | | |

## 7. Not verified

- No branch was walked end to end. Every driver named above is an unrun stub; every sim except
  close-area-arena and sitl-docker was not run in the hub.
- Setup times are README-based estimates from [doc 02](research/close-area-nav/02-sims-platforms-competitions.md), not timings.
- IMAV 2026 factors come from doc 02's PDF extraction of the rulebook; the scoring of your task is unknown until it is announced.
- The defaults in section 1 are guesses about a likely venue, not information from whoever set the task.
- Platform frame and unit items marked "not confirmed" in [frames.md](../templates/drone-adapter/frames.md)
  still need a bench test.

## Sources

Hub files only, read on 2026-11-09:
[close-area-nav README](research/close-area-nav/README.md), [01](research/close-area-nav/01-planning-and-mapping.md),
[02](research/close-area-nav/02-sims-platforms-competitions.md), [03](research/close-area-nav/03-close-area-localization.md),
[04](research/close-area-nav/04-innovation-prior-art.md), [07](research/close-area-nav/07-pl-margin-prior-art.md),
[drone-adapter README](../templates/drone-adapter/README.md), [frames.md](../templates/drone-adapter/frames.md),
[close-area-arena README](../samples/close-area-arena/README.md), [first three hours](first-three-hours.md),
[decoder rows 31-33](problem-statement-decoder.md), [full-brief routing](problem-statement-decoder.md#route-a-full-brief-to-rows-and-first-pages).
External facts (PX4, ArduPilot, Bitcraze, Tello, DJI, IMAV) are as cited in those files.
