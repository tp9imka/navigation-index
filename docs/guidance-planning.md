# Guidance and planning for a navigation entry

Written 2026-11-09 for an autonomous flight navigation task ([full-brief routing](problem-statement-decoder.md#route-a-full-brief-to-rows-and-first-pages)).
The hub is strong on estimation and integrity. This page covers the other half of GNC: where
the vehicle should go, and how it gets there, given what the estimator knows.

Records: [data/repos/guidance-planning.json](../data/repos/guidance-planning.json) (28 repos),
[data/resources/guidance-planning.json](../data/resources/guidance-planning.json) (20 resources).
Licenses and last-push dates below come from `gh api` on 2026-11-09, or from the LICENSE file
when GitHub reports NOASSERTION. Nothing on this page was built or run unless it says so.

Scope: navigation and guidance of the vehicle's own flight. No terminal guidance, homing,
intercept or targeting. See [export-control-and-ethics.md](export-control-and-ethics.md).

## 1. What guidance means for a nav entry

A flight stack has five layers. The hub's samples already cover the bottom-right corner (state
estimate and its integrity). Guidance is everything that consumes that estimate.

| Layer | Question | Typical method | Where it lives |
|---|---|---|---|
| Mission planning | Which waypoints, in what order, with what reserve? | Graph search, energy budget | GCS / companion |
| Route planning | Which path through terrain, wind and no-go areas? | A*, RRT*, Dubins / Dubins-airplane | Companion |
| Trajectory generation | Smooth, feasible reference in time | Min-snap polynomials, B-splines, MINCO | Companion |
| Guidance / path following | Turn the path into attitude or rate commands | L1, NPFG, TECS (fixed-wing); MPC, geometric control (multirotor) | Autopilot or offboard |
| Control | Track the commands | PID, INDI, rate loops | Autopilot |

The navigation angle: **every layer above control can use the estimator's uncertainty**. A
route can stay over terrain that TRN can lock onto. A trajectory can keep a nadir camera on
matchable texture. Guidance can slow down, climb or loiter when the protection level grows.
That coupling is the differentiator. A plain min-snap tracker is a commodity demo.

Default stance: let PX4 or ArduPilot own the inner loops and the path follower (NPFG / L1 /
TECS). Put your guidance logic on the companion and feed the autopilot waypoints, mission items
or offboard setpoints. Replacing the autopilot's guidance in 48h is a trap (section 5).

## 2. Capability table

Setup cost is a reading of each README, not a measured install, unless a hub sample says
otherwise. "Copyleft" means GPL: fine for the demo, rewrite or relicense before anyone ships it closed.

| Need | Pick | License | Setup cost |
|---|---|---|---|
| Fixed-wing GNC chain in pure Python (path following, Dubins manager, TECS, RRT, wind) | [mavsim_public](../catalog/repos/byu-magicc__mavsim_public.md) | GPL-3.0 (copyleft) | Low: Python, no ROS. Some files are student templates |
| Fixed-wing path following on a real autopilot | PX4 NPFG + TECS ([PX4](../catalog/repos/px4__px4-autopilot.md), [tuning guide](https://docs.px4.io/main/en/config_fw/position_tuning_guide_fixedwing.html)); ArduPlane L1 + TECS ([ArduPilot](../catalog/repos/ardupilot__ardupilot.md), [L1 guide](https://ardupilot.org/plane/docs/navigation-tuning.html)) | BSD-3 / GPL-3.0 | Zero extra: already in [sitl-docker](../samples/sitl-docker/) images |
| 2D minimum-radius paths | [pydubins](../catalog/repos/andrewwalker__pydubins.md) | MIT | Low: pip, builds a C extension |
| 3D fixed-wing paths in wind with climb limits | [EDuPlane](../catalog/repos/dlr-ft__eduplane.md) | Apache-2.0 (REUSE header; GitHub shows none) | Low: pip from source. Released 2026-11, unproven |
| Fixed-wing route over a DEM with terrain clearance | [terrain-navigation2](../catalog/repos/ethz-asl__terrain-navigation2.md) (ROS 2), [terrain-navigation](../catalog/repos/ethz-asl__terrain-navigation.md) (ROS 1 + Dockerfile) | BSD-3 | High: ROS + grid_map + OMPL workspace |
| Multirotor min-snap trajectory | [RotorPy](../catalog/repos/spencerfolk__rotorpy.md) `MinSnap` (Python, already carded); [mav_trajectory_generation](../catalog/repos/ethz-asl__mav_trajectory_generation.md) (C++) | MIT / Apache-2.0 | Low / medium (ROS 1 catkin) |
| Write your own min-snap or linear MPC QP | [OSQP](../catalog/repos/osqp__osqp.md) | Apache-2.0 | Low: pip |
| Trajectory optimisation, offline | [CasADi](../catalog/repos/casadi__casadi.md) | LGPL-3.0 | Low: pip wheels |
| MPC prototype in Python | [do-mpc](../catalog/repos/do-mpc__do-mpc.md) | LGPL-3.0 | Low: pip; not real-time onboard |
| Real-time NMPC with C code generation | [acados](../catalog/repos/acados__acados.md) | BSD-2 | Medium: build from source, 30-60 min first time (estimate) |
| MPC on a microcontroller | [TinyMPC](../catalog/repos/tinympc__tinympc.md) | MIT | Medium: linearised MPC only |
| Learned residual dynamics in MPC | [ML-CasADi](../catalog/repos/tum-aas__ml-casadi.md); method from [data_driven_mpc](../catalog/repos/uzh-rpg__data_driven_mpc.md) | MIT / GPL-3.0 | Medium / high (old ROS stack) |
| Close a custom loop around PX4 | [PX4 ROS 2 offboard](https://docs.px4.io/main/en/ros2/offboard_control.html), [px4-ros2-interface-lib card](integration-cards/auterion__px4-ros2-interface-lib.md); control law from [mavros_controllers](../catalog/repos/jaeyoung-lim__mavros_controllers.md) | BSD-3 | Medium: ROS 2 + micro XRCE-DDS |
| Localisability map (perception-aware planning) | Idea from [rpg_information_field](../catalog/repos/uzh-rpg__rpg_information_field.md); DEM version from the CRB gate in [terrain-heightmap-pf](../samples/terrain-heightmap-pf/) `nav2.py` | MIT / hub | Low if you build a 2D grid yourself; high to build the original |
| Perception term in the controller | PAMPC method ([rpg_mpc](../catalog/repos/uzh-rpg__rpg_mpc.md)), re-implemented in acados or do-mpc | GPL-3.0 (method is free to re-implement) | Medium |
| Belief-space planning | Implement directly: propagate EKF covariance along candidate routes. Reference: [edpl-ompl](../catalog/repos/sauravag__edpl-ompl.md), RRBT paper | edpl-ompl has no license: read only | Low for a 2D Python version |
| Energy per metre vs airspeed, wind, propeller | [AeroSandbox](../catalog/repos/peterdsharpe__aerosandbox.md), [UIUC propeller data](https://m-selig.ae.illinois.edu/props/propDB.html), rotary-wing power model (Zeng et al. 2018) | MIT / site terms | Low: pip + a lookup table |
| Battery model for remaining range | [PyBaMM](../catalog/repos/pybamm-team__pybamm.md) (equivalent-circuit model is enough) | BSD-3 | Low: pip |
| Propeller BEM | [CCBlade.jl](../catalog/repos/byuflowlab__ccblade.jl.md) | MIT | Medium: Julia |
| Clutter avoidance, multirotor | [EGO-Planner-v2](../catalog/repos/zju-fast-lab__ego-planner-v2.md); older [EGO-Planner](../catalog/repos/zju-fast-lab__ego-planner.md), [GCOPTER](../catalog/repos/zju-fast-lab__gcopter.md) | GPL-3.0 | Medium-high: ROS 1 |

Skip for a 48h build: [Agilicious](../catalog/repos/uzh-rpg__agilicious.md) (academic-use
license, code by request), [PANTHER](../catalog/repos/mit-acl__panther.md) and
[LA-Planner](../catalog/repos/robotics-star-lab__la-planner.md) (heavy ROS 1 builds; cite them,
do not build them), [mav_active_3d_planning](../catalog/repos/ethz-asl__mav_active_3d_planning.md),
[mav_control_rw](../catalog/repos/ethz-asl__mav_control_rw.md) and
[rpg_quadrotor_control](../catalog/repos/uzh-rpg__rpg_quadrotor_control.md) (ROS 1, unmaintained;
read for architecture).

## 3. 48h project ideas

Each idea adds a guidance piece to a sample that already ran in this hub. Numbers quoted from
samples are from [samples/README.md](../samples/README.md); check their input type in the
[evidence matrix](evidence-matrix.md) before pitching them.

### G1. Localisability-aware fixed-wing routing over terrain

**Pitch:** "The route is chosen so terrain navigation keeps working when GNSS is gone."

1. From a [Copernicus GLO-30](dataset-cards/copernicus-glo30.md) tile, compute a per-cell TRN
   information score. The CRB information gate in
   [terrain-heightmap-pf](../samples/terrain-heightmap-pf/) `nav2.py` already computes the
   Cramer-Rao bound for a fix; evaluate it on a grid instead of along one track.
2. Plan two routes between the same endpoints: shortest, and min (length + lambda x
   uncertainty). Use A* on the grid, then smooth with [pydubins](../catalog/repos/andrewwalker__pydubins.md)
   or [EDuPlane](../catalog/repos/dlr-ft__eduplane.md) for the turn radius.
3. Fly both through the [blind-flight-bench](../samples/blind-flight-bench/) navigators (radar
   altimeter over real GLO-30) and report final error and time-to-lock vs extra distance.
4. Stretch: load the route as an ArduPlane mission in
   [golden-demo-fixedwing](../samples/golden-demo-fixedwing/).

Risk: the info score correlates with roughness, and rough terrain also means terrain-clearance
limits. Add a clearance constraint or the "better" route flies into a ridge.

### G2. Integrity-aware guidance: the protection level drives the flight

**Pitch:** "When the navigation system stops trusting itself, the aircraft changes what it does."

1. Take the protection level (PL) and alert limit (AL) from
   [altpnt-integrity](../samples/altpnt-integrity/) or [multi-source-fde](../samples/multi-source-fde/).
2. Write a small guidance supervisor on the companion: PL < AL/2 => continue; AL/2 <= PL < AL
   => slow down and widen the corridor; PL >= AL => climb or divert to the nearest
   high-information area (from G1's map) and loiter until a fix restores PL.
3. Drive it in [golden-demo-px4](../samples/golden-demo-px4/) (PX4 SIH, coherent GPS drag,
   companion monitor already computes SS + PL) via MAVLink mission or offboard setpoints.
4. Report time with PL >= AL and cross-track error, with and without the supervisor.

Risk: the PL is only as honest as its error models. Quote the sample's own caveats.

### G3. Wind- and energy-aware fixed-wing route under GNSS loss

**Pitch:** "Plans the route that arrives with the most battery and the least dead-reckoning drift in this wind."

1. Build an energy-per-metre table vs airspeed with [AeroSandbox](../catalog/repos/peterdsharpe__aerosandbox.md)
   (or the airframe's real polar plus [UIUC propeller data](https://m-selig.ae.illinois.edu/props/propDB.html)).
2. Plan with [EDuPlane](../catalog/repos/dlr-ft__eduplane.md) trochoids in uniform wind;
   choose airspeed per leg from the table (max-range speed shifts with head / tail wind).
3. Score each candidate by energy and by dead-reckoning error growth. Use the airspeed DR case
   of [golden-demo-fixedwing](../samples/golden-demo-fixedwing/) (it already flies with 6 m/s
   wind and `SIM_WIND_TURB 1`) and the outage model of
   [gnss-ins-ekf-outage](../samples/gnss-ins-ekf-outage/).
4. Compare against ArduPlane's default straight legs at cruise airspeed.

Risk: an energy model with made-up coefficients. State the source of every coefficient, or
say "illustrative".

### G4. Perception-aware multirotor trajectory for visual fixes

**Pitch:** "The drone flies where its camera can find itself on the map."

1. Over a [VPAIR](dataset-cards/vpair.md) or [UAV-VisLoc](dataset-cards/uav-visloc.md) area,
   build a match-likelihood grid: run the matcher from
   [visual-geolocalization-lightglue](../samples/visual-geolocalization-lightglue/) or
   [geoloc-license-clean](../samples/geoloc-license-clean/) on tiles and record inlier counts.
2. Generate a [RotorPy](../catalog/repos/spencerfolk__rotorpy.md) `MinSnap` trajectory whose
   waypoints are pulled toward high-likelihood cells (penalty in the waypoint selection, not in
   the QP, to keep it simple).
3. Feed the expected fix rate along each trajectory into
   [altpnt-integrity](../samples/altpnt-integrity/) and compare position error and PL.

Risk: match likelihood measured on one season or altitude does not transfer. Say which
imagery the grid came from.

### G5. MPC tracking that knows the estimate is degrading (stretch)

Prototype an NMPC in [do-mpc](../catalog/repos/do-mpc__do-mpc.md) on RotorPy dynamics, with
tracking weights scaled by the EKF covariance from
[gnss-ins-ekf-outage](../samples/gnss-ins-ekf-outage/): track loosely while uncertain, tightly
after a fix. Port to [acados](../catalog/repos/acados__acados.md) only if time remains. Lower
priority than G1-G3: harder to demo and reviewers see MPC often.

Measured MPC number for close-area A=>B: [close-area-planner-mpc](../samples/close-area-planner-mpc/README.md)
(synthetic arena, known map, M3 Max laptop in Python): same outcomes as the A* carrot follower
(both 100 % reached, 0 % collision, 50 layouts per family), QP 0.22 ms median / 0.46 ms p95 with
warm start. Not a flight-computer timing.

## 4. Proposed decoder rows (proposed, not yet merged)

Same columns as [problem-statement-decoder.md](problem-statement-decoder.md). Numbered G1-G5
so they do not collide with existing rows. "Start from" lists hub samples that ran; the
guidance part itself has no runnable starter yet.

| # | Problem statement | Recommended approach | Stack | Datasets | Start from | Main risk | Pitch |
|---|---|---|---|---|---|---|---|
| G1 | Plan routes that keep the aircraft navigable without GNSS | Per-cell localisability score (TRN Cramer-Rao bound or visual match likelihood) => A* / RRT* with length + uncertainty cost => Dubins smoothing => fly both routes through the nav filter. Idea G1 / G4 above. | [pydubins](../catalog/repos/andrewwalker__pydubins.md), [EDuPlane](../catalog/repos/dlr-ft__eduplane.md), [Rasterio card](integration-cards/rasterio__rasterio.md), [terrain-navigation2](../catalog/repos/ethz-asl__terrain-navigation2.md) (reference) | [Copernicus GLO-30](dataset-cards/copernicus-glo30.md), [VPAIR](dataset-cards/vpair.md) | [terrain-heightmap-pf](../samples/terrain-heightmap-pf/) (CRB gate), [blind-flight-bench](../samples/blind-flight-bench/), [golden-demo-fixedwing](../samples/golden-demo-fixedwing/) | Informative terrain is often rough terrain: clearance constraint required; no guidance sample exists yet | "The route is chosen so the aircraft can still find itself." |
| G2 | Guidance that reacts to navigation integrity | Companion supervisor maps PL vs AL to actions (continue / slow and widen / climb or divert and loiter for a fix); autopilot keeps its own path follower. Idea G2. | [pymavlink card](integration-cards/ardupilot__pymavlink.md), [px4-ros2-interface-lib card](integration-cards/auterion__px4-ros2-interface-lib.md), [ArduPilot card](integration-cards/ardupilot__ardupilot.md) | Reuse the sample's flights | [golden-demo-px4](../samples/golden-demo-px4/), [altpnt-integrity](../samples/altpnt-integrity/), [multi-source-fde](../samples/multi-source-fde/) | PL honesty depends on error models; action thresholds are a design choice to justify | "When the nav system stops trusting itself, the aircraft changes what it does." |
| G3 | Fixed-wing long range with energy and wind limits | Energy-per-metre table from aero + propeller data => wind-correct trochoidal paths => airspeed per leg => score energy and DR drift. Idea G3. | [EDuPlane](../catalog/repos/dlr-ft__eduplane.md), [AeroSandbox](../catalog/repos/peterdsharpe__aerosandbox.md), [mavsim_public](../catalog/repos/byu-magicc__mavsim_public.md), [ArduPilot card](integration-cards/ardupilot__ardupilot.md) (TECS) | UIUC propeller data (no dataset card) | [golden-demo-fixedwing](../samples/golden-demo-fixedwing/) (airspeed DR in wind), [gnss-ins-ekf-outage](../samples/gnss-ins-ekf-outage/) | Invented aero coefficients; SITL airframe is not the real one | "Arrives with more battery and less drift in the same wind." |
| G4 | Smooth multirotor trajectory through waypoints in simulation | Waypoints => min-snap (RotorPy `MinSnap` or OSQP QP) => SE(3) tracking; add MPC only if the brief asks for control. | [RotorPy card](integration-cards/spencerfolk__rotorpy.md), [OSQP](../catalog/repos/osqp__osqp.md), [do-mpc](../catalog/repos/do-mpc__do-mpc.md), [acados](../catalog/repos/acados__acados.md) | None needed | No guidance sample; RotorPy's own examples per its card | Commodity unless coupled to the estimator (see G1, G2) | "Feasible trajectories, tracked in the loop with our own estimator." |
| G5 | Onboard path following / MPC that can run on the aircraft | Keep NPFG / L1 / TECS on the autopilot; if MPC is required, prototype in do-mpc, deploy via acados codegen or TinyMPC; measure solve time on the target CPU. | [acados](../catalog/repos/acados__acados.md), [TinyMPC](../catalog/repos/tinympc__tinympc.md), [PX4 card](integration-cards/px4__px4-autopilot.md) | None needed | [sitl-docker](../samples/sitl-docker/), [golden-demo-px4](../samples/golden-demo-px4/) | Solve time on laptop is not solve time on a flight computer; no timing measured here | "The controller runs on the aircraft, not just in the demo." |

## 5. Traps

- **Replacing the autopilot's guidance.** NPFG / L1 / TECS are tuned and flight-proven. Feed
  them better waypoints; do not rewrite them in 48h.
- **Planning on ground truth.** A planner demo that reads simulator truth is a planning demo,
  not a navigation demo. Plan on the estimate and show the gap.
- **ROS 1 everywhere.** Most research planners here are ROS 1 Noetic (EOL). Budget a Docker
  image or re-implement the core in Python. Do not discover this at hour 20.
- **GPL in a product pitch.** mavsim_public, rpg_mpc, data_driven_mpc, EGO-Planner-v2,
  LA-Planner and ArduPilot are GPL-3.0. Fine for the demo; say how the product path avoids it.
  edpl-ompl and high_mpc have no license at all: read only.
- **Agilicious is not open code.** Academic-use license, access by request.
- **Offboard heartbeat.** PX4 leaves offboard mode if the setpoint stream stops. Keep the
  stream in its own thread.
- **Wind is a guidance input.** Fixed-wing path following uses the wind estimate; under GNSS
  loss the wind estimate degrades too (golden-demo-fixedwing notes wind frozen at the switch).
- **Made-up energy numbers.** Every coefficient needs a source, or label the result
  illustrative.
- **Scope.** Keep it to own-vehicle flight. No pursuit, intercept or proportional-navigation
  material.

## 6. Reading order

1. [Beard & McLain](https://github.com/byu-magicc/mavsim_public) chapters 10-12 (path
   following, path manager, path planning) - fixed-wing guidance in one sitting.
2. PX4 [fixed-wing position tuning](https://docs.px4.io/main/en/config_fw/position_tuning_guide_fixedwing.html)
   and ArduPlane [L1](https://ardupilot.org/plane/docs/navigation-tuning.html) /
   [TECS](https://ardupilot.org/plane/docs/tecs-total-energy-control-system-for-speed-height-tuning-guide.html).
3. [Richter, Bry, Roy 2013](https://groups.csail.mit.edu/rrg/papers/Richter_ISRR13.pdf) for
   min-snap; [MINCO / GCOPTER](https://arxiv.org/abs/2103.00190) for the current approach.
4. Perception- and uncertainty-aware: [PAMPC](https://arxiv.org/abs/1804.04811),
   [Fisher Information Field](https://arxiv.org/abs/2008.03324),
   [RRBT](https://groups.csail.mit.edu/rrg/papers/abry_icra11.pdf).
5. Wind and energy: [Stastny & Siegwart 2019](https://arxiv.org/abs/1908.01381),
   [EDuPlane paper](https://arxiv.org/abs/2611.08004),
   [rotary-wing power model](https://arxiv.org/abs/1804.02238),
   ArduPlane [soaring](https://ardupilot.org/plane/docs/soaring.html) (thermal-energy use built
   into the autopilot).

## 7. Not verified

- No repo on this page was built or run in this hub. Setup costs are README readings.
- EDuPlane: license read from REUSE headers; GitHub API reports none. Repo is days old.
- The NPFG-to-Stastny link is inferred from PX4 naming and authorship, not checked in code.
- Lim et al. 2024 (terrain-navigation paper) open-access status not checked.
- No search found a maintained open wind-aware or energy-aware fixed-wing route planner beyond
  EDuPlane (wind) and AeroSandbox (energy models). Small single-author repos on GitHub search
  were skipped: no license, no maintenance.
