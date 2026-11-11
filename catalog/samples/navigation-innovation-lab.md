# Sample: Navigation innovation laboratory: active localization, asynchronous fix scheduling and selective model adaptation

`sample:navigation-innovation-lab` - code and walkthrough in [samples/navigation-innovation-lab](../../samples/navigation-innovation-lab/)

Three stdlib synthetic POCs with conventional baselines, ablations, held-out seeds, stress cases and paired intervals. Tests possible contributions rather than claiming novelty; exposes map-shift failures, harmful slowdown and limits of model adaptation. A separate causal replay evaluates cached VPAIR observations under artificial frame delays and an uncalibrated covariance proxy; no consistent scheduling advantage.

**Verification:** Ran 2026-11-09 on Python 3.9.6/macOS arm64: 8000 synthetic evaluation episodes, 100 seeds per scenario, disjoint from 16 tuning seeds; 19 stdlib unit tests. Source hashes, tuning grids and all per-seed metrics committed. No images, aircraft dynamics, SITL, hardware or field validation; offline network-denial test not performed. Also ran 48 cached VPAIR replay cases, with hashes of three sibling input files; real-flight-derived inputs but artificial timing and a simplified filter.

## Practical readiness

| Compute | Hardware | Offline | Setup | Dataset download | Tested platforms | Validation |
|---|---|---|---|---|---|---|
| cpu | none | unknown | unknown | 0 MB | macos-arm64 | integrated |

**Main limitation:** Primary benchmark uses synthetic descriptor/scalar models; optional replay is one previously studied flight with artificial frame delays, not field validation.

**Readiness evidence:** [samples/navigation-innovation-lab/results/results.json](../../samples/navigation-innovation-lab/results/results.json)

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md)

**Tags:** `innovation`, `hypothesis`, `active-localization`, `sensor-scheduling`, `observability`, `calibration`, `benchmark`, `stdlib`

## Related

- extends: [End-to-end GNSS-denied visual navigation on one real flight: nadir VO + DINOv2 retrieval + LightGlue fixes + multi-frame voting + altpnt integrity (VPAIR)](../../catalog/samples/e2e-visual-nav-vpair.md)
- explains: [AI-IO](../../catalog/repos/sjtu-visys-team__ai-io.md)

## Referenced by

- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [H1: move to distinguish competing location hypotheses](../../docs/hypotheses/h1-active-disambiguation.md) (mentions)
- [H2: request a localization fix before its navigation deadline](../../docs/hypotheses/h2-localization-scheduling.md) (mentions)
- [H3: adapt a navigation model only when the data identify it](../../docs/hypotheses/h3-selective-adaptation.md) (mentions)
- [Navigation invention hypothesis cards](../../docs/hypotheses/README.md) (mentions)
- [Innovation experiments: hypotheses before claims](../../docs/innovation-experiments.md) (mentions)
- [Choose a stack you can run](../../docs/practical-readiness.md) (mentions)
- [Brief decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Research rounds: which one applies, and the innovation story per brief](../../docs/research/README.md) (mentions)
- [Motion Planning for Global Localization in Non-Gaussian Belief Spaces](../../catalog/resources/agarwal-2015-nongaussian-global-localization.md) (explains)
- [On-Device CPU Scheduling for Robot Systems](../../catalog/resources/catan-2022-robot-scheduling.md) (explains)
- [The Kidnapped UAV Problem: Self-Supervised Detection and Recovery of Localization Failures for GNSS-Denied Navigation](../../catalog/resources/deng-sentis-2026-kidnapped-uav.md) (explains)
- [Estimating wind using a quadrotor](../../catalog/resources/hattenberger-2022-estimating-wind.md) (explains)
- [Safe, Real-Time Active Model Discrimination and Fault Diagnosis for Nonlinear Systems via Differentiable Reachability](../../catalog/resources/ni-2026-active-model-discrimination.md) (explains)
- [Planning and Control with Imperfect Sensors and Perception](../../catalog/resources/rss-2026-imperfect-perception-workshop.md) (explains)
- [Learning Agile, Vision-based Drone Flight: from Simulation to Reality](../../catalog/resources/scaramuzza-kaufmann-2023-agile-notes.md) (explains)
- [Reduced latent belief spaces for active perception in robotics](../../catalog/resources/wakulicz-2026-reduced-belief-seminar.md) (explains)

_Indexed by lane(s): samples_
