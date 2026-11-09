# 10. Kill test for the new headline: does relocalization after VIO loss already exist?

Prior-art scan, 2026-11-09 (loop-57), copying the method of [07](07-pl-margin-prior-art.md).
Claim under test, from [close-area-relocalize](../../../samples/close-area-relocalize/README.md)
and the [README](README.md) headline:

> When VIO is lost indoors, the drone hovers, matches its range scan against the known map with up
> to 5 pose hypotheses, flies a short information-gain move if they still tie after a hover
> timeout, never commits on a tie, and re-anchors the estimate only when one hypothesis wins.

Scope: the vehicle's own navigation. Nothing was run for this doc. Every number below is the
source's own claim with the input type the source reports, or a hub sample number marked
synthetic. Autopilot behaviour was read from source code at a pinned tag (section 4).

## 1. Verdict

**Exists (cite), in mechanism.** Every part of the loop is published, and the passive half
already runs on a Crazyflie:

1. **Multi-hypothesis tracking + a null hypothesis + a move to gather information + a commit
   threshold** is Jensfelt and Kristensen, IEEE T-RA 17(5), 2001 (full text read). They keep
   Gaussian hypotheses with a probability of correctness each, add H0 "none of them is right",
   stop only when the strongest hypothesis passes P > 0.8, and move the robot to where new
   features are visible. They also name "pick the action that best separates the two most likely
   hypotheses" as the cheaper alternative, which is our separation score (e). Indoor ground robot,
   real runs: 90 % of 20 trials localized, 2 min and 17.5 m on average.
2. **Expected-entropy move choice over a multimodal belief in a symmetric corridor** is Fox,
   Burgard, Thrun 1998 (already in the hub, read in full in
   [innovation-prior-art 01](../innovation-prior-art/01-disambiguating-maneuvers.md)). It is our
   arm (f). (f) beat our proposed (e) in the corridor (80 % vs 70 % reached) and was within 1
   run of it on random layouts (seed 0 jump 99 vs 100, seed 1 100 vs 99), all synthetic.
3. **Scan-to-map relocalization after kidnapping on a small indoor drone** is AF-MCL,
   [arXiv 2610.32645](https://arxiv.org/abs/2610.32645), Oct 2026 (full text read): Crazyflie
   2.1, four Multi-ranger beams plus yaw, EDT likelihood field (the same model as our
   `ScanMatcher`), augmented-MCL particle injection on divergence. Global localization from
   sparse ToF on a nano drone is Muller et al., DATE 2023,
   [arXiv 2212.00710](https://arxiv.org/abs/2212.00710).

**For small indoor drones, augmented MCL on the range sensors is the obvious baseline.** AMCL has
had kidnap recovery (slow / fast likelihood averages) for two decades. AF-MCL is that baseline on
the exact Day-1 platform. An AF-MCL-style arm was added later (loop-67, seed 2 held out, synthetic: on the 72-beam sensor the hub's arm reached B as often or more than an AF-MCL-style filter in all 4 cells, 0 wrong commits vs 0-32; on 4 beams every arm fails; [relocalize README](../../../samples/close-area-relocalize/README.md#af-mcl-baseline-particle-filter-with-random-particle-injection-loop-67)).

**Novel composition, one sentence (engineering only):** a hover gate plus a "never commit on a
tie" acceptance rule plus a collision check over every live hypothesis, wrapped around the
autopilot's reset contract so that PX4 or ArduPilot only receives a re-anchored pose (with a new
`reset_counter`) once one hypothesis has won. The autopilots themselves snap to whatever pose a
reset hands them (section 4).

## 2. Strongest baseline and the numbers to beat

| Baseline | Source, input type | Number |
|---|---|---|
| AF-MCL (augmented MCL, beam filtering) on a Crazyflie | arXiv 2610.32645; Webots simulation for kidnapping, real flights for accuracy | Kidnap recovery 2.9 s vs 16.9 s for plain MCL (sim). Real flights in a 2.10 x 1.63 m arena: 6.4-7.7 cm mean error, filter on a host PC |
| Global MCL from two 8x8 ToF sensors on a nano drone | arXiv 2212.00710; recorded real flights replayed offline, 6 seeds | 0.15 m accuracy, above 95 % success in a 31.2 m2 map |
| Jensfelt MHT with H0 and active moves | T-RA 2001; real ground robot | 90 % of 20 runs, 2 min, 17.5 m travelled |
| Our (f) Fox-style info-gain move | [close-area-relocalize](../../../samples/close-area-relocalize/README.md), synthetic | Corridor 80 % reached vs (e) 70 %; random layouts 99-100 %, 0 wrong commits (seed 0 and held-out seed 1). **Narrowed since:** held-out seeds 2-4 pass only on random and u_trap (100 %, 0 wrong); 83.3-97.2 % in five other families, 33 wrong commits in warehouse ([held-out matrix](../../../samples/close-area-relocalize/README.md#held-out-matrix-seeds-2-4-7-families-harder-faults-loop-56)) |
| Our (b) commit at once + innovation re-check | same sample, synthetic | 100 % reached on random layouts and on the corridor, with 2-8 wrong commits per 100 or 20 runs that later matches corrected. Held-out matrix since: 69 wrong commits and 17 of 180 runs collided in warehouse; on a stale map it reached 97-100 % on every rung with 0-2 % collisions ([stale map](../../../samples/close-area-relocalize/README.md#imperfect-prior-map-loop-55)) |

The hardest baseline in our own data is (b). It reached B every time; the safety case for (c)
to (f) rests on 0 wrong commits, not on reach rate. A judge who knows AMCL will say (b) plus
the innovation test is "AMCL with a reset". That is fair.

## 3. Hits

Closeness: **same** = the claim's mechanism; **partial** = most of it, one key piece missing;
**adjacent** = related idea, different mechanism. "Full" = full text read; "abstract" = abstract
or search summary only.

### 3.1 Active and multi-hypothesis localization (ground robots)

| # | Source | Label, read | What it does | Close |
|---|---|---|---|---|
| 1 | Jensfelt, Kristensen, "Active Global Localisation for a Mobile Robot Using Multiple Hypothesis Tracking", IEEE T-RA 17(5):748-760, 2001 ([PDF](https://www.csc.kth.se/~patric/publications/gal_journal.pdf)) | peer-reviewed, full | MHT Kalman hypotheses, P(correct) per hypothesis, H0 for "none is right", run ends when the best passes 0.8, greedy move to the unvisited node with most visible features | **same** (ground robot, features not scans) |
| 2 | Fox, Burgard, Thrun, Active Markov Localization, RAS 1998 (hub record) | peer-reviewed, full (hub doc 01) | Grid belief, action = expected entropy reduction minus path cost; symmetric corridor, random motion failed in all 10 extra runs | **same** for the move; no hover, ground robot |
| 3 | Platt et al., Non-Gaussian belief space planning, ICRA 2012 (hub record) | peer-reviewed, full (hub doc 01) | Plans actions that maximize predicted-observation separation between hypotheses | **same** as our (e) score |
| 4 | Thrun, Burgard, Fox, Probabilistic Robotics (2005) augmented MCL; Nav2 AMCL `recovery_alpha_slow` / `recovery_alpha_fast` ([docs](https://docs.nav2.org/jazzy/configuration_and_development/configuration_guide/others/configuring_amcl/)) | docs, full (Nav2 page); book from memory | Random-particle injection when the short-term likelihood falls below the long-term one. Both alphas default 0.0 (off); docs suggest 0.001 / 0.1. Nav2 BT node `ReinitializeGlobalLocalization` for a kidnapped robot | **partial**: passive recovery, commits to the particle mean |
| 5 | Zhang et al., kidnapped robot via sparse feasible hypotheses, IEEE TIM 2026, [arXiv 2511.01219](https://arxiv.org/abs/2511.01219) | peer-reviewed, abstract | Stationary single-scan global relocalization, RRT-sampled hypotheses, early termination | **partial**: stationary multi-hypothesis scan-to-map, no move, no tie refusal stated |
| 6 | Zangeneh et al., CVAE pose regression, IROS 2024, [arXiv 2410.04989](https://arxiv.org/abs/2410.04989) | peer-reviewed, abstract | Camera relocalization with a sampled pose posterior under repetitive structure | adjacent (camera, no action) |
| 7 | Agarwal, Tamjidi, Chakravorty, "Motion Planning for Active Data Association and Localization in Non-Gaussian Belief Spaces", WAFR 2016 ([Springer](https://link.springer.com/10.1007/978-3-030-43089-4_19)) | peer-reviewed, abstract | Plans motion to resolve multimodal beliefs from ambiguous data association | **partial** (theory and sim, ground) |

### 3.2 Small and indoor drones

| # | Source | Label, read | What it does | Close |
|---|---|---|---|---|
| 8 | AF-MCL, [arXiv 2610.32645](https://arxiv.org/abs/2610.32645), 2026 | preprint, full | Crazyflie + Multi-ranger, known map, EDT likelihood, beam rejection, particle injection; kidnap recovery 2.9 s vs 16.9 s (Webots) | **same** for passive scan-to-map recovery; no hover gate, no move, no tie refusal |
| 9 | Muller, Zimmerman, Polonelli, Magno, Behley, Stachniss, Benini, DATE 2023, [arXiv 2212.00710](https://arxiv.org/abs/2212.00710) | peer-reviewed (venue from AF-MCL refs), full | Onboard MCL on GAP9 from two 64-zone ToF; starts in the wrong maze, converges as the drone flies; >95 % success, 0.15 m | **partial**: global localization on a nano drone, passive |
| 10 | Faessler, Fontana, Forster, Scaramuzza, ICRA 2015 (hub record, [PDF](https://rpg.ifi.uzh.ch/docs/ICRA15_Faessler.pdf)) | peer-reviewed, full | After tracking loss or a throw: level attitude from IMU, hold height from the range sensor, let it drift to initialize SVO, null velocity, then lock the current position. >85 % success over several hundred throws; failures when vision could not initialize | **partial**: "stabilize first, re-initialize second" on a quadrotor, but restarts in a new frame; no map, no hypotheses |
| 11 | Niculescu et al., NanoSLAM, IEEE IoT-J 2023, [arXiv 2309.12008](https://arxiv.org/abs/2309.12008) | peer-reviewed, abstract | Onboard SLAM on a 44 g drone, 4.5 cm mapping accuracy | adjacent (mapping, not recovery) |
| 12 | Grzonka, Grisetti, Burgard, "A Fully Autonomous Indoor Quadrotor", T-RO 2012 ([PDF](http://ais.informatik.uni-freiburg.de/publications/papers/grzonka12tro_quad.pdf)); Bry, Bachrach, Roy, ICRA 2012 ([PDF](http://groups.csail.mit.edu/rrg/papers/icra12_aggressive_flight.pdf)) | peer-reviewed, abstract | Laser localization in a known map on MAVs (ground-robot MCL adapted; Gaussian particle filter) | **partial**: map-based MAV localization exists since 2012; whether either does kidnap recovery was not checked |

### 3.3 VIO and SLAM stacks on tracking loss

| # | Source | Label, read | Behaviour on loss | Close |
|---|---|---|---|---|
| 13 | ORB-SLAM3, T-RO 2021, [arXiv 2007.11898](https://arxiv.org/abs/2007.11898) | peer-reviewed, abstract | Starts a new map in the Atlas; merges with old maps when a place is recognized | adjacent: place-recognition reloc, commits on a verified match |
| 14 | RTAB-Map ([rtabmap_ros #100](https://github.com/introlab/rtabmap_ros/issues/100)) | code / community, summary | `Odom/ResetCountdown` resets odometry after N lost frames; a new map hides the old one until a loop closure links them; localization mode relocalizes by loop closure | adjacent |
| 15 | VINS-Mono, [arXiv 1708.03852](https://arxiv.org/abs/1708.03852) (hub record) | peer-reviewed, abstract | Failure detection restarts the estimator; loop detection gives relocalization | adjacent |
| 16 | ModalAI VOXL OpenVINS, [Initialization and Resets](https://docs.modalai.com/voxl-open-vins-init/) | docs, full | 30 Hz health monitor issues hard resets on low quality, feature starvation, bad covariance; the estimator restarts in a new frame; docs warn of jump discontinuities | adjacent: no map reloc, so the autopilot sees a reset |
| 17 | DJI forum and help pages ([forum](https://forum.dji.com/forum.php?mod=viewthread&tid=332301)) | community, snippet | No GPS and no vision => ATTI mode: no position hold, no braking, pilot flies | adjacent: vendor gives up position |
| 18 | Skydio X10 attitude-mode article ([support](https://support.skydio.com/hc/en-us/articles/24882788195995-How-to-fly-in-Attitude-Mode-with-Skydio-X10)); R10 limitations | docs, search snippet only (page returned 403) | Loss of reliable navigation => Attitude Mode, pilot must fly; to regain VIO, descend to about 60 ft AGL and fly side to side | adjacent: the "move to recover" step exists, but as a manual instruction |

No hit was found for "multi-hypothesis tracking with a hover gate" on a drone, or for a drone
that refuses to commit on a tie and holds a hover instead.

## 4. What the autopilots do with `reset_counter`

Read with `gh api repos/.../contents/<file>?ref=<tag>` on 2026-11-09. Line numbers are at the tag.

### 4.1 PX4 EKF2, tag v1.17.0 (commit d6f12ad1, released 2026-05-13)

- `src/modules/mavlink/mavlink_receiver.cpp:1532` copies ODOMETRY `reset_counter` into
  `vehicle_odometry`; `src/modules/ekf2/EKF2.cpp:2338` copies it into the EV sample.
- `src/modules/ekf2/EKF/aid_sources/external_vision/ev_control.cpp:52`: `ev_reset` is true when
  the counter differs from the previous sample. Line 97: the previous sample is stored only when
  quality passes `EKF2_EV_QMIN`, so a reset sent at low quality is still seen once quality returns.
  Same line in `main` is 54.
- `ev_pos_control.cpp:194`: reset = `ev_reset` or yaw-alignment change or bias-estimator change.
  `updateEvPosFusion` (lines 239-258): if quality passes and GNSS position is not fused =>
  `resetHorizontalPositionTo(measurement)` (line 246), a hard snap to the EV pose; with GNSS
  fused it only re-sets the EV bias. If quality fails at a reset => `stopEvPosFusion()` (line 258).
- Without a counter change, a step is innovation-gated (`EKF2_EVP_GATE`) and rejected while
  quality is low (line 266). After 1 s without fusion (`no_aid_timeout_max`, `common.h:481`) and
  with quality passing, EKF2 resets to the EV position anyway (lines 269-298), up to 5 times per
  flight (line 231).
- Height, velocity and yaw: `ev_height_control.cpp:113` resets altitude; `ev_vel_control.cpp:66`
  resets velocity only if EV is the only horizontal aiding source; `ev_yaw_control.cpp:89` resets yaw.

### 4.2 ArduPilot EKF3, tag Copter-4.7.2 (commit fb773567)

- `libraries/AP_VisualOdom/AP_VisualOdom_MAV.cpp:49`: a pose is consumed only if
  quality >= `VISO_QUAL_MIN`; line 51 passes `get_reset_timestamp_ms(reset_counter)` to the EKF.
- `AP_VisualOdom_Backend.cpp:83-88`: a changed counter sets the reset timestamp to now. It is
  only called for consumed poses, so a reset at low quality is registered on the next good one.
- `libraries/AP_NavEKF3/AP_NavEKF3_Measurements.cpp:1083` (`writeExtNavData`): a new reset time
  sets `posReset`.
- `AP_NavEKF3_PosVelFusion.cpp:629-636`: in absolute aiding with ExtNav as the XY source, `posReset`
  => `ResetPositionNE` to the ExtNav position, plus `ResetPositionD` if ExtNav is the height source.
- The velocity path (`writeExtNavVelData`, `AP_NavEKF3_Measurements.cpp:1137`) has no reset handling.

**What follows for the design.** Neither autopilot checks a reset; both trust the companion's new
pose. PX4 also snaps to any step that persists for 1 s at good quality. So the companion must hold
`quality` below `EKF2_EV_QMIN` / `VISO_QUAL_MIN` while it hovers lost, and raise it together with
one `reset_counter` increment only at accept. A wrong commit by arm (b) reaches the EKF either way.
This gating is our contract, not a feature of the autopilot. Hover without EV is then the
autopilot's own fallback (flow, or attitude-only drift), which the sample models as a perfect hover.

## 5. What survives (narrow, engineering only)

- The **hover gate with a bounded timeout**, then a move, then hover again. Faessler 2015 is the
  nearest drone precedent (stabilize first), but it re-initializes into a new frame with no map.
- **Never commit on a tie** on a flying vehicle: Jensfelt's 0.8 threshold and H0 do the same on a
  ground robot that can stop for free; AF-MCL and AMCL always output a particle mean.
- **Move feasibility checked against every live hypothesis**, not only the best one. Fox and
  Jensfelt plan from the best hypothesis or the belief; we did not find a drone version.
- **The autopilot contract** in section 4: quality held low while lost, one counter increment at
  accept. Not novel, but not written down anywhere we found for PX4 / ArduPilot relocalization.

None of these is an algorithm. Our own data shows no gain from our move score over Fox's (f), so the
contribution is "Fox / Jensfelt, made safe to fly", not a new estimator.

**The sentence a judge would accept:** "Map-based relocalization with several hypotheses and an
information-gain move is known (Fox 1998, Jensfelt 2001) and already runs passively on a
Crazyflie (AF-MCL 2026). We add the flight-safety wrapper: the drone hovers instead of flying on
a guess, re-anchors PX4 or ArduPilot only when one hypothesis wins, and only flies moves that
are safe for every hypothesis it still holds. In our synthetic arena that gave 0 wrong commits
against 2-8 for committing at once."
**Narrowed since (synthetic):** say "on open layouts with a dense range sensor and an exact map".
The 0 wrong commits held on random and u_trap only; warehouse gave 33 and maze 6
([held-out matrix](../../../samples/close-area-relocalize/README.md#held-out-matrix-seeds-2-4-7-families-harder-faults-loop-56)).
Unmapped added obstacles gave 16 / 21 wrong commits and 7 % collisions; all 12 hits on an
unmapped obstacle came after a move ([stale map](../../../samples/close-area-relocalize/README.md#imperfect-prior-map-loop-55)).
A 4-beam deck gave 48 / 64 % reached
([4-beam](../../../samples/close-area-relocalize/README.md#relocalization-with-a-4-beam-sensor-hover-and-yaw-spin-loop-54)).
"Safe for every hypothesis" checks moves against the map, not the live scan.

**Closest prior art a judge will name:** AF-MCL (same platform and sensor, same likelihood model).
Second: Fox 1998 / Jensfelt 2001. Third: plain AMCL with recovery alphas on.

**Test that would kill what is left:** add an AF-MCL / AMCL arm (particle filter, injection on,
output = particle mean, no hover gate) to close-area-relocalize on the same layouts, faults and
corridor. If it reaches B as often as (f) with no more wrong commits (> 0.5 m at the time the
pose is used), the hover gate and tie refusal add nothing measurable.

## 6. Queries run (WebSearch and fetch, 2026-11-09, 2010-2026 focus plus the 1998-2001 classics)

Academic: Faessler 2015 "automatic re-initialization and failure recovery" quadrotor; NanoSLAM
Crazyflie ToF multizone localization; AMCL kidnapped robot augmented MCL recovery_alpha;
Jensfelt Kristensen 2001 active global localization MHT; ORB-SLAM3 tracking lost relocalization
atlas; Grzonka Grisetti Burgard indoor quadrotor MCL; nano drone Crazyflie MCL known map
multi-ranger kidnapped; active localization UAV multiple hypotheses information gain; "active
localization" quadrotor symmetric entropy particle filter; UAV LiDAR relocalization prior map
multi-hypothesis 2024-2025; quadrotor global localization yaw in place hover until converged;
"perceptual aliasing" drone indoor multi-hypothesis; Bry Bachrach Roy 2012 Gaussian particle
filter; VINS-Fusion failure detection relocalization.

Stacks and vendors: RTAB-Map `Odom/ResetCountdown`; ModalAI qVIO / OpenVINS auto reset PX4;
Skydio lost visual navigation behaviour; DJI vision positioning lost ATTI; Nav2 AMCL global
localization and recovery.

Full texts fetched: Faessler 2015 and Jensfelt 2001 PDFs (text pulled with a stdlib zlib
extractor, words partly split), AF-MCL and Muller 2023 arXiv HTML, ModalAI and Nav2 doc pages.

Code: PX4-Autopilot `gh search code reset_counter`, then `ev_control.cpp`, `ev_pos_control.cpp`,
`ev_vel_control.cpp`, `ev_height_control.cpp`, `ev_yaw_control.cpp`, `EKF2.cpp`,
`mavlink_receiver.cpp`, `common.h` at v1.17.0; ArduPilot `AP_VisualOdom_MAV.cpp`,
`AP_VisualOdom_Backend.cpp`, `AP_NavEKF3_Measurements.cpp`, `AP_NavEKF3_PosVelFusion.cpp`,
`GCS_Common.cpp` at Copter-4.7.2. `gh api` on ETH-PBL/NanoSLAM and ETH-PBL/Matrix_ToF_Drones
(both GPL-3.0).

Not searched: Google Scholar, IEEE Xplore, patents, Skydio and DJI engineering papers, Bitcraze
forum, IMAV / IROS drone-race team reports, Chinese and Russian literature.

## 7. Not verified

Reconciled 2026-11-09 (loop-28) against
[close-area-relocalize](../../../samples/close-area-relocalize/README.md). The sample's later runs
narrowed our own numbers (sections 2 and 5) but verified none of the source claims below. Still open:

- The section 5 kill test ran after this doc (loop-67): see the AF-MCL baseline section of the
  relocalize README. Not re-run here: the paper's own kidnap scenario.
- AF-MCL author list: only the arXiv submitter and the last author were visible; the 2.9 s /
  16.9 s kidnapping result is Webots simulation; its real flights ran the filter on a host PC.
- Muller 2023 venue (DATE 2023) comes from AF-MCL's reference list; its success rate comes from
  replaying recorded flights, not closed-loop recovery.
- Jensfelt 2001 and Faessler 2015 text came from a crude PDF text extraction; numbers were read
  in context (90 % of 20 runs, 0.8 stop threshold, >85 % of throws) but tables were not parsed.
- Grzonka 2012 and Bry 2012: abstracts only; text extraction of the Grzonka PDF failed. Whether
  either recovers from kidnapping was not checked.
- Zhang 2026, Zangeneh 2024, Agarwal 2016, ORB-SLAM3, VINS-Mono, NanoSLAM: abstracts or search
  summaries only.
- Skydio: the X10 attitude-mode and R10 limitations pages returned 403; claims come from search
  snippets. DJI behaviour is from forum and help-page snippets.
- Probabilistic Robotics augmented MCL is named from memory; the Nav2 defaults were read.
- PX4 and ArduPilot code was read, not run; parameter interplay (`EKF2_EV_QMIN`, `EKF2_EVP_GATE`,
  `VISO_QUAL_MIN`, source sets) was not tested in SITL. Behaviour on `main` was checked only for
  the `ev_reset` line. The flight-repo `make first-flight-reloc` run increments `reset_counter`
  inside the synthetic arena loop, not inside an autopilot.
- "Not found" in section 3 means not found by these queries; Skydio, DJI and defence vendors may
  do map relocalization internally without publishing it.

Records added: `data/resources/loop-57.json` (7 resources).
