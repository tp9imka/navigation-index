# 03. Adapt aerodynamic navigation parameters only when the data make them identifiable

<!-- about: res:sharma-laupre-skaloud-2023-identifying-aerodynamics-fixed-wing, res:laupre-pirlet-skaloud-2023-reliable-vdm-navigation, res:ardupilot-ekf3-drag-wind-source-copter-4-6-3, res:px4-ekf2-drag-wind-source-v1-16, res:ardupilot-pr-33326-wind-truth-cross-covariance, res:hausman-2016-observability-aware-trajectory-optimization, res:borup-fossen-johansen-2016-wind-velocity-observer, res:khaghani-skaloud-2018-vdm-navigation, res:leishman-2014-quadrotors-accelerometers -->

Research date 2026-11-09. Challenge 2 "Autonomous Frontiers" (EDGE hackathon). This is a
robustness layer for the top pick in [differentiators-scan.md](../../differentiators-scan.md)
section 2.1 (propulsion and drag as a virtual velocity sensor), not a standalone entry.

Records: [data/resources/innovation-pa-aero-adaptation.json](../../../data/resources/innovation-pa-aero-adaptation.json)
(26 resources). No new repos: ArduPilot and PX4 are already indexed and nothing else
needed a repo record.

## 1. Idea

A model-aided INS carries parameters: multirotor drag coefficients (momentum `k_m`, bluff
body `B`), fixed-wing aero coefficients, airspeed scale, mass/thrust, and wind. If the filter
keeps adapting them when the measurements carry no information about them, it drifts or
corrupts itself, and the corrupted value is what it flies on after GNSS loss.

The confounding is concrete. Multirotor drag in body x/y:

```
a_drag = -k_m * (v - w) - (rho / 2B) * |v - w| * (v - w)        (v = ground velocity, w = wind)
```

- GNSS on, straight steady leg: `v` is known, but `k_m` and `w` enter as `k_m * (v - w)`.
  One equation per axis, two unknowns => a ridge, not a point. Turns or speed changes
  (changing `v` direction and magnitude) break it, the same way the wind triangle needs
  heading changes.
- GNSS off: `v` is unknown too. Only air-relative velocity `v - w` is observable from drag.
  `w` and absolute `v` cannot be separated by any manoeuvre.
- GNSS off, our derivation (not verified): the IMU still measures velocity *changes*, so
  `v(t) = v0 + dv(t)`. With `dv` varying (accelerations), `k_m` and the constant `v0 - w`
  become separable. So a speed change can re-identify `k_m` without GNSS, but never `w`.

Proposal: compute an identifiability measure online (information increment of the
parameter block over a sliding window, from the observability Gramian or Fisher information
of the drag/airspeed measurements), update parameter directions only when the increment
passes a threshold, keep them as Schmidt consider states otherwise, and optionally request
excitation (a speed change or a turn) when a parameter is stale.

## 2. Prior art

Labels: **peer-reviewed** (read full text or substantial HTML), **preprint**, **abstract
only**, **code** (source read at a pinned ref), **discussion** (forum/PR), **talk, recording
not viewed**. "Hub" rows are already indexed and were not re-read here.

| Source | Type | What it does | How close |
|---|---|---|---|
| [Sharma, Laupre, Skaloud 2023, NAVIGATION 70(4)](https://navi.ion.org/content/70/4/navi.611) | peer-reviewed (HTML full text read; tables not reached) | Calibrates VDM aero coefficients and wind from flight data. Recursive observability Gramian in its eigenbasis; directions whose information increment exceeds a threshold are updated, the rest are Schmidt consider states (partial-update SKF). Offline: "cannot calibrate in real time". | **Closest.** Same gate mechanism, but offline calibration, fixed-wing, PPK-smoothed inputs |
| [Laupre, Pirlet, Skaloud 2023, J. Navigation](https://doi.org/10.1017/S0373463323000267) | peer-reviewed (full PDF read) | Real-time-oriented VDM filter, UD factorisation + partial Schmidt. During GNSS outage all VDM parameter error states and position go to consider mode by a fixed rule; initialisation ramps parameters from consider to full. Real flights: partial updates gave lower errors than full updates in all compared 2-min outages but one; 6-min outage about 250 m vs about 4.5 km for inertial coasting. | **Very close.** Freezing during outage exists and is flight-tested; the rule is phase-based, not measured |
| [Khaghani, Skaloud 2016, EuroCOW](https://isprs-archives.copernicus.org/articles/XL-3-W4/117/2016/) | abstract only | VDM as process model; wind and model parameters are filter states (always adapted). Simulation. | Origin of always-adapt baseline |
| [Khaghani, Skaloud 2018](../../../catalog/resources/khaghani-skaloud-2018-vdm-navigation.md) | hub | VDM navigation on a real fixed-wing, 3-min outages | Baseline context |
| [Mwenegoha et al. 2021, J. Navigation](https://doi.org/10.1017/S0373463321000424) | peer-reviewed (abstract + method pages read) | VDM-EKF with wind error states and VDM parameter states; Monte Carlo with mixed-dynamics trajectory and variable wind, outages 10-90 s | Always-adapt, simulation |
| [Svacha et al. 2020, RA-L](https://doi.org/10.1109/LRA.2020.2976308) | abstract only | Quadrotor UKF, 32 states incl. 14 constant parameters, IMU + motor speed; analytical observability | Online params, no gate (abstract level) |
| [Leishman 2014](../../../catalog/resources/leishman-2014-quadrotors-accelerometers.md), [Abeywardena 2013](../../../catalog/resources/abeywardena-2013-drift-free-velocity-estimator.md) | hub | Rotor drag makes accelerometers a velocity sensor | Physics basis |
| [Cioffi et al. 2023, HDVIO](https://arxiv.org/abs/2306.11429) | preprint (RSS 2023, read in part) | Hybrid point-mass + learned model as VIO residuals; external force from model mismatch | Needs vision; no parameter gate |
| [HDVIO2.0](../../../catalog/resources/cioffi-2025-hdvio2-wind-disturbance.md), [AI-IO](../../../catalog/resources/cui-2026-ai-io-aerodynamics-inertial-odometry.md), [NeuroBEM](../../../catalog/resources/bauersfeld-2021-neurobem.md) | hub | Wind/disturbance VIO, learned IO with rotor speed, hybrid aero model | Data and baselines |
| [ArduPilot EKF3, Copter-4.6.3](https://github.com/ArduPilot/ardupilot/blob/Copter-4.6.3/libraries/AP_NavEKF3/AP_NavEKF3_AirDataFusion.cpp) | code | See section 2.1. Source-type wind freeze; fixed drag coefficients; drag gains only on wind | Freeze by rule, no measurement |
| [ArduPilot PR 33326](https://github.com/ArduPilot/ardupilot/pull/33326) | discussion (merged PR) | Wind-as-truth zeroed variances but not cross-covariances => non-PD covariance, flaky dead-reckoning test for years. Fixed on master 2026-06-09 | Real defect from naive freezing |
| [PX4 EKF2 v1.16.0](https://github.com/PX4/PX4-Autopilot/blob/v1.16.0/src/modules/ekf2/EKF/aid_sources/drag/drag_fusion.cpp) | code | See section 2.1. Full-gain drag fusion, fixed coefficients, wind never frozen, heuristic accel-bias inhibit | Heuristic excitation gate, bias only |
| [PX4 draft PR 27884](https://github.com/PX4/PX4-Autopilot/pull/27884) | discussion (open draft) | Wind-only airspeed fusion on VTOL in MC mode, gated by lateral specific force; author says drag-based wind "was not precise enough" on their VTOL | Heuristic informativeness gate |
| [ArduPilot discourse 143360](https://discuss.ardupilot.org/t/custom-ekf3-position-wind-reset-for-gps-denied-flight-arduplane-4-4-3/143360) | discussion | GPS-denied ArduPlane: wind frozen at last value, injected externally; learning resumes with GPS | Practice: freeze + external wind |
| [Copter dead-reckoning failsafe docs](https://ardupilot.org/copter/docs/deadreckoning-failsafe.html) | doc | DR is seconds to tens of seconds (`FS_DR_TIMEOUT` typ. 10-30 s); drag coefficients hand-set | Scope of stock DR |
| [Borup, Fossen, Johansen 2016](https://torarnj.folk.ntnu.no/NOLCOS16_final_submission.pdf) | peer-reviewed (author PDF read) | Model-based wind observer with pitot scale; removes the PE requirement that the model-free version has | States the PE trade explicitly |
| [Wenz, Johansen 2019, MHE air data](https://hdl.handle.net/11250/2630200) | abstract only | MHE for wind, AoA, lift coefficient; related papers say attitude changes needed for PE | Excitation stated, not gated |
| Johansen et al. 2015 ICUAS, wind/AoA/SSA with standard sensors | abstract only (catalogue record) | Kinematic KF; cited by Laupre 2023 for insufficient observability on constant-velocity missions | Background |
| [Hausman et al. 2016](https://arxiv.org/abs/1604.07905) | preprint (read) | Plans trajectories maximising empirical local observability Gramian measures (condition number, smallest singular value) | Excitation request side |
| [Preiss et al. 2017, RSS](https://roboticsproceedings.org/rss13/p54.html) | abstract only | Observability cost inside mission trajectory optimisation | Excitation request side |
| [Bahnemann et al. 2017, ICRA](https://arxiv.org/abs/1612.05143) | abstract only | Sampling-based planning of informative multirotor ID trajectories (inertia, aero coefficients) | Active aero ID, offline planned |
| [Yang et al. 2019, RA-L](https://udel.edu/~pgeneva/downloads/papers/r05.pdf) | preprint (tech report read) | Four degenerate motions for online spatial/temporal calibration in aided INS | Degeneracy analysis, no gate |
| [Schneider et al. 2019](https://arxiv.org/abs/1901.07242) | preprint (read in part) | Information-theoretic selection of informative segments; calibration updated only from them | Information gate, VI calibration domain |
| [Zhang, Kaess, Singh 2016](https://frc.ri.cmu.edu/~kaess/pub/Zhang16icra.html) | abstract only | Solve only in well-conditioned directions of a degenerate problem | Same mechanism, odometry domain |
| [Huang, Mourikis, Roumeliotis 2010](https://experts.umn.edu/en/publications/observability-based-rules-for-designing-consistent-ekf-slam-estim/) | abstract only | Relinearisation creates spurious observable directions; OC-EKF and FEJ | Gate can be fooled the same way |
| [Ramos, Brink et al. 2022, JGCD](https://doi.org/10.2514/1.G006449) | abstract only | Factorised partial-update Schmidt-Kalman; FUSION 2023 follow-up adapts percentages from nonlinearity | The update knob a gate would drive |
| Brink 2017, "Partial-update Schmidt-Kalman filter", JGCD 40(9) | not read (cited by Laupre 2023) | Original partial-update SKF | Mechanism origin |
| [Chowdhary, Johnson 2011, ACC](https://skoge.folk.ntnu.no/prost/proceedings/acc11/data/papers/1207.pdf) / [2010, CDC](https://repository.gatech.edu/entities/publication/9827172d-a512-436d-9ff2-369a36d79b99) | abstract only | Concurrent learning: recorded-data buffer with min-singular-value test replaces PE | Excitation test pattern from adaptive control |
| [Ntouros et al. 2025](https://arxiv.org/abs/2507.03456) | preprint (abstract) | Fixed-wing airspeed from ESC power and rpm; in-flight ID from GPS velocity alone | Same wind-vs-scale confound, not discussed in abstract |
| [Udagedara, Bisheban 2026](https://arxiv.org/abs/2606.30581) | preprint (abstract) | UKF wind estimation on quadrotor along trajectories, simulation | No gate |
| [ION webinar, Sharma](https://www.ion.org/publications/webinar-sharma.cfm) | talk, recording not viewed (page has no recording link) | Presents the NAVIGATION 2023 paper | - |

L1 adaptive control was in the brief; no source on L1 with excitation gating was read in
this pass, so nothing is claimed about it.

### 2.1 What PX4 and ArduPilot actually do (source read, not run)

**ArduPilot EKF3, tag `Copter-4.6.3`:**

- `AP_NavEKF3_Control.cpp`, `NavEKF3_core::setWindMagStateLearningMode()`: wind states are
  inhibited on ground, without aiding, or without (yaw-aligned drag fusion or fly-forward).
- `AP_NavEKF3_Control.cpp`, `NavEKF3_core::setAidingMode()`: `windStateIsObservable =
  !inhibitWindStates && (posUsed || gpsVelUsed || optFlowUsed || rngBcnUsed ||
  bodyOdmUsed)`. A source-type rule. `dragUsed` and `airSpdUsed` count as velocity aiding
  but not as making wind observable.
- `AP_NavEKF3_core.cpp`, `NavEKF3_core::CovariancePrediction()`: if drag dead reckoning or
  `!windStateIsObservable`, `treatWindStatesAsTruth = true` and `P[22][22] = P[23][23] = 0`,
  no wind process noise. On return of observability, wind variance is reset to
  `WIND_VEL_VARIANCE_MAX` to relearn fast. `ConstrainVariances()` keeps them at zero.
- `AP_NavEKF3_AirDataFusion.cpp`, `NavEKF3_core::FuseDragForces()`: drag model uses fixed
  `EK3_DRAG_BCOEF_X/Y` and `EK3_DRAG_MCOEF`; only `Kfusion[22]` and `Kfusion[23]` (wind)
  are computed. The code comment: "Don't allow modification of any states other than wind
  velocity at this stage of development - we only need a wind estimate." Same on master
  (checked 2026-11-09).
- Master only: [PR 33326](https://github.com/ArduPilot/ardupilot/pull/33326) replaced the
  variance zeroing with `zeroStatesVarCov(22, 23)`. Our inference from the gain formulas: on
  master, while wind is treated as truth, every term of the wind gain is zero, so drag
  fusion changes no state during drag dead reckoning. In 4.6.3 the leftover cross-terms let
  the wind drift slightly. Not run.

**Consequence for section 2.1 of the scan:** in EKF3, drag fusion is a wind estimator, not a
velocity aid. It never corrects velocity or position, and after GNSS loss the wind is frozen
by rule. The "drag-aided vs unaided" SITL arm on stock EKF3 will probably show no holdover
gain. Verify in hour 1 before building on it (see section 8).

**PX4 EKF2, tag `v1.16.0`** (`drag_fusion.cpp` at `v1.17.0` differs only in parameter
names):

- `aid_sources/drag/drag_fusion.cpp`, `Ekf::fuseDrag()`: full `K = P * H / S` over all
  states, 5-sigma innovation gate, fixed `EKF2_BCOEF_X/Y`, `EKF2_MCOEF`. Drag does correct
  velocity here.
- `ekf_helper.cpp`, `Ekf::clearInhibitedStateKalmanGains()`: wind gains zeroed only when the
  wind flag is off. No observability freeze for wind during GNSS loss.
- `covariance.cpp`, `Ekf::predictCovariance()`: wind process noise added while variance is
  below `initial_wind_uncertainty^2`.
- `ekf_helper.cpp`, `Ekf::updateIMUBiasInhibit()`: accel-bias learning inhibited on
  heuristics (manoeuvre level too high, clipping, fake-position axis alignment); gyro has
  `bool is_bias_observable = true; // TODO: gyro bias conditions`. This is the only
  excitation gate in either stack, and it is heuristic.
- `python/tuning_tools/mc_wind_estimator/readme.md`: offline coefficient fit; "the current
  state of this script assumes no wind".

**Answer to the brief's question:** ArduPilot freezes wind on a source-type rule and never
adapts drag coefficients. PX4 never freezes wind and never adapts drag coefficients. Neither
measures identifiability. Neither adapts any aero coefficient online.

## 3. Remaining narrow contribution

Not found in this search: an online, measured-identifiability gate on aero/drag parameter
updates inside a navigation filter, evaluated through GNSS loss against the phase-based
Schmidt rule. Queries used: "observability-gated online aerodynamic parameter estimation
model-aided INS GNSS outage freeze parameters unobservable"; "multirotor drag coefficient
online adaptation wind GNSS-denied excitation identifiability Fisher information gating";
"quadrotor wind estimation drag model observability analysis wind and drag coefficient
jointly estimated EKF GNSS outage"; "Laupre Skaloud VDM navigation real-time Schmidt-Kalman";
plus author searches in section 2. One pass, English only.

What could still be ours, narrowest first:

1. **Move the Sharma 2023 Gramian-increment gate online** and run it inside the navigation
   filter, per eigen-direction, instead of offline calibration or Laupre's phase rule.
2. **Apply it to a small multirotor drag model** (`k_m`, `B`, wind, accel bias) of the kind
   PX4/ArduPilot already carry, where coefficients are today hand-set or fitted offline in
   still air.
3. **Use the GNSS-off identifiability of `k_m` from speed changes** (section 1, unverified):
   the gate may legitimately reopen `k_m` during an outage when the vehicle accelerates,
   while `w` stays frozen. Not seen in the sources read.
4. **Excitation request** when `k_m` is stale (a short speed change, not a turn). Planning
   for observability exists (Hausman, Preiss, Bahnemann); triggering it from a navigation
   filter's gate was not found in this pass.

Honest size: 1 and 2 are an engineering transfer of published EPFL ideas to multirotors. 3
is the only part with a chance of being new, and it is our own derivation, unproven. The
gate can only protect coefficients. It cannot make wind observable, and wind error is the
dominant post-loss drift term (scan section 2.1: ~1.1 m/s wind error => ~800 m over ~20 km).

## 4. Strongest baselines

| Baseline | What it is | Why it is strong |
|---|---|---|
| B1 never-adapt, offline-calibrated | Coefficients fitted once (PX4 tuning script style, or Sharma 2023 offline), fixed in flight; wind frozen at loss (EKF3 rule) | What both COTS stacks do. Unbeatable when coefficients have not changed |
| B2 phase-based Schmidt (Laupre 2023) | Parameters full while GNSS is on, considered during outage | Published, flight-tested, simple; already removes most outage corruption |
| B3 always-adapt | Parameters as random-walk states, always updated (Khaghani 2016, Mwenegoha 2021 style) | Tracks real changes (payload, battery, density) when excitation exists |
| B0 oracle | True coefficients | Upper bound |

The gate must beat B2 where B2 is weak (long straight leg with GNSS before loss, after a
coefficient change) and must not lose to B1 when nothing changed. If it only ties B2, drop it.

## 5. Falsification experiment (48h)

**Data.** ArduCopter 4.6.3 SITL as a data generator only (truth from `SIMSTATE`, IMU,
GNSS), our filter replayed offline in Python. SITL's multicopter frame models momentum and
bluff-body drag (scan section 2.1, not re-checked here). Real-data side check on
[AI-IO](../../../catalog/repos/sjtu-visys-team__ai-io.md) or [NeuroBEM](../../../catalog/resources/neurobem-dataset.md)
raw data (indoor, wind = 0, rotor speed present).

**Design.** Each flight: 60 s turns or speed changes (excited), then a 120 s straight
constant-speed leg (ridge), then GNSS removed for 120 s with one speed change at +40 s.
Factors:

- wind `SIM_WIND_SPD` 0 / 3 / 6 / 9 m/s, random direction;
- filter prior on `k_m` at 0.7x, 1.0x, 1.3x truth (stands in for a payload or battery change,
  no SITL physics change needed);
- seeds 1-5 => 60 flights per arm, same logs for all arms.

**Arms.** B0, B1, B2, B3 and G (gated: Gramian/Fisher information increment of the
parameter block over a 10 s window, threshold on the smallest eigenvalue increment, consider
states below it; FEJ-style fixed linearisation for the gate's own Jacobians).

**Metrics.** Horizontal error at 60 s and 120 s after GNSS loss; `|k_m - k_true| / k_true` at
loss and at +120 s; NEES of position and velocity (fraction inside the 95% chi-square band).

**Pass (keep the idea):** in the 0.7x and 1.3x cells with wind >= 3 m/s, G's median 120 s
error <= 0.75 x min(B2, B3); and in the 1.0x cells G is within 1.1 x B1; and G's NEES inside
the band at least as often as B3.

**Fail (drop it, keep B2 as the design):** G within 10% of B2 in the mismatch cells, or worse
than B1 by more than 10% in the 1.0x cells. Also fail if the `k_m` error at loss is not lower
for G than for B3 (the gate is not doing its one job).

**Real-data check (pass/fail on parameter only):** on AI-IO/NeuroBEM, G's `k_m` estimate over
hover and straight segments must vary less than B3's (std ratio <= 0.5) while staying within
10% of the batch fit over the whole sequence. Indoor data cannot test wind confounding.

## 6. Failure-mode checklist

- [ ] **Missing true hypothesis (model structure wrong).** Linear + quadratic drag misses
  blade flapping, ground effect, propwash, payload swing, gusts. The gate then measures
  information about the wrong model and adapts confidently. Check residual whiteness and
  NIS per window; refuse adaptation when residuals are structured; report it.
- [ ] **Correlated errors.** Body x/y accel bias looks like a constant air velocity under
  drag; keep accel bias in the gate's information matrix or the gate opens on bias. Turbulence
  is coloured, so per-sample information is overcounted => use an effective sample size or
  inflate `R`. The same accelerometer drives propagation and the drag measurement (both
  stacks do this); our GNSS-off `k_m` argument depends on it and may double count.
- [ ] **Map mismatch.** No map here. The analogue is model mismatch between airframes or
  configurations (payload, air density, battery sag changing thrust per rpm). That is the
  case the gate exists for; if mismatch is rare in the product, B1 wins.
- [ ] **Delayed measurements.** Both stacks fuse drag on the delayed time horizon (EKF3
  `storedDrag.recall`, PX4 drag buffer). The gate must use the same delayed states. Rotor
  speed vs accel latency and vibration aliasing shift the drag fit.
- [ ] **Wind/velocity ambiguity (central).** Without an absolute velocity or position fix,
  `w` and `v` are not separable by any manoeuvre. The gate cannot fix this; it only stops
  coefficients absorbing wind error. Frozen-wind error still dominates long outages. Say so
  in the pitch.
- [ ] **Spurious information from relinearisation** (Huang et al. 2010): an EKF evaluated at
  current estimates can report information that does not exist; compute the gate on fixed or
  first-estimate Jacobians.
- [ ] **Freezing done wrong.** Zeroing a variance but not its cross-covariances breaks
  positive definiteness (ArduPilot PR 33326). Consider states must keep their cross terms
  in a proper Schmidt update, or zero them together.
- [ ] **Threshold tuning.** One threshold across wind levels may not exist. If the pass
  result depends on per-cell tuning, it is a fail.

## 7. POC sketch (48h)

| Hours | Step | Reuses |
|---|---|---|
| 0-3 | Go/no-go: confirm in SITL logs that stock EKF3 drag fusion moves only wind (section 2.1), and that SITL prints drag coefficients | [sitl-docker](../../../samples/sitl-docker/), [golden-demo](../../../samples/golden-demo/) flight script |
| 3-10 | Generate the 60-flight log set (wind x seed), export IMU, GNSS, `SIMSTATE` truth | sitl-docker, [recording-replay](../../../samples/recording-replay/) contract |
| 10-22 | Extend the stdlib EKF to states `[p, v, w, k_m, 1/B, b_a]` with the drag measurement; implement B1, B2, B3, G as update policies over one filter | [gnss-ins-ekf-outage](../../../samples/gnss-ins-ekf-outage/) (`ekf_outage.py`, `matlite.py`) |
| 22-30 | Run all arms, score with the existing drift analyzer (time to N m and error at 60/120 s) | [px4-sitl-gps-denial](../../../samples/px4-sitl-gps-denial/) `drift.py` |
| 30-38 | Real-data parameter check on AI-IO raw data | AI-IO dataset (363 MB, per scan) |
| 38-44 | Fixed-wing branch only if the brief is fixed-wing: airspeed scale vs wind in the `dr` scenario | [golden-demo-fixedwing](../../../samples/golden-demo-fixedwing/) |
| 44-48 | Plot: `k_m` traces per arm through the straight leg and the outage, error bars per wind level | - |

Pitch line if it passes: "Our filter knows when it cannot learn: it freezes what the flight
does not reveal and asks for one speed change to relearn the drag."

## 8. Not verified

- Every statement in section 2.1 comes from reading source, not from running it. Whether
  stock EKF3 holdover improves with `EK3_DRAG_*` set at all is the hour-1 SITL check.
- The inference that master EKF3 drag fusion updates nothing during drag dead reckoning
  after PR 33326.
- GNSS-off identifiability of `k_m` from speed changes (section 1) is our derivation, not
  from a source and not simulated.
- Sharma 2023 numeric outage results (Tables 4-5 not reached in the HTML); only the method
  and qualitative results are cited.
- Brink 2017, Preiss 2017, Bahnemann 2017, Svacha 2020, Zhang 2016, Huang 2010, Ramos 2022,
  Chowdhary 2010, Wenz 2019, Johansen 2015, Khaghani 2016: abstract level or less.
- Whether ArduCopter SITL logs IMU at a rate useful for offline drag fitting under the
  default `LOG_BITMASK`, and whether SITL rotor speed (ESC telemetry) is logged.
- Ntouros 2025 journal venue (Aerospace Science and Technology) is from a search listing.
- The AIAA DOI link (Ramos 2022) returned HTTP 403 to curl (bot block); it was not opened
  in a browser.
- EuRoC lacking motor speeds is taken from the brief, not re-checked.
