# 01. Flyable maneuvers that separate competing location hypotheses

Prior-art scan, 2026-11-09, for EDGE hackathon Challenge 2 "Autonomous Frontiers". Scope: the
vehicle's own navigation only. Records added: `data/resources/innovation-pa-maneuvers.json`
(17 resources) and `data/repos/innovation-pa-maneuvers.json` (4 repos, each checked with
`gh api repos/...` on 2026-11-09).

Source labels used below:

- **paper (full text read)** - peer-reviewed, PDF or journal HTML read.
- **paper (abstract only)** - peer-reviewed, only the abstract or catalog record read.
- **preprint (abstract only)** - arXiv, abstract page read.
- **metadata only** - title/venue confirmed via Crossref, content not read. No claims made.
- **code** - repository checked with `gh api`, README read, code not run.

## 1. Idea

A UAV doing visual geolocalization (satellite-tile retrieval + matching) or terrain matching
(radar altimeter or heightmap vs DEM) often ends up with a multimodal posterior: two to ten
places that all explain the data so far. Repeated fields, parallel valleys, flat farmland,
look-alike road junctions. The passive answer is "keep flying and wait". The proposed answer:
pick the next short maneuver (bank-limited turn, S-turn, climb or descent, a camera look
direction, a short path segment) from a library of segments the airframe can actually fly, and
choose the one whose predicted observations differ most between the live hypotheses. Then fly
it, update the filter, repeat until one hypothesis holds.

## 2. Prior art

"How close" is to the full idea: multimodal hypotheses + maneuver choice + aircraft limits +
aerial map (imagery or DEM).

| # | Source | Type | What it does | How close |
|---|---|---|---|---|
| 1 | Fox, Burgard, Thrun, "Active Markov Localization for Mobile Robots", Robotics and Autonomous Systems 25(3):195-207, 1998 ([PDF](https://publications.ri.cmu.edu/storage/publications/pub_files/pub1/fox_dieter_1998_1/fox_dieter_1998_1.pdf)) | paper (full text read) | Grid Markov localization. Actions are target points relative to the robot; utility = expected entropy reduction, weighed against expected path cost from an occupancy map. Also picks sensor pointing. Starts with random motion until the belief has a few local maxima (six in the shown run), then plans. In a symmetric office corridor, random wandering failed in all 10 extra runs; the active method localized in all 20+ runs. Section 2 notes that greedy one-step entropy minimisation fails when the disambiguating place is far away. | **High in mechanism.** Same loop: multimodal belief => pick action by expected disambiguation. Ground robot, indoor sonar/laser, no airframe dynamics. |
| 2 | Platt, Kaelbling, Lozano-Perez, Tedrake, "Non-Gaussian Belief Space Planning: Correctness and Complexity", ICRA 2012, pp. 4711-4717, doi 10.1109/ICRA.2012.6225223 ([PDF](https://people.csail.mit.edu/tlp/pdf/2012/ICRA12_1775_FI.pdf)) | paper (full text read) | Takes the MAP state as "hypothesis" plus k-1 samples from the belief. Optimises an action sequence under the system dynamics `x_{t+1} = f(x_t, u_t)` so the expected observation sequence of the hypothesis is as far as possible from the samples' (cost `sum exp(-||h(x_i,u) - h(x_1,u)||^2_Gamma)`). Re-plans when the belief leaves the nominal path. Proves convergence with as few as two samples under stated conditions (planner finds low-cost plans, exact Bayes filter). Demo: planar arm with one range laser localizing two boxes. | **High in mechanism.** This is the "maximize separation of predicted observations between hypotheses, subject to dynamics" formulation. Not aerial, not map-based, small state. |
| 3 | Dudek, Romanik, Whitesides, "Localizing a Robot with Minimum Travel", SIAM J. Computing 27(2):583-604, 1998 ([abstract](https://cim.mcgill.ca/~mrl/pubs/dudek/siamj_abs.html)) | paper (abstract only) | Robot in a known polygon, start position known only up to k look-alike candidates. Minimum-travel localization is NP-hard; gives an approximation strategy with travel bounded relative to the optimal verification tour. | Medium. Formal hypothesis-elimination by travel; noise-free geometry, no dynamics. Sets expectations: exact optimal disambiguation is hard, so a heuristic is the honest choice. |
| 4 | Jensfelt, Kristensen, "Active Global Localization for a Mobile Robot Using Multiple Hypothesis Tracking", IEEE T-RA 17(5):748-760, 2001, doi 10.1109/70.964673 ([page](https://www.csc.kth.se/~patric/publications/berlinMHT.html)) | paper (abstract only) | Multi-hypothesis Kalman tracking with a probability of correctness per hypothesis, plus movement commands chosen to gather information. Office and hospital building. | Medium. Same "MHT + act to disambiguate" structure, indoor ground robot. |
| 5 | Bar-Gill, Ben-Ezra, Bar-Itzhack, "Improvement of terrain-aided navigation via trajectory optimization", IEEE T-CST 2(4):336-342, 1994, doi 10.1109/87.338654 (also CDC 1993) | paper (abstract only) | Maps terrain information (entropy, FFT-based analysis), runs A* for minimum TAN error trajectories, then imposes airframe maneuver constraints afterwards for a suboptimal but flyable path. | **High on the aircraft side.** Aircraft + terrain information + flyability. Offline mission planning, unimodal error, constraints applied a posteriori. |
| 6 | Kang, Herrera, Mudrik, Kragelund, Sciacchitano, Kaminer, "Optimal Trajectory Generation for Improved Magnetic Navigation", arXiv 2609.27553, Sep 2026 ([abs](https://arxiv.org/abs/2609.27553)) | preprint (abstract only) | Optimal control problem minimising the posterior Cramer-Rao bound on position error along a magnetic-anomaly map, with a path-length penalty. Beats straight-line paths in simulation. | Medium-high. Map-referenced aircraft-style trajectory design by an information bound. The abstract does not mention vehicle constraints or multimodal hypotheses; a CRB is a local (unimodal) measure. |
| 7 | Carroll, Canciani, "Terrain-referenced navigation using a steerable-laser measurement sensor", NAVIGATION 68(1):115-134, 2021, doi 10.1002/navi.406 ([HTML](https://navi.ion.org/content/68/1/115)) | paper (full text read, ~100k of 121k characters, via a summarizer) | Steers a gimballed laser to the terrain points that maximize the trace of the position Fisher information block; PSO over pitch/yaw. Reports large CRLB gains vs nadir (about 4x flat, up to 20x mountainous) and about 2x lower error in the mountainous simulation. The aircraft path is not changed. | Medium. "Look-direction" half of the idea for TRN, with a Fisher (local) criterion, not hypothesis separation. |
| 8 | Yang, Khalife, Morales, Kassas, "UAV Waypoint Opportunistic Navigation in GNSS-Denied Environments", IEEE TAES 58(1):663-678, 2022, doi 10.1109/TAES.2021.3103140 ([preprint PDF](https://ece.osu.edu/sites/default/files/2022-09/UAV_waypoint_opportunistic_navigation_in_GNSS_denied_environments.pdf)) | paper (accepted preprint read: abstract and method section) | Greedy one-step multi-objective motion planner over UAV acceleration and heading, within speed and acceleration limits, trading progress to a waypoint against position uncertainty from signals of opportunity (EKF). Reports 95% success reaching the waypoint vs 36% for "fly straight", plus a real cellular-SOP flight. | Medium. Shows "fly straight" losing to information-aware maneuvering on a UAV with limits. Gaussian EKF, RF pseudoranges, not multimodal map matching. |
| 9 | Bryson, Sukkarieh, "Observability Analysis and Active Control for Airborne SLAM", IEEE TAES 44(1):261-280, 2008, doi 10.1109/TAES.2008.4517003 ([author PDF](http://www-personal.acfr.usyd.edu.au/m.bryson/publications/Bryson2008_TAES.pdf)) | paper (full text of the 6-page author PDF read) | Inertial SLAM on a UAV: entropy as the planning utility over finite-horizon trajectories, plus an observability analysis that tabulates which aircraft maneuvers excite which otherwise unobservable modes (for example heading). | Medium. Aircraft maneuvers chosen for estimability, Gaussian SLAM, no prior map and no competing location hypotheses. |
| 10 | Naghshvar, Javidi, "Active Sequential Hypothesis Testing", Annals of Statistics 41(6):2703-2738, 2013, doi 10.1214/13-AOS1144 ([arXiv](https://arxiv.org/abs/1203.4626)) | paper (abstract only) | Theory for choosing sensing actions sequentially to decide between hypotheses fast with bounded error; lower bounds and two heuristic policies, one asymptotically optimal. | Theory backbone. No vehicle. Useful for the stopping rule and for "greedy is not always enough". |
| 11 | Placed, Strader, Carrillo, Atanasov, Indelman, Carlone, Castellanos, "A Survey on Active SLAM", IEEE T-RO 39(3):1686-1705, 2023, doi 10.1109/TRO.2023.3248510 ([arXiv](https://arxiv.org/abs/2207.00254)) | paper (abstract only) | Survey: unified formulation, modular scheme, belief-space planning, deep RL, multi-robot. | Context. Entry point to loop-closure seeking and belief-space planning. |
| 12 | Stachniss, Hahnel, Burgard, "Exploration with active loop-closing for FastSLAM", IROS 2004, doi 10.1109/IROS.2004.1389609 | metadata only | Not read. Listed because "seek a loop closure" is the SLAM version of "seek a disambiguating view". | Not assessed. |
| 13 | Chaplot, Parisotto, Salakhutdinov, "Active Neural Localization", ICLR 2018, arXiv 1801.08214 ([abs](https://arxiv.org/abs/1801.08214)) | preprint (abstract only; conference per ICLR listing) | Differentiable structured belief + RL policy that moves to localize in few steps; 2D mazes, Doom, Unreal office. | Medium. Learned version of active localization; ground agent, discrete actions. |
| 14 | Gottipati, Seo, Bhatt, Mai, Murthy, Paull, "Deep Active Localization", IEEE RA-L 4(4):4394-4401, 2019, arXiv 1903.01669 | preprint (abstract only); venue from the repo README | Learned CNN perception + deep-RL planner for active localization; Gym/Gazebo, domain randomization, sim-to-real claim. | Low-medium. Indoor ground robot. |
| 15 | Honerkamp, Guttikonda, Valada, "Active Particle Filter Networks", arXiv 2209.09646, 2022 | preprint (abstract only) | Differentiable particle filter + RL agent with continuous actions, using only local map information so it scales to large maps. Indoor 3D-scanned apartments. | Medium. Particle belief + continuous actions + large map; indoor, no aircraft limits. |
| 16 | Di Giammarino, Sun, Grisetti, Pollefeys, Blum, Barath, "Learning Where to Look", arXiv 2407.15593 (ECCV 2024 per README) | preprint (abstract only) + code | Self-supervised prediction of the camera orientation that best localizes against an SfM model, used inside a planner. | Low-medium. Look-direction for unimodal accuracy, not hypothesis separation. |
| 17 | Li, Sun, Di Giammarino, Blum, Pollefeys, "ActLoc", arXiv 2508.20981, 2025 | preprint (abstract only) | Attention model predicts localization accuracy over yaw/pitch at 3D waypoints; planner picks camera orientations under motion constraints. No code link on the arXiv page. | Low-medium. Same as 16. |
| 18 | Yuan et al., "SWA-PF: Semantic-Weighted Adaptive Particle Filter for ... 4-DoF UAV Localization in GNSS-Denied Environments", arXiv 2509.13795, 2025 | preprint (abstract only) | Particle filter over 4-DoF UAV pose with semantic UAV-to-satellite matching; MAFS dataset announced ("will be available"). The abstract does not discuss multimodal posteriors. | Low. Passive estimator side only; a candidate hypothesis generator. |

Already in the hub and adjacent: [FIF](../../../catalog/resources/zhang-scaramuzza-fisher-information-field-2020.md)
and [PAMPC](../../../catalog/resources/falanga-pampc-2018.md) (perception-aware planning for
VIO), [RRBT](../../../catalog/resources/bry-roy-rrbt-icra2011.md) (Gaussian belief-space
planning), [LA-Planner](../../../catalog/resources/yu-la-planner-perception-aware-2025.md),
[terrain-navigation2](../../../catalog/repos/ethz-asl__terrain-navigation2.md) (Dubins-airplane
RRT* over a DEM, no information term), Bergman's terrain-navigation Bayesian work, and the
guides' G1 (localisability-aware routing, offline, CRB) and G4 (perception-aware multirotor
trajectory, match-likelihood grid) in [guidance-planning.md](../../guidance-planning.md). All
of these score information for one estimate (unimodal). None of them picks a maneuver to
separate several live hypotheses.

Out of scope and excluded: GOMAA-Geo / AiRLoc style "active geo-localization" (a UAV searching
for a goal location from aerial views). That is goal search, not own-vehicle localization.

## 3. What may remain (narrow)

The mechanism is not new. Fox 1998 (expected entropy over a multimodal grid) and Platt 2012
(maximize predicted-observation separation between a hypothesis and samples, subject to
dynamics) already define it. Aircraft-side, Bar-Gill 1994 and Kang 2026 optimize trajectories
for map-referenced navigation by an information measure, but for one unimodal estimate.

What was **not found in this search** (queries listed below) is the combination:

1. a **receding-horizon** maneuver choice (tens of seconds, not a whole route) triggered **only
   when the posterior is multimodal**,
2. over a **library of fixed-wing-flyable primitives** (bank-limited Dubins turns, S-turns,
   climb/descent within climb-rate limits, camera look direction) checked against terrain
   clearance,
3. scored by **pairwise hypothesis separation** of predicted observations from an **aerial map**
   (DEM for a radar altimeter / heightmap, or orthophoto tiles for VPR), with a **null
   hypothesis** for "truth is not in the set",
4. evaluated on **real terrain or imagery** against straight flight, random maneuvers, a
   standard S-turn, Fisher/CRB-greedy and expected-entropy-greedy on the same library, with
   **wrong-lock rate** as a first-class metric.

Phrase it to judges as an engineering contribution: "Fox and Platt's active disambiguation,
made flyable for a fixed-wing over real terrain, with a guard for the case where the truth is
not among the hypotheses." Not as a new theory.

Queries run (WebSearch, 2026-11-09): "Fox Burgard Thrun 1998 Active Markov localization";
"active localization UAV visual geolocalization multiple hypotheses maneuver information gain
satellite imagery"; "terrain aided navigation path planning observability Fisher information
trajectory optimization aircraft"; "path planning terrain-aided navigation terrain information
entropy route planning AUV or aircraft observability-aware"; "active visual place recognition
viewpoint selection ambiguity next best view localization"; "terrain referenced navigation path
planning aircraft Cramer-Rao lower bound route optimization"; "active terrain-aided navigation
multimodal position ambiguity trajectory selection resolve ambiguity AUV particle filter"; "UAV
active localization mutual information trajectory planning GNSS-denied map-based localization
belief space fixed-wing"; "UAV visual geo-localization particle filter multimodal ambiguity
satellite map GNSS-denied multi-hypothesis"; "fixed-wing UAV terrain navigation localizability
aware path planning Dubins". GitHub: `gh search repos` for "active localization", "active
markov localization", "belief space planning", "terrain aided navigation path planning",
"informative path planning". Not searched: IEEE Xplore / Scopus directly, ION GNSS+ and PLANS
proceedings full text, Chinese and Russian TAN literature, patents beyond one hit. Classified
or vendor work on TERCOM route planning would not show up here.

## 4. Strongest baseline

A judge will ask "why not just ...". In order of strength:

1. **Expected-entropy greedy on the same flyable library** (Fox 1998 utility). This is the
   strongest. It uses the same hypotheses and the same primitives; only the score differs. If
   the separation score does not beat it, the contribution is "Fox 1998 with Dubins segments",
   which is still a fine demo but not a new algorithm.
2. **Fisher/CRB-greedy at the MAP estimate** (turn toward the most informative terrain around
   the best hypothesis, using the CRB in [terrain-heightmap-pf](../../../samples/terrain-heightmap-pf/)
   `core.ncc_crb`). Cheap, already in the hub, and what G1 does offline.
3. **Standard S-turn or a fixed 360 deg orbit** on ambiguity. Operationally plausible, no
   planning.
4. **Random flyable maneuver** from the library.
5. **Fly straight and wait** (the passive filter). Weakest, but it is what the hub's samples
   do today.

Greedy information gain **without** dynamics is not a fair baseline for a fixed-wing; it picks
segments the aircraft cannot fly. Use it only to show the cost of the flyability constraint.

## 5. Falsification experiment (48h, open data, no hardware)

**Data.** Copernicus GLO-30 windows already cached by [blind-flight-bench](../../../samples/blind-flight-bench/)
(four ~36 x 35 km regions) and [terrain-heightmap-pf](../../../samples/terrain-heightmap-pf/)
(hilly, mixed, flat, flat_smooth). Optional visual branch: NAIP 2015-2023 vintages from
[vpr-large-area](../../../samples/vpr-large-area/) (49 km2).

**Steps.**

1. Sensor and world: reuse `blind-flight-bench/sim.py` (radar altimeter on a world surface =
   DEM + correlated error, baro reference error). Fixed-wing at 25 m/s, 1500 m MSL.
2. Ambiguous start: GNSS lost, prior = uniform over a 6 x 6 km box (kidnapped case), or
   seeded with the top-5 VPR candidates. Run the passive particle filter (`navs.ParticleFilter`)
   until it has 2-8 clusters holding at least 90% of the mass; that is the decision point.
3. Library: 12 primitives of 60-90 s each: straight; constant-bank turns at +-15 / +-30 deg
   (turn radius from `v^2 / (g tan(bank))`); left-right S-turns; climb or descend 150 m at a
   fixed climb rate; all checked for terrain clearance on the DEM. Build with
   [pydubins](../../../catalog/repos/andrewwalker__pydubins.md) or plain kinematics.
4. Prediction: for each cluster mean (plus a wind hypothesis, see failure modes), propagate the
   primitive in the air frame and read the predicted altimeter profile from the DEM.
5. Scores, same library for all: (F) proposed pairwise separation
   `sum_{i<j} w_i w_j (1 - exp(-d_ij^2 / 8 sigma^2))`, d_ij = profile distance, sigma inflated
   for correlated map error; (E) expected entropy after the segment (Fox); (D) CRB at the MAP;
   (C) fixed S-turn; (B) random; (A) straight.
6. Execute the chosen primitive in the simulator, update the PF, re-decide until locked or
   20 km flown. 100 seeds per region, paired seeds across arms.

**Metric.** Primary: distance flown from the decision point to **correct lock** (at least 95%
of mass within 150 m of truth, held for 2 km). Co-primary: **wrong-lock rate** (95% of mass on
a cluster more than 500 m from truth). Secondary: extra path length vs straight, horizontal
error at 10 km.

**Pass / fail.** Pass if F cuts median distance-to-correct-lock by at least 30% vs A and by at
least 15% vs the better of D and E, with wrong-lock rate not higher than A's (paired bootstrap,
95% CI), in at least two of the three non-flat regions. **Fail** if E is within 10% of F (then
the score adds nothing over Fox 1998), or if F's wrong-lock rate is higher than A's. On
`flat_smooth` every arm should fail to lock; if F "locks" there, the likelihood is
overconfident and the run is invalid.

## 6. Failure-mode checklist

- [ ] **Missing true hypothesis (truth not in the set).** The planner happily separates two
  wrong places and the filter locks onto the less wrong one. Mitigation: a null hypothesis with
  a broad predicted observation; if the null wins mass after a maneuver, trigger a fresh global
  search (VPR top-k or a wider PF reseed) instead of locking. Test: inject runs where the truth
  is removed from the seeded candidates; report wrong-lock rate there separately.
- [ ] **Correlated sensor errors.** The separation score treats each altimeter sample or match
  as independent. DEM error, radar footprint bias and VPR descriptor errors are spatially
  correlated (the hub sim uses 60 m correlation), so d_ij looks larger than it is and locks come
  early. Mitigation: use an effective sample count (decimate to the correlation length) or a
  full covariance in d_ij. Test: sweep the world-error correlation length and watch wrong-lock.
- [ ] **Map mismatch (seasonal change, map age).** For imagery the planner's predicted
  observation comes from one vintage and the world is another; a maneuver can steer toward
  features that no longer exist or changed appearance. Mitigation: inflate sigma per map age;
  prefer DEM-based separation where both are available. Test: plan on NAIP 2023, simulate
  observations from 2015 or 2017 in the [vpr-large-area](../../../samples/vpr-large-area/) data.
- [ ] **Delayed measurements.** VPR retrieval and fine matching take seconds; a radar altimeter
  is near real time. A 60 s primitive with a 3-5 s fix latency is fine; a 10 s primitive is not.
  Mitigation: time-stamp observations at capture, predict at capture time, and set the
  minimum primitive length to several latencies. Test: add 0 / 2 / 5 s latency to the visual
  branch.
- [ ] **Wind / velocity ambiguity.** In a turn, the ground track depends on wind, so each
  location hypothesis also needs a wind (or ground-velocity) hypothesis; otherwise predicted
  profiles are wrong in a way that grows with turn duration. A turn also makes wind more
  observable from airspeed + heading, which helps. Mitigation: hypotheses over (position, wind)
  with 3-5 wind samples per cluster. Test: SITL-style wind 0 / 5 / 10 m/s; compare F with and
  without wind hypotheses.
- [ ] **Terrain clearance and energy.** The most informative terrain is often the roughest
  (G1 risk). Every primitive must pass a clearance check, and the extra distance must be
  reported. A climb costs energy that a long-range fixed-wing may not have.
- [ ] **Overconfident likelihood.** If the PF likelihood is too sharp, any score "wins". Keep
  the `flat_smooth` control from terrain-heightmap-pf as a sanity check.

## 7. POC sketch (48h)

| Hours | Work | Reuse |
|---|---|---|
| 0-4 | Ambiguous-start scenario and cluster extraction (k-means over particles, mass per cluster) | `blind-flight-bench/sim.py`, `navs.ParticleFilter`; `core.largest_cluster_centroid` from terrain-heightmap-pf |
| 4-10 | Primitive library with bank and climb limits, DEM clearance check, air-frame propagation with wind | pydubins or 30 lines of kinematics; `core.bilinear` for DEM lookup |
| 10-18 | Predicted altimeter profile per (cluster, wind, primitive); scores F, E, D, C, B, A | `blind-flight-bench/sim.radar_range`; `core.ncc_crb` / `translation_crb` for D |
| 18-30 | Receding-horizon loop and the 100-seed paired experiment on the GLO-30 regions; metrics | `blind-flight-bench/metrics.py` |
| 30-40 | Stretch: visual branch, hypotheses from VPR top-k, predicted views from rendered NAIP tiles, map-age test | `vpr-large-area/vpr.py` `render_tile`, `index.py` |
| 40-48 | Plots (tracks per arm, distance-to-lock CDF, wrong-lock bars), pitch | - |

Pitch line, only if section 5 passes: "When the aircraft is not sure where it is, it flies the
one short turn that tells the places apart, and it says so when none of them is right."

## 8. Not verified

- Bar-Gill 1994, Dudek 1998, Jensfelt 2001, Naghshvar 2013, Placed 2023: only abstracts or
  catalog records read. Their methods are described from abstracts.
- Kang 2026 (MagNav PCRB trajectories): abstract only; whether it models turn-rate or bank
  limits is unknown. No code link found.
- Carroll and Canciani 2021: read through a summarizer, last ~20% of the page not read.
- Stachniss 2004: metadata only.
- Chaplot 2018, Gottipati 2019, Honerkamp 2022, Di Giammarino 2024, ActLoc 2025, SWA-PF 2025:
  abstracts only; no numbers reproduced.
- Repos in `data/repos/innovation-pa-maneuvers.json`: README read, nothing installed or run.
- The falsification thresholds (30% / 15% / 10%) are our choice, not taken from any source.
- No experiment in section 5 has been run. Whether a 60-90 s primitive separates hypotheses on
  GLO-30 at 30 m is unknown; at 30 m posting, small turns may not move the profile enough.
- "Not found in this search" is not a novelty claim. Defence TERCOM/TRN mission-planning
  practice is likely to contain route-for-fix rules that are not public.
