# Innovation experiments: hypotheses before claims

<!-- about: sample:navigation-innovation-lab, concept:path-planning, concept:sensor-fusion, concept:assured-pnt -->

For an autonomous flight navigation task, start from an existing estimator and flight stack, then identify a
specific algorithmic contribution with a strong baseline and a falsification test.
These experiments were authorized on 2026-11-09 after discussion of the three ideas.
They complement the completed [differentiator](differentiators-scan.md),
[guidance](guidance-planning.md), and [product](path-to-product.md) research lanes.

## Read in this order

1. [Hypothesis cards](hypotheses/README.md): prior art, exact proposed difference,
   assumptions, strongest baseline, test, and decision.
2. [Runnable laboratory](../samples/navigation-innovation-lab/README.md): three
   dependency-free POCs with a shared reproduction command.
3. [Measured report](../samples/navigation-innovation-lab/results/report.md): all
   policies and stress cases, including unfavorable results and paired intervals.
4. Prior art: each card's "Closest work and proposed difference" section lists what was
   searched and what is still open.

## Experimental contract

- Synthetic descriptor-level or one-axis models first. No claim of aircraft,
  perception-network, hardware, or field validation. No flight commands.
- Tune all configurable competitors on seeds 0..15. Evaluate on 1000..1099.
  Stress conditions are excluded from tuning except the explicitly listed
  nominal/slow-compute and nominal/no-excitation development scenarios.
- Share exogenous randomness across policies within a seed. Actions can change
  observations and episode duration. A policy never receives hidden truth or
  future random disturbances.
- Compare against plausible simple alternatives, not just a broken baseline.
  Report ablations separately from conventional competitors.
- Record every per-seed metric, configuration search, source hash, environment,
  runtime receipt, and one trace per policy/scenario.
- Bootstrap paired differences, with no significance claim across multiple
  endpoints. Simulation confidence intervals do not cover model error.
- Do not change the benchmark until the candidate wins. Record negative findings
  and require fresh seeds/maps/flights for a later redesigned candidate.

## First decisions

| Idea | What the POC says | Next decision |
|---|---|---|
| H1: move to distinguish locations | Faster than passive movement, but tuned candidate becomes standard information gain; map error causes many false accepts | No demonstrated novel advantage. Investigate nuisance/map uncertainty before attempting a flight demo |
| H2: schedule fixes around navigation deadlines | Predictive fixed-speed scheduling beats a covariance threshold in some constructed cases; a simpler opportunity heuristic is competitive; slowdown often hurts | Retain as an integration experiment; no established advantage over the strongest simple baseline |
| H3: adapt only identifiable parameters | Helps after an observable parameter change; one-time calibration is better in nominal conditions; all fail after an unobserved change | Narrow the contribution to adaptation under changing conditions, not general navigation accuracy |

These are results of this laboratory, not a literature novelty assessment. Research
must still establish whether even the narrowed contributions are already published.

## Architecture of the POCs

`world + seeded disturbances -> policy observations -> action/update -> world`

Truth goes only to measurement generation and the evaluator. H1 chooses a local
motion; H2 chooses a fix request and optionally speed; H3 chooses which calibration
updates to accept. The shared runner only tunes, evaluates, aggregates and records.
The same code is usable without the dashboard or the rest of the index.

## From this evidence to an aircraft

H1 needs a renderer or a branching real-view dataset to test actions that were not
flown. A fixed recorded trajectory cannot validate an active movement policy.
H2 can first replay recorded VO/fixes with explicit artificial delivery delays;
that cannot establish actual embedded compute savings or altered flight behavior.
H3 needs synchronized actuator, IMU and independent reference data with payload/wind
changes, then a model different from the estimator in simulation. Use the data
leads in the differentiator lane and preserve their license/availability caveats.

Keep the [evidence matrix](evidence-matrix.md) and hypothesis decisions synchronized
with each new measured result. Do not turn simulation tuning into a product claim.

## Recorded-observation follow-up

The [VPAIR replay](../samples/navigation-innovation-lab/replay-results/report.md)
adds 48 cases using already committed real-flight-derived observations. It finds
no consistent predictive-scheduling improvement. It also exposes the dependence on
filter consistency and delayed-correction handling. Artificial delays are in frames,
not physical time; the simplified estimator and shared flight/map reference prevent
an independent field-performance claim. See the laboratory README for every caveat.
