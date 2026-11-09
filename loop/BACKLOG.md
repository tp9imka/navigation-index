# Loop backlog

The one coordination artifact for the loop ([DRIVER.md](DRIVER.md)). The driver edits Status;
rows are appended, never rewritten. Status: `ready` | `in-flight <job>` | `done <sha>` |
`retry` | `failed <reason>` | `needs-human <question>` | `dropped <reason>`.
Type: P poc, R research, T template, A agent-aid, S sweep. Size S = one job; M = split into
S parts (a, b, c) before launch. Deps marked B are binding; others are listing only.

Initial backlog: fable brainstorm, 2026-11-09, base dbafbff.

## Design decisions (apply to every item)

- **One sim for every comparison:** `samples/close-area-arena`, 2.5D (2D occupancy at flight
  altitude), numpy + scipy only, 50 Hz double integrator with 0.15 s velocity lag, ray-cast
  range fan with configurable FoV. No pybullet, no PX4 + gz in the loop. SIH Offboard (15) is
  the product-credible step.
- **One adapter contract:** `pose()/ranges()/send_setpoint()` defined in
  `templates/drone-adapter`; the arena ships a `SimAdapter` with the same signatures.
- **One sample per approach,** importing the arena by relative path (precedent:
  blind-flight-bench => terrain-heightmap-pf).
- **Shared files** are edited by the driver or by the single sweep item (27) of a wave. Each
  sample leaves `INTEGRATION.md` with the rows it wants added.
- **Done when** = the printed table pasted into the README from a real run, with command and
  runtime. FAIL is an accepted deliverable.

## Items

| # | Status | Title | T | Sz | Deps | Path | Why on Day 1 | Done when |
| 01 | done 6d72ea1 | Arena S1: world gen, range fan, vehicle, SimAdapter, scorer, straight-line planner, CLI | P | S | - | `samples/close-area-arena/` | Everything else runs here | `run.py --planner straight --layouts 20` prints collision/reached/stuck/time/min-clearance; scipy EDT on 200x200x50 timed; stdlib test on scorer |
| 02 | done af25b73, 46a6e40 | Adapter template: Protocol, Pose (quality, reset_counter), RangeScan, Setpoint, frames.md, MockAdapter; driver stubs for cflib, djitellopy, MAVSDK, pymavlink | T | M (2: protocol+mock+tests; stubs) | - | `templates/drone-adapter/` | Hour-0 planner code ports to any drone | stdlib tests incl. ENU/NED, FLU/FRD; stubs import lazily, labelled unrun |
| 03 | done 7a55438 | Arena S2: A* on inflated grid, ESDF clearance cost, shortcut, 2-5 Hz replan, unknown penalty | P | S | 01 B | `close-area-arena/planners/astar_esdf.py` | The baseline under the filter | 50 layouts: A* reach >= 90 %, table vs straight line |
| 04 | done 7616f5c | Arena S3: EKF pos/vel, VIO-like updates, good/dark zones, faults (0.5 m jump, 0.05 m/s bias, dropout), 2 UWB anchors for a PL | P | S | 01 B | `close-area-arena/estimator.py`, `faults.py` | Plan on the estimate, not truth | A* on estimate vs truth: collision rate per fault case |
| 05 | done cf93eb1 | CBF baselines read faithfully: PX4-CBF code + arXiv 2504.15850, Vahs 2023, gatekeeper, full text | R | S | - | `docs/research/close-area-nav/05-cbf-baselines-faithful.md` | Beat real baselines, not strawmen | Equations, params, pseudo-code per filter; full-text vs abstract labelled |
| 06 | ready | Kill test (doc 04 §3.4): a) F0, F1 CP-stop, F2 range CBF on P1; b) F3 BCBF, F4 PL margin + speed cap + hover; c) 200 layouts x 5 faults x P1-P3 | P | M (3) | 01,03,04,05 B | `samples/close-area-safety-filter/` | Decides by hour 24 if the headline lives | README says PASS or FAIL against doc 04 thresholds; interventions and "stuck" reported separately |
| 07 | done 530ea69 | Decoder rows 31-33 (A=>B with obstacles; goal is a marker; indoor VIO-loss recovery) + eval cases; fix challenge-2 §3 "none yet" | A | S | - | `docs/problem-statement-decoder.md`, `tools/decode_eval.json`, decoder part of `tools/query.py` | `decode` on the real brief hits rover row 30 or nothing | `decode_eval.py` passes with 3 new positives, 2 negatives (rover still => 30) |
| 08 | 08a done 226dd1f; 08b ready | Flight-repo template: Adapter => Health => Planner => SafetyFilter => send at 20 Hz with heartbeat thread; mock; Makefile; AGENTS.md | T | M (2: core+tests; Makefile/README) | 02 soft | `templates/flight-repo/` | project-repo is filter-shaped; this gets cloned at H+0 | `make test` green stdlib; `make sim` flies mock A=>B, prints scorer line |
| 09 | needs-human: build the sitl-docker images (docker compose build pulls base images)? | ArduPilot OA in headless SITL: stay-out polygon between A and B, GUIDED, Dijkstra and BendyRuler, contrast without OA | P | S | sitl-docker images | `samples/ardupilot-oa-fence-sitl/` | Zero-companion-code fallback, untested in hub | Two logged flights: avoids with OA, crosses without; min distance in README |
| 10 | done 2ced628 | Reactive planners: APF and VFH+ on the range fan, U-trap layouts | P | S | 01 B | `samples/close-area-planner-reactive/` | Ranger-only fallback (Crazyflie); the stuck slide | APF/VFH+/A* on 50 layouts: reached, stuck, collisions |
| 11 | done 881d7e1 | Log scorer + plot: flown JSONL + world => completion, min clearance, interventions; planned-vs-flown PNG | P | S | 01 B | `close-area-arena/score_log.py` | The one plot judges need, sim or real | Sim log and hand-made log score as expected; PNG written |
| 12 | done 914e5e6 | Task-phrasing survey: 8-10 indoor A=>B events (IMAV, ICUAS, Teknofest, LSY, IROS ADR): how B is given, arena size, sensors, scoring | R | S | - | `docs/research/close-area-nav/06-task-phrasing-survey.md` | Lane 03 admits no primary source on B | Table with primary links; ranked Day-1 shapes; organiser questions revised |
| 13 | done d4180ee | Prior-art kill search: "protection level / RAIM / integrity monitor" x "CBF / safety filter / UAV", 2022-2026, patents, Skydio/Shield AI/Exyn | R | S | - | `docs/research/close-area-nav/07-pl-margin-prior-art.md` | Kill the claim now, not on stage | Query list, hits, verdict: novel composition or exists (cite) |
| 14 | done 9501e7c | Day-1 intake tree: organiser answers (drone, SDK, sensors, B spec, sim/real, scoring, compute) => stack, adapter, sim, samples, IMAV multipliers | A | S | - | `docs/day1-close-area-intake.md` | The first 20 minutes | Every branch ends in a hub path, none in "TBD" |
| 15 | needs-human: same sitl-docker image build as 09 | PX4 SIH Offboard: MAVSDK velocity setpoints with keep-alive, companion-held map, raycast from LOCAL_POSITION_NED; a) straight; b) A* + planned-vs-flown | P | M (2) | 01,03 B; sitl-docker | `samples/close-area-px4-offboard/` | Same planner on a real autopilot loop | SITL flight around companion obstacles; min ESDF distance along flown path plotted |
| 16 | done 6e12000 | AprilTag goal: render tags (OpenCV) at known poses, detect (pupil-apriltags), error vs range/angle; tag-relative final approach in arena | P | S | 01 soft | `samples/fiducial-goal-apriltag/` | "Land on the marker" is the likeliest B | Error table vs range/angle; failure angle named; last-metres run |
| 17 | ready | Gatekeeper-style backup: commit longest prefix with brake-to-hover in known-free; unknown = unsafe | P | S | 01,03,04 B | `samples/close-area-planner-gatekeeper/` | Unknown space is lane 01's top failure | Unknown-space collision rate with/without, 100 layouts |
| 18 | done d0dc4d8 | Pitch scaffold: close-area hooks, 3-min skeleton, judge questions ("why not just the lidar?", "where does the planner run?", "VIO lost?"), demo-script variant | T | S | - | `templates/pitch/close-area-story.md`, `templates/demo-script-close-area.md` | Pitch kit has no close-area hooks | Each question points at a sample path or says pending |
| 19 | ready | Cheat sheet close-area-a-to-b | A | S | 01,03,06 soft | `docs/cheatsheets/close-area-a-to-b.md` | The 3-minute page for this brief family | Numbers only from READMEs that ran, with input type; first commands re-run |
| 20 | ready | Sampling planners: RRT*, Informed RRT* (own impl; OMPL wheel optional), narrow-gap set | P | S | 01 B | `samples/close-area-planner-sampling/` | Shows why A* is the default | Success vs gap width for A* and RRT*; path-length std across runs |
| 21 | ready | Linear MPC tracker (OSQP) with corridor half-planes along the A* path | P | S | 01,03 B | `samples/close-area-planner-mpc/` | Have the MPC number, not the slide | Tracking error, min clearance vs velocity tracking; solve time on M-series |
| 22 | ready | Relocalization after VIO loss: 2-5 hypotheses from scan-to-map matching, hover until one wins | P | S | 01,04 B | `samples/close-area-relocalize/` | First question a product owner asks indoors | Recovery rate within N s vs single hypothesis; wrong commits counted |
| 23 | ready | Crazyflie sensing limits: Multi-ranger beams/FoV/rate/noise, Flow floor failures, implied unsensed-obstacle classes | R | S | - | `docs/research/close-area-nav/08-crazyflie-sensing-limits.md` | Sets arena FoV and the unsensed case honestly | Sourced numbers; arena config values proposed |
| 24 | ready | VIO NEES feasibility: which indoor set (EuRoC, UZH-FPV indoor, TUM-VI room) + relative-nav-benchmark's OpenVINS docker gives NEES in < 30 min | R | S | - | `docs/research/close-area-nav/09-vio-nees-feasibility.md` | Hub calls VIO overconfidence unknown | Dataset, sequence, command, runtime, or "none fits" |
| 25 | ready | VIO NEES POC on that sequence; inflation factor for the kill test's R x 0.25 check | P | M (2) | 24 B; OpenVINS image | `samples/vio-nees-indoor/` | Measured factor replaces a guess | NEES table + fitted factor; input real |
| 26 | ready | Conformal trust for visual fixes on cached VPAIR results (long-range fallback; only if `e2e-visual-nav-vpair/results/` exists) | P | S | cache | `samples/visual-fix-trust-conformal/` | Cheapest long-range item; the only one worth a slot | 90 % radius + acceptance set on 199 frames; held-out coverage |
| 27 | ready | Integration sweep per wave: evidence-matrix, decoder Start-from, challenge-2 §3/§4, docs/README, cheatsheets README, stdlib-sample-tests.txt; re-run each new first_command | S | S | wave | shared files only | Keeps the hub coherent | `build.py` dangling 0, `check_links`, `check_sample_tests`, `decode_eval` pass |
| 28 | ready | Not-verified reconciliation: move research "Not verified" lines to verified with the measured number | S | S | end | `docs/research/close-area-nav/*` | Docs stop over-hedging once things ran | Each moved line cites a sample README anchor |

## Planned waves

- Wave 1: 01, 02a, 05, 07, 09, 12, 13. Then 27.
- Wave 2: 03, 04, 08, 10, 11, 14, 16. Then 27.
- Wave 3: 06a-c (sequential), 15, 17, 18, 19, 20, 21. Then 27.

If 01 fails twice: no third variation. The driver flags it `needs-human` and proposes a
hand-written arena with a `CONTRACT.md` so wave 2 can code against the contract.

## Deliberately not doing (re-open only with a reason in JOURNAL)

- gym-pybullet-drones or PX4 + gz inside the loop (installs, GUI). Human rehearsal instead.
- NoMaD/ViNT, RL, event cameras, learned high-speed flight (GPU or ROS 1, no renderer).
- Perception-aware planning (parked by doc 04), LLM goal spec, EGO-Planner / Fast-Planner ports.
- Drag-aided filter and guidance G1-G3 (need windy SITL logs). More long-range cheat sheets.
