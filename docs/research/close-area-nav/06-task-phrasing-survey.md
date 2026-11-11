# Close-area A=>B: how real events specify the task

Lane 6 of the close-area research pass (2026-11-09). Question: when an event asks a
drone to go from A to B in a confined space, how does it state B, the arena, the
sensors, the compute rule and the score? Goal: guess the likely shape of a new close-area task and
ask whoever set it the right questions. This extends the competition table in
[02](02-sims-platforms-competitions.md) section 3 and replaces the "no primary source was
searched" note in [03](03-close-area-localization.md) section 3.

Nothing here was run. Every number below is quoted from the cited source. No number is a
measurement by the hub.

**Source labels:** [rules] = official rulebook or handbook, [docs] = official event or project
page, [code] = repository file read via `gh api`, [forum] = an answer from the event's own staff in the official
GitHub discussions, [preprint] = arXiv, [news] = press or team blog. "Full" = the whole text
was read; "part" = only the sections named; "abstract" = abstract only.

**PDF extraction.** The machine has no PDF tools and nothing was installed. PDFs were piped
through a stdlib zlib + text-operator parser, never saved. Where that was rough it is said in
the row. The worst cases: IMAV 2026 (words run together; the weight-factor formula did not
extract), ICUAS 2026 (glyph-ID font, decoded with a fixed offset; prose is clean), Teknofest
2026 (scoring Table 3 not extracted) and the RECF quick guide (score table columns may be
misaligned).

## TL;DR

- **B is almost never a bare coordinate.** In 11 events, B is a marker or object to detect
  (IMAV indoor, ICUAS, Teknofest, SUAS delivery, RECF, IEEE R5), an ordered gate list with
  nominal positions (LSY, IROS ADR, A2RL), or an area to search (MBZIRC, ENRICH, ICUAS).
  Plain coordinates appear for the route, not the goal: SUAS GPS waypoints handed out at
  check-in, LSY nominal poses in a TOML file, the IEEE R5 grid cell shown at run start.
- **The layout is usually known; exact poses are not.** LSY gives nominal gate and pole
  positions and reveals the exact pose only within 0.7 m [code]. ICUAS ships the world as an
  octomap [code]. IMAV publishes a top view of the cage and lets the team pick bar heights
  [rules].
- **Compute rules are explicit and priced.** IMAV: autonomy factor 1.0 onboard, 0.7 off-board
  compute or beacons, 0.4 any manual action [rules]. Teknofest: 1.0 fully autonomous, 0.7 if
  take-off or landing is manual [rules]. IEEE R5 runs two divisions, onboard-only vs a
  standalone off-board computer [rules]. A2RL requires onboard compute (Jetson Orin NX) [docs].
- **Scores reward completion and accuracy first, then speed.** Time is the primary score only
  in the racing events (LSY, IROS ADR, A2RL). Elsewhere time is a weight or a tie-break.
- **Most likely task shape:** fly to a marked B (pad or tag) in a small known arena with a few
  static obstacles, sim or a small drone, with an onboard-vs-offboard penalty. See section 3.

## 1. Survey table

One row per event, latest edition found. "A / B" is how start and goal are stated.

| Event, year | A and B | Arena, obstacles | Sensors allowed | Compute rule | Scoring | Primary link |
|---|---|---|---|---|---|---|
| IMAV indoor, 2026 [rules, part, rough] | A = team's landing area. B = mission elements (windows, bars, pipe, dark room, hot box, turbine ring), then optional landing on an 80 x 80 cm ArUco 5x5 ID 0 platform. A mission counts only once the drone is back on its landing area | 14 x 7 x 4 m net cage in a hall with 7.90 m ceiling. Static, known layout (top-view figure), bar heights chosen by the team. Platform static, 0.1 m/s translation, or 10 deg pitch plus translation. Textured wallpaper floor "to improve navigation" | Free. Team beacons (UWB etc.) allowed but cut the autonomy factor to 0.7. Max 3 kg | A = 1.0 all onboard; 0.7 off-board compute or beacons; 0.4 any action (mode change, switch, GCS) | Per mission max 20: completion up to 7 x A, x mass factor 1.13 (3 kg) to 2.0 (0.1 kg), + landing 1 static / 2 moving, + multi-mission 1 or 2, + self-made up to 2. Mission 1: 1 pt red window, 0.5 pt blue, bars 0.25 / 0.5 / 0.75, tubes 0.5. 30 min slot | [Rulebook V3](https://2026.imavs.org/wp-content/uploads/2026/07/Rulebook_IMAV2026_V3.pdf) |
| IMAV outdoor, 2026 [rules, part, rough] | Exact GPS points of zones and landing areas "provided on the day of the competition". Reported positions must be in decimal degrees | Geofence of four GPS corners given in the rulebook. 80 m max altitude | Free | Same A factors | Positions count if within 5 m. Landing zone for multicopters 1 x 1 m precision, 3 x 3 m zone, ArUco 80 x 80 cm | same PDF |
| ICUAS UAV competition, 2026 (sim phase) [rules full, forum, code] | A = base. B = unknown number of ArUco markers (threats) to find and report, ArUco landing spots, decoy markers. Ground vehicle position published live | Known urban world (octomap supplied). Size not stated in rulebook v1.0. Obstacles static; touching them is penalised | Only the provided camera, UAV pose and octomap; model edits not allowed (#49) | Team code as ROS 2 nodes in a Docker image, run on the organisers' machine (Gazebo, ROS 2 Humble, Crazyflies in CrazySim) | Run void on crash, battery below 20 %, out of bounds, landing off a spot. Points per benchmark (detection, connectivity, time) finalised later. Organiser gist of 2025: about 30 connectivity + 70 detection, weighted by time (#46). Full detection points within about 15 cm, none beyond about 1 m, "may vary across worlds" (#34) | [Rulebook PDF](https://github.com/larics/icuas26_competition/tree/main/rulebook), [discussions](https://github.com/larics/icuas26_competition/discussions) |
| Teknofest International UAV, rotary wing, 2026 [rules, part, rough] | A = runway take-off. Mission 1: two laps of a figure-eight around reference poles 1 and 2. Mission 2: two targets "whose locations are unknown", found by image processing; drop a payload on each | Outdoor airfield (Malatya Tulga). Targets: blue hexagon 2 m side, red triangle 1 m side | One camera on the auxiliary computer; a second camera is "strictly prohibited". GNSS used | Image processing "from the air or ground" allowed. Coefficient c: 1.0 autonomous take-off, flight and landing; 0.7 manual take-off and/or landing with autonomous flight | Mission 1: storage box volume, unpacking time, weight, lap time (formula in Table 3, not extracted). Drop distance measured from target centre, up to 10 m. Hits without proven image processing score 0. 8 min set-up limit | [Spec EN 2026](https://cdn.teknofest.org/media/upload/userFormUpload/2026_%C4%B0HA_Yar%C4%B1%C5%9Fmalar%C4%B1_%C5%9Eartnamesi_EN_VBU_Ee7DO.pdf) |
| TUM LSY drone racing, 2026 (`main` at 3027337) [code, full] | A = start pose (randomised by +-0.1 m). B = gates in a given order and direction (`gate_order = [1, 2, 3, 4, 2]` at level 2) | Safety box x +-2.5, y +-1.5, z 0 to 2.0 m. 4 square gates (0.4 m opening), 4 poles 0.03 m wide. Level 2: gates and poles shifted +-0.15 m from nominal; exact pose revealed within `sensor_range = 0.7` m. Level 3: track randomised, known only at runtime | Sim: state observation. Real: Vicon pose of drone, gates and poles | Python controller; on hardware run by `deploy.py` on the ground PC (inferred from deployment docs) | Online leaderboard: fastest submission with at least 50 % success rate, on level 2 | [overview.md](https://github.com/learnsyslab/lsy_drone_racing/blob/main/docs/challenge/overview.md), [level2.toml](https://github.com/learnsyslab/lsy_drone_racing/blob/main/config/level2.toml) |
| IROS Autonomous Drone Race, 2018 and 2019 [preprint full, news] | Ordered gate course. 2018: 8 gates. 2019: laps of a gate set | Indoor. Rulebook not found | Onboard sensing (hub record of Moon 2019, abstract only) | Winner's 2018 stack ran onboard (Kaufmann 2018); the rule itself not read | 2018: time; winner 31.8 s, second 61 s, third 90.1 s [preprint]. 2019: most runs in five minutes; winner 15 runs in 4:47, second 14 in 4:42 [news] | [Kaufmann 2018](https://arxiv.org/abs/1810.06224), [UMD 2019](https://isr.umd.edu/news/story/student-autonomous-drone-racing-team-takes-2nd-place-at-iros) |
| A2RL drone, season 1 (Apr 2025) and 2 (Jan 2026) [docs, news] | Gate track. S1: 22 gates on a 170 m course. S2: 14 gates, ladder and split-S obstacles; announced "dynamic obstacles and mission-style tasks" | Indoor hall (ADNEC). S1: wide gate spacing, inconsistent light, few visual markers | Single front-facing camera + IMU, no GPS, no remote control (official blog). No lidar or stereo [news] | Onboard NVIDIA Jetson Orin NX; no external compute [news] | Race time. S1 best 17.225 s over 22 gates. Formal rulebook not public | [A2RL drone page](https://a2rl.io/autonomous-drone-race), [S1 blog](https://a2rl.io/blog/5/a2rl-drones-season-1-when-the-sky-wasnt-the-limit) |
| IEEE Region 5 student contest (Tello), 2021 [rules, full] | A = hand launch outside the grid. B = four coloured balloons; judges screen-share each balloon's grid cell and the order only at run start. Pop them in order, then land on a deflated one | 3 x 3 m floor, at least 2 m headroom, 1 x 1 m numbered grid. Balloons 1 to 2 m high. Mission Pads not allowed in or touching the grid | DJI Tello or Tello EDU, factory motors, props, batteries | Division A: no comms with any device. Division B: one standalone off-board computer, no human input | 1 pt per balloon in correct order, +1 for landing on a popped balloon. Ends on wrong order, touch, landing, 3 min, leaving camera view. Tie-break: shortest time | [Rules V4 PDF](https://dfc3f084-31d4-418a-8426-e5b4a3d7ef9b.filesusr.com/ugd/2898c3_d846e340f0784f3a91d22469bc16a43c.pdf) |
| RECF Aerial Drone Competition, autonomous flight, 2026 [rules, quick guide only, rough] | Fixed field elements: arch gates, keyholes, tunnel, colour mats to identify, panel; end on one landing option (cube, bullseye or pad) | Field size not read (full manual not fetched) | Not read | Team starts the program from a computer, then may not touch drone, controller or computer except for resets or e-stop | 3 min match, resets allowed with timer running. Task values 5 to 40 pts (take-off 5, tunnel 25, panel 40, landing 5 to 15 as extracted) | [Quick guide 2026](https://recf.org/documents/2025/09/autonomous-flight-mission-2026-aerial-drone-competition.pdf/) |
| MBZIRC Maritime, 2023 [preprint full] | A = base / USV. B = one target vessel among seven types, position unknown; find it, then intervene | 4 km2 sea area, 60 min mission. Moving vessels | Limits on number of UAVs and payload sensors (values not in the paper). No GNSS for positioning; short-range comms only | Not stated in the paper | Not read (official rules not fetched) | [Peti et al. 2023](https://arxiv.org/abs/2306.12767) |
| AUVSI SUAS, 2026 [rules, part] | A = runway (40 x 500 ft or 40 x 40 ft VTOL pad). Route = GPS waypoints with altitudes, up to 15 per lap, about 2 miles, given at check-in; pass within 100 ft. B for delivery = a mannequin and a tent to detect in a search boundary | GPS polygon flight boundary, 150 to 400 ft AGL; out of bounds ends the mission. Search boundary about 10 acres. Trees up to 100 ft | Free (team payload). GCS display of position, speed, altitude mandatory | Not restricted. Fewer operators score more | Mission 1000 pts: endurance 250 = 20 (take-off and landing) + 30 (all autonomous) + 200 x (N_L/10)^2 for N_L of 10 laps; operators 200 x min(1, (4 - O)/2); rapid response 200; risk mapping 150; delivery 2 x 100 = 20 survive + 50 within 50 ft + 30 correct target. Docs 250 | [2026 handbook](https://robonation.gitbook.io/suas-resources/2026-team-handbook) |
| ENRICH (industrial indoor inspection), 2025 [docs, full page] | UAV and UGV start from the same point. B = radiation sources to find and map, a 3D map, dummies to find, a valve to close | Real never-operated nuclear plant (Zwentendorf): low or no light, closed doors, dead ends, stairs, narrow passages. Unknown interior | Radiation sensor mandatory or no start. GoPro mount required | Comms hard (concrete, metal); no one may accompany the robot; about 30 min per run | No point formula; judges' awards. Deliverables: map readable in CloudCompare, ROS bags | [ENRICH 2025](https://enrich.european-robotics.eu/enrich-2025/) |

## 2. Patterns that matter for a new task

**How B is given.** Four forms recur:

1. *Marker or object at B*: IMAV ArUco pad, ICUAS ArUco markers and landing spots, Teknofest
   coloured shapes, SUAS mannequin and tent, IEEE R5 coloured balloons, RECF colour mats and
   landing pad. The drone needs a detector plus odometry good enough to get it in view.
2. *Coordinates handed out late*: SUAS waypoints at check-in, IMAV outdoor GPS points on the
   day, IEEE R5 grid cells at run start. Code must accept B as input; no hard-coded path.
3. *Nominal positions, exact pose seen up close*: LSY level 2 (0.7 m reveal), IROS ADR gate
   layout. This is the "known map, wrong by 15 cm" case.
4. *Search*: MBZIRC, ENRICH, ICUAS. B's position is the unknown.

**Goal tolerance is always stated.** 15 cm full, 1 m cut-off (ICUAS, organiser answer); 100 ft
(SUAS waypoints); 50 ft (SUAS drop); 5 m (IMAV outdoor GPS report); 1 x 1 m pad (IMAV outdoor);
10 m measuring radius (Teknofest). If your task does not state one, ask.

**Off-board help is penalised, not banned.** IMAV 0.7, Teknofest 0.7 for manual take-off or
landing, IEEE R5 separate division. Only A2RL mandates onboard. Beacons (UWB) are allowed at
IMAV but cost the same 0.7.

**Disqualifiers are crash, out of bounds and human touch.** ICUAS voids a run on any crash or
leaving bounds; SUAS ends the mission out of bounds; IEEE R5 ends on any touch. A geofence and a
"stop and hover" fallback are worth more than speed.

**Time limits are short.** 3 min (IEEE R5, RECF), 5 min (IROS 2019), 30 min slot (IMAV,
ENRICH), 8 min set-up (Teknofest). The first attempt has to work.

## 3. Ranked task shapes

Ranking is judgement, from how often each shape appears above and how easy it is to judge in
one day. Not verified against any specific upcoming task.

1. **Marked B in a small known arena, few static obstacles.** "Take off at A, fly to the pad /
   tag at B, avoid the boxes, land." Seen at IMAV indoor, ICUAS, IEEE R5, RECF. Likely scored on
   completion, landing accuracy, collisions, autonomy. Hub material: lane 01 grid A* + ESDF
   planner ([01](01-planning-and-mapping.md)); AprilTag/ArUco goal and PX4 `LANDING_TARGET`
   notes ([03](03-close-area-localization.md) section 3); gym-pybullet-drones or PX4 gz
   `walls` world ([02](02-sims-platforms-competitions.md) section 1); Tello path
   `repo:damiafuentes/djitellopy` + `res:tello-sdk-2-user-guide`.
2. **B as coordinates given at the start, reach within a tolerance, stay inside a geofence.**
   Seen at SUAS, IMAV outdoor, IEEE R5. Hub material: `samples/sitl-docker` and
   `samples/golden-demo-px4` for MAVLink offboard; `samples/llm-mission-agent` vehicle tools
   (goto, geofence, altitude band, SITL only); lane 03 VIO-to-EKF path and
   `samples/vio-to-mavlink-bridge` if indoors without GNSS; frame alignment note in lane 03
   (an AprilTag at A gives the venue frame).
3. **Ordered waypoints or gates, nominal positions known, exact poses shifted.** Seen at LSY,
   IROS ADR, A2RL. Scored on time with a success-rate floor. Hub material:
   `repo:learnsyslab/lsy_drone_racing` (levels 0 to 3, crazyflow sim), lane 01 replanning at
   2 to 5 Hz, lane 04 replan trigger.
4. **Find B, then go there.** Search a room or area for an object, report or land on it. Seen at
   ICUAS, MBZIRC, SUAS, ENRICH. Hub material: thinnest coverage. Lane 01 for mapping
   (OctoMap, unknown-is-not-free), `repo:osrf/mbzirc` for a reference sim, a detector chosen once
   the real target is known. Exploration planners are not covered by a sample.

All four shapes share one need: B must be a runtime input, and the drone must stop safely when
its estimate is bad. That supports the lane 04 safety-filter headline under every shape.
**Refuted since for the headline (synthetic):** the lane 04 filter failed its kill test on
held-out seeds (2.5 % [1.1, 5.7] jump collisions vs <= 1.0 % for a fixed 0.2 m bound,
[safety-filter Part e](../../../samples/close-area-safety-filter/README.md#part-e-held-out-seeds-and-families-ran-2026-11-09-synthetic));
the "stop safely" need stands, the pitch choice is in the
[research decision](../README.md#decision-2026-11-09-evening-what-the-close-area-innovation-claim-is).

## 4. Questions for whoever set the task (revised)

Start-point list from the [README](README.md), regrouped and extended with what the events
above made explicit. Ask in this order; the first group decides the stack.

**Platform and setting**
1. Which drone and SDK? Real flight, sim, or both? If sim, which simulator, and does it run on
   our laptop or yours (Docker image submitted, as ICUAS)?
2. Indoor or outdoor? Arena size and height, net or open, floor texture?

**How A and B are given**
3. Is B a coordinate, a marker, a GPS point, or something to find? In which frame (start
   frame, venue / mocap frame, WGS84) and units?
4. When is B revealed: before the task starts, at check-in, or at run start? Can B change between runs?
5. What counts as "at B": hover within a radius, land on a pad, touch? What radius or pad size?
6. Are markers (AprilTag, ArUco) at A or B provided, allowed, or forbidden? Are our own beacons
   (UWB, tags) allowed, and do they cost points?

**Obstacles and environment**
7. Obstacles known in advance (map file, drawing) or unknown? Static or moving? Do positions
   change between runs, and by how much?
8. Does touching an obstacle end the run or cost points? Is there a geofence, and what happens
   at the boundary?

**Sensors and compute**
9. Which sensors are on the drone (camera, depth, lidar, flow, rangefinder, GNSS)? Is ground
   truth or mocap pose available, and to whom? Can we add sensors?
10. Must planning run onboard, or may a laptop run it? Is off-board compute penalised (as IMAV
    0.7)? Link type and latency to the laptop?

**Scoring and runs**
11. What is scored and with what weights: completion, time, accuracy, collisions, autonomy,
    innovation, presentation? Is speed a primary score or a tie-break?
12. Does any human action (mode switch, takeover, restart) void the run or scale the score?
13. How many attempts, how long per attempt, set-up time, resets allowed? Best or average run?
14. Do you want logs, a map, or a reported position of B as a deliverable?

## 5. Not verified

Reconciled 2026-11-09: no sample measures event rules, so every bullet below is still
open. The one body claim a sample contradicted is marked in section 3.

- IMAV 2026 weight-factor formula and the exact total-score formulas (garbled in extraction;
  component values match across the four mission tables).
- ICUAS 2026 final scoring and finals format: rulebook v1.0 says both were to be announced
  later. Thresholds of 15 cm and 1 m are an organiser forum answer, not rulebook text.
- ICUAS world size; RECF field size and drone; SUAS rapid-response and risk-mapping formulas.
- Teknofest mission score formula (Table 3 not extracted); whether its target coordinates are
  ever given.
- IROS ADR rulebooks for any year; the onboard-sensing rule rests on the hub's Moon 2019 record
  (abstract) and the winner's paper, not on rules text.
- A2RL rules: no public rulebook found. Sensor and compute limits come from the official blog
  and one news article.
- MBZIRC scoring and sensor limits: only a team preprint was read, not the official rules.
- ENRICH award criteria beyond the event page.
- A DJI RoboMaster contest: none with public rules was found in this pass; IEEE R5 2021 (Tello)
  stands in. A newer IEEE R5 edition may differ.
- LSY compute location on hardware is inferred from `deploy.py` usage, not stated as a rule.

## 6. Records added

The competition-rules lane file in `data/resources/`: ICUAS 2026 rulebook, Teknofest 2026 UAV specification, IEEE R5
2021 Tello rules, A2RL drone championship page, SUAS 2026 handbook, Peti 2023 MBZIRC preprint,
ENRICH 2025 page, Kaufmann 2018 IROS ADR preprint, RECF 2026 autonomous flight quick guide,
UMD IROS 2019 news.
