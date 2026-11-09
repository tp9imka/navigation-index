# Navigation innovation laboratory

Three executable POCs and a cached real-flight replay test proposed contributions against conventional baselines,
with negative cases retained. All initial results are **synthetic mechanism tests**.
No image inference is rerun; no autopilot, physical aircraft dynamics, hardware or real-time guarantees.

## Run

Python 3 standard library only; no installation, download or credentials:

```sh
python3 benchmark.py
python3 replay_vpair.py   # optional: uses committed sibling observation caches
python3 -m unittest -v
```

From repository root: `python3 samples/navigation-innovation-lab/benchmark.py`.
Default output goes beside the script, irrespective of working directory. Use
`--out /tmp/nav-innovation-repeat` for a separate receipt, or `--seeds 200 --seed-start 2000`
for additional evaluation seeds. The CLI rejects overlap with development seeds.

Open [the standalone dashboard](results/dashboard.html), read [full results](results/report.md),
or inspect [CSV means](results/summary.csv), [per-seed JSON](results/results.json),
and [example traces](results/traces.json). No network requests are made by the programs;
offline operation has not been independently verified under network denial.

## What each program tests

| Program | Proposed mechanism | Strongest conventional comparator | Main limit |
|---|---|---|---|
| [disambiguation.py](disambiguation.py) | Choose observations by moving between possible map locations | Expected information gain with identical constraints | Scalar invented descriptor maps; no image prediction or aircraft dynamics |
| [scheduling.py](scheduling.py) | Request fixes before route uncertainty becomes problematic | Tuned opportunity timing and covariance thresholds | Fixed route; artificial delay/success model; estimator error, not flight control |
| [adaptation.py](adaptation.py) | Reject calibration updates with weak excitation or absent reference | Calibrate once then freeze | Algebraic one-axis drag model; reference availability assumed |

Cards: [H1](../../docs/hypotheses/h1-active-disambiguation.md),
[H2](../../docs/hypotheses/h2-localization-scheduling.md),
[H3](../../docs/hypotheses/h3-selective-adaptation.md).
Design and roadmap: [innovation experiments](../../docs/innovation-experiments.md).

## Protocol

16 development seeds (0..15), grid search separately for every tunable policy,
100 evaluation seeds (1000..1099), 8,000 evaluation episodes across 14 scenarios.
Each seed shares its exogenous random errors across policies; evaluation does not
change the selected settings. H1 trains on nominal, H2 on nominal/slow-compute, H3
on nominal/no-excitation. Other named conditions are held-out stress distributions.
All noise distributions and route/map structures are intentionally simple and documented
in source. Seeds are independent repetitions of those models, not independent real worlds.

The runner records source SHA256 hashes, interpreter/platform, elapsed wall time,
tuning grids, all metrics and 95% paired-bootstrap difference intervals (1,000 resamples).
Intervals quantify the seed distribution only. They are not corrected for multiple
comparisons and do not cover simulator mismatch. A zero observed error count is not
a zero-risk guarantee. Distance/time means include abstentions and failed episodes;
always read success/false-accept rates alongside them.

## Verification

Ran on 2026-11-09, Python 3.9.6 on macOS arm64. The standard-library unit tests cover
unidentifiable hypotheses, unknown rejection, information-gain limits, common map
constraints, delayed updates, request budgets, parameter identifiability, missing
references, deterministic evaluation and paired confidence-interval arithmetic.
The exact run time and environment are in the result receipt (about 11 seconds here).

## What survived the first experiment

- **H1:** selected cost weight is zero, so the proposed policy is the conventional
  information-gain baseline. Nominal 3.11 versus 13.11 mean distance for passive;
  99% versus 100% correct acceptance. Shifted maps cause 72% false acceptance.
  No novel advantage established.
- **H2:** fixed-speed predictive triggering gives 64% nominal tolerance-respecting
  completion versus 54% threshold triggering, using 6.93 versus 10 requests. A simpler
  opportunity heuristic is competitive. Slowdown is often harmful. No general win.
- **H3:** selective calibration helps after an observable parameter change (0.2465 m/s
  velocity RMSE versus 2.2660 initial calibration), but initial calibration is better
  nominally (0.3433 versus 0.3579). An unobserved late change defeats both.

Keep these outcomes when pitching or continuing work. A runnable POC is not proof
of novelty, calibrated integrity, or readiness to control an aircraft.

## Recorded VPAIR follow-up

[replay_vpair.py](replay_vpair.py) adds 48 cases: dense/sparse reference maps,
Q=4/16 m² per frame, artificial delivery delays of 0/2/5 frames, and VO-only,
periodic, covariance-threshold and predictive request policies. It reads the
committed sibling cache, so no downloads or GPU are needed. Match outcomes are
read only for requested frames; decisions use past completed jobs, never future
outcomes or evaluation truth. A fixed 40-request cap applies to every scheduler.

[Replay report](replay-results/report.md) · [receipt](replay-results/results.json) ·
[causal traces](replay-results/traces.json). The first ten known-reference frames
fit the affine pixel-to-map transform (37 pairs); frames 10..198 are evaluated.
The estimator is a simple VO offset filter, not the sibling's heading/scale EKF.
The default 19 tests also check arrival ordering, calibration truth exclusion,
future-outcome causality and no unrequested matching on the VO-only path.

Results do **not** show consistent predictive superiority. For example, dense map,
Q=16, delay=2 frames: threshold RMSE 61.86 m, periodic 73.14 m, predictive 108.02 m.
Sparse map, Q=4, delay=5 frames: threshold 155.82 m, periodic 129.00 m, predictive
146.96 m. VO-only RMSE is 155.82 m. All cases are retained; these are not confidence
intervals over independent flights. The conservative covariance and simple filter
can reject useful corrections after error growth, so this is not an isolated test
of the scheduler's merits.

The source VO has an injected 2-degree heading error. Its calibration and rendered
map share the same flight's reference. The simplified affine map transform omits
changing attitude corrections. There are no real timestamps: source time fields
are frame indices. Historical cached matching-time sums are accounting estimates,
not measured savings on current hardware. No altered trajectory or speed policy is
validated by replaying this fixed flight.
