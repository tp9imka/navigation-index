# Navigation invention hypothesis cards

<!-- about: sample:navigation-innovation-lab -->

Status: first POCs executed on 2026-11-09. No global novelty claim. These cards
distinguish an interesting mechanism from an advantage over prior art.

| Card | Proposed contribution | Current decision |
|---|---|---|
| [H1: active location disambiguation](h1-active-disambiguation.md) | Cheap motion selection using disagreement between candidate locations | Candidate collapses to standard information gain; map mismatch exposes a failure |
| [H2: deadline-aware localization scheduling](h2-localization-scheduling.md) | Decide when a fix is useful before its result arrives | Predictive trigger merits replay; slowdown and complexity have not earned their cost |
| [H3: selective model adaptation](h3-selective-adaptation.md) | Learn only identifiable parameters when trustworthy reference evidence is available | Conditional benefit after parameter change; not better than initial calibration everywhere |

Run all three: `python3 samples/navigation-innovation-lab/benchmark.py` from the
repository root. See the [laboratory](../../samples/navigation-innovation-lab/README.md)
and [experiment design](../innovation-experiments.md).

Each card contains the failure case, nearest prior art, proposed difference,
observable inputs, baselines, disproof condition, measured result, and next test.
