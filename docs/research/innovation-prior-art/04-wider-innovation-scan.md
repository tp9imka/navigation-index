# Wider innovation scan: ten algorithmic directions for a 48h navigation POC

<!-- about: res:sier-2026-safevpr-empirical-fdr-vpr, res:yang-pavone-2023-conformal-keypoint-pose, res:weisman-2026-conformalized-kalman-filters, res:delama-2026-galilean-ins-unknown-time-delay, res:fornasier-2023-equivariant-symmetries-ins, res:gupta-gao-2024-reliable-urban-localization-faulty-gnss, res:park-bang-2026-contours-seeking-pf-trn, res:feng-2026-implicitterrainv2, res:trukhina-2026-sasgeo-semantic-map-localization, res:sarkka-nummenmaa-2009-vb-adaptive-kalman -->

Scan date 2026-11-09, for an autonomous flight navigation task (full brief
not yet known). Scope: navigation of the vehicle's own flight. Nothing here covers targeting or
terminal guidance.

Status: **not verified by running anything.** Every number below is quoted from a paper
abstract, a README or a hub sample, and says which. Nothing was built for this scan.

What this page does not repeat:

- [differentiators-scan.md](../../differentiators-scan.md): drag / propulsion as a velocity
  sensor, learned inertial odometry, fixed-wing VDM, factor graphs with robust kernels, radar /
  thermal / event odometry, LEO signals of opportunity.
- [guidance-planning.md](../../guidance-planning.md): G1-G5 (localisability-aware routing,
  integrity-driven guidance, wind/energy routes, perception-aware trajectories, degrading-estimate MPC).
- [trends-2025-2026.md](../../landscape/trends-2025-2026.md): commodity camera-to-map modules,
  quantum MagNav, OSNMA, LEO PNT.
- Three sibling lanes (separate files in this folder): maneuvers that disambiguate visual
  location hypotheses, deadline-aware scheduling of expensive fixes, identifiability-gated aero
  parameter adaptation. Where a direction here touches one of them, the boundary is stated.

Records: [data/resources/innovation-pa-wider.json](../../../data/resources/innovation-pa-wider.json)
(37 resources) and [data/repos/innovation-pa-wider.json](../../../data/repos/innovation-pa-wider.json)
(11 repos, each checked with `gh api repos/OWNER/NAME` on 2026-11-09; license is GitHub's
`spdx_id`, `none` means no license file was detected).

Evidence labels used below: **peer-reviewed** (journal or proceedings version exists),
**preprint** (arXiv only), **abstract only** (only the abstract or a listing was read),
**code** (repo exists and was checked), **README claim** (number is from a README).
For arXiv items the metadata (title, authors, date) was read from arXiv on 2026-11-09; full
texts were not read unless stated.

## 1. Ranked table

Each column 1-5, total out of 30. Novelty = how new it looks to reviewers who have seen
camera-to-map demos. Evidence = strength of published support. 48h = buildable by a small team
on hub samples. Data = open data or SITL that can falsify it. License = commercial path for code
and data. Fit = match with "GNC, propulsion, applied maths, applied physics".

| # | Direction | Nov | Evid | 48h | Data | Lic | Fit | Total |
|---|---|---|---|---|---|---|---|---|
| 1 | **Conformal acceptance and error radius for learned visual fixes, fed to the EKF and its protection level** | 5 | 4 | 5 | 4 | 4 | 3 | **25** |
| 2 | **Integrity from a multimodal posterior, with a "true hypothesis is missing" test (TRN particle filter)** | 4 | 3 | 4 | 5 | 5 | 4 | **25** |
| 3 | **Delay-aware invariant / equivariant INS filter for late GNSS and late visual fixes** | 4 | 4 | 3 | 3 | 4 | 5 | **23** |
| 4 | Adaptive noise estimation (Sage-Husa / VB) under spoofing: red-team it, then anchor it | 4 | 2 | 4 | 4 | 5 | 3 | 22 |
| 5 | Neural implicit terrain (compressed DEM with analytic gradients) for TRN | 4 | 2 | 4 | 5 | 4 | 3 | 22 |
| 6 | Optical flow + rangefinder + vehicle model as a minimal-sensor nav mode | 2 | 3 | 4 | 3 | 4 | 4 | 20 |
| 7 | Map-age / change-aware matching: detect map mismatch online and down-weight | 3 | 3 | 3 | 4 | 4 | 2 | 19 |
| 8 | Zero-shot foundation-model geolocalization and a measured failure map | 2 | 3 | 4 | 4 | 4 | 1 | 18 |
| 9 | Cooperative inter-aircraft ranging without a ground station | 3 | 2 | 4 | 3 | 4 | 2 | 18 |
| 10 | Skylight polarization heading | 3 | 2 | 2 | 2 | 3 | 4 | 16 |

Ties broken by novelty to reviewers. Directions 1 and 2 share a theme the hub has already measured
from the other side: the [altpnt-integrity](../../../samples/altpnt-integrity/) v2 map-age stress
showed "the overbound from the golden table does not hold under a different map age"
([evidence matrix](../../evidence-matrix.md)). Both directions are ways to make the error bound
honest when the learned or multimodal component is wrong.

Lower priority, one line each (not scored):

- **Anytime-valid (e-process) fault monitors.** E-value theory gives a sequential test whose
  false-alarm bound holds at any stopping time (["Hypothesis testing with e-values",
  arXiv 2410.23614](https://arxiv.org/abs/2410.23614), preprint, listing only). A navigation fault monitor built
  this way was not found in this search (queries: "e-values anytime-valid sequential test
  anomaly detection navigation fault detection GNSS 2025"). Good maths story, weak demo; fold
  into direction 4 as the detector if time allows.
- **Schmidt / consider states for correlated map georeferencing bias.** Schmidt-EKF for prior
  maps exists ([Geneva et al. 2019](https://arxiv.org/abs/1903.08636), peer-reviewed CVPR);
  the hub's altpnt-integrity v2 already carries a geoloc bias state with an assumed 300 s
  correlation time, so the gain over the hub is small.
- **Render-and-compare against 3D Gaussian splats of satellite data.** Active 2024-2026 vision
  work ([Li et al. 2024](https://arxiv.org/abs/2411.14816), preprint; ISPRS 2026 evaluation of
  GS maps, abstract only). GPU-heavy and a vision demo, not a GNC one.

## 2. Per-direction sections

Each section: what exists, the narrow open angle, the strongest baseline, a falsification
experiment, failure modes, code and data with license, and 48h buildability on hub samples.
The five failure modes checked everywhere: **missing true hypothesis**, **correlated sensor
errors**, **map mismatch**, **delayed measurements**, **wind / velocity ambiguity**.

### 2.1 Conformal acceptance and error radius for learned visual fixes

**What exists.**

- Yang and Pavone, CVPR 2023 ([arXiv 2303.12246](https://arxiv.org/abs/2303.12246),
  peer-reviewed, abstract only): inductive conformal prediction turns keypoint heatmaps into
  prediction sets with a target coverage, then propagates them into a pose uncertainty set.
  Code: [NVlabs/ConformalKeypoint](https://github.com/NVlabs/ConformalKeypoint) (no license
  file => read only).
- SafeVPR, Sier et al. 2026 ([arXiv 2605.28048](https://arxiv.org/abs/2605.28048), preprint;
  arXiv comment and README say accepted to RA-L): frozen DINOv2 patch agreement score, then a
  Mondrian (score-binned) Learn-Then-Test calibration of accept thresholds with Clopper-Pearson
  bounds. README claim: target FDR held on 23/23 held-out cross-condition setups at alpha 0.10;
  in pose-graph relocalization 29.6x fewer wrong loop closures, median trajectory error 95.5 m
  => 9.7 m. The README itself says the control is empirical, not a formal guarantee under
  arbitrary shift. Ground-vehicle data only (Oxford RobotCar, NCLT, St Lucia). Code:
  [TIERS/SafeVPR](https://github.com/TIERS/SafeVPR), MIT, `demo.py` runs on bundled scores
  without a GPU (README claim).
- Weisman, Shlezinger, Laufer-Goldshtein 2026, "Conformalized Kalman Filters"
  ([arXiv 2609.27506](https://arxiv.org/abs/2609.27506), preprint, abstract read): conformally
  calibrates Kalman confidence regions from the filter's own moments, including a Gaussian-mixture
  variant for multimodal regions; sample-wise and trajectory-wise coverage. No code link found on
  the abstract page.
- Kulkarni, Poulakakis, Huang 2026 ([arXiv 2603.18308](https://arxiv.org/abs/2603.18308),
  preprint, abstract read): learned measurement noise expressed as distribution-free set-coverage
  statements and used inside a Gaussian filter; abstract says it stays consistent where Gaussian
  baselines drift (legged robots).
- Miller et al. 2025 ([arXiv 2510.13464](https://arxiv.org/abs/2510.13464), preprint, abstract
  read): training-free VPR confidence from the similarity-score distribution (SD, RS, SU). A
  cheap non-conformal score to calibrate.
- UASTHN, Xiao and Loianno 2025 ([arXiv 2502.01035](https://arxiv.org/abs/2502.01035), ICRA 2025
  per the repo; already in the hub as `repo:arplaboratory/uasthn`): ensembles and test-time
  augmentation for thermal-to-satellite homography uncertainty. Uncertainty, not coverage.
- Background: Lindemann et al. 2024 survey of conformal prediction for verification and control
  ([arXiv 2409.00536](https://arxiv.org/abs/2409.00536), preprint); Jiang, Shi, Moura,
  covariance recalibration for overconfident nonlinear KFs
  ([arXiv 2407.05717](https://arxiv.org/abs/2407.05717), Automatica 194 (2026) per arXiv
  journal-ref, peer-reviewed); Gupta and Gao data-driven protection levels for camera + 3D map
  localization (already in the hub as `res:gupta-gao-2021-data-driven-protection-levels`).

**Open angle.** Conformal, condition-binned acceptance of **aerial absolute visual fixes**
(retrieval + matcher + homography => lat/lon) with a calibrated error radius that becomes the
EKF measurement covariance and feeds the solution-separation protection level. Aerial
nav-to-satellite with conformal acceptance plus calibrated R in the filter: not found in this
search (queries: "conformal prediction visual place recognition localization uncertainty
calibration arXiv 2024 2025", "conformal prediction aerial visual localization satellite image
UAV uncertainty", "conformal prediction Kalman filter state estimation calibrated covariance
learned measurement arXiv", arXiv API `abs:conformal AND abs:localization`). The nearest are
SafeVPR (ground VPR, accept/abstain only, no error radius into a filter) and UASTHN
(uncertainty without coverage).

**Strongest baseline.** The hub's own gate in
[e2e-visual-nav-vpair](../../../samples/e2e-visual-nav-vpair/): min 25 inliers + voting or
chi-square gate, 0 false fused fixes on the 8.5 km VPAIR flight, 4.8 m RMS with fixes
(hub sample, real input). Second baseline: SafeVPR's own calibration applied to aerial scores.

**Falsification experiment.**

- Data: the cached candidate fixes in `samples/e2e-visual-nav-vpair/results/frontend.json`
  (199 queries, top-5 retrieval at two strides, per-pair matches / inliers / homography scale,
  already computed) with VPAIR truth; cross-condition split from the
  [thermal-geolocalization](../../../samples/thermal-geolocalization/) held-out flights (1620
  gated attempts in its README).
- Score per candidate: retrieval margin (Miller SD/RS), inlier count, inlier ratio, homography
  scale deviation. Mondrian bins on score; calibrate on the first half of the VPAIR track, test
  on the second half and on thermal held-out flights.
- Metrics: (a) accepted-fix false-discovery rate, wrong = error > 50 m, target alpha 0.10;
  (b) empirical coverage of the 90 % conformal error radius; (c) EKF NEES with R from the radius
  vs fixed R; (d) protection-level availability at AL 50 m.
- **Pass:** FDR <= 0.10 within a binomial 95 % interval on both test splits, 90 % radius coverage
  >= 0.85 on both, 0 false fused fixes, and either more accepted fixes or a lower PL than the
  hub gate at equal integrity. **Fail:** cross-condition coverage < 0.80 (calibration does not
  transfer from day RGB to night thermal), or no gain over min-inliers + voting. A fail is still
  a slide: "this is how far the guarantee travels".

**Failure modes.**

- Missing true hypothesis: if the right tile is not in top-5, every candidate is wrong;
  conformal acceptance still controls FDR but availability drops. Report it.
- Correlated errors: conformal coverage is marginal per fix; consecutive fixes over the same old
  orthophoto share bias, so per-fix coverage overstates trajectory coverage. Use the
  trajectory-wise variant (Weisman 2026) or keep the hub's bias state.
- Map mismatch: exchangeability breaks across map vintages; this is exactly what Mondrian bins
  and the cross-condition split test.
- Delayed measurements: fix latency (0.73 s/frame on M2 in the e2e sample) is independent of
  calibration but must be time-stamped at capture, not at match completion.
- Wind / velocity ambiguity: not involved.

**Code and data, license.** SafeVPR MIT (code), ConformalKeypoint no license (read only),
our calibration is ~150 lines numpy. VPAIR: academic use only per its README (fine for
evaluation, not for training a shipped model; [card](../../dataset-cards/vpair.md)). Thermal set:
Apache-2.0 on its HF card with "academic research" wording ([sample README](../../../samples/thermal-geolocalization/README.md)).
NAIP (public domain US imagery) for a license-clean rerun via
[geoloc-license-clean](../../../samples/geoloc-license-clean/).

**48h buildability: high.** No GPU needed for the first result: the expensive front end is
already cached. Reuse `nav_core.py` / `run_fusion.py` from e2e-visual-nav-vpair and the PL code
from altpnt-integrity.

### 2.2 Integrity from a multimodal posterior, with a missing-hypothesis test

Boundary: the sibling lane on maneuvers that disambiguate hypotheses chooses **how to fly**;
this direction only decides **what the filter is allowed to claim**.

**What exists.**

- Gupta and Gao, particle filter with GMM likelihood and a test statistic for integrity,
  [arXiv 2101.06380](https://arxiv.org/abs/2101.06380) (preprint) and the journal version
  "Reliable urban vehicle localization under faulty satellite navigation signals", EURASIP
  J. Adv. Signal Process. 2024 ([DOI 10.1186/s13634-024-01150-2](https://doi.org/10.1186/s13634-024-01150-2),
  peer-reviewed, abstract only). Urban GNSS, not terrain.
- Park, Lee, Lee 2022, EKF-based TRN error modelling for integrity under nominal conditions
  (IET RSN 16(9), [DOI 10.1049/rsn2.12277](https://doi.org/10.1049/rsn2.12277), peer-reviewed,
  abstract only): radar altimeter, DEM vertical, lateral-offset and interpolation errors, the
  last two as functions of terrain roughness. Gaussian / EKF view.
- Park and Bang 2026, contours-seeking proposal PF for resilient TRN
  ([arXiv 2608.15489](https://arxiv.org/abs/2608.15489), preprint, abstract read): names
  multimodal likelihoods and unknown prediction biases as the cause of PF degeneration; Gaussian
  mixture random forcing along terrain contours. Robustness, not integrity bounds.
- Weisman et al. 2026 (above): conformal regions from a learned Gaussian mixture of the posterior.
- Hub: [terrain-heightmap-pf](../../../samples/terrain-heightmap-pf/) (information gate,
  confidence) and [blind-flight-bench](../../../samples/blind-flight-bench/) (beam-aware PF
  148 m median at 20 km, 18 % diverged on straight flights; on turns every navigator diverges in
  80-100 % of flights; synthetic flights over real GLO-30). SPRIN-D heightmap-gradient system is
  already in the hub (`res:sprind-heightmap-gradients-2025`).

**Open angle.** A protection level computed from a TRN particle posterior that **also tests
whether the posterior contains the truth at all**, using the predictive distribution of the
altimeter innovations (a hypothesis-coverage test), and declares "unavailable" instead of a
small PL when the cloud has collapsed on a wrong mode. TRN-specific PF protection levels with a
missing-hypothesis check: not found in this search (queries: "particle filter integrity
protection level non-Gaussian terrain navigation 2024", "terrain referenced navigation
integrity monitoring particle filter protection level Gaussian mixture", "terrain aided
navigation integrity protection level multimodal posterior particle filter aircraft 2023 2024
2025", arXiv API `abs:terrain AND abs:navigation AND abs:integrity`).

**Strongest baseline.** Weighted-quantile radius of the particle cloud as PL, and the
Gupta-Gao GMM tail statistic re-implemented for altimeter measurements. Both are expected to
fail silently on diverged runs, which is the point of the experiment.

**Falsification experiment.**

- Data: blind-flight-bench, all four GLO-30 regions, straight and turning flights, its PF
  navigator unchanged; plus terrain-heightmap-pf v2 runs (flat / mixed / hilly).
- Three PLs at P_MD 1e-3: (a) particle-radius quantile, (b) GMM tail bound, (c) (b) + the
  missing-hypothesis test (windowed sum of log predictive likelihoods vs its Monte Carlo
  distribution under the filter's own model; fail => unavailable).
- Metrics: HMI epochs (PE > PL while declared available), availability at AL 150 m and 300 m,
  per flight type.
- **Pass:** (c) gives 0 HMI epochs over all runs including diverged ones, with availability
  >= 50 % on straight flights; (a) and/or (b) show HMI on diverged runs (the demonstration that
  the test matters). **Fail:** (c) has any HMI, or availability < 20 % on straight flights
  (too conservative to use).

**Failure modes.**

- Missing true hypothesis: the target of the method. Residual risk: a wrong mode that explains
  the altimeter as well as the true one (repeating terrain) passes the test; measure how often.
- Correlated errors: DEM vertical error is spatially correlated; the predictive test will be
  optimistic unless the DEM error is a correlated state or inflated (Park 2022 models it).
- Map mismatch: GLO-30 vs real surface (canopy, buildings) is a bias, not noise; the bench
  already has a "world surface the radar sees" model, so this is testable.
- Delayed measurements: minor at 1-10 Hz altimeter rate.
- Wind / velocity ambiguity: velocity error shifts the whole cloud coherently; the test sees it
  only through terrain disagreement, so on flat terrain it is blind. Report flat-terrain results.

**Code and data, license.** All hub code (blind-flight-bench, terrain-heightmap-pf). GLO-30
under the Copernicus DEM licence, free for the public with attribution
([card](../../dataset-cards/copernicus-glo30.md)). NRW LiDAR under Datenlizenz Deutschland Zero
2.0 (per terrain-heightmap-pf README). No third-party license risk.

**48h buildability: high.** Pure numpy on top of existing navigators; the bench already logs
per-epoch error.

### 2.3 Delay-aware invariant / equivariant INS filter

Boundary: the sibling lane on deadline-aware scheduling decides **when** to run an expensive
fix; this direction **estimates and absorbs the delay** of whatever fix arrives.

**What exists.**

- Delama, Scheiber, Ge, Hamel, Weiss, Mahony, "Galilean State Estimation for Inertial Navigation
  Systems with Unknown Time Delay", RSS XXII 2026
  ([paper page](https://roboticsproceedings.org/rss22/p130.html), peer-reviewed, abstract
  read). Abstract: commercial GNSS receivers add unknown delays of about 50-300 ms; validated on
  two fixed-wing UAVs with 90 ms and 120 ms lags, 2-3 min flights, simulations up to 500 ms;
  the EqF stays consistent while the EKF degrades. No code link on the page.
- Fornasier, Ge, van Goor, Mahony, Weiss, "Equivariant Symmetries for Inertial Navigation
  Systems" ([arXiv 2309.03765](https://arxiv.org/abs/2309.03765), preprint; repo says an
  Automatica submission): IEKF and other modern EKF variants as EqFs with different symmetry
  groups; GNSS-aided variants compared. MATLAB code:
  [aau-cns/equivaraint-symmetries-for-inertial-navigation-systems](https://github.com/aau-cns/equivaraint-symmetries-for-inertial-navigation-systems)
  (no license file).
- Scheiber, Fornasier, Brommer, Weiss, multi-GNSS EqF with per-antenna extrinsics for UAVs
  ([arXiv 2310.10597](https://arxiv.org/abs/2310.10597), preprint).
- MSCEqF, Fornasier et al., RA-L 2023 ([arXiv 2311.11649](https://arxiv.org/abs/2311.11649),
  peer-reviewed): equivariant VIO. Code [aau-cns/MSCEqF](https://github.com/aau-cns/MSCEqF),
  Apache-2.0; Lie group library [aau-cns/Lie-plusplus](https://github.com/aau-cns/Lie-plusplus),
  Apache-2.0.
- InGVIO, Liu, Jiang, Wang ([arXiv 2210.15145](https://arxiv.org/abs/2210.15145), RA-L 2023
  per search snippet, not confirmed on arXiv): invariant filter for visual-inertial + raw GNSS,
  fixed-wing datasets. Code [ChangwuLiu/InGVIO](https://github.com/ChangwuLiu/InGVIO), no
  license file.
- Diker and Klein 2026, neural-aided adaptive innovation-based invariant KF
  ([arXiv 2603.26709](https://arxiv.org/abs/2603.26709), preprint, abstract read).
- Already in the hub: Barrau-Bonnabel InEKF (`res:barrau-bonnabel-invariant-ekf`),
  `repo:rosshartley/invariant-ekf`, `repo:contagon/iekf`, `repo:artivis/manif`, and the
  semi-aerodynamic IEKF for fixed-wing (`res:ye-2023-semi-aerodynamic-model-aided-iekf`).

**Open angle.** The Delama method applied to the hub's **visual fixes**, whose delay is
compute-bound and variable (0.73 s/frame on M2 in e2e-visual-nav-vpair, sample measurement),
not only to GNSS; plus an open, permissive implementation. An open-source delay-estimating EqF /
InEKF for GNSS or visual fixes: not found in this search (queries: "equivariant filter EqF
GNSS-INS navigation 2024 2025 arXiv consistency", "invariant EKF UAV GNSS-denied visual
inertial navigation consistency 2024 2025 open source", GitHub search "equivariant filter",
"invariant kalman filter"). The RSS page links no code.

**Strongest baseline.** ArduPilot EKF3 / PX4 EKF2 delayed-horizon fusion with a fixed
configured delay (`GPS_DELAY_MS`-style parameter, exact names to be checked in hour 1), and a
plain EKF with the delay as an extra state.

**Falsification experiment.**

- Data: ArduPlane SITL from [sitl-docker](../../../samples/sitl-docker/) on the
  [golden-demo-fixedwing](../../../samples/golden-demo-fixedwing/) route, logging IMU, GNSS and
  truth; inject a GNSS lag of 0, 100, 200, 300, 500 ms in the simulator (SITL lag parameter
  name not verified). Replay offline into three Python filters: EKF with fixed assumed delay,
  EKF with delay state, right-invariant EKF (or EqF) with delay state.
- Metrics: ANEES over 10 seeds, position error in turns, delay estimate error after 60 s.
- **Pass:** the invariant filter with delay state keeps ANEES inside the 95 % chi-square band
  for all lags up to 300 ms and estimates the delay within 20 ms after 60 s, while the fixed-delay
  EKF leaves the band at >= 200 ms. **Fail:** the EKF with a delay state is equally consistent =>
  the gain is delay estimation, not invariance; pitch it that way or drop the invariance claim.

**Failure modes.**

- Missing true hypothesis: not applicable (unimodal filter).
- Correlated errors: delay and lever-arm / clock errors are correlated in turns; identifiability
  needs maneuvering (straight-and-level makes delay unobservable). Keep the observability point
  honest; it overlaps the sibling identifiability lane only in principle.
- Map mismatch: not involved.
- Delayed measurements: the target.
- Wind / velocity ambiguity: delay and wind both shift the GNSS-vs-INS velocity residual on a
  fixed-wing; separate them with turns.

**Code and data, license.** Lie-plusplus and MSCEqF Apache-2.0 (C++), manif MIT (has Python
bindings per its README, not checked here). Our Python filter is ours. ArduPilot GPL-3.0 is only
configured, not linked. No real flight data with unknown-delay ground truth was found; SITL only.

**48h buildability: medium.** A Python right-invariant EKF for INS + position is a day of
work for someone who knows Lie groups; the delay state is the risky part. Applied-maths fit is
the strongest of all ten.

### 2.4 Adaptive noise estimation under spoofing: red-team, then anchor

**What exists.**

- Baselines: Sarkka and Nummenmaa, VB adaptive KF, IEEE TAC 2009
  ([DOI 10.1109/TAC.2008.2008348](https://doi.org/10.1109/TAC.2008.2008348), peer-reviewed,
  not opened); Huang, Zhang, Wu, Li, adaptive KF with inaccurate Q and R, IEEE TAC 2018
  ([DOI 10.1109/TAC.2017.2730480](https://doi.org/10.1109/TAC.2017.2730480), peer-reviewed, not
  opened).
- Many VB / Sage-Husa GNSS/INS variants target multipath, NLOS and jamming-like noise (search
  results only: Wasserstein VB KF, IEEE Sensors J. 2024; VBRAKF, Measurement 2023; Gaussian /
  Student-t VBAKF, Remote Sensing 2025). None framed around spoofing in this search.
- Spoofing-side: Panda and Guo 2025, Bayesian detection of drift-evasive GNSS spoofing
  ([arXiv 2507.11173](https://arxiv.org/abs/2507.11173), preprint, title only); Oliva et al.
  2026, innovation whiteness tests catch stealthy colored attacks that keep NIS in range
  ([arXiv 2604.17572](https://arxiv.org/abs/2604.17572), preprint, abstract read, maritime).
- Hub: [autopilot-spoof-response](../../../samples/autopilot-spoof-response/) measured that
  PX4 EKF2 and ArduPilot EKF3 believe 96-110 % of a coherent 0.1-5 m/s drag (SITL);
  [golden-demo](../../../samples/golden-demo/) catches a 1 m/s coherent drag with a median TTD
  of 2.8 s (SITL).

**Open angle.** Show that innovation-driven R adaptation **turns a slow coherent spoof into
"higher noise"** and so lengthens time to detect, then fix it by adapting R only from evidence
the spoofer does not control (C/N0 / AGC, a second velocity source such as the drag model of
the differentiators scan). A measured study of VB / Sage-Husa adaptation as a spoofing amplifier:
not found in this search (queries: "variational Bayesian adaptive Kalman filter GNSS spoofing
jamming INS integrated navigation 2024 2025", "variational Bayesian adaptive filter GNSS spoofing
arXiv covariance inflation attack absorbs slow drift", "adaptive Kalman filter vulnerability
stealthy attack noise covariance estimation adversary exploits adaptation navigation",
"innovation-based adaptive noise estimation GNSS spoofing detection INS Sage-Husa variational
Bayes detection time 2025").

**Strongest baseline.** Fixed-R EKF with the hub's chi-square gate and velocity-consistency
monitor (golden-demo). For jamming-like noise, a standard VB-AKF.

**Falsification experiment.**

- Data: first in the stdlib [gnss-ins-ekf-outage](../../../samples/gnss-ins-ekf-outage/)
  synthetic EKF (minutes to run), then on GNSS / IMU logs from golden-demo SITL flights with
  coherent drags of 0.1, 0.3, 1 m/s and with injected white noise growth (jamming proxy).
- Filters: fixed R; Sage-Husa; VB-AKF (Sarkka); anchored VB (R scale from C/N0 proxy and
  agreement with an independent velocity, never from innovations alone).
- Metrics: TTD of the same monitor, max horizontal deviation, RMS error under the noise-growth
  case.
- **Pass (red-team claim):** VB or Sage-Husa max deviation >= 1.5x fixed-R at 0.3 m/s drag in
  >= 4 of 5 seeds. **Pass (fix):** anchored VB matches fixed-R TTD within 20 % under spoofing
  and has >= 20 % lower RMS than fixed R under noise growth. **Fail:** adaptation does not
  lengthen TTD (then the red-team slide is dropped and only the jamming gain remains).

**Failure modes.** Missing hypothesis: n/a. Correlated errors: a coherent spoof is perfectly
correlated, which is why innovation-based adaptation misreads it. Map mismatch: n/a. Delayed
measurements: a delay mis-set looks like noise growth in turns and will trigger adaptation;
test it. Wind / velocity ambiguity: if the anchor is the drag velocity, wind error leaks into
the anchor; use it as a consistency check, not as truth.

**Code and data, license.** All ours on hub samples; no third-party code needed. SITL GPL
binary only configured.

**48h buildability: high** for the synthetic version, medium with SITL logs.

### 2.5 Neural implicit terrain for TRN

**What exists.**

- ImplicitTerrain, Feng, Xu, De Floriani 2024 ([arXiv 2406.00227](https://arxiv.org/abs/2406.00227),
  preprint): SIREN-style continuous surface model for terrain analysis. Code
  [Fengyee/implicit-terrain](https://github.com/Fengyee/implicit-terrain) (no license file).
- ImplicitTerrainV2, same authors 2026 ([arXiv 2605.22556](https://arxiv.org/abs/2605.22556),
  preprint; numbers from a search snippet of the abstract): wavelet-guided adaptive frequency,
  derivative-aware training, quantization; reported 1.23 bits per pixel with a 0.28 dB PSNR drop
  on 50 Swiss tiles. Code [Fengyee/implicitterrainv2](https://github.com/Fengyee/implicitterrainv2),
  MIT.
- Michaelson, Wang, Zanetti, TRN with neuro-inspired elevation encoding (NeuroGrid), PLANS 2023
  ([DOI 10.1109/PLANS53410.2023.10139925](https://doi.org/10.1109/PLANS53410.2023.10139925),
  peer-reviewed, abstract only): position measurements from a brain-inspired elevation encoding,
  fused with INS, motivated by onboard map cost.
- Loc-NeRF, Maggio et al. 2022 ([arXiv 2209.09050](https://arxiv.org/abs/2209.09050)), code
  [MIT-SPARK/Loc-NeRF](https://github.com/MIT-SPARK/Loc-NeRF) MIT: particle filter against a
  NeRF map (camera, not elevation).
- Jia, Li, How 2025 ([arXiv 2511.18183](https://arxiv.org/abs/2511.18183), preprint): implicit
  terrain with gradients for ground-robot planning.

**Open angle.** Replace the DEM raster in a gradient-based TRN filter with a compressed neural
field whose **analytic gradients** feed the filter, and measure the accuracy-vs-onboard-memory
curve. An implicit neural DEM used inside an aircraft TRN filter: not found in this search
(queries: "neural implicit terrain representation terrain relative navigation differentiable
elevation map matching UAV", "implicit neural representation digital elevation model compression
SIREN terrain DEM 2024 2025").

**Strongest baseline.** terrain-heightmap-pf v2 with bilinear GLO-30 (median 12 / 27 / 25 m at
10 km on hilly / mixed / flat vs odometry 311-404 m; synthetic flights over real terrain) and
the same raster stored as int16 + standard compression (LERC or zstd).

**Falsification experiment.** Fit fields of 32 KB to 2 MB per GLO-30 window; rerun the v2
evaluation with network heights and gradients. **Pass:** median 10 km error within +10 % of the
raster baseline at >= 20x smaller storage than the compressed raster, and per-step inference
under 5 ms for the particle batch on CPU. **Fail:** standard compression already reaches the
same size at equal error (then the neural field buys nothing for TRN).

**Failure modes.** Missing hypothesis: network smoothing can erase the small features that
disambiguate modes; check divergence rate, not only median. Correlated errors: fitting error is
spatially correlated, exactly like DEM error, so count it in R. Map mismatch: unchanged. Delayed
measurements, wind: not involved.

**Code and data, license.** ImplicitTerrainV2 MIT; GLO-30 Copernicus licence. 48h
buildability: high on CPU or MPS for a few 36 x 35 km windows (training time not measured).
Weak spot: reviewers may read it as compression, not navigation.

### 2.6 Optical flow + rangefinder + vehicle model

**What exists.** ArduPilot and PX4 already fuse flow + rangefinder (hub: `res:px4-optical-flow-docs`,
`res:ardupilot-optical-flow-setup`). Xiong, Chen, Dong 2024 ([arXiv 2409.06501](https://arxiv.org/abs/2409.06501),
preprint, abstract via search snippet): single-anchor UWB + flow + IMU with an aerodynamic drag
term in the motion model. A 2025 Electronics paper fuses IMU + altimeter + flow in an EKF
(search snippet only, not opened).

**Open angle.** A flow + rangefinder mode whose motion model is the drag model of the
differentiators scan, so flow quality (texture, altitude) and drag (wind) cross-check each
other. Mostly a combination of known parts; novelty low.

**Baseline / falsification.** ArduCopter SITL optical flow simulation (`SIM_FLOW_*`, names not
verified) with and without drag fusion over water / low-texture segments. Metric: drift per
minute at 30, 60, 100 m AGL with 0 / 3 / 6 m/s wind. Pass: drag + flow drift <= 50 % of flow-only
drift where flow quality drops. Failure modes: wind ambiguity (drag gives air-relative, flow gives
ground-relative velocity, so their difference **is** the wind: a positive), map mismatch n/a,
delays small. **License:** all configuration and our code. **48h: high.**

### 2.7 Map-age / change-aware matching

**What exists.**

- SASGeo, Trukhina and Vashkelis 2026 ([arXiv 2607.07737](https://arxiv.org/abs/2607.07737),
  preprint, synthetic proof of concept): localization on persistent semantic structures (roads,
  buildings, waterways) with positive / contradictory / unknown evidence and integrity-aware
  rejection; reported Recall@1 58.6 % global descriptor vs 94.5-95.5 % spatial variants in 220
  synthetic trials. No code link seen.
- AeroMap3D, Deng and Sentis 2026 ([arXiv 2607.14009](https://arxiv.org/abs/2607.14009),
  preprint): names map-validity modelling as future work (search snippet).
- SWA-PF, Yuan et al. 2025 ([arXiv 2509.13795](https://arxiv.org/abs/2509.13795), preprint):
  semantic-weighted PF, abstract reports errors below 10 m with low-resolution maps and 10x
  efficiency over feature extraction. Code [YuanJiayuuu/SWA-PF](https://github.com/YuanJiayuuu/SWA-PF),
  no license file. MAFS dataset terms not checked.
- OrthoLoC, Dhaouadi et al., NeurIPS 2025 Datasets and Benchmarks
  ([arXiv 2509.18350](https://arxiv.org/abs/2509.18350), peer-reviewed): 16,425 UAV images with
  orthophotos and DSMs (abstract). Repo [deepscenario/OrthoLoC](https://github.com/deepscenario/OrthoLoC);
  LICENSE file is **CC BY-NC-SA 4.0** (read via `gh api`): evaluation only.
- Hub: [vpr-large-area](../../../samples/vpr-large-area/) R@10 0.98 on same imagery vs
  0.48-0.73 across 2-8 year map gaps (real NAIP vintages); DenseUAV has two satellite epochs
  ([card](../../dataset-cards/denseuav.md)).

**Open angle.** An online per-tile "map still valid" score learned from the residuals of
accepted fixes, which down-weights or retires stale tiles during the flight. Online map-validity
estimation for aerial visual nav: not found in this search (query: "satellite map outdated
change detection UAV visual localization map age mismatch robust 2025"; AeroMap3D lists it as
future work). Overlaps direction 1: a Mondrian bin per map age is the cheap version.

**Falsification.** NAIP vintages from vpr-large-area: match queries from one vintage against
maps of the others; inject controlled changes (synthetic building removal / new roads) for
labels. Metric: AUROC of the validity score for changed tiles; fix error with and without
down-weighting. Pass: AUROC >= 0.8 and no rise in false fused fixes. Fail: AUROC < 0.7.
Failure modes: correlated errors (a stale tile biases every fix over it: the target), missing
hypothesis (a fully changed area has no correct tile). **License:** NAIP public domain; DenseUAV
Apache-2.0 / MIT tags. **48h: medium** (labels are the effort).

### 2.8 Zero-shot foundation-model geolocalization and its failure map

**What exists.** MegaLoc, Berton and Masone 2025 ([arXiv 2502.17237](https://arxiv.org/abs/2502.17237),
preprint), code [gmberton/MegaLoc](https://github.com/gmberton/MegaLoc) MIT. VFM-Loc, Lu et al.
2026 ([arXiv 2603.13855](https://arxiv.org/abs/2603.13855), preprint): training-free cross-view
matching with domain-wise PCA and Procrustes alignment; abstract claims > 20 % Recall@1 gain over
supervised methods on LO-UCV (large oblique angles). (MGS)^2-Net 2026
([arXiv 2602.10704](https://arxiv.org/abs/2602.10704), preprint) and Li et al. 2024
([arXiv 2403.12702](https://arxiv.org/abs/2403.12702), preprint) both report frozen foundation
features degrade sharply from drone-to-drone to drone-to-satellite (search snippets). AnyLoc
already in the hub.

**Open angle.** Narrow: a measured failure map (altitude, obliquity, map vintage, texture) with a
cheap failure predictor (Miller SD/RS margin). Mostly benchmarking; low novelty to reviewers.

**Falsification.** MegaLoc vs AnyLoc vs the hub's DINOv2 GeM on vpr-large-area queries by
vintage. Pass: a failure predictor with AUROC >= 0.85 for wrong top-1. Failure modes: missing
hypothesis (no correct tile in DB) dominates. **License:** MegaLoc MIT (weights terms not
checked separately). **48h: high**, but it is the commodity lane.

### 2.9 Cooperative inter-aircraft ranging without a ground station

**What exists.** Hub samples already cover it: [swarm-coop-localization](../../../samples/swarm-coop-localization/)
(synthetic) and [swarm-coop-real-uwb](../../../samples/swarm-coop-real-uwb/) (real MILUV UWB,
denied drone 0.48 m DR => 0.20 m centralized). Recent aircraft-scale work found in this search
was thin: a 2024 EAI conference paper on INS + inter-aircraft ranging (search snippet), a 2026
MDPI Drones preprint on UWB TDMA swarms (search snippet), older AFIT work (2020). Peer flight
data at fixed-wing ranges: not found in this search (queries: "cooperative navigation UAV
inter-aircraft ranging GNSS-denied UWB relative localization fixed-wing 2024 2025 arXiv",
"multi-UAV cooperative localization inter-agent ranging GNSS-denied 2025 arXiv flight
experiment").

**Open angle.** A two-aircraft fixed-wing pair where one keeps GNSS and the other is denied,
with formation geometry chosen for range observability. Falsification: two ArduPlane SITL
instances (aau-cns `Ardupilot_Multiagent_Simulation` exists, GPL-3.0, not checked further),
simulated range with MILUV-measured error statistics; pass if denied-aircraft error at 20 km is
<= 50 % of airspeed dead reckoning. Failure modes: collinear geometry makes cross-track
unobservable; correlated errors if both aircraft share a spoofed GNSS. **License:** MILUV data
CC BY 4.0 ([card](../../dataset-cards/miluv.md)). **48h: high**, novelty to the hub low.

### 2.10 Skylight polarization heading

**What exists.** Potter, Mounier, Noureldin, Antar 2026, polarization navigation via Rayleigh
model optimization on a road vehicle ([arXiv 2610.20797](https://arxiv.org/abs/2610.20797),
preprint, title and metadata only). Hub: [PVI dataset](https://github.com/TS-FuPeng/PVI-dataset)
and `res:opensky-sky-polarization-simulator-2024`. A TU Delft UAV polarization heading dataset
was mentioned in search results (not opened). PolaRestNet (IEEE TCI 2026, listing only).

**Open angle.** Heading without a magnetometer as a cross-check for magnetic disturbance near
motors (the SPRIN-D paper reports a slowly changing compass bias, already in the hub). Heading
only; needs sky; a camera with a polarizer. **Falsification:** OpenSky simulator + injected
magnetometer bias; pass if polarization heading detects a 5 deg compass bias within 10 s. **48h:
low** without hardware or a UAV dataset.

## 3. Top 3 POC plans

All three reuse hub samples, need no new hardware, and have a pass/fail threshold fixed before
the build. They also combine: 1 and 2 are the same idea (honest integrity from a learned or
multimodal component) on the two absolute sources the hub already has, visual and terrain.

### 3.1 POC A: "Calibrated trust" for visual fixes (direction 1)

Take the cached VPAIR candidate fixes from e2e-visual-nav-vpair (no GPU needed), compute a
per-candidate score from retrieval margin, inliers, inlier ratio and homography-scale
deviation, and fit SafeVPR-style Mondrian conformal thresholds plus a 90 % conformal error
radius on the first half of the flight. Hours 0-8: calibration and FDR / coverage on the second
half. Hours 8-20: replace fixed R with the conformal radius in `nav_core.py`, rerun the fusion and
the solution-separation PL from altpnt-integrity, and compare PL availability at AL 50 m against
the hub gate at equal integrity. Hours 20-32: cross-condition check on thermal-geolocalization
held-out flights and on NAIP vintages via geoloc-license-clean; report how far the guarantee
travels. Hours 32-48: one Stanford diagram per gate, a slide with "accepted wrong fixes vs
target alpha" on each split. Pitch line: "Every visual fix comes with a coverage-calibrated
error bound, and we show where that bound stops holding."

### 3.2 POC B: "Know when the terrain filter is lost" (direction 2)

Run blind-flight-bench unchanged to get per-epoch particle clouds and truth over the four
GLO-30 regions, straight and turning flights. Hours 0-6: add three protection levels (particle
quantile, GMM tail, GMM tail + missing-hypothesis test from windowed predictive likelihoods of
the altimeter innovations vs Monte Carlo under the filter's own model). Hours 6-18: HMI and
availability tables per flight type at AL 150 / 300 m; the diverged runs are the test set.
Hours 18-30: add spatially correlated DEM error to the likelihood (Park 2022 style) and the
radar "world surface" mismatch from the bench; check the test still has 0 HMI. Hours 30-48:
port the test into terrain-heightmap-pf v2 and a Stanford diagram slide. Pitch line: "The
terrain navigator says 'I am lost' before it is wrong, not after."

### 3.3 POC C: "Late fixes, consistent filter" (direction 3)

Fly the golden-demo-fixedwing route in ArduPlane SITL and log IMU, GNSS and truth with injected
GNSS lag 0-500 ms (hour 1: confirm the SITL lag parameter and the EKF3 delay parameter names).
Hours 1-14: a Python right-invariant EKF on SE_2(3) for INS + position with the delay as a
state, next to a plain EKF with fixed delay and an EKF with a delay state. Hours 14-26: ANEES
over 10 seeds per lag, delay-estimate convergence, error in turns. Hours 26-38: feed the same
filter the e2e-visual-nav-vpair fixes with their measured compute latency as an unknown delay.
Hours 38-48: plots and the honest result on whether invariance or only delay estimation buys
the consistency. Pitch line: "Every fix arrives late; our filter knows by how much and stays
consistent." Highest GNC / applied-maths fit, highest build risk of the three.

Runner-up worth keeping in reserve: direction 4 (adaptive-noise red-team) is quick on the stdlib
EKF and pairs naturally with the golden-demo story if the full brief says "spoofing".

## 4. Not verified

- No experiment on this page was run. All pass/fail thresholds are proposed, not tested.
- Numbers quoted from abstracts or READMEs (SafeVPR 23/23 and 29.6x, ImplicitTerrainV2 1.23 bpp,
  SASGeo Recall@1, SWA-PF < 10 m, VFM-Loc > 20 %, Delama delay ranges) were not reproduced.
- Full texts not read for: Weisman 2026, Kulkarni 2026, Delama 2026 (abstract only), Gupta-Gao
  EURASIP 2024, Park 2022, Park-Bang 2026, Michaelson 2023, Sarkka 2009, Huang 2018.
- InGVIO's RA-L 2023 venue comes from a search snippet; arXiv shows no journal reference.
- `Fornasier et al. 2023` Automatica status comes from the repo description, not a journal page.
- SITL parameter names for GNSS lag, optical flow simulation and EKF delay were not checked
  against ArduPilot 4.6.3 source.
- Weights / dataset terms not checked separately for MegaLoc, SWA-PF (MAFS), Loc-NeRF.
- Search-snippet-only items (2025 Electronics flow paper, 2024 EAI cooperative paper, 2026 MDPI
  Drones UWB preprint, TU Delft polarization dataset, PolaRestNet, ISPRS 2026 GS evaluation)
  have no records and should not be quoted without opening them.
- "Not found in this search" means only that: the listed queries did not surface it.
