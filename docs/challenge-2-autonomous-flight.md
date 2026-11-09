# Challenge 2 "Autonomous Frontiers": entry point

Start here when the task is the EDGE Group internal hackathon, Challenge 2. This page narrows
the hub to what fits an autonomous flight navigation product and routes the full brief to the
right decoder rows, samples and guides. Agents: read this before running `decode`, and prefer
the rows, samples and guides listed here over the rest of the hub.

Snapshot 2026-11-09. The full brief drops on Day 1 (18 Nov 2026); re-route with section 3 then.

**Update 2026-11-09: likely task.** Additional information says the task is probably "move a
drone from A to B in a close area, potentially with obstacles". Start from
[research/close-area-nav](research/close-area-nav/README.md): baseline planner, sims, local
localization, and the proposed headline (an integrity-aware safety filter). The long-range
GNSS-denied material below stays as the fallback if the full brief says otherwise.

## 1. The brief as published before Day 1

> Develop an innovative navigation algorithm for an autonomous flight and navigation product.
> The winning team will have the opportunity to take its solution towards real-world
> implementation. Recommended expertise: software, electrical and electronics, guidance,
> navigation and control (GNC), propulsion, aerospace engineering, applied mathematics and
> applied physics.

How to read it:

- **"navigation algorithm"** - the core is state estimation, but "GNC" and "propulsion" in the
  expertise list mean guidance and the vehicle's own physics may be in play. Do not assume
  GNSS-denied until the brief says so.
- **"autonomous flight ... product"** - an aircraft, platform unknown until Day 1 (multirotor,
  fixed-wing or VTOL). Ask what it carries: IMU grade, camera, radar altimeter, airspeed,
  flight computer.
- **"real-world implementation"** - an EDGE entity may take the winner towards a product. Two
  consequences: licenses must allow commercial use, and the pitch needs a "how this runs on
  the aircraft" story, not only a SITL result.
- **"innovative"** - satellite-image matching alone is a commodity demo
  ([landscape](landscape/gnss-denied-nav-products.md)). Lead with a differentiator.

## 2. Scope line

Navigation and guidance of the vehicle's own flight only. Weapon terminal guidance, homing,
intercept guidance and targeting are out of scope for this hub and for our entry, even if a
product line the brief names is close to them. See
[export-control-and-ethics.md](export-control-and-ethics.md).

## 3. Day 1 routing: the full brief says... => open

| Words in the full brief | Decoder rows | Open first |
|---|---|---|
| "point A to B", "obstacles", "indoor", "arena", "close area", "avoid" | none yet | [close-area-nav synthesis](research/close-area-nav/README.md), [planning and mapping](research/close-area-nav/01-planning-and-mapping.md), [sims and platforms](research/close-area-nav/02-sims-platforms-competitions.md), [localization](research/close-area-nav/03-close-area-localization.md) |
| "without GPS / GNSS-denied", a distance or route, multirotor | 1, 2 | [gnss-denied-drone-nav cheat sheet](cheatsheets/gnss-denied-drone-nav.md), [e2e-visual-nav-vpair](../samples/e2e-visual-nav-vpair/), [golden-demo](../samples/golden-demo/) |
| "fixed-wing", "long range", "20-30 km", "endurance" | 27, 15, 25 | [golden-demo-fixedwing](../samples/golden-demo-fixedwing/), [terrain-heightmap-pf](../samples/terrain-heightmap-pf/), [terrain-night-celestial cheat sheet](cheatsheets/terrain-night-celestial.md) |
| "spoofing", "integrity", "trust", "assured" | 4, 20 | [spoofing-keep-flying cheat sheet](cheatsheets/spoofing-keep-flying.md), [multi-source-fde](../samples/multi-source-fde/), [autopilot-gnss-fault-handling](autopilot-gnss-fault-handling.md) |
| "drop-in", "COTS autopilot", "PX4", "ArduPilot" | 20 | [vio-to-mavlink-bridge](../samples/vio-to-mavlink-bridge/), [golden-demo-px4](../samples/golden-demo-px4/), [autopilot-resilient-configs](../samples/autopilot-resilient-configs/) |
| "night", "thermal", "no light", "no RF" | 16, 18, 25 | [thermal-geolocalization](../samples/thermal-geolocalization/), [magnav-quickstart](../samples/magnav-quickstart/), [celestial-star-tracker](../samples/celestial-star-tracker/) |
| "how long after GNSS loss", "holdover", "IMU grade" | 26 | [gnss-ins-ekf-outage](../samples/gnss-ins-ekf-outage/), [relative-nav-benchmark](../samples/relative-nav-benchmark/) |
| "guidance", "path planning", "trajectory", "control", "energy" | proposed rows in the guidance guide | [guidance-planning.md](guidance-planning.md) |
| "propulsion", "dynamics", "physics", "model-based", "low-cost IMU" | none yet | [differentiators-scan.md](differentiators-scan.md) |
| "product", "onboard", "embedded", "certifiable", "real-time" | none | [path-to-product.md](path-to-product.md) |
| "swarm", "multiple drones", "cooperative" | 10, 11 | [swarm-cooperative cheat sheet](cheatsheets/swarm-cooperative.md) |

If two rows fit, score both with the [day-0 rubric](day0-runbook.md#2-pick-the-idea-scoring-rubric).

## 4. The working set

These samples fit an autonomous flight entry. Status, first command and the key measured
result are in [samples/README.md](../samples/README.md); quote numbers only from the
[evidence matrix](evidence-matrix.md), which marks real vs SITL vs synthetic input.

| Need | Sample | Input |
|---|---|---|
| Full visual nav chain on one real flight | [e2e-visual-nav-vpair](../samples/e2e-visual-nav-vpair/) | real flight |
| Spoof detect => EKF3 source switch, multirotor | [golden-demo](../samples/golden-demo/) | SITL |
| Same on PX4 EKF2 | [golden-demo-px4](../samples/golden-demo-px4/) | SITL |
| Same on a 27.6 km fixed-wing route | [golden-demo-fixedwing](../samples/golden-demo-fixedwing/) | SITL |
| Exclude a faulty source and keep flying | [multi-source-fde](../samples/multi-source-fde/) | real flight + injected faults |
| Second absolute source makes the protection level usable | [two-source-integrity-vpair](../samples/two-source-integrity-vpair/) | real flight, simulated TRN sensor |
| Onboard autopilot configs ranked under GNSS drag | [autopilot-resilient-configs](../samples/autopilot-resilient-configs/) | SITL, 156 flights |
| Terrain-relative nav on real terrain | [terrain-heightmap-pf](../samples/terrain-heightmap-pf/) | real DEM, simulated flight |
| Lost-UAV retrieval over a large area | [vpr-large-area](../samples/vpr-large-area/) | real imagery |
| Measured VO / VIO drift models | [relative-nav-benchmark](../samples/relative-nav-benchmark/) | real datasets |
| Pose into PX4 / ArduPilot | [vio-to-mavlink-bridge](../samples/vio-to-mavlink-bridge/) | stationary SITL check |
| Simple GNSS/INS EKF and outage | [gnss-ins-ekf-outage](../samples/gnss-ins-ekf-outage/) | synthetic |
| SITL images | [sitl-docker](../samples/sitl-docker/) | - |

Not for this challenge unless the full brief asks: timing, maritime / AIS, counter-UAS and
Remote ID, jammer maps, TAK-only pictures, dismounted and indoor navigation. The decoder will
route to them on keyword overlap; skip those rows.

## 5. What the pre-Day-1 research added

Three lanes added on 2026-11-09, each with its own records and a guide. Read the guide's own
"not verified" section before quoting it.

- **[differentiators-scan.md](differentiators-scan.md)** - eight candidates ranked for novelty,
  48h buildability, open data and commercial license. Top pick: **propulsion and drag as a
  virtual velocity sensor** (score 22/25). The demo is "GNSS off, keep flying on the
  airframe's physics", measured as time from GNSS loss to 50 m error. It has to be our own
  filter: ArduPilot EKF3's drag fusion only updates wind states, not velocity (correction in
  the scan, section 2.1); ArduCopter 4.6.3 SITL still models drag, so it can generate logs. Runner-up: learned
  inertial odometry with rotor speed (AI-IO, MIT), cross-checked against the physics model so
  it cannot fail silently. Both answer the brief's "propulsion / applied physics" wording.
- **[guidance-planning.md](guidance-planning.md)** - the G in GNC: trajectory generation, MPC,
  fixed-wing guidance, energy and wind. Five 48h ideas (G1-G5) tied to existing samples, and
  five decoder rows marked "proposed, not yet merged". Strongest: G1, routes chosen so terrain
  navigation keeps working (`ethz-asl/terrain-navigation2` + the information gate in
  [terrain-heightmap-pf](../samples/terrain-heightmap-pf/)). No open belief-space planner was
  found; write a small covariance-propagation one instead.
- **[path-to-product.md](path-to-product.md)** - how a nav algorithm runs on the aircraft:
  compute table with cited latencies (vendor claims marked), the four integration paths into
  PX4 / ArduPilot (PX4 `AuxGlobalPosition` takes up to 4 tagged alt-nav fixes), time sync and a
  latency budget template, a plain-language certification map (DO-178C, DO-254, DO-160,
  ASTM F3269, EASA AI concept paper, SORA, STANAG 4703), the runtime-assurance pattern (ship
  the new algorithm next to a trusted baseline; ArduPilot's `ahrs-source.lua` is a working
  switch), license traps, and a 7-bullet "path to product" slide.

Deeper prior-art round (2026-11-09): [research/innovation-prior-art/](research/innovation-prior-art/README.md)
checks what already exists for each candidate, the strongest baseline and a falsifier, and
recommends the POC set.

For the close-area A=>B task, use the shape in
[research/close-area-nav](research/close-area-nav/README.md#recommended-direction) instead.
For a long-range GNSS-denied brief, the suggested shape is: differentiator 2.1 as the headline,
the runtime-assurance monitor from path-to-product as the safety story, and G2 (integrity drives
guidance) as the stretch.

## 6. Product constraints for the entry

- **New repo on Day 1** from [templates/project-repo](../templates/project-repo/). Copy in only
  the samples you build on; this hub stays the knowledge base.
- **Licenses.** SuperPoint weights are non-commercial: use ALIKED + LightGlue. VPAIR is
  academic-use only: fine for evaluation, not for training a shipped model. ArduPilot is GPLv3,
  PX4 is BSD-3. Details: [model-weights-licenses.md](model-weights-licenses.md),
  [dataset cards](dataset-cards/README.md).
- **Honest numbers.** Every number in the pitch carries its input type. Never present SITL or
  synthetic results as flight results.

## 7. Rehearsal before Day 1

Pick one bundle from [starter-bundles.md](starter-bundles.md) and run it end to end on the
laptop that goes to the event, from a fresh shell, with timings written down.

Recommended: **`vehicle-sim`** ([golden-demo](../samples/golden-demo/) v2 on ArduCopter 4.6.3
SITL). It is the same stack the top differentiator builds on. After the bundle runs green, add
one rehearsal step from
[differentiators-scan.md section 2.1](differentiators-scan.md#21-propulsion-and-drag-as-a-virtual-velocity-sensor):
check the SITL frame prints suggested drag values, then log one windy GNSS-off leg at full rate
for the offline drag filter.
