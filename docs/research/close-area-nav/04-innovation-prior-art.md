# 04. Close-area navigation: prior art for three innovation angles, plus a wider scan

Prior-art scan, 2026-11-09, for EDGE hackathon Challenge 2. Assumed task: fly a multirotor from
A to B in a close area (indoor, under canopy, between buildings) with obstacles. Scope: the
vehicle's own navigation only. Method and labels follow
[innovation-prior-art/README.md](../innovation-prior-art/README.md) and
[01-disambiguating-maneuvers.md](../innovation-prior-art/01-disambiguating-maneuvers.md).

Records added: `data/resources/close-area-innovation.json` (26 resources) and
`data/repos/close-area-innovation.json` (10 repos, each checked with `gh api repos/...` on
2026-11-09). Items already in the hub, or added by the sibling close-area lanes the same day
(PX4 Collision Prevention, ArduPilot BendyRuler docs, FASTER paper and repo, DecompUtil,
Loquercio 2021 and agile_autonomy), are linked or named, not re-added.

Source labels used below:

- **paper (abstract only)** - peer-reviewed, only the abstract, a catalog record or a search
  summary read.
- **preprint (abstract only)** - arXiv abstract page read, no confirmed peer-reviewed venue.
- **doc** - official product documentation, read through a search summary.
- **code** - repository checked with `gh api`, README read, code not run.

No paper below was read in full text. No experiment in this doc has been run. Every threshold
is our proposal. "Not found in this search" means the listed queries returned nothing; it is
not a novelty claim.

## 0. One finding that shapes all three ideas

In a close area the obstacle you must not hit is usually **seen by a range sensor in the body
frame** (depth camera, ToF, lidar). A safety layer built on those ranges does not need the
position estimate at all. PX4 Collision Prevention (`CP_DIST`) and the NTNU PX4-CBF filter both
work this way. So "inflate clearance by position uncertainty" only matters for obstacles the
range sensor cannot see right now: outside a narrow field of view, behind the vehicle, stored in
a prior map, a geofence or no-fly volume, or when the range sensor itself is degraded (glass,
smoke, dust, thin wires). Any pitch that ignores this will be asked "why not just use the
lidar?" by the first judge. Every falsifier below includes the range-only filter as a baseline.

## 1. Idea A: uncertainty-aware planning

Inflate obstacle clearance by live position uncertainty; slow down or replan when the estimator
degrades.

### 1.1 Prior art

| # | Source | Type | What it does | How close |
|---|---|---|---|---|
| 1 | Blackmore, Ono, Williams, "Chance-Constrained Optimal Path Planning With Obstacles", IEEE T-RO 27(6):1080-1094, 2011, doi 10.1109/TRO.2011.2161160 ([MIT DSpace](https://dspace.mit.edu/handle/1721.1/80914)) | paper (abstract only) | Plans the future state distribution of a linear-Gaussian vehicle so the probability of collision stays below a bound; disjunctive convex program, branch-and-bound. Aircraft obstacle example. | **High in mechanism.** The theory for "margin grows with uncertainty". Offline, open-loop covariance, no live estimator. |
| 2 | Bry, Roy, RRBT, ICRA 2011 ([hub](../../../catalog/resources/bry-roy-rrbt-icra2011.md)) | already in hub | Tree over state and estimator covariance with chance constraints; sensing varies in space. | High. Belief-space planning with a filter in the loop. Slow for 48h. |
| 3 | Prentice, Roy, "The Belief Roadmap", IJRR 28(11-12):1448-1465, 2009, doi 10.1177/0278364909341659 ([PDF](https://people.csail.mit.edu/prentice/papers/ijrr09-brm.pdf)) | paper (abstract only) | PRM in belief space; factored covariance makes multi-step covariance prediction one matrix product. UWB beacon localization. | Medium-high. Plans routes that keep localization good. Offline roadmap. |
| 4 | Okamoto, Tsiotras, "Optimal Stochastic Vehicle Path Planning Using Covariance Steering", IEEE RA-L 2019, [arXiv 1809.03380](https://arxiv.org/abs/1809.03380) | paper (abstract only) | Steers mean and covariance of a linear stochastic system with non-convex obstacle chance constraints (mixed-integer convex). | Medium. Closed-loop covariance is less conservative than open-loop growth. Linear model, offline. |
| 5 | Zhu, Alonso-Mora, "Chance-Constrained Collision Avoidance for MAVs in Dynamic Environments", IEEE RA-L 4(2):776-783, 2019, doi 10.1109/LRA.2019.2893494 ([TU Delft](https://repository.tudelft.nl/record/uuid:4c2e8664-4eb7-45ff-9e7e-a57ae643a371)); code [tud-amr/mrca-mav](https://github.com/tud-amr/mrca-mav) | paper (abstract only) + code | Chance-constrained NMPC; tight bound on collision probability; real quadrotors with humans. Lin, Zhu, Alonso-Mora ICRA 2020 extends it to stereo-vision obstacle sensing with state-estimation uncertainty. | **High.** This is the live, onboard version of idea A for quadrotors. GPL-3.0, MATLAB. |
| 6 | Florence, Carter, Ware, Tedrake, "NanoMap", ICRA 2018, [arXiv 1802.09076](https://arxiv.org/abs/1802.09076); code [peteflorence/nanomap_ros](https://github.com/peteflorence/nanomap_ros) | paper (abstract only) + code | Keeps depth frames with noisy relative poses instead of a fused map; proximity queries return the most certain view, so the planner sees pose uncertainty. 10 m/s quadrotor. | Medium-high. Uncertainty-aware obstacle queries in the body-frame spirit of section 0. |
| 7 | Papachristos, Khattak, Alexis, "Uncertainty-aware receding horizon exploration and mapping", ICRA 2017, doi 10.1109/ICRA.2017.7989531; code [ntnu-arl/rhem_planner](https://github.com/ntnu-arl/rhem_planner) | paper (abstract only) + code | Picks the exploration branch that minimises expected localization uncertainty of a stereo VIO. | Medium. Uncertainty drives route choice; exploration, not A-to-B. |
| 8 | Vahs, Pek, Tumova, "Belief Control Barrier Functions for Risk-aware Control", [arXiv 2309.06499](https://arxiv.org/abs/2309.06499), 2023 | preprint (abstract only) | CBF on the EKF belief (mean and covariance) so the vehicle stays safe with a chosen confidence. Quadrotor, up to 1 kHz. | **High.** "Clearance inflated by live covariance" as a filter. Strongest prior art for A and C together. |
| 9 | Lee, Seo, Kassas, "Integrity-Based Path Planning Strategy for Urban Autonomous Vehicular Navigation Using GPS and Cellular Signals", ION GNSS+ 2020, doi 10.33012/2020.17589 ([arXiv 2010.03761](https://arxiv.org/abs/2010.03761)) | paper (abstract only) | Path cost includes the predicted GNSS/LTE horizontal protection level; constraint HPL < HAL. Ray-traced, offline. | Medium. Uses a protection level, not a covariance, as the planning margin. Ground, offline. |
| 10 | Liu et al., safe flight corridors, ICRA 2017; code [sikang/DecompUtil](https://github.com/sikang/DecompUtil), [sikang/DecompROS](https://github.com/sikang/DecompROS) | paper (abstract only) + code | Ellipsoid-based convex corridors around a path in a point cloud, then a QP inside the corridors. | Low on uncertainty. The corridor is where an inflation term would plug in. BSD-3. |

Also relevant: Chen and Shen (IEEE Access 2022, Berkeley HiPeR lab) sample minimum-jerk
trajectories and score them by predicted position uncertainty plus speed, which trades speed
against VIO uncertainty; EVA-Planner (arXiv 2011.04246) adapts aggressiveness to obstacle
density, not to estimator health. Not added as records (search summary only).

### 1.2 What may remain (narrow)

The margin-from-covariance mechanism is old (Blackmore 2011) and already runs onboard
quadrotors (Zhu 2019, Vahs 2023). What was **not found in this search**:

1. a margin taken from a **fault-aware protection level** (solution separation over VIO, range
   sensors and baro, as in the hub's [multi-source-fde](../../../samples/multi-source-fde/)) rather
   than the filter covariance, so a VIO jump or slow bias that the covariance does not show still
   widens the margin,
2. a **speed cap** derived from that bound (stopping distance + PL < clearance), and
3. a **consistency gate** (NEES or innovation test) that refuses to shrink the margin when the
   covariance is overconfident.

This is guidance idea G2 ("integrity drives guidance") applied to a close-area multirotor. It is
an engineering combination, not a new theory.

### 1.3 Strongest baseline

1. **Belief-CBF / CC-NMPC with live EKF covariance** (Vahs 2023, Zhu 2019). Same margin idea,
   Gaussian only. If our PL margin does not beat it on fault cases, the contribution is "BCBF
   with a different sigma".
2. **Range-only filter** (PX4 `CP_DIST`, PX4-CBF). Needs no position estimate.
3. **Fixed worst-case inflation** tuned so the nominal arm never crashes. Safe and slow.
4. **Fixed nominal inflation** tuned for good VIO. Fast and unsafe in degraded zones.

### 1.4 Falsification experiment (Python, no hardware)

**Sim.** Point-mass double integrator with first-order velocity tracking lag (tau 0.15 s),
accel limit 5 m/s^2, 50 Hz; confirm 20 seeds on [RotorPy](../../../catalog/repos/spencerfolk__rotorpy.md)
(or [safe-control-gym](https://github.com/learnsyslab/safe-control-gym), MIT, which has constrained quadrotor tasks).
World: 30 x 20 m room or corridor set with 15-40 box/cylinder obstacles, 200 random layouts.
Range sensor: 90 deg horizontal FoV, 8 m, so side and rear obstacles are not sensed.

**Estimator.** EKF on position and velocity with IMU-like accel input and VIO-like position
updates. Zones: good (sigma 0.03 m), dark (no updates, drift), and fault cases: VIO step jump
0.5 m, VIO bias ramp 0.05 m/s for 10 s. A second source (range-to-wall residuals or UWB to 2
anchors) gives the redundancy the PL needs.

**Arms (same A* + min-jerk planner, plan on the estimate).** (A) fixed nominal inflation;
(B) fixed worst-case inflation; (C) BCBF-style margin k*sqrt(lambda_max(P)); (D) ours: margin
from PL plus speed cap plus NEES gate. All arms also get the range-only filter, so we test
what the margin adds on top of it.

**Metric.** True collision rate (truth state), goal reached within 120 s, time to goal. 200
layouts x 5 fault cases, paired seeds.

**Pass / fail.** Pass if D has collision rate <= 1% on every fault case, at least 3x lower than
C on jump and bias cases, and median time to goal at least 15% shorter than B. **Fail** if C is
within 1 percentage point of D on jump and bias (then PL adds nothing over covariance), or if
the range-only filter alone already gives <= 1% collisions everywhere (then idea A is not needed
in this world; widen the scenario to unsensed obstacles or drop it).

### 1.5 Failure modes

- [ ] **Overconfident covariance.** VIO covariances are known to be optimistic. If P is wrong,
  C and D shrink margins exactly when they should not. Test: scale reported R by 0.25.
- [ ] **No redundancy, no PL.** Solution separation needs two independent sources. With VIO only
  the PL equals the covariance bound and D collapses to C. Say so if that is the hardware.
- [ ] **Correlated errors.** VIO drift and map registration share a frame; obstacles in a prior
  map move with the frame error. Body-frame obstacles do not.
- [ ] **Delay.** VIO at 30 Hz with 50-100 ms latency; margin must cover v * latency.
- [ ] **Freezing robot.** Margins grow until the corridor closes. Report "stuck" separately from
  "reached" and from "crashed".

## 2. Idea B: perception-aware planning

Choose path and yaw so VIO stays well conditioned.

### 2.1 Prior art

| # | Source | Type | What it does | How close |
|---|---|---|---|---|
| 1 | Costante, Forster, Delmerico, Valigi, Scaramuzza, "Perception-aware Path Planning", [arXiv 1605.04151](https://arxiv.org/abs/1605.04151) (listed as TRO16 by the authors' group; venue not confirmed) | preprint (abstract only) | Plans paths that maximise photometric information for direct visual localization; replans as texture is discovered. Quadrotor. | **High.** The original statement of idea B. |
| 2 | Falanga et al., PAMPC, IROS 2018 ([hub](../../../catalog/resources/falanga-pampc-2018.md)) | already in hub | Perception cost inside NMPC. Code in rpg_mpc (GPL-3.0). | High. |
| 3 | Zhang, Scaramuzza, Fisher Information Field ([hub](../../../catalog/resources/zhang-scaramuzza-fisher-information-field-2020.md)) | already in hub | Voxel map of localization information for fast planning queries. | High. The best scoring map for idea B. |
| 4 | Murali, Spasojevic, Guerra, Karaman, "Perception-aware trajectory generation for aggressive quadrotor flight using differential flatness", ACC 2019 ([MIT DSpace](https://dspace.mit.edu/handle/1721.1/132953)) | paper (abstract only) | Yaw trajectory that keeps tracked features co-visible during aggressive flight; reports almost 70% lower tracking RMSE. | **High for yaw-only.** Exactly what a 48h team would build. |
| 5 | Bartolomei, Teixeira, Chli, "Perception-aware Path Planning for UAVs using Semantic Segmentation", IROS 2020 ([PDF](https://lucabartolomei.github.io/publications/IROS_2020_Active_perception.pdf)) | paper (abstract only) | A* + B-spline favouring semantic classes that are good for VIO; beats Zhang-Scaramuzza on state estimation. | Medium-high. |
| 6 | Zhou, Pan, Gao, Shen, "RAPTOR", IEEE T-RO 37(6):1992-2009, 2021, [arXiv 2007.03465](https://arxiv.org/abs/2007.03465); code in [Fast-Planner](../../../catalog/repos/hkust-aerial-robotics__fast-planner.md) | paper (abstract only) + code | Topological path-guided optimisation, risk-aware refinement, yaw planning to look into unknown space. | Medium. Perception for mapping, not for VIO health. GPL-3.0. |
| 7 | Qin et al., "Perception-Aware Time-Optimal Planning for Quadrotor Waypoint Flight", [arXiv 2603.04305](https://arxiv.org/abs/2603.04305), Mar 2026 | preprint (abstract only) | Time-optimal planner with an information-theoretic position-uncertainty metric, FoV constraints; 9.8 m/s real flights; Split-S success 55% => 100%. | High and recent. Racing gates, not cluttered A-to-B. |
| 8 | LA-Planner, IROS 2025 ([hub](../../../catalog/resources/yu-la-planner-perception-aware-2025.md)) | already in hub | Predicts visible features along candidates; steers yaw and path in sparse-feature scenes. | **High.** Closest to idea B in a close area. |
| 9 | Papachristos 2017 (section 1, #7) | - | Uncertainty-minimising branch selection for stereo VIO. | Medium. |

### 2.2 What may remain (narrow)

Very little. Path, yaw, MPC, time-optimal and semantic variants all exist, several with code.
The only gap seen: perception-awareness applied as a **runtime action of the safety layer**
(when VIO health drops, yaw toward the last feature-rich direction and slow down) instead of
inside the planner. That is a supporting behaviour, not a headline.

### 2.3 Strongest baseline

1. **Yaw toward maximum predicted feature count** (Murali-style, or LA-Planner). Cheap, strong.
2. **FIF-greedy yaw and path** with the same feature map.
3. **Yaw along velocity** (what most planners do).

### 2.4 Falsification experiment

**Sim.** Same world as 1.4. Landmarks scattered on walls with density varying 0-50 per m^2
(textured and blank walls). VIO model: position update noise sigma = s0 / sqrt(n_visible) with
n_visible = landmarks inside a 90 deg camera FoV within 6 m; tracking lost when n_visible < 15
for 0.5 s (no updates until re-acquire).

**Arms.** (A) yaw along velocity; (B) Murali-style yaw to max features; (C) FIF-greedy over
path and yaw; (D) ours: yaw-to-features only when the health monitor fires, plus speed cap.

**Metric.** Track-loss events per run, RMS position error at goal, time to goal.

**Pass / fail.** Pass if D cuts track-loss events by at least 50% vs A with <= 10% time
penalty, and is within 10% of B on error while flying at least 10% faster (D only deviates when
needed). **Fail** if B dominates D on both error and time, which is the expected result. Then
use B as-is and claim nothing.

### 2.5 Failure modes

- [ ] **You test your own model.** The VIO noise model decides the winner. Calibrate s0 and the
  loss threshold on a real VIO run (OpenVINS on EuRoC in [relative-nav-benchmark](../../../samples/relative-nav-benchmark/)) before trusting any number.
- [ ] **Map mismatch.** Feature maps built on one pass do not match lighting on the next.
- [ ] **Yaw fights the range sensor.** Yawing toward texture can point the narrow-FoV range
  sensor away from the obstacle ahead. Measure collisions, not only VIO error.
- [ ] **Motion blur.** Faster flight hurts features; the model must include speed.

## 3. Idea C: safety filter around any planner

A minimal-change filter or runtime-assurance switch between any planner (classical, learned,
LLM) and the autopilot.

### 3.1 Prior art

| # | Source | Type | What it does | How close |
|---|---|---|---|---|
| 1 | Simplex ([Sha 2001](../../../catalog/resources/sha-2001-simplex.md)), [Black-box Simplex](../../../catalog/resources/mehmood-2022-black-box-simplex.md), [ASTM F3269](../../../catalog/resources/astm-f3269-21-rta.md), [Clark 2020](../../../catalog/resources/clark-2020-rta-autonomous-aerospace.md), [act3-ace/run-time-assurance](../../../catalog/repos/act3-ace__run-time-assurance.md) | already in hub | Switch from complex to verified fallback on a monitor. Python ASIF library exists. | Architecture. See [path-to-product.md](../../path-to-product.md) section 4. |
| 2 | PX4 Collision Prevention ([docs](https://docs.px4.io/main/en/computer_vision/collision_prevention.html)) | doc | Position mode; limits velocity so the vehicle stops at `CP_DIST` from range data (OBSTACLE_DISTANCE or rangefinder); `CP_DELAY` for latency; blocks motion where there is no data. | **Baseline.** Free, on every PX4 vehicle. Position mode only. |
| 3 | ArduPilot Object Avoidance ([Simple](https://ardupilot.org/copter/docs/common-simple-object-avoidance.html), [BendyRuler](https://ardupilot.org/copter/docs/common-oa-bendyruler.html), [Dijkstra+BendyRuler](https://ardupilot.org/copter/docs/common-oa-dijkstrabendyruler.html)) | doc | Simple avoidance stops or slides in Loiter/AltHold; BendyRuler is a local planner in Auto/Guided/RTL; Dijkstra routes around fences. | **Baseline.** GPL-3.0 firmware. |
| 4 | Misyats, Harms, Nissov, Jacquet, Alexis, "Embedded Safe Reactive Navigation for Multirotors Systems using Control Barrier Functions", ICUAS 2025, [arXiv 2504.15850](https://arxiv.org/abs/2504.15850); code [ntnu-arl/PX4-CBF](https://github.com/ntnu-arl/PX4-CBF), [ntnu-arl/composite_cbf](https://github.com/ntnu-arl/composite_cbf) | paper (ICUAS 2025 pp. 697-704; full text read in [05](05-cbf-baselines-faithful.md#1-px4-cbf-misyats-harms-nissov-jacquet-alexis-icuas-2025)) + code | Composite CBF from onboard ranges only, inside the PX4 velocity loop, minimal change to the acceleration setpoint; FoV-constrained variant. BSD-3. | **Very high.** The product-shaped version of idea C, already in PX4. Strongest baseline. |
| 5 | Zhou, Papatheodorou, Leutenegger, Schoellig, "Control-Barrier-Aided Teleoperation with Visual-Inertial SLAM for Safe MAV Navigation", ICRA 2024, [arXiv 2403.04331](https://arxiv.org/abs/2403.04331) | paper (abstract only) | CBF filter on VI-SLAM + occupancy map; unmapped space counts as unsafe; real flights. | High. Map-based filter; does not react to estimator health. |
| 6 | Agrawal, Chen, Panagou, "gatekeeper", IEEE T-RO 2024, [arXiv 2211.14361](https://arxiv.org/abs/2211.14361); code [dev10110/gatekeeper](https://github.com/dev10110/gatekeeper) | paper (IEEE T-RO 2024; full text read in [05](05-cbf-baselines-faithful.md#3-gatekeeper-agrawal-chen-panagou-ieee-t-ro-2024)) + code | Checks each candidate trajectory forward with a backup controller (e.g. hover); commits the longest safe prefix. Quadrotor hardware; 3-10x faster than MPC in sim. | High. Planner-agnostic, simple to explain. Needs a backup set. |
| 7 | Chen et al., "Backup Control Barrier Functions: Formulation and Comparative Study", [arXiv 2104.11332](https://arxiv.org/abs/2104.11332); Singletary, Swann, Chen, Ames, "Onboard Safety Guarantees for Racing Drones: High-speed Geofencing with CBFs", [arXiv 2201.04331](https://arxiv.org/abs/2201.04331) | preprint (abstract only) | Backup CBFs grow a small invariant set via a backup controller; geofencing a 7-inch racing drone above 100 km/h on a 10 g microcontroller. | High for geofence. |
| 8 | Wabersich, Zeilinger, "A predictive safety filter for learning-based control of constrained nonlinear dynamical systems", Automatica 129, 2021, doi 10.1016/j.automatica.2021.109597, [arXiv 1812.05506](https://arxiv.org/abs/1812.05506) | paper (abstract only) | MPC-based filter that changes a learned input only when needed. | Medium-high. Theory for "any planner + filter". |
| 9 | Dean, Taylor, Cosner, Recht, Ames, "Guaranteeing Safety of Learned Perception Modules via Measurement-Robust CBFs", CoRL 2020, PMLR 155 ([page](https://proceedings.mlr.press/v155/dean21a.html)); Cosner et al., "Measurement-Robust CBFs: Certainty in Safety with Uncertainty in State", IROS 2021, [arXiv 2104.14030](https://arxiv.org/abs/2104.14030) | paper (abstract only) | CBF condition robust to bounded measurement error; Segway with stereo state estimation. | **High in mechanism** for "filter that knows the estimate is wrong". Not quadrotor. |
| 10 | Agrawal, Panagou, "Safe and Robust Observer-Controller Synthesis using CBFs", IEEE L-CSS 7:127-132, 2022, [arXiv 2211.14364](https://arxiv.org/abs/2211.14364) | paper (abstract only) | CBFs built from bounded observer error; separately designed observer and controller can be unsafe; quadrotor experiments. | High. |
| 11 | Vahs et al. BCBF (section 1, #8) | paper (IEEE RA-L 2023; full text read in [05](05-cbf-baselines-faithful.md#2-belief-cbf-vahs-pek-tumova-ieee-ra-l-2023)) | EKF-belief CBF on a quadrotor. | High. |
| 12 | Sinha, Schmerling, Pavone, "Closing the Loop on Runtime Monitors with Fallback-Safe MPC", CDC 2023, [arXiv 2309.08603](https://arxiv.org/abs/2309.08603) | paper (abstract only) | Conformal-calibrated runtime monitor for perception; robust MPC keeps a perception-free fallback; simulated quadrotor slows and descends when perception degrades. | **High** for "monitor => slow down". Simulated perception errors. |
| 13 | Cosner, Culbertson, Taylor, Ames, "Robust Safety under Stochastic Uncertainty with Discrete-Time CBFs", RSS 2023 ([page](https://roboticsproceedings.org/rss19/p084.html)) | paper (abstract only) | Finite-time safety bounds for discrete-time CBFs under unbounded noise. | Theory for the noise case. |
| 14 | Tordesillas, Lopez, Everett, How, "FASTER", IEEE T-RO 38(2):922-938, 2022, [arXiv 2001.04420](https://arxiv.org/abs/2001.04420); code [mit-acl/faster](https://github.com/mit-acl/faster) | paper (abstract only) + code | Keeps a safe backup trajectory in known-free space each replan, optimises through unknown space. 7.8 m/s. BSD-3. | Medium. Backup inside the planner, not a filter. |
| 15 | Python CBF code: [hocherie/cbf_quadrotor](https://github.com/hocherie/cbf_quadrotor) (MIT), [shaoanlu/CBF_QP_safety_filter](https://github.com/shaoanlu/CBF_QP_safety_filter) (no license) | code | Exponential CBF on a simple 3D quadrotor sim; 2D CBF-QP playground. | Starting code for the 48h build. |

### 3.2 What may remain (narrow)

Range-based CBF filters are in PX4 already (PX4-CBF). Estimation-aware CBFs exist (MR-CBF,
BCBF, observer-controller). Runtime monitors that slow the vehicle exist (Sinha 2023). What was
**not found in this search** is the composition, on a close-area multirotor:

1. a planner-agnostic filter that keeps **two barrier sets**: body-frame range obstacles (no
   position needed, PX4-CBF style) and map/geofence obstacles whose margin is the live
   **protection level** from a fault-detecting nav monitor;
2. a **speed cap and fallback** triggered by nav health (PL vs alert limit, VIO track count),
   gatekeeper-style backup = hover or retreat along the last known-good path;
3. measured against PX4 Collision Prevention and PX4-CBF with a **deliberately bad planner**
   (straight-line, or a learned policy) to show the filter carries safety.

Phrase it as: "PX4-CBF and belief CBFs, joined by the hub's integrity monitor, so the safety
filter also knows when the navigation is lying." Engineering, not theory.

### 3.3 Strongest baseline

1. **PX4-CBF (composite range CBF)**, re-implemented in Python on the same sim. Strongest and
   already productised. Two arms, per [05 section 1](05-cbf-baselines-faithful.md#1-px4-cbf-misyats-harms-nissov-jacquet-alexis-icuas-2025):
   **as shipped** (fork branch `cbf` HEAD `e7ef0c61`: closed-form single constraint, linear
   alpha, no FoV constraint) and **with the FoV QP** (paper eq. 17, the qpOASES variant at commit
   `338fb51f`). The FoV variant is the faithful baseline for a fan under 180 deg. Use the paper's
   Table II gains, not the PX4 parameter defaults.
2. **Belief-CBF** with covariance prediction every control step and the Theorem 3 update-jump
   margin ([05 section 2](05-cbf-baselines-faithful.md#2-belief-cbf-vahs-pek-tumova-ieee-ra-l-2023)).
   A plain `k * sqrt(lambda_max(P))` inflation is a weaker copy.
3. **MR-CBF with a fixed worst-case bound** `epsilon` measured offline against truth (Cosner
   2021 practice, [05 section 4](05-cbf-baselines-faithful.md#4-measurement-robust-cbf-dean-taylor-cosner-recht-ames-corl-2020)).
   If a PL margin does not beat it on time to goal at equal breach rate, the PL adds nothing over
   a calibrated constant.
4. **FT-CBF residual dropping** (Zhang, Li, Clark, [07](07-pl-margin-prior-art.md#1-verdict)):
   drop the largest-residual estimates until the QP is feasible.
5. **Tan union of states** (Tan et al. IROS 2025, [07](07-pl-margin-prior-art.md#1-verdict)):
   margin = the union of states consistent with every sensor subset that excludes up to s
   attacked sensors, inflated by a noise bound.
6. **gatekeeper** backup filter ([05 section 3](05-cbf-baselines-faithful.md#3-gatekeeper-agrawal-chen-panagou-ieee-t-ro-2024)):
   keeps the last committed trajectory when none validates; count "stuck" separately.
7. **PX4 Collision Prevention**: stop at `CP_DIST` along velocity.
8. **No filter** (planner alone).

Inputs each arm needs from the sim and three ways a naive copy would be unfair are in
[05 sections 5-6](05-cbf-baselines-faithful.md#5-baseline--minimal-faithful-implementation-for-the-kill-test).

### 3.4 Falsification experiment

**Sim.** Same as 1.4. Nominal planners: (P1) straight line to goal (adversarial), (P2) A* +
min-jerk on the estimate, (P3) noisy "learned" planner = P2 plus heading noise and 5% random
bad commands. Obstacles: sensed (in range FoV) and unsensed (outside FoV, plus a geofence box
and two map-only thin poles the range sensor misses at > 3 m). Estimator fault cases as in 1.4.

**Arms.** (F0) no filter; (F1) CP-style stop; (F2a) PX4-CBF as shipped (closed form, no FoV);
(F2) PX4-CBF with the FoV QP; (F3) F2 + Belief-CBF margin on map obstacles, with covariance
prediction and the update-jump margin; (F3m) F2 + MR-CBF with a fixed worst-case bound; (F3f)
F2 + FT-CBF residual dropping; (F3t) F2 + Tan union of plausible states; (F4) ours: F2 + PL
margin + health speed cap + hover when the monitor cannot tell which source is lying. Faithful
forms, parameters and sim inputs per arm: [05](05-cbf-baselines-faithful.md). Each fault case
states whether it hits position (PX4-CBF does not use it) or velocity (PX4-CBF does).

**Metric.** True collision or geofence breach rate; goal reached; time to goal; filter
intervention rate (fraction of steps where the command was changed).

**Pass / fail.** Pass if, across P1-P3 and all fault cases, F4 has breach rate <= 1%, at least
3x lower than F3 on jump and bias cases, and goal-reach rate >= 90% of F2's (not frozen).
**Fail** if F3 is within 1 percentage point of F4 on jump and bias (then the PL adds nothing
over BCBF), or if F2 alone is already <= 1% on all cases (then map-based margins are not
needed and the honest pitch is "we integrated PX4-CBF"). Also fail the narrowed claim
([07 section 2](07-pl-margin-prior-art.md#2-what-survives-narrow-engineering-only)) if F4 does
not cut wrong-exclusion breaches or the freezing rate against F3f and F3t, or does not beat F3m
on time to goal at equal breach rate.

### 3.5 Failure modes

- [ ] **Missing obstacle (truth not in the map).** A barrier only protects against obstacles it
  knows. Unmapped and unsensed means unprotected. Treat unknown space as unsafe (Zhou 2024).
- [ ] **Correlated errors.** If the "independent" source for the PL is range-to-wall residuals
  from a map registered with VIO, it shares VIO's error. Use a truly independent source.
- [ ] **Delay.** Range data latency up to 0.2 s for vision (PX4 docs `CP_DELAY`). The barrier
  must use delay-compensated state.
- [ ] **Actuator limits.** CBF-QP can be infeasible near obstacles at speed. Report
  infeasibility count; fall back to max braking.
- [ ] **Chatter and deadlock.** Filters can stall in symmetric corridors. Count "stuck".
- [ ] **Wind.** Unmodelled disturbance eats the margin; add a disturbance bound (shaoanlu
  repo has a disturbance observer variant).

## 4. Wider scan, ranked

Scores 1-5 per column. Novelty = what may remain after the hub's prior art. Build = 48h for a
team of our size in Python sim. Code = open code exists. License = commercial-friendly code.
Demo = visible on a screen in 3 minutes. Fit = fit to "real-world implementation".

| Direction | Key sources | Nov | Build | Code | Lic | Demo | Fit | Total /30 |
|---|---|---|---|---|---|---|---|---|
| Multi-hypothesis relocalization after VIO loss (keep 2-5 pose hypotheses from place recognition, hover-safe until one wins) | Faessler et al. ICRA 2015 (re-init after tracking loss; abstract only); hub doc 01 (Fox 1998, Platt 2012); RTAB-Map / ORB-SLAM3 relocalization in hub | 4 | 3 | 3 | 4 | 4 | 5 | 23 |
| LLM/VLM goal specification ("fly to the red door") feeding a classical planner + filter | [TypeFly](../../../catalog/resources/typefly-2023.md) (Apache-2.0), LM-Nav, AerialVLN, OpenFly in hub | 2 | 4 | 4 | 4 | 5 | 1 | 20 |
| Learned navigation foundation models (NoMaD / ViNT) as the nominal planner under a safety filter | [NoMaD](../../../catalog/resources/nomad-diffusion-nav-2023.md), [visualnav-transformer](../../../catalog/repos/robodhruv__visualnav-transformer.md) (MIT) | 2 | 3 | 5 | 4 | 3 | 2 | 19 |
| Energy- or time-optimal through obstacles | [rpg_time_optimal](../../../catalog/repos/uzh-rpg__rpg_time_optimal.md) (GPL-3.0), [GCOPTER](../../../catalog/repos/zju-fast-lab__gcopter.md), Qin 2026 | 2 | 3 | 3 | 2 | 3 | 3 | 16 |
| Learned high-speed flight (Loquercio et al., Science Robotics 2021, doi 10.1126/scirobotics.abg5810) | [uzh-rpg/agile_autonomy](https://github.com/uzh-rpg/agile_autonomy) (GPL-3.0, ROS Noetic, needs 15 Hz inference) | 2 | 1 | 4 | 2 | 2 | 2 | 13 |
| Event cameras for obstacle dodging (Falanga, Kleber, Scaramuzza, Science Robotics 2020, ~3.5 ms latency) | [event-vision list](https://github.com/uzh-rpg/event-based_vision_resources) in hub; no event camera here | 2 | 1 | 2 | 2 | 2 | 3 | 12 |
| RL racing policies (Swift) | [Swift, Nature 2023](../../../catalog/resources/swift-champion-drone-racing-nature.md); code not released | 1 | 1 | 1 | 1 | 2 | 2 | 8 |

Notes:

- **Relocalization** scores high on fit because "what does the drone do when VIO is lost
  indoors" is the question a product owner asks first. It reuses the hub's multi-hypothesis
  work (doc 01) in a new setting. Risk: needs a prior map or a first pass; in a never-seen room
  the hypotheses have nothing to match against.
- **LLM goal spec** demos well and fits our filter story (the LLM picks the goal, the filter
  keeps it safe), but adds no navigation innovation and judges asking for "real-world
  implementation" will discount it. Use as a demo garnish at most.
- **NoMaD/ViNT** is the best "any planner" to put under the filter in idea C: it shows the
  filter carrying safety for a learned policy. Trained on ground robots, so its own flight
  performance is not the point.
- Scores are our judgement from abstracts and READMEs, not from runs.

## 5. Synthesis: what to build

**Headline: idea C, the integrity-aware safety filter.** One sentence: "Any planner, even a
learned or LLM one, flies through our filter; it never hits what the range sensor sees, and when
navigation integrity drops it widens margins, slows down and holds a safe hover."

Why this one:

- It is the product shape judges recognise: runtime assurance (Simplex, ASTM F3269), a minimal
  change to the autopilot setpoint, and PX4-CBF proves it can live inside PX4 (BSD-3).
- It is the one place where the hub's strength (integrity, protection levels, FDE) adds
  something the prior art does not show: BCBF and MR-CBF use Gaussian or bounded error, not a
  fault-detecting integrity bound.
- The falsifier has a clean kill condition (F3 within 1 pp of F4), so we will know by hour 24
  whether the claim holds. If it fails, we still ship a working PX4-CBF-style filter with a
  measured comparison, which is a fine demo.
- It is buildable in Python in a day (CBF-QP for a double integrator is a closed-form or a tiny
  QP), and transferable to PX4 offboard via the hub's integration cards.

**Supporting piece: idea A as the replan trigger, not a planner.** When the filter intervenes
more than X% of steps or PL exceeds half the free-corridor width, the planner replans on a grid
inflated by the PL and caps speed by stopping distance. This turns "the filter blocks you" into
"the planner routes around it", and it is a few lines on top of A*.

**Parked: idea B.** Heavily covered (Costante, PAMPC, FIF, Murali, LA-Planner, Qin 2026). Keep a
Murali-style "yaw toward features" as the filter's recovery action only if time remains.

## 6. Not verified

- No full text was read for any paper in this doc. Claims come from abstracts, catalog records
  and search summaries. Numbers quoted (70% RMSE, 9.8 m/s, 55% => 100%, 3-10x, 3.5 ms, 7.8 m/s,
  > 100 km/h) are the authors' claims as summarised, not checked.
- Costante 2016 venue: the authors' group lists it as TRO16; not confirmed against IEEE.
- Gatekeeper venue (T-RO 2024) comes from a search summary; the repo README (last push
  2023-10-20) still says "under review at T-RO".
- Chen et al. backup CBF and Singletary 2022: arXiv only checked, venue not confirmed.
- Vahs 2023 BCBF: no peer-reviewed venue on the arXiv page.
- Chen and Shen (IEEE Access 2022), EVA-Planner, Lin et al. ICRA 2020, the 2026 conformal
  CBVF preprint (arXiv 2608.13819), the UWB covariance-margin preprint (arXiv 2512.17249) and
  SUPER (arXiv 2512.14189; v1 summary reported 89.1% recall for degradation prediction, the v2
  abstract reports no general accuracy gain): search snippets only, not added as records.
- PX4-CBF README notes the qpOASES FoV-constrained variant crashes on PixRacer Pro firmware;
  the unconstrained analytic case is what to trust. Not built here.
- `ntnu-arl/rhem_planner` has no license field; `shaoanlu/CBF_QP_safety_filter` has no license;
  `peteflorence/nanomap_ros` shows NOASSERTION. Read-only for a product.
- Faessler et al. ICRA 2015: title from search, PDF resolved but title page not extracted;
  author first names (Matthias Faessler, Flavio Fontana, Christian Forster) are from memory.
- Okamoto first name (Kazuhide) and Florence middle initial are from memory, not a fetched page.
- The ArduPilot and PX4 behaviour is from documentation summaries, not SITL runs.
- Wider-scan scores are judgement, not measurement.
- Queries run (WebSearch, 2026-11-09): uncertainty-aware quadrotor planning with obstacle
  inflation and chance constraints; Blackmore Ono Williams; Prentice Roy BRM; Okamoto Tsiotras
  covariance steering; Zhu Alonso-Mora CC-NMPC; NanoMap; Papachristos rhem; quadrotor speed
  adapted to VIO covariance; integrity-aware path planning with protection levels; Costante,
  Murali, Bartolomei, RAPTOR, Qin 2026; measurement-robust CBF (Dean, Cosner); gatekeeper;
  Wabersich predictive safety filter; backup CBF (Chen, Singletary); stochastic DTCBF (Cosner);
  CBF margin from estimator covariance; safety filter reacting to VIO degradation; open-source
  quadrotor CBF code; PX4 collision prevention; ArduPilot object avoidance; FASTER; Loquercio
  agile_autonomy; Falanga event dodging; VIO failure recovery and relocalization. GitHub:
  `gh search repos` for "gatekeeper quadrotor", "control barrier function quadrotor". Not
  searched: IEEE Xplore directly, patents, defence or vendor documentation (Skydio, Exyn,
  Shield AI) whose autonomy stacks likely contain similar runtime-assurance layers.
