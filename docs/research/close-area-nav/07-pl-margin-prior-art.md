# 07. Kill test for idea C: does a PL-margin safety filter already exist?

Prior-art scan, 2026-11-09 (loop-13). Claim under test, from
[04-innovation-prior-art.md](04-innovation-prior-art.md) section 3.2 and the
[README](README.md) headline:

> A safety filter whose clearance margin for obstacles the range sensor cannot see comes from a
> fault-detecting protection level (RAIM-style integrity), not the estimator covariance.

Scope: the vehicle's own navigation and collision avoidance. Nothing was run for this doc. Every
number below is the source's own claim, with the input type the source reports.

## 1. Verdict

**Exists (cite).** The mechanism is published twice, once on a PX4 multirotor:

1. **Tan, Sundar, Bruzzone, Ong, Lunardi, Andreoni, Tabuada, Ames, "Secure Safety Filter: Towards
   Safe Flight Control under Sensor Attacks", IROS 2025**, doi 10.1109/IROS60139.2025.11247729,
   [arXiv 2505.06845](https://arxiv.org/abs/2505.06845). Caltech with TII Abu Dhabi. A CBF
   safety filter on PX4 velocity setpoints keeps a drone inside a keep-in geofence. Its margin is
   the set of all states consistent with every subset of sensors that excludes up to s attacked
   ones, inflated by a noise bound. That is fault-tolerant subset consistency driving the margin,
   on a position-based constraint a range sensor cannot see. PX4 SITL plus Holybro X500 hardware.
2. **Zhang, Li, Clark, fault-tolerant CBFs**, CDC 2020 (Clark, Li, Zhang) and IEEE TAC 2025,
   [arXiv 2207.05146](https://arxiv.org/abs/2207.05146). One EKF per fault pattern, a CBF
   constraint per estimate with its own error bound, and conflict resolution by comparing each
   estimate with pair-excluded filters against a threshold. This is a solution-separation bank
   feeding a safety filter. Ground robot in simulation.

Neither paper uses the words "protection level". A judge will not care. "Margin from a
fault-detecting multi-hypothesis bound instead of the covariance" is their contribution, so we
cannot claim it. The README sentence "BCBF and MR-CBF use Gaussian or bounded error, not a
fault-detecting integrity bound" was true of those two papers and is false as a statement about
the field.

## 2. What survives (narrow, engineering only)

None of the hits does all of the following. This is a composition of known parts:

- two barrier sets on one multirotor: body-frame range obstacles with no position needed
  (PX4-CBF style) and map or geofence obstacles with the integrity margin;
- a probabilistic protection level with an integrity budget (P_FA, P_MD, fault priors), where
  Tan 2025 uses a deterministic worst case and Zhang/Clark use per-estimator bounds;
- the hub's "ambiguous => unavailable => hover" rule. FT-CBF step 3 instead drops the
  largest-residual estimates until the QP is feasible. That is the max-separation-like rule that
  [multi-source-fde](../../../samples/multi-source-fde/README.md) measured as excluding a
  fault-free source in 25 of 30 GNSS-denied fault runs (synthetic faults on a real VPAIR flight,
  simulated GNSS and TRN; not a field result);
- VIO, range-to-wall or UWB as the redundant sources in a close area, instead of duplicated
  GNSS/EKF outputs. The Tan hardware test fed one EKF output twice and attacked one copy, so
  independent sources were never exercised (their Section V-B).

**The sentence a judge would accept:** "We apply PX4-CBF-style range barriers to what the drone
sees, and a fault-detecting protection level to what it cannot see; when the integrity monitor
cannot tell which source is lying, the filter refuses to guess and holds a hover, which
FT-CBF-style residual dropping does not do."

**Closest prior art a judge will name:** Tan et al. IROS 2025 (same platform family, same
geofence task, UAE co-authors). Second: Zhang, Li, Clark TAC 2025.

The surviving claim is testable as a delta over these two: same sim, same faults, arms "FT-CBF
residual drop" and "Tan union-of-plausible-states" against "PL + ambiguity => hover". If our arm
does not cut wrong-exclusion breaches or the freezing rate, there is nothing left.

**Refuted since (synthetic), before the FT-CBF and Tan arms ran:** "PL + ambiguity => hover" (F5)
failed the doc 04 kill test against a simpler arm. On held-out seeds it collided in 2.5 % [1.1,
5.7] of jump runs; MR-CBF with a hand-tuned fixed 0.2 m bound stayed at 1.0 % [0.3, 2.9] or less
in every case on seeds 0-2. 4 of F5's 7 jump collisions ended in hover, because the hover rule
drops the map rows. The in-loop PL also breached its 1e-3 risk in the VIO + UWB case. The FT-CBF
and Tan arms were dropped after this verdict
([safety-filter Part e](../../../samples/close-area-safety-filter/README.md#part-e-held-out-seeds-and-families-ran-2026-11-09-synthetic)).

## 3. Hits

Closeness: **same** = the claim's mechanism; **partial** = most of it, one key piece missing;
**adjacent** = related idea, different mechanism. Source labels: peer-reviewed / preprint / code
/ docs / news. "Full" = full text read (arXiv HTML); "abstract" = abstract or search summary only.

### 3.1 Safety filters and control

| # | Source | Label, read | What it does | Close |
|---|---|---|---|---|
| 1 | Tan et al., Secure Safety Filter, IROS 2025, [arXiv 2505.06845](https://arxiv.org/abs/2505.06845); code [tiiuae/px4-secure-state-reconstruction](https://github.com/tiiuae/px4-secure-state-reconstruction) (no license file, last push 2025-02-27, `gh api`) | peer-reviewed (venue from Nature Index listing), full | Sliding-window secure state reconstruction over sensor subsets, bounded noise inflates plausible states into boxes, robust CBF keeps all of them in a square keep-in region ([-6,6] m SITL, [-3,3] m hardware). Two copies of position and velocity; SITL on PX4 X500 in Gazebo, hardware X500 with two Pixhawk 5X and RTK GPS | **same** for geofence; no range barrier, deterministic not probabilistic |
| 2 | Zhang, Li, Clark, "Safe Control for Nonlinear Systems Under Faults and Attacks Via CBFs", IEEE TAC 2025, doi 10.1109/TAC.2025.3571338, [arXiv 2207.05146](https://arxiv.org/abs/2207.05146) | peer-reviewed, full | Bank of m EKFs (each omits one fault pattern) plus C(m,2) pair-excluded EKFs; CBF constraint per estimate with bound gamma_i; drop estimate i when its separation from the pair filter exceeds theta_ij/2; else drop largest residual. Wheeled robot with a constant sensor bias attack, simulation | **same** in mechanism; ground robot, sim |
| 3 | Clark, Li, Zhang, "CBFs for Safe CPS Under Sensor Faults and Attacks", CDC 2020, pp. 796-803 ([PAR](https://par.nsf.gov/servlets/purl/10310663)) | peer-reviewed, abstract | Conference version of #2 | **same** (priority 2020) |
| 4 | Zhang, Cheng, Niu, Clark, "Barrier Certificate based Safe Control for LiDAR-based Systems under Sensor Faults and Attacks", [arXiv 2208.05944](https://arxiv.org/abs/2208.05944) | preprint, abstract + intro | GPS + LiDAR: exclude state estimates whose rebuilt scan disagrees with the LiDAR, remove compromised sectors, barrier certificates on the rest. Simulated UAV delivery, urban | **partial**: UAV and LiDAR, no PL |
| 5 | Tan, Ong, Tabuada, Ames, "Safety of Linear Systems under Severe Sensor Attacks", CDC 2024, [arXiv 2409.08413](https://arxiv.org/abs/2409.08413); follow-ups [2502.20718](https://arxiv.org/abs/2502.20718), [2505.06842](https://arxiv.org/abs/2505.06842) | peer-reviewed (#5), preprints, abstract | Theory under #1: set of all possible states under spoofing, QP safety filter; faster bounds; sampled-data nonlinear version | **partial** (theory) |
| 6 | Zhang et al., "Fault Tolerant Neural CBFs for Robotic Systems under Sensor Faults and Attacks", [arXiv 2402.18677](https://arxiv.org/abs/2402.18677) | preprint, abstract | Learned CBFs in the same fault-tolerant framework | adjacent |
| 7 | Abdul Hafez et al. (Spenko, Joerger group), "Integrity Risk-Based Model Predictive Control for Mobile Robots", ICRA 2019 ([PAR](https://par.nsf.gov/biblio/10203876)) | peer-reviewed, abstract | Integrity risk with data-association faults as an MPC constraint over a receding horizon | **partial**: integrity in the controller, but bounds localization risk, not obstacle clearance (not confirmed from full text) |
| 8 | Vahs 2023 BCBF; Dean 2020 / Cosner 2021 MR-CBF; Agrawal 2022 observer-CBF | in hub ([04](04-innovation-prior-art.md) 3.1) | Covariance or bounded-error margins | adjacent (the baseline the claim was written against) |
| 9 | Sankaranarayanan et al., [arXiv 2605.15782](https://arxiv.org/abs/2605.15782); Misyats 2025 PX4-CBF (in hub) | preprint, abstract | Body-frame LiDAR composite CBF; robust to "abrupt localization anomalies" because it does not use the pose | adjacent: the range half of our design |

### 3.2 Integrity used for planning or no-fly zones

| # | Source | Label, read | What it does | Close |
|---|---|---|---|---|
| 10 | Sun, Zhang, Zheng, Ochieng, "GNSS/INS Integration with Integrity Monitoring for UAV No-fly Zone Management", Remote Sensing 12(3):524, 2020 | peer-reviewed, abstract | FDE + real-time HPL for UAV no-fly-zone compliance | **partial**: PL vs geofence, monitoring only, no control law in the abstract |
| 11 | Lee, Seo, Kassas, integrity-based path planning, ION GNSS+ 2020 | in hub | HPL < HAL as a path constraint, offline | adjacent (planning) |
| 12 | Zhu et al., Safety-critical LIO with deterministic PL, [arXiv 2605.09383](https://arxiv.org/abs/2605.09383) | in hub, preprint | Set-membership LIO whose feasible set is offered as a "safety reference" downstream | adjacent: a PL source, no filter |
| 13 | Yoon, Chou, Chen, Frew, Sankaranarayanan, predictive runtime monitoring for UAV geofence, RV 2019 ([PDF](https://home4.cs.colorado.edu/~srirams/papers/uav-geofence-rv-2019-yoon-etal.pdf)) | peer-reviewed, abstract | Controller-agnostic monitor; GPS error modelled as stochastic disturbance, not fault-detected | adjacent |
| 14 | Spirent, US 12292515 B2, "GNSS risk analysis data for safe routing of autonomous drones", priority 2020 ([Google Patents](https://patents.google.com/patent/US12292515)) | patent, metadata only | Distributes GNSS risk maps for drone routing | adjacent (routing, not a filter) |

### 3.3 Aviation, automotive, vendors

| # | Source | Label, read | What it does | Close |
|---|---|---|---|---|
| 15 | RNP / PBN: TSE combines path definition, flight technical and navigation system error; RNP needs onboard monitoring and alerting to stay in containment ([engineeringpilot.com](https://www.engineeringpilot.com/post/pbn-errors-and-obstacle-clearance), [Garmin FAQ](https://support.garmin.com/en-US/?faq=OhOmf8eu9v7ldhYxAsgea6)) | docs, search summary | Obstacle clearance areas sized from RNP; integrity alert when NSE bound exceeds the limit | **partial**: integrity-sized clearance, but at procedure design time plus an alert, not a live filter |
| 16 | Haro, Aguilera, Lucchi, "Required Navigation Performances for Drone Flight Operations", Eng. Proc. 54(1):51, 2023 | conference, abstract | RNP specs for drones built from TSE components | adjacent |
| 17 | Reid et al., "Localization Requirements for Autonomous Vehicles", SAE J. CAV 2(3), 2019, [arXiv 1906.01061](https://arxiv.org/abs/1906.01061) | peer-reviewed, abstract | Alert limits from lane geometry; freeway lateral bound 0.57 m (0.20 m 95 %), local streets 0.29 m (authors' derived numbers) | adjacent: geometry => alert limit, no controller |
| 18 | ISO 21448 SOTIF ([iso.org](https://www.iso.org/standard/77490.html)) | docs, summary | Process standard for functional insufficiencies of perception and localization | adjacent: no PL-margin mechanism found |
| 19 | Shield AI, "Resilient Shield" MM-RTA blog, 2025 ([shield.ai](https://shield.ai/resilient-shield-strengthening-hivemind-for-safe-real-world-flight/)) | news, full | ASTM F3269 multi-monitor RTA between Hivemind and the autopilot; GCAS and well-clear flight tests | adjacent: RTA exists in product; no word on nav integrity in the margins |
| 20 | Skydio X2D release note, "Variable Margins" ([support.skydio.com](https://support.skydio.com/hc/en-us/articles/27741578619419-Skydio-X2D-INTL-v24-10-60-25-September-2023)) | docs, search snippet | Obstacle margins shrink in narrow spaces and grow with wind | adjacent: adaptive margin, no integrity link stated |
| 21 | NASA / AFRL Auto-GCAS incl. small-UAV version ([NTRS 20150014106](https://ntrs.nasa.gov/citations/20150014106)) | docs, abstract | Terrain-map collision avoidance with multi-trajectory scan | adjacent; whether nav error sizes the scan buffer was not checked |
| 22 | Exyn (ExynAI), Auterion (Skynode, GNSS-denied workflow) | docs, search summary | No public material found on integrity-sized obstacle or geofence margins | not found |

## 4. Queries run (WebSearch, 2026-11-09, 2018-2026 focus)

Academic: "control barrier function protection level integrity navigation UAV"; "safety filter
protection level collision avoidance robot integrity monitoring"; "protection level" "control
barrier function"; "integrity-aware geofence UAV protection level containment"; "integrity risk"
model predictive control mobile robot Joerger Spenko; control barrier function GNSS integrity
"alert limit" safe control; safety-critical control localization integrity protection level
autonomous vehicle barrier function; runtime assurance UAV navigation integrity monitor
protection level geofence buffer; "integrity" "control barrier" localization faults safe
navigation robot; Gupta Gao protection level safe trajectory planning; integrity-constrained
motion planning UAV protection level obstacle clearance; "fault detection and exclusion"
"control barrier function" localization; "integrity-aware" control barrier function;
"protection level" safety filter drone obstacle margin; Clark Li Zhang CBF sensor faults CDC
2020; "solution separation" control barrier function / safety filter; Joerger control barrier
navigation integrity risk; UAV urban trajectory planning GNSS integrity protection level (PolyU);
integrity risk MPC alert limit obstacles (Hafez).

Aviation: RNP TSE NSE obstacle clearance containment PANS-OPS; SORA containment buffer GNSS
error FTE geofence ASTM F3442; Auto-GCAS navigation uncertainty buffer; TAWS HPL / HIL position
source; geofence "protection level" margin UAV keep-out.

Automotive: lane keeping localization integrity alert limit lane width; ISO 21448 SOTIF
localization integrity safety margin.

Patents: drone geofence buffer from GNSS protection level (Google Patents via WebSearch).

Vendors: Skydio / Shield AI / Exyn / Auterion navigation integrity and obstacle margin; Shield
AI Hivemind runtime assurance; Auterion Skynode integrity geofence.

GitHub: `gh api repos/tiiuae/px4-secure-state-reconstruction`; `gh search repos "fault tolerant
control barrier function"` (0 results).

Not searched: Google Scholar directly (no access, WebSearch only), IEEE Xplore, Espacenet or
USPTO full-text, ION GNSS+ 2024-2026 proceedings beyond search summaries, defence primes.

## 5. Not verified

Reconciled 2026-11-09 (loop-28) against
[close-area-safety-filter](../../../samples/close-area-safety-filter/README.md). Still open:

- Tan 2025 IROS venue comes from a Nature Index listing; the arXiv page says "Submitted to
  IROS 2025". Their safety-region sizes and setup are from the arXiv HTML; I did not run their code.
- FT-CBF CDC 2020 page numbers come from the TAC paper's reference list; the CDC paper itself
  was not opened.
- Hafez 2019: abstract only. I did not confirm whether its alert limit is tied to obstacle
  distance. Full author list not confirmed, so no record was added.
- Sun 2020 and Haro 2023: abstracts only; author initials from MDPI citation strings.
- RNP, TAWS and Auto-GCAS behaviour comes from secondary summaries, not ICAO Doc 9613/8168 or
  RTCA text.
- Skydio "Variable Margins": search snippet of a release note only.
- Vendor silence (Exyn, Auterion) means nothing public was found, not that nothing exists.
- The 25-of-30 wrong-exclusion figure is the hub's multi-source-fde result for the max-separation
  rule, used here as an analogy for FT-CBF step 3. Nobody has run FT-CBF step 3 on those inputs,
  and the FT-CBF and Tan arms were dropped from the kill test. The nearest close-area number is
  the safety-filter monitor's max-separation variant, open loop: wrong source in 9 runs (UWB NLOS)
  and 19 runs (VIO + UWB), 100 layouts per case, synthetic
  ([integrity monitor](../../../samples/close-area-safety-filter/README.md#integrity-monitor-ran-2026-11-09-synthetic)).

### Refuted since

- Section 2, "the sentence a judge would accept": the composition it describes (F5) did not beat
  a fixed 0.2 m bound; see the note at the end of section 2.

Records added: `data/resources/loop-13.json` (7 resources).
