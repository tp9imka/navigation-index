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
| 06 | 06a done 1d1fd4a; 06b done fe3bb5f; 06c done 559d7d8; 06d = item 34 | Kill test (doc 04 §3.4): a) F0, F1 CP-stop, F2 range CBF on P1; b) F3 BCBF, F4 PL margin + speed cap + hover; c) 200 layouts x 5 faults x P1-P3 | P | M (3) | 01,03,04,05 B | `samples/close-area-safety-filter/` | Decides by hour 24 if the headline lives | README says PASS or FAIL against doc 04 thresholds; interventions and "stuck" reported separately |
| 07 | done 530ea69 | Decoder rows 31-33 (A=>B with obstacles; goal is a marker; indoor VIO-loss recovery) + eval cases; fix challenge-2 §3 "none yet" | A | S | - | `docs/problem-statement-decoder.md`, `tools/decode_eval.json`, decoder part of `tools/query.py` | `decode` on the real brief hits rover row 30 or nothing | `decode_eval.py` passes with 3 new positives, 2 negatives (rover still => 30) |
| 08 | 08b dropped (covered by 08a: Makefile, README, AGENTS.md shipped); 08a done 226dd1f; 08b ready | Flight-repo template: Adapter => Health => Planner => SafetyFilter => send at 20 Hz with heartbeat thread; mock; Makefile; AGENTS.md | T | M (2: core+tests; Makefile/README) | 02 soft | `templates/flight-repo/` | project-repo is filter-shaped; this gets cloned at H+0 | `make test` green stdlib; `make sim` flies mock A=>B, prints scorer line |
| 09 | needs-human: build the sitl-docker images (docker compose build pulls base images)? | ArduPilot OA in headless SITL: stay-out polygon between A and B, GUIDED, Dijkstra and BendyRuler, contrast without OA | P | S | sitl-docker images | `samples/ardupilot-oa-fence-sitl/` | Zero-companion-code fallback, untested in hub | Two logged flights: avoids with OA, crosses without; min distance in README |
| 10 | done 2ced628 | Reactive planners: APF and VFH+ on the range fan, U-trap layouts | P | S | 01 B | `samples/close-area-planner-reactive/` | Ranger-only fallback (Crazyflie); the stuck slide | APF/VFH+/A* on 50 layouts: reached, stuck, collisions |
| 11 | done 881d7e1 | Log scorer + plot: flown JSONL + world => completion, min clearance, interventions; planned-vs-flown PNG | P | S | 01 B | `close-area-arena/score_log.py` | The one plot judges need, sim or real | Sim log and hand-made log score as expected; PNG written |
| 12 | done 914e5e6 | Task-phrasing survey: 8-10 indoor A=>B events (IMAV, ICUAS, Teknofest, LSY, IROS ADR): how B is given, arena size, sensors, scoring | R | S | - | `docs/research/close-area-nav/06-task-phrasing-survey.md` | Lane 03 admits no primary source on B | Table with primary links; ranked Day-1 shapes; organiser questions revised |
| 13 | done d4180ee | Prior-art kill search: "protection level / RAIM / integrity monitor" x "CBF / safety filter / UAV", 2022-2026, patents, Skydio/Shield AI/Exyn | R | S | - | `docs/research/close-area-nav/07-pl-margin-prior-art.md` | Kill the claim now, not on stage | Query list, hits, verdict: novel composition or exists (cite) |
| 14 | done 9501e7c | Day-1 intake tree: organiser answers (drone, SDK, sensors, B spec, sim/real, scoring, compute) => stack, adapter, sim, samples, IMAV multipliers | A | S | - | `docs/day1-close-area-intake.md` | The first 20 minutes | Every branch ends in a hub path, none in "TBD" |
| 15 | needs-human: same sitl-docker image build as 09 | PX4 SIH Offboard: MAVSDK velocity setpoints with keep-alive, companion-held map, raycast from LOCAL_POSITION_NED; a) straight; b) A* + planned-vs-flown | P | M (2) | 01,03 B; sitl-docker | `samples/close-area-px4-offboard/` | Same planner on a real autopilot loop | SITL flight around companion obstacles; min ESDF distance along flown path plotted |
| 16 | done 6e12000 | AprilTag goal: render tags (OpenCV) at known poses, detect (pupil-apriltags), error vs range/angle; tag-relative final approach in arena | P | S | 01 soft | `samples/fiducial-goal-apriltag/` | "Land on the marker" is the likeliest B | Error table vs range/angle; failure angle named; last-metres run |
| 17 | dropped (re-plan: kill test part a answered it; CP-stop brake already 0 % sensed collisions) | Gatekeeper-style backup: commit longest prefix with brake-to-hover in known-free; unknown = unsafe | P | S | 01,03,04 B | `samples/close-area-planner-gatekeeper/` | Unknown space is lane 01's top failure | Unknown-space collision rate with/without, 100 layouts |
| 18 | done d0dc4d8 | Pitch scaffold: close-area hooks, 3-min skeleton, judge questions ("why not just the lidar?", "where does the planner run?", "VIO lost?"), demo-script variant | T | S | - | `templates/pitch/close-area-story.md`, `templates/demo-script-close-area.md` | Pitch kit has no close-area hooks | Each question points at a sample path or says pending |
| 19 | done d705042 | Cheat sheet close-area-a-to-b | A | S | 01,03,06 soft | `docs/cheatsheets/close-area-a-to-b.md` | The 3-minute page for this brief family | Numbers only from READMEs that ran, with input type; first commands re-run |
| 20 | done 98f1e86 | Sampling planners: RRT*, Informed RRT* (own impl; OMPL wheel optional), narrow-gap set | P | S | 01 B | `samples/close-area-planner-sampling/` | Shows why A* is the default | Success vs gap width for A* and RRT*; path-length std across runs |
| 21 | done 8f39a8e | Linear MPC tracker (OSQP) with corridor half-planes along the A* path | P | S | 01,03 B | `samples/close-area-planner-mpc/` | Have the MPC number, not the slide | Tracking error, min clearance vs velocity tracking; solve time on M-series |
| 22 | done ac5a899 | Relocalization after VIO loss: 2-5 hypotheses from scan-to-map matching, hover until one wins | P | S | 01,04 B | `samples/close-area-relocalize/` | First question a product owner asks indoors | Recovery rate within N s vs single hypothesis; wrong commits counted |
| 23 | done 04e147c | Crazyflie sensing limits: Multi-ranger beams/FoV/rate/noise, Flow floor failures, implied unsensed-obstacle classes | R | S | - | `docs/research/close-area-nav/08-crazyflie-sensing-limits.md` | Sets arena FoV and the unsensed case honestly | Sourced numbers; arena config values proposed |
| 24 | done 4c0dca7 | VIO NEES feasibility: which indoor set (EuRoC, UZH-FPV indoor, TUM-VI room) + relative-nav-benchmark's OpenVINS docker gives NEES in < 30 min | R | S | - | `docs/research/close-area-nav/09-vio-nees-feasibility.md` | Hub calls VIO overconfidence unknown | Dataset, sequence, command, runtime, or "none fits" |
| 25 | needs-human: Docker build of the OpenVINS image (~20 min) + 1.61 GB UZH-FPV bag; plan in doc 09 section 5 | VIO NEES POC on that sequence; inflation factor for the kill test's R x 0.25 check | P | M (2) | 24 B; OpenVINS image | `samples/vio-nees-indoor/` | Measured factor replaces a guess | NEES table + fitted factor; input real |
| 26 | parked (long-range only; reopen if the brief is long-range) | Conformal trust for visual fixes on cached VPAIR results (long-range fallback; only if `e2e-visual-nav-vpair/results/` exists) | P | S | cache | `samples/visual-fix-trust-conformal/` | Cheapest long-range item; the only one worth a slot | 90 % radius + acceptance set on 199 frames; held-out coverage |
| 27 | sweep 1 done 42e9fe1; run again after each wave | Integration sweep per wave: evidence-matrix, decoder Start-from, challenge-2 §3/§4, docs/README, cheatsheets README, stdlib-sample-tests.txt; re-run each new first_command | S | S | wave | shared files only | Keeps the hub coherent | `build.py` dangling 0, `check_links`, `check_sample_tests`, `decode_eval` pass |
| 28 | done 4d82ae0 | Not-verified reconciliation: move research "Not verified" lines to verified with the measured number | S | S | end | `docs/research/close-area-nav/*` | Docs stop over-hedging once things ran | Each moved line cites a sample README anchor |

| 29 | in-flight | Docs navigation audit (read-only): 12 cold-start agent walkthroughs, orphan docs, stale pointers, entry-point gaps, ranked fix list in disjoint work packages | R | S | - | report only (docs-audit.md via --out) | Agents on Day 1 find things in 1-2 hops | Report with hop counts per question and <= 25 ranked fixes |
| 30 | done 1ea1d6c | Showcase page for humans: hero + live counters, arena replay animation, sample gallery with honest status, agent-flow diagram | T | S | 01,03,04 soft | `site/showcase.*`, `site/data/showcase/`, `samples/close-area-arena/export_replay.py`, one nav link | Show case for judges and managers | Desktop and phone screenshots, node site tests pass |
| 31 | WP B, C, E, F, G, I done; D (+A, 19) done; H open | Docs work packages from the 29 audit (entry points, research index, README one-liners, stale pointers), split into disjoint file sets | A | M | 29 B | per package | Agent navigation | Audit's hop counts re-measured after the fix |

| 32 | done 0a62876 | Arena sensor realism from doc 08: 27 deg cone beams (sub-rays, min), 0.04 m min range, range-dependent noise, glass panels and thin poles family, SENSOR_PRESETS + --sensor flag (crazyflie, crazyflie_bright, ideal) | P | S | 23 B | new files in samples/close-area-arena only (sensors_cone.py, world_glass.py, presets.py) plus one --sensor hook proposed in Driver edits | The safety-filter claim is about what sensors miss; the arena must miss the same things | A* + freest_beam on glass family with crazyflie preset: collision table |

| 33 | done 5683770 | Relocalization 22b: hover timeout + disambiguating move (expected scan disagreement) vs random move vs hover; symmetric corridor + random layouts | P | S | 22 B | samples/close-area-relocalize new files + README section | Backup headline: recover without wrong commits and without hovering forever | Table: (e) chosen move vs (d) random vs (c) hover vs (b) single |

| 34 | done 5f5e16c (seed-0 FAIL on reach) | 06d ours arm F4: F2 range barrier + PL margin on map obstacles from the 06c monitor + health speed cap + hover when the monitor cannot name the lying source | P | S | 06b B, 06c B | samples/close-area-safety-filter (filters.py F4, run_kill.py, results/kill_d_*, README Part d) | The headline lives or dies here | kill_d table, 100 layouts seed 0, unsensed on; PASS/FAIL per doc 04 line; FAIL accepted; do not write PASS before 37 |
| 35 | done 2e3f270 | Sweep 2: INTEGRATION rows from mpc, sampling, relocalize, safety-filter into evidence 14, decoder 31/33, guidance-planning G5, readiness overrides, cheat sheet | S | S | - | docs/evidence-matrix.md, docs/problem-statement-decoder.md, tools/decode_eval.json, docs/guidance-planning.md, samples/_meta_overrides.json, docs/cheatsheets/close-area-a-to-b.md | Four ran samples invisible to decode | each sample in evidence + decoder; decode 'VIO lost indoors' names close-area-relocalize; gate green |
| 36 | done 10ce290 | First flight end to end: flight-repo flies in the arena world (arena adapter + estimator, arena planner, kill-test filter shim), make first-flight => JSONL => score_log => PNG | T | S | - | templates/flight-repo/ | Hour 0-1 chain has never run as one | one command => score line + PNG; wall time in README; make test green |
| 37 | done 51ce9d6 (headline FAIL) | Held-out and adversarial kill-test rerun: seeds 1-2, straight planner, u_trap and narrow_gap, arms F0/F2/F3/F4, Wilson intervals | P | S | 34 B | samples/close-area-safety-filter run_kill.py, results/kill_e_* | A seed-0 PASS is one collision | table with 95 % intervals; verdict holds or flips |
| 38 | done e7898d3 | Tooling follow-ups: md_plain keeps '=>', GUIDE_GLOBS for paper-digests/dataset-cards indexes, card_index trigger line, licences query and how-to holdout in search_eval, recall boost mirrored in app.js | A | S | - | tools/build.py, tools/query.py, tools/card_index.py, tools/search_eval.py + query set, site/app.js | Search is every agent's front door | parity passes; recall >= 0.671; licences top 3 has model-weights-licenses; snippet shows A=>B |
| 39 | done 0f3d466 | Pivot kit: relocalization as headline if 34 fails, filled with 22/33 numbers | T | S | 33 B; 34 soft | templates/pitch/close-area-story.md section 3, templates/demo-script-close-area.md variant rows | Decide-by-H+24 needs the pivot on the shelf | both files carry an 'if kill test FAIL' branch with numbers and anchors |
| 40 | dropped (headline failed on held-out seeds; FT-CBF/Tan comparison no longer decides anything) | F3f FT-CBF residual dropping and F3t Tan union of states vs F4 | P | S | 34 B | samples/close-area-safety-filter (Part g) | 'What is new vs Tan 2025' needs a number | table with wrong-exclusion and freeze columns |
| 41 | parked (re-open only if the safety filter comes back as a supporting demo) | Crazyflie-preset kill-test rerun via --sensor (ideal / crazyflie / crazyflie_bright), wedge hits counted | P | S | 32 B, 34 B | samples/close-area-safety-filter run_kill.py --sensor, results/kill_f_* | Crazyflie likeliest; 360 deg fan flatters range filters | F0/F2/F4 x presets table |
| 42 | done a9e253f | Judge drill: 15 questions with numbers, input types, anchors | T | S | 34 soft | templates/pitch/judge-drill-close-area.md, templates/pitch/README.md row | H+36 rehearsal sheet | every answer has a number or 'no number' |
| 43 | done 33f19e2 | Moving obstacles family: person-sized cylinders 0.5/1.0 m/s; A* replan vs A* + F2 vs APF | P | S | - | samples/close-area-moving-obstacles/ | Intake asks static or moving | 50 layouts x 2 speeds x 3 arms table |
| 44 | dropped (superseded by 64) | Showcase 2: Challenge 2 preset link, headline status card, kill-test F0 vs F2 replay with unsensed pole, relocalize hypotheses replay | T | S | 34 soft | site/index.html, site/showcase.*, site/data/showcase/, two export_replay.py | Judges see the kill test as a picture | both replays render in headless Chrome; site tests pass |
| 45 | done ae0065e | Altitude: window-and-bar family, 3D A* picks altitude, vs 2.5D planner | P | M | - | samples/close-area-arena world_z.py, planners/astar_esdf_3d.py, vehicle_z.py | IMAV elements are over/under/through | 2.5D vs 3D reach, plan ms, side-view PNG |

| 46 | done 64bddae, 47400b5 | Complex arenas: office, warehouse, forest, maze, glass_office + world JSON format (a); benchmark matrix of every algorithm x every arena with replay export (b) | P | M | 01 B | samples/close-area-arena worlds_complex.py, world_json.py (a); samples/close-area-benchmark/ (b) | Ivan asked for 3-4+ harder arenas | 5 families, preview PNG, sanity table; matrix table |
| 47 | done e844e9f | Showcase v2: replay picker grouped by arena and algorithm, side-by-side compare | T | S | 46b B | site/showcase.*, site/data/showcase/ | Ivan liked the replay; more arenas and algorithms | renders in headless Chrome; site tests pass |
| 48 | done f40bc12, 8d9011d | Playground: Pyodide runs the real arena code in the browser; editor (draw obstacles, A/B, presets), pick planner / sensor / fault / filter, run + replay + score; compare mode | T | M (a spike, b editor+run, c compare) | 46a soft | site/playground/ | Ivan asked for a playground | 48a timing verdict; 48b working page on Pages |
| 49 | done ae4aa6d | DWA and Bug2/TangentBug local planners vs APF/VFH+ (72 and 4 beams) | P | S | - | samples/close-area-planner-dwa-bug/ | Nav2 default local planner and classic complete planners | table on 3 families x 2 fans |
| 50 | done 8bcecad | D* Lite incremental replanning vs A* from scratch on unknown maps | P | S | - | samples/close-area-planner-dstar/ | Does incremental search matter here | table + plan-time comparison |

| 51 | done 2544945 | flight-repo arrival gating: 'arrived' only with healthy nav (or adapter-confirmed), pass NavHealth to the safety arm; rerun first-flight-jump | T | S | 36 B | templates/flight-repo/flightloop/loop.py, safety_shim.py, results/ | Under a VIO jump the loop declares arrival 0.63 m from B | first-flight-jump reaches B or hovers, never false-arrives |

| 52 | done 5887392 | Sweep 3: verdict + new results into evidence matrix, decoder, cheat sheet, intake, Challenge 2, research docs, sample.json | S | S | 37 B | shared docs (see brief) | Agents must see the final verdict, not seed-0 claims | gate green; no stale 'running/pending' lines |

| 53 | done 66ad30e | 46c: DWA, Bug2/TangentBug, D* Lite added to the benchmark matrix and replays | P | S | 46b, 49, 50 B | samples/close-area-benchmark, site/data/showcase/replays_v2 | Every algorithm on every arena | new matrix rows + replays |

| 54 | done 5a9e222 (FAIL on 4 beams) | Relocalization on a 4-beam Crazyflie-like sensor: the matcher needs >= 10 returns per scan, a Multi-ranger gives 4; accumulate scans during a slow yaw spin (or a short motion) and match the stacked returns; measure recovery on crazyflie preset | P | S | 22, 32 B | samples/close-area-relocalize new files + README section | The headline must work on the likeliest hardware (judge drill Q6 found the gap) | reached / wrong commits on crazyflie preset vs ideal |

| 55 | done (FAIL: 7 % collisions with unmapped obstacles) | Relocalization vs an imperfect map (removed / added / shifted obstacles, self-built map) | P | S | 33 B | samples/close-area-relocalize map_perturb.py, run_stalemap.py | Intake default = moved obstacles | table per rung, FAIL accepted |
| 56 | done 878c841 (holds on random/u_trap only) | Relocalization held-out matrix: seeds 2-4 x 7 families x 2 faults + severity rungs, Wilson intervals | P | S | 33, 46a B | samples/close-area-relocalize run_matrix.py | Drill Q3 rests on one held-out seed | 42 cells with intervals |
| 57 | done (mechanism exists: Jensfelt 2001, AF-MCL 2026) | Relocalization prior-art kill search + EKF2/EKF3 reset_counter in code | R | S | - | docs/research/close-area-nav/10-relocalization-prior-art.md | The second headline never had its search | verdict + code file/line |
| 58 | done (36 min fresh-clone run, 8 blockers listed) | Day-1 dry run, agent only, fresh clone, timed | A | S | - | docs/day1-dry-run.md | H+0..H+2 never run end to end | measured runbook + blockers |
| 59 | done b2c4127 | flight-repo --reloc pose source + reset_counter through the bridge (dry run) | T | S | 33, 51 B | templates/flight-repo reloc_shim.py etc. | Product shape; closes first-flight-jump unconfirmed | jump run reaches B or hovers |
| 60 | done (yaw search 100 % at 10 deg bias; 180 deg case fails) | Yaw search in the relocalizer (+-15 deg lattice), yaw bias 5/10 deg, 180 deg case | P | S | 33 B | samples/close-area-relocalize relocalize_yaw.py, run_yaw.py | 'yaw is truth' is the first judge question | table + ms per scan |
| 61 | done 2a3df1d | Sweep 4 (45a, 46b/c, 47, 49, 50, 54 + 55-57 when landed) | S | S | 53 B; 54-57 soft | shared files | decode warehouse 4 beams => benchmark | gate green, no stale pending |
| 62 | done 7d0fbc0 | Playground: 6 more planners + shareable #w= links | T | S | 48b B | site/playground | 6 of 14 planners; no sharing | parity on 6 new; link restores world |
| 63 | done 67faf17 | Playground relocalization with hypothesis ghosts | T | M | 62, 33 B | site/playground (after 62) | Headline invisible in playground | browser = native on 3 cases |
| 64 | done d45f67c | Showcase story page: headline status, kill-test replay, relocalization replay | T | M | 47 B | samples/*/export_replay.py, site/showcase.* | Judges see the pivot as pictures | both replays render |

| 65 | done (wired into the playground) | Playground advisor: per-map success/collision stats for every planner, ranked recommendation, plain-language docs for every option (Ivan request) | T | S | 46c B; 62 soft (driver wires in after 62 lands) | site/playground advisor.* data/ ADVISOR.md advisor-demo.html | Ivan: most planners fail in maze/office; a non-expert cannot choose | demo page renders; wired into the playground |

| 67 | done 1ab503b | AF-MCL-style particle filter arm vs the hub's relocalizer (ideal and 4-beam) | P | S | 57 B | samples/close-area-relocalize mcl.py, run_mcl.py | Published baseline the headline never faced | table + verdict |

| 68 | done aa1beb0 (FAIL; best 4-beam arm 66-89 %) | Relocalization on 4 beams via a rolling submap built while moving (vs spin and MCL) | P | S | 54, 67 B | samples/close-area-relocalize submap.py, run_submap.py | The headline must survive the likeliest drone | >= 90 % and 0 wrong commits on crazyflie, or FAIL |
| 69 | done 239333a + 69b seed jitter | Solver page: run every planner x variation on one map in a worker pool, race view, result matrix + ranking | T | S | 62 B | site/solver | Ivan: pick the best planner for a given map on the day | no-clear-winner rule; phone width; export |
| 70 | done (Theta*: faster with prior map, too slow unknown) | Theta* / Lazy Theta* planner sample (any-angle) | P | S | - | samples/close-area-planner-thetastar | Ivan asked for more algorithms; any-angle vs A* + shortcut | 8 families, Pyodide-safe |
| 71 | done (MPPI+A*: faster, same reach; 4-beam collisions) | MPPI planner sample (sampling MPC, numpy, browser-safe) | P | S | - | samples/close-area-planner-mppi | MPC sample needs osqp, not in browser; local-minimum fix? | 8 families + K/horizon sweep |
| 72 | done (Hybrid A*: 81.9 vs 91.2 % reached, no collision gain) | Hybrid A* planner sample (turn-rate limited) | P | S | - | samples/close-area-planner-hybrid-astar | feasible paths vs A* + follower | 8 families + curvature stats |
| 73 | in-flight | Wire 70-72 into playground worker/manifest and benchmark matrix | T | S | 69, 70, 71, 72 B | site/playground, samples/close-area-benchmark | new planners show in solver automatically | parity browser = native |

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
