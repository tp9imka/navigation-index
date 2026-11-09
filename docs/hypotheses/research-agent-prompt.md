# Research handoff: challenge the innovation claims

Work in this repository. The implementation agent owns
`samples/navigation-innovation-lab/`, `docs/hypotheses/`, shared guides, evidence and
generated outputs. Put research in `docs/research/innovation-prior-art/` and a uniquely
named file under `data/resources/`. Do not edit generated files or shared code concurrently.

Investigate closest prior art, failure modes and usable data for:

1. Aircraft-feasible maneuvers that distinguish competing visual location hypotheses,
   especially data-association uncertainty, map errors, missing true hypotheses and
   common appearance changes. Compare to information gain, not only passive movement.
2. Scheduling costly localization using navigation deadlines, capture opportunity,
   arrival latency and compute budget. Compare to event-triggered covariance control,
   simple opportunity scheduling and sensing/control co-design. Check whether flight
   speed affects time-driven and distance-driven error differently.
3. Selective aerodynamic navigation adaptation with intermittent references. Separate
   wind/velocity/bias identifiability, reference health, correlated sensor errors,
   persistent excitation and forgetting. Compare to batch calibration and established
   adaptive-filter/system-identification methods.

Read [current cards](README.md) and [measured POCs](../../samples/navigation-innovation-lab/results/report.md)
before searching. The first POCs already show: H1 collapses to information gain and
fails with map shift; H2 does not beat a simple opportunity policy convincingly;
H3 is useful after observable changes but not universally better than initial calibration.

Find primary papers, author slides/talks, workshop discussions, code, and datasets.
For each candidate deliver: closest 3-5 works; the exact overlap; a narrow remaining
contribution (if any); assumptions; strongest baseline; falsification experiment;
dataset sensor channels, timestamps, ground-truth independence, size, license and
download availability. Distinguish published paper/preprint/abstract, read/watched
versus merely linked, and reported versus reproduced measurements. Do not infer
novelty from an unsuccessful search or independence from different algorithm names.

Prioritize a concrete redesign over a long bibliography. If existing work already
solves the proposed contribution, say so and identify a testable adjacent gap.
