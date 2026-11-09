# Innovation prior art: synthesis

Deeper research round for EDGE hackathon Challenge 2, 2026-11-09. Four lanes checked what
already exists before we build POCs. Each lane doc gives: prior art with a source-type label
(peer-reviewed / preprint / abstract only / slides viewed / recording not viewed / code), the
narrow contribution that might remain, the strongest baseline, a falsification experiment with
a pass/fail threshold, and a failure-mode checklist (missing true hypothesis, correlated errors,
map mismatch, delayed measurements, wind/velocity ambiguity).

"Not found in this search" in these docs means the listed queries returned nothing. It is not
a novelty claim. No experiment in these docs has been run; every threshold is a proposal.

| Doc | Idea | What exists | What may remain | Verdict |
|---|---|---|---|---|
| [01](01-disambiguating-maneuvers.md) | Flyable maneuvers that separate competing visual / terrain position hypotheses | Fox, Burgard, Thrun 1998 (expected entropy over a multimodal belief); Platt et al. 2012 (actions under dynamics that separate hypotheses); Bar-Gill 1994 TAN route planning | Short-horizon maneuver choice, triggered only on a multimodal posterior, over fixed-wing-flyable primitives, with an explicit "truth not in set" hypothesis. Engineering, not theory | Narrow. Falsifier on real GLO-30 terrain via blind-flight-bench |
| [02](02-deadline-aware-fix-scheduling.md) | Schedule expensive fixes by deadline, success probability and delay | Covariance-triggered updates reduce to a fixed schedule (Trimpe, Campi 2015); compute-budgeted VIO; per-frame VPR success prediction; delayed fusion; aviation "limit time" | One scheduler combining all three, with a success model that captures failure clustering and the filter's delay horizon | Narrow, and at risk: the cheap pre-match signal has AUC 0.68 on VPAIR; pays only when compute is shared |
| [03](03-identifiability-gated-aero-adaptation.md) | Adapt aero parameters only when identifiable | Sharma, Laupre, Skaloud 2023 (Gramian-gated updates + consider states, offline); Laupre et al. 2023 (consider mode during outages) | Online per-direction gate inside the filter, applied to the multirotor drag model | Weak as a headline. Keep as a robustness layer under the drag filter |
| [04](04-wider-innovation-scan.md) | Ten other directions, ranked | See its table | Top 3: calibrated trust for visual fixes (25/30), particle-filter integrity with a missing-hypothesis test for TRN (25/30), delay-aware invariant filter (23/30) | Two strong, one risky |

## Findings that change earlier docs

- **ArduPilot EKF3 drag fusion is a wind estimator, not velocity aiding.** At `Copter-4.6.3`,
  `FuseDragForces` sets gains only for the two wind states. PX4 EKF2 `fuseDrag` applies the full
  gain (velocity is corrected), gated on `!fake_pos`. The drag differentiator therefore has to
  be our own filter; [differentiators-scan.md](../../differentiators-scan.md) section 2.1 and
  the [Challenge 2 page](../../challenge-2-autonomous-flight.md) are corrected.
- **PX4 EKF2 cannot fuse a fix much older than its delay horizon** (`EKF2_DELAY_MAX` default
  200 ms, max 1000 ms). The hub's top-5 visual match is 0.82 s at p95 on an M2 Max.
- **Visual fix failures cluster.** On the cached VPAIR front end, after a failed attempt the next
  one fails 62-69 % of the time (strides 1-8). Any model assuming independent attempts is wrong.

## Relation to the innovation lab

Ideas 01-03 are the hypotheses H1-H3 that `samples/navigation-innovation-lab` (branch
`feat/innovation-pocs`) tests with synthetic mechanism models. Its first results agree with
this prior art: H1 collapsed to the information-gain baseline, H2 showed no general win, H3
helped only after an observable change. These docs supply the real-data falsifiers and the
strongest baselines for the next round of that lab.

## Recommended POC set (not yet built)

One story, three parts: the airframe keeps us flying, every fix carries a calibrated trust,
and the filter knows when it is lost.

1. **Drag-aided velocity filter with an identifiability gate** (scan 2.1 + doc 03). Our own
   filter, fitted and tested on real rotor-speed data (AI-IO, NeuroBEM), SITL logs for the wind
   sweep. Matches "propulsion / applied physics". Metric: time from GNSS loss to 50 m error at
   0 / 3 / 6 m/s wind.
2. **Calibrated trust for visual fixes** (doc 04, A). Conformal acceptance and a 90 % error
   radius fitted on cached VPAIR fixes, used as the filter's R. Small sample (199 frames), so
   wide intervals.
3. **Terrain filter that knows it is lost** (doc 04, B). Protection levels plus a
   missing-hypothesis test on blind-flight-bench particle clouds. Pass: zero epochs where error
   exceeds the bound, including diverged runs.

Parked: the delay-aware invariant filter (doc 04, C), no open reference code; and ideas 01-02,
which stay with the innovation lab.
