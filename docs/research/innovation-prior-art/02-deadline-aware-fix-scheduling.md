# 02. Deadline-aware scheduling of expensive absolute fixes

Prior-art scan, 2026-11-09, for EDGE hackathon Challenge 2 "Autonomous Frontiers". Scope: the
vehicle's own navigation only. Records added: `data/resources/innovation-pa-scheduling.json`
(20 resources) and `data/repos/innovation-pa-scheduling.json` (2 repos, each checked with
`gh api repos/...` on 2026-11-09). JointLoc's repo was already indexed (`repo:luoxubo/jointloc`,
alt-nav lane) and is only linked.

Source labels used below:

- **paper (full text read)** - peer-reviewed, PDF or journal HTML read (fully or the sections named).
- **paper (abstract only)** - peer-reviewed, only the abstract or a catalog record read.
- **preprint (abstract only)** - arXiv, abstract page read.
- **patent (full text read)** - Google Patents page read.
- **code** - repository checked with `gh api`, README or source file read, code not run.
- **metadata only** - title and venue confirmed via Crossref, content not read. No claims made.
- **computed here** - a number derived in this scan from a committed hub result file.

## 1. Idea

Onboard absolute fixes are expensive and only sometimes succeed. In the hub's
[e2e-visual-nav-vpair](../../../samples/e2e-visual-nav-vpair/) run, one DINOv2 + LightGlue
top-5 fix costs 0.73 s median per frame on an M2 Max, and LightGlue is 78 % of it. A Pi 5 runs a
ViT at 611.65 ms per inference ([path-to-product](../../path-to-product.md)), so a Pi-class
fix is seconds. TRN and thermal matching have the same shape.

Proposal: a scheduler that decides **when** to run a fix, **on which frame** and **with which
method** (skip, top-1, top-5, TRN), from three predicted quantities:

- (a) **deadline** - time until the predicted protection level (or error bound) crosses the
  alert limit if no fix arrives, from covariance propagation;
- (b) **success probability** - from cheap signals: retrieval score, map coverage under the
  position prior, outcome of the last attempt, terrain informativeness, map age;
- (c) **processing delay** - the fix arrives late; it must still fit the filter's
  delayed-fusion horizon, or be handled as an out-of-sequence measurement.

The decision is worth making only when compute is contended (shared GPU with obstacle
detection, power or thermal limits, several fix methods competing). On a dedicated
accelerator with nothing else to run, fixed-rate at the max sustainable rate is optimal and
this idea has no value. Say that in the pitch.

## 2. Prior art

"How close" is to the full idea: deadline + success probability + delay, choosing when and
which expensive fix to run on an aircraft.

| # | Source | Type | What it does | How close |
|---|---|---|---|---|
| 1 | Trimpe, Campi, "On the Choice of the Event Trigger in Event-based Estimation", EBCCSP 2015, doi 10.1109/EBCCSP.2015.7300691 ([PDF](https://marco-campi.unibs.it/pdf-pszip/EBCCSP-2016.pdf)) | paper (full text read, extracted text, conclusion section not located) | Compares send-on-delta, measurement-based, variance-based (VBT) and relevant-sampling triggers for a scalar KF. VBT thresholds the prediction variance `c^2 P(k|k-1) + r` and does not need the measurement value. The paper shows the optimal VBT decisions "can thus be precomputed off-line" from (a, q, r, X0) and run as a time-based schedule. | **High on (a).** Covariance-threshold triggering is solved and, for a linear model with sure arrival, collapses to a fixed schedule. So the deadline alone is not a contribution. Communication cost, not compute; no success probability; no delay. |
| 2 | Trimpe, "Predictive and Self Triggering for Event-based State Estimation", CDC 2016, doi 10.1109/CDC.2016.7798733 ([arXiv 1609.07534](https://arxiv.org/abs/1609.07534)) | preprint (abstract only); CDC version per Crossref | Self-trigger predicts the next trigger instant at the current one; predictive trigger says whether a transmission is needed within a horizon, so the resource can be re-allocated in advance. One Bayesian decision framework. | **High on (a) + "plan ahead".** This is "predict the deadline and book the resource". Networked sensors, sure arrival, no compute latency. |
| 3 | Mourikis, Roumeliotis, "Optimal Sensor Scheduling for Resource-Constrained Localization of Mobile Robot Formations", IEEE T-RO 22(5):917-931, 2006, doi 10.1109/TRO.2006.878947 ([record](https://experts.umn.edu/en/publications/optimal-sensor-scheduling-for-resource-constrained-localization-o/)) | paper (abstract only) | Chooses per-sensor measurement frequencies under a cap on total EKF updates (processing / bandwidth) to minimise the trace of the weighted steady-state covariance. Convex SDP. | **High on "compute-constrained localization".** Steady-state rates, not event decisions; measurements always succeed; no delay. The closest robotics framing. |
| 4 | Joshi, Boyd, "Sensor Selection via Convex Optimization", IEEE T-SP 57(2):451-462, 2009 ([page](https://web.stanford.edu/~boyd/papers/sensor_selection.html)) | paper (abstract only) | Picks k of m sensors to minimise estimation error; convex relaxation gives a subset and a bound. | Low-medium. Static selection math a scheduler can borrow for "which method". |
| 5 | Mo, Sinopoli, "Towards Finding the Critical Value for Kalman Filtering with Intermittent Observations", arXiv 1005.2442, 2010 | preprint (abstract only) | Abstract restates Sinopoli et al. 2004: with Bernoulli observation arrival there is a critical probability below which the KF error diverges; bounds only for general systems. Sinopoli et al., IEEE TAC 49(9):1453-1464, 2004: metadata only. | Medium on (b). Random success is modelled, but as i.i.d. and not chosen. The hub data shows fix failures are not i.i.d. (section 6). |
| 6 | Carlone, Karaman, "Attention and Anticipation in Fast Visual-Inertial Navigation", ICRA 2017 / IEEE T-RO 2019, doi 10.1109/TRO.2018.2872402 ([arXiv 1610.03344](https://arxiv.org/abs/1610.03344)) | preprint (abstract only); venues per Crossref | Selects which visual features to process under limited compute, by forward-simulating dynamics and predicting each feature's utility over a horizon. Greedy with submodularity guarantees. | Medium. Same "anticipate future value under a compute budget" logic, but inside the VIO front end, not for absolute fixes, no deadline or delay. |
| 7 | Mathur, Khedekar, Alexis, "Resource-aware Online Parameter Adaptation for Computationally-constrained Visual-Inertial Navigation Systems", arXiv 2106.00289, 2021 | preprint (abstract only) | Profiles available compute online and adapts VIO front-end and back-end parameters (S-MSCKF, VINS-Mono, OKVIS on EuRoC); reports comparable accuracy "at a fraction of the original computational cost". | Low-medium. Compute-aware VIO; no absolute fixes, no deadline. |
| 8 | Zhao, Smith, Vela, "Good Graph to Optimize: Cost-Effective, Budget-Aware Bundle Adjustment in Visual SLAM", arXiv 2008.10123, 2020 ([code](https://github.com/ivalab/gf_orb_slam2)) | preprint (abstract only) + code | Predicts upcoming estimation needs, sets a per-step size budget, picks the best-conditioned BA subgraph. | Low-medium. Budget-aware back end, same anticipate-and-budget pattern. GPL-3.0 code (ORB-SLAM2 base). |
| 9 | Hajebi, Zhang, "Stopping Rules for Bag-of-Words Image Search and Its Application in Appearance-Based Localization", arXiv 1312.7414, 2013 | preprint (abstract only) | Stops BoW search early for easier queries; less compute, small accuracy loss; applied to appearance-based localization. | Medium on "anytime" fix. Per-query effort, not when to query. |
| 10 | Carson, Ford, Milford, "Predicting to Improve: Integrity Measures for Assessing Visual Localization Performance", IEEE RA-L 7(4):9627-9634, 2022, doi 10.1109/LRA.2022.3191205 ([QUT](https://eprints.qut.edu.au/234489/), [code](https://github.com/QVPR/predict2improve)) | paper (abstract only) + code (README read) | Supervised per-frame predictor of whether a VPR estimate is correct, from signals of the VPR technique itself; 74 % average precision over 12 dataset/technique pairs. Used to discard bad estimates. | **High on (b), after the fact.** It predicts success once retrieval has run. Not used to decide whether to spend the expensive matching step. MIT code. |
| 11 | Carson, Ford, Milford, "Unsupervised Quality Prediction for Improved Single-Frame and Weighted Sequential Visual Place Recognition", ICRA 2023, doi 10.1109/ICRA48891.2023.10160679 ([arXiv 2307.01464](https://arxiv.org/abs/2307.01464)) | preprint (abstract only); ICRA per Crossref | Training-free quality prediction used to weight sequence matching. | Medium on (b). Same limitation as row 10. |
| 12 | Malone, Vora, Peynot, Milford, "Dynamically Modulating Visual Place Recognition Sequence Length For Minimum Acceptable Performance Scenarios", IROS 2024, doi 10.1109/IROS58592.2024.10802570 ([arXiv 2407.00863](https://arxiv.org/abs/2407.00863)) | preprint (abstract only); IROS per Crossref | MLP predicts, per map section, the shortest VPR sequence that meets a target performance, from appearance variation in the region under a coarse position prior. | **High on (b) + compute.** Spend just enough compute where the place is hard, set from a position prior. Per-place effort, not deadline- or delay-driven; ground vehicle. |
| 13 | Luo et al., "JointLoc: A Real-time Visual Localization Framework for Planetary UAVs Based on Joint Relative and Absolute Pose Estimation", IROS 2024 ([arXiv 2405.07429](https://arxiv.org/abs/2405.07429), [code](https://github.com/LuoXubo/JointLoc)) | preprint (full text read via HTML summary) + code (README read) | States that absolute localization on every frame "will consume a lot of computing resources", so runs it at a fixed interval: tried 1, 10, 50, 100 frames, picked 10. Match confidence (SSIM x mean match degree) sets the next search radius. RTX 2080 Ti desktop. | **High as a baseline.** A UAV paper that hits exactly this trade-off and answers it with a hand-tuned fixed rate. MIT code. |
| 14 | Power et al., "A Benchmark Comparison of Visual Place Recognition Techniques for Resource-Constrained Embedded Platforms", arXiv 2109.11002, 2021 | preprint (abstract only) | Accuracy, encoding time, matching time, memory on ODroid, UP, Raspberry Pi 3 boards. | Low. Input for (c): cost tables, no scheduling. No Jetson. |
| 15 | Larsen, Andersen, Ravn, Poulsen, "Incorporation of Time Delayed Measurements in a Discrete-time Kalman Filter", CDC 1998, pp. 3972-3977 ([DTU record](https://orbit.dtu.dk/en/publications/incorporation-of-time-delayed-measurements-in-a-discrete-time-kal/)) | paper (abstract only) | Delayed vision measurement (long processing) is extrapolated to the present with past and present estimates, then fused with an optimal gain; reviews alternatives. | Medium on (c). How to fuse a late fix, not whether to start one. |
| 16 | Bar-Shalom, "Update with out-of-sequence measurements in tracking: exact solution", IEEE T-AES 38(3):769-777, 2002, doi 10.1109/TAES.2002.1039398 | metadata only (Crossref); abstract seen only as a search snippet | Standard OOSM reference (exact one-step-lag update, extended to multi-step lags in 2004). Content not read; no claims taken from it. | Medium on (c), by reputation. |
| 17 | PX4 EKF2 delayed fusion horizon: [`estimator_interface.cpp`](https://github.com/PX4/PX4-Autopilot/blob/cb61f8c4f1f57573746f8a75999e24225ee6c0fc/src/modules/ekf2/EKF/estimator_interface.cpp), `TimestampedRingBuffer.hpp`, `module.yaml` at main `cb61f8c` (2026-10-29); [tuning guide](https://docs.px4.io/main/en/advanced_config/tuning_the_ecl_ekf.html) | code (source read) + doc | EKF runs on a delayed horizon; `EKF2_DELAY_MAX` default 200 ms, **max 1000 ms**. EV samples are stamped `time_us - EKF2_EV_DELAY - dt/2` and buffered; a sample is popped only when the horizon time is within 100 ms after its timestamp (`pop_first_older_than`). Observation buffer = 1.5 x `EKF2_DELAY_MAX`. | **Hard constraint on (c).** A fix older than about 1 s cannot enter PX4 EKF2 at its capture time. A Pi-class VPR fix is already near or past that. |
| 18 | Yano, Azumi, "Work-in-Progress: Multi-Deadline DAG Scheduling Model for Autonomous Driving Systems", arXiv 2505.06780, 2025 (related DOI 10.1109/RTSS62706.2024.00049) | preprint (abstract only) | Splits Autoware's end-to-end timing constraint into local deadlines per sub-DAG; extends Global EDF. | Low-medium. Real-time scheduling of the perception graph with fixed deadlines; deadlines are not derived from navigation error. |
| 19 | Ali et al., "On the Necessity of Real-Time Principles in GPU-Driven Autonomous Robots", ICRA 2025, doi 10.1109/ICRA55743.2025.11128627 ([PDF](https://robotics.cs.unc.edu/publications/Ali2025_ICRA.pdf)) | paper (abstract and introduction read) | Simulated drone in a forest: interference from non-flight-critical GPU work degrades reaction time and causes crashes; TimeWall isolates and prioritises obstacle detection and control. | Medium on motivation. Shows the GPU is contended on a real drone stack, which is the condition under which fix scheduling pays. |
| 20 | Thales, US 9,046,894 B2, "Navigation aid method for determining the path of an aircraft", priority FR 2009-04-28 ([Google Patents](https://patents.google.com/patent/US9046894B2/en)) | patent (full text read via summary) | Defines a "limit time": when the predicted protection radius reaches the alarm limit assuming GNSS is lost now. Recomputed each epoch; used to decide whether an approach can be completed and when to leave it. | **High on (a) for aircraft.** The deadline exists in aviation practice, used for guidance decisions, not to schedule aiding. |
| 21 | Sagem, US 8,843,243 B2, "Method and system for determining protection limits with integrated extrapolation over a given time horizon", priority FR 2009-09-07 ([Google Patents](https://patents.google.com/patent/US8843243B2/en)) | patent (full text read via summary) | Extrapolates the KF error model over a horizon with a constant transition matrix to give future protection limits. No alert-limit crossing time, no aiding scheduling. | Medium on (a). Forward PL prediction mechanics. |

Hub overlap:

- [e2e-visual-nav-vpair](../../../samples/e2e-visual-nav-vpair/) already runs fix period 1 and 5
  and caches per-candidate cost (`t_s`) and inliers in `results/frontend.json`. It is the
  fixed-rate baseline and the replay substrate.
- [guidance-planning.md G4](../../guidance-planning.md) "fly where the camera can find itself"
  uses a match-likelihood grid to change the **path**. This idea keeps the path and changes
  **when to compute**. The same grid can feed (b).
- [terrain-heightmap-pf](../../../samples/terrain-heightmap-pf/) has a CRB information gate on
  TRN updates, an informativeness signal for (b) on the TRN side.
- [hackathon-playbook.md section 17](../../hackathon-playbook.md) lists "USBL fix scheduling" as a
  stretch, underwater. Same question, other domain.
- [gnss-ins-ekf-outage](../../../samples/gnss-ins-ekf-outage/) and
  [altpnt-integrity](../../../samples/altpnt-integrity/) give the covariance growth and the PL
  machinery for (a). Neither predicts time-to-AL.

## 3. What may remain (narrow)

Not found in this search: a scheduler for **aircraft absolute fixes** that combines a
PL-to-AL deadline, a per-attempt success probability **with temporal correlation of
failures**, and a processing delay checked against the filter's fusion horizon, and chooses
between fix methods of different cost. Queries run (WebSearch, 2026-11-09):

- `Trimpe event-based state estimation "send-on-delta" Kalman filter arXiv`
- `sensor scheduling Kalman filter value of information visual localization UAV when to localize`
- `"localizability" prediction aerial visual localization uncertainty when to trigger map matching UAV`
- `"anytime" visual localization computational budget place recognition early termination robot`
- `event-triggered visual localization UAV map matching trigger covariance threshold absolute fix computation`
- `scene matching suitability analysis matching area selection probability of correct match aircraft navigation`
- `resource-aware visual-inertial odometry computational budget adaptive keyframe embedded drone paper`
- `deadline-aware scheduling perception tasks autonomous vehicle DAG GPU real-time "localization" response time ROS 2 executor analysis`
- `terrain-aided navigation when to take altimeter measurement informative terrain adaptive measurement scheduling TRN`
- `UAV absolute visual localization satellite image matching adaptive frequency trigger only when uncertainty grows computational load Jetson`
- `"time to alert" OR "time to exceed alert limit" covariance prediction aiding request integrity navigation "when to" request fix`
- `"learning when to localize" OR "when to relocalize" OR "relocalization trigger" visual localization compute budget`

That is absence in this search, not novelty. Each piece exists: (a) rows 1, 2, 20; (b) rows
10-12 and the Chinese "matchability" literature (not read, see section 9); (c) rows 15-17;
compute budgets rows 3, 6-8. The defensible claim is the **combination, measured on real-flight
fix costs and outcomes**, plus two findings the hub data already shows:

1. Fix failures cluster. On VPAIR, P(fail | previous attempt failed) is 0.66-0.69 against an
   unconditional 0.21-0.53 (section 6). An i.i.d. success model (row 5) is wrong here, and
   "retry right after a failure" is the wrong default.
2. The cheap pre-match signal is weak. The DINOv2 top-1 similarity separates success from
   failure with AUC 0.68 (stride 1 and 8). A scheduler cannot lean on it alone.

## 4. Strongest baseline

Ranked by how hard it is to beat:

1. **Covariance threshold with lead time** (VBT, row 1, plus the latency). Start a fix when
   predicted PL at `now + expected latency` crosses `theta * AL`. Row 1 shows that for a linear
   model with sure arrival this is just a precomputable schedule, so it is cheap and strong.
   This is the baseline the idea must beat; the only levers left are (b) and (c).
2. **Fixed rate at the max sustainable rate.** On the M2 Max that is about one fix per frame
   (0.73 s per ~1 s frame). JointLoc (row 13) does a hand-tuned version (every 10th frame).
   On VPAIR, stride 8 map, strict gate, +2 deg heading, gate mode: period 1 gives 89 fixes,
   94.1 % availability at AL 50 (fault-free PL), max error 40.7 m; period 5 gives 19 fixes,
   61.2 %, max 94.4 m (`results/e2e_result.json`).
3. **Run every frame, drop late ones.** One matcher worker; frames that arrive while it is busy
   are skipped; a result older than the fusion horizon is discarded. This is what a naive
   ROS 2 pipeline does.

If the matcher has its own accelerator and nothing else needs it, baseline 2 wins outright.
The pitch must name the contended resource.

## 5. Falsification experiment (48 h, open data, no GPU)

**Data.** VPAIR sample (Zenodo 6473989), already cached by the hub: per-frame candidate
lists and per-candidate `t_s`, `inliers`, `h_scale` in
`samples/e2e-visual-nav-vpair/results/frontend.json` (heading 0) and `frontend_yaw2.json`
(+2 deg). 188 scored frames, 8.53 km, map strides 1/4/8. No re-matching needed.

**Replay rules.**

- Time: 1 frame = 1 s (VPAIR has no timestamps; the e2e README uses the same convention).
- Cost of an attempt = query prep + DINOv2 (0.086 s median, from `timing`) + sum of `t_s` over
  the candidates matched. Top-1 vs top-5 is the "method" choice.
- One worker. A fix captured at frame k with cost c arrives at `k + c * s`, where `s` is a
  platform slowdown: 1 (M2), 2, 4 (Pi-class guess, not measured). Fuse at capture time if
  `c * s <= H`; H = 1.0 s (PX4 `EKF2_DELAY_MAX` max) or H = 3 s (companion-side filter with
  delayed-state fusion). Otherwise drop, or fuse with an OOSM/delayed-state update as a
  variant.
- Filter, gate and PL: reuse `altpnt_v2` through `run_fusion.py` imports, gate mode, AL 50 m.

**Schedulers.** B1 fixed period 1-8; B2 VBT with lead time, sweep theta; B3 every frame, drop
late; S proposed: start an attempt when expected PL reduction x p_hat per compute second beats
a price lambda, or when the deadline minus expected latency falls under one frame. p_hat from
(top-1 similarity, margin, last-attempt outcome, map coverage under the VO prior). Ablations:
S with p_hat constant; S without the delay term.

**Leakage control.** Fit p_hat on frames 10-99, test on 100-198, then swap. Also fit on heading
0, test on +2 deg.

**Metrics.** Compute seconds per km vs availability (PL < AL), deadline misses (epochs with
error >= AL or PL >= AL), HMI epochs, false fixes fused. Plot each scheduler as a curve
(compute per km on x, availability on y).

**Pass / fail.**

- **Pass**: at the availability of B1 period 1, S spends at most 70 % of B1's compute, **and** at
  equal availability S spends at least 15 % less compute than B2, on both halves, strides 1 and
  8, and both headings, with HMI and false fused no higher than B2.
- **Fail (idea falsified)**: S is within 10 % of B2's compute at equal availability, or
  "S with p_hat constant" is within 10 % of S. Then the deadline is all that matters, and
  row 1 already owns it. Given AUC 0.68 for the cheap signal, this is a likely outcome; the
  last-attempt and map-coverage features carry the bet.
- **Delay check**: at s = 4 and H = 1.0 s, report how many fixes B3 drops. If S does not
  reduce deadline misses vs B3 by at least 25 %, the delay term adds nothing.

## 6. Failure-mode checklist

| Failure mode | What it does to the scheduler | Evidence or test |
|---|---|---|
| Missing true hypothesis (no overlapping tile, out-of-map) | p_hat should be about 0; spending is pure waste. If the position prior has drifted, the coverage feature lies. | Stride 8 is wider than the 336 x 252 m footprint, so many frames have no overlapping tile (e2e README). Test: S must skip those frames without being told. |
| Correlated errors (failures cluster on the same terrain) | i.i.d. success model over-retries. Back-to-back attempts on the same water body or field fail together. | **Computed here** from `frontend.json`, heading 0, strict gate (25 inliers, scale 0.67-1.5), top-5, frames 10-198: stride 1 pass rate 0.79, P(fail \| prev fail) 0.69, longest failure run 9 frames; stride 4: 0.61, 0.62, 9; stride 8: 0.47, 0.66, 13. Six runs of 5+ failures at stride 8. One flight, one season. |
| Map mismatch (season, render vs photo, registration offset) | p_hat learned on one map does not transfer; a well-matched but offset fix passes as "success". | VPAIR map and truth share a source, so registration offset is invisible here (e2e README limits). Test on frontend_yaw2 and say the map is not independent. |
| Delayed measurement older than the filter horizon | Fix is computed, then silently dropped; compute spent, no information. | PX4 EKF2 pops an EV sample only within 100 ms after its stamped time; `EKF2_DELAY_MAX` max 1000 ms (row 17). M2 match p95 0.82 s already sits near that; a 2-4x slower board passes it. Mitigation: companion-side delayed-state filter (rows 15-16), or the scheduler picks top-1 to stay inside H. |
| Wind / velocity ambiguity (drift model wrong) | Deadline predicted too late, error crosses AL before the fix is started. Worst for fixed-wing airspeed dead reckoning. | The VO error model (heading 2.77 deg, scale 3.3 %) is fitted on this same flight (e2e README). Test: run S with the filter told 1 deg heading error while the data carries +2 deg; count deadline misses vs B1. |
| Gate rejects a true fix | Scheduler books a success that the filter throws away. | 0 false fused in all 48 gate-mode e2e runs, but true-fix rejections were not counted. Count them. |
| Shared resource priority inversion | Fix scheduled "just in time" is pre-empted by obstacle detection and misses its deadline. | Row 19 shows GPU contention on a drone stack. Not modelled in the replay; add a random busy-time process as a variant. |

## 7. POC sketch (48 h)

1. **Hours 0-4.** New script beside, not inside, the e2e sample (imports `nav_core`,
   `run_fusion`, `altpnt_v2`). Load `frontend.json` and `frontend_yaw2.json`; build per-frame
   tables: candidates, `t_s`, gate pass, retrieval scores, VO-prior position.
2. **Hours 4-12.** Event-driven replay with one worker, slowdown s and horizon H. Implement B1,
   B2, B3 and reproduce the e2e period-1 and period-5 rows within rounding before going on.
3. **Hours 12-24.** Deadline: propagate the filter covariance forward with no fix, find the
   first epoch where the fault-free PL crosses AL (closed form per step, same Q as altpnt v2).
   p_hat: logistic regression on 4 features, split as in section 5. Scheduler S.
4. **Hours 24-36.** Sweeps (theta, lambda, s in {1, 2, 4}, H in {1, 3} s), curves, ablations,
   the wind-misspecification run.
5. **Hours 36-48.** One SVG of compute-per-km vs availability for all schedulers, a table of
   pass/fail per condition, and a navdash replay of one run where S skips a map gap that B1
   pays for.

Measured timings reused: `match_pair_s` median 0.098 s / p95 0.178 s per candidate,
`match_topk_s` stride 1 median 0.567 s / p95 0.822 s, prep 0.064 s, DINOv2 0.022 s (M2 Max,
MPS, `frontend.json`). Second method: the TRN source from
[two-source-integrity-vpair](../../../samples/two-source-integrity-vpair/) (simulated sensor,
real DSM) as "method 2", only if hours remain; its runtime is not in the committed results.

Real-world story: the scheduler is a few hundred lines on the companion computer, between the
camera queue and the matcher. It needs a position covariance, so it should run on the
companion-side filter (as the e2e sample does), not on autopilot telemetry: the hub's
[autopilot-gnss-fault-handling](../../autopilot-gnss-fault-handling.md) shows that
`EKF_STATUS_REPORT.pos_horiz_variance` and `ESTIMATOR_STATUS.pos_horiz_ratio` are test ratios,
not covariances.

## 8. Verdict

- **Exists**: covariance-triggered updates (and their reduction to fixed schedules), compute-
  budgeted VIO, per-frame VPR success prediction, delayed-measurement fusion, and an aviation
  "limit time" when PL hits AL. Each is solved on its own.
- **May remain**: one scheduler for aircraft absolute fixes that combines deadline, a success
  probability that models failure clustering and map coverage, and the fusion-horizon limit,
  measured on real-flight fix costs. Narrow, and only useful when compute is contended.
- **Falsifier**: VPAIR replay; fail if S is within 10 % of the covariance-threshold baseline's
  compute at equal availability, or if removing p_hat costs under 10 %.

## 9. Not verified

- Trimpe and D'Andrea, "Event-based state estimation with variance-based triggering", IEEE TAC
  59(12), 2014: cited inside row 1 only; not read.
- Sinopoli et al., TAC 2004: metadata only; result known through row 5's abstract.
- Bar-Shalom 2002 OOSM: metadata only.
- Vitus, Zhang, Abate, Hu, Tomlin, "On efficient sensor scheduling for linear dynamical
  systems", Automatica 2012: seen only in search snippets; not added.
- Joerger, Duenas Arana, Spenko, Pervan, "Landmark data selection and unmapped obstacle
  detection in lidar-based navigation", ION GNSS+ 2017 (integrity-driven measurement
  selection): PDFs returned 404 / connection refused; seen only in search snippets; not added.
- Chinese "scene matching suitability / matchability" papers (e.g. Remote Sensing 15(17):4353,
  2023): MDPI returned 403; not read; not added. Likely the deepest prior art on predicting
  match success for aircraft reference imagery.
- KAIST dissertation on "anytime" VPR (Kim, 2026): only a table-of-contents snippet seen.
- Kalman sensor scheduling with i.i.d. intermittent fixes vs the clustered failures computed
  here: one flight, one season, 188 frames. Not a general claim.
- Jetson / Pi fix latency: not measured; s = 2, 4 are guesses. Quote only the M2 numbers.
- Which autopilot topic carries a usable horizontal position covariance (PX4 uORB
  `vehicle_local_position.eph` is a candidate): not checked.
- JointLoc row: the full text was read through a fetch summarizer, not line by line.
