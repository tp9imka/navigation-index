# Sample: Close-area relocalization after VIO loss: scan-to-map pose hypotheses, ratio + persistence acceptance, hover until one wins

`sample:close-area-relocalize` - code and walkthrough in [samples/close-area-relocalize](../../samples/close-area-relocalize/)

Relocalizer for the close-area arena. After a detected VIO loss (reset_counter change, quality 0, or a scan-to-map innovation test) a pose source that wraps the arena's VIO-like estimator reports quality 0 (a planner gate hovers), matches the 72-beam range scan against the known 0.1 m occupancy grid by correlative grid search on a likelihood field (EDT distance, sigma 0.10 m, +-2 m window), keeps up to 5 hypotheses 0.5 m apart, and accepts one with a named rule: best score >= 0.6, best >= 1.02 x second, and the same winner for 3 scans; 'none of them' keeps hovering and widens the window to +-4 m. On accept it re-anchors the estimate. experiment.py flies the arena's A* known-map planner on 100 random layouts under the dropout and jump faults and compares no relocalization, hover only, single-hypothesis commit at once, and the multi-hypothesis rule, with ablations without the innovation test, plus a symmetric 2 m x 14.8 m corridor where shifted poses look the same. Thresholds set on seed-1 static poses (tune.py). Synthetic arena only.

**Verification:** ran 2026-11-09 with CPython 3.12.10 + numpy 2.5.4 / scipy 1.18.1 on an Apple M3 Max, in the sample venv: experiment.py --layouts 100 --seed 0 ran twice with identical tables (wall 70.7 s on 8 workers for the kept run); experiment.py --corridor --runs 20 ran once (21.3 s); tune.py on seed 1 wrote results/tune_seed1.json. Every number in README is from results/. test_smoke.py: 1 passed in the venv, 1 skipped under plain python3 without numpy. No arena file was edited. Layouts, vehicle, estimator and range sensor are simulated; yaw is truth; the map is the exact prior grid; no SITL, no real drone or lidar. Later: run_disambiguate.py --corridor --runs 20 (22 s) and --layouts 100 --seed 0 (75 s) in the sample venv (CPython 3.11.15, numpy 2.4.6, scipy 1.17.1); the loop driver ran --layouts 100 --seed 1 as a held-out check (76.5 s, results/disamb_random_1.md). Acceptance thresholds came from seed-1 static poses (tune.py); no flight parameter was tuned on seed 1.

## Practical readiness

| Compute | Hardware | Offline | Setup | Dataset download | Tested platforms | Validation |
|---|---|---|---|---|---|---|
| cpu | none | unknown | unknown | 0 MB | macos-arm64 | integrated |

**Main limitation:** Synthetic 2.5D arena, yaw is truth, exact prior map, perfect hover. Setup needs network for PyPI wheels (uv venv + uv pip install); cold setup time not measured; no network-denied run, so offline is unknown. README names an Apple M3 Max host; macOS assumed from the M3 Max host, Linux not tested.

**Readiness evidence:** [samples/close-area-relocalize/README.md](../../samples/close-area-relocalize/README.md), [samples/close-area-relocalize/sample.json](../../samples/close-area-relocalize/sample.json), [samples/close-area-relocalize/results/reloc_random_0.json](../../samples/close-area-relocalize/results/reloc_random_0.json), [samples/close-area-relocalize/results/disamb_random_1.md](../../samples/close-area-relocalize/results/disamb_random_1.md)

**Concepts:** [LiDAR odometry and SLAM](../../catalog/concepts/lidar-slam.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md)

**Tags:** `close-area`, `a-to-b`, `relocalization`, `kidnapped-robot`, `multi-hypothesis`, `scan-matching`, `correlative-scan-matching`, `likelihood-field`, `occupancy-grid`, `vio-loss`, `reset-counter`, `innovation-test`, `hover`, `symmetric-corridor`, `python`, `numpy`, `scipy`

## Related

- explains: [Close-area arena: seeded 2.5D A=>B simulator, published drone interface, truth scorer](../../catalog/samples/close-area-arena.md)
- explains: [Active Markov Localization for Mobile Robots](../../catalog/resources/fox-burgard-thrun-1998-active-markov-localization.md)
- explains: [FAST_LIO_LOCALIZATION](../../catalog/repos/hviktortsoi__fast_lio_localization.md)

## Referenced by

- [Challenge 2 "Autonomous Frontiers": entry point](../../docs/challenge-2-autonomous-flight.md) (mentions)
- [Cheat sheets: pick one in 30 seconds](../../docs/cheatsheets/README.md) (mentions)
- [Day-1 intake: close-area A=>B, organiser answers => stack](../../docs/day1-close-area-intake.md) (mentions)
- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Choose a stack you can run](../../docs/practical-readiness.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [04. Close-area navigation: prior art for three innovation angles, plus a wider scan](../../docs/research/close-area-nav/04-innovation-prior-art.md) (mentions)
- [Close-area A=>B navigation: synthesis](../../docs/research/close-area-nav/README.md) (mentions)
- [Research rounds: which one applies, and the innovation story per brief](../../docs/research/README.md) (mentions)
- [Demo script: close-area A to B](../../templates/demo-script-close-area.md) (mentions)
- [Close-area pitch scaffold: A to B through obstacles](../../templates/pitch/close-area-story.md) (mentions)
- [Judge drill: close-area A=>B, relocalization pitch (H1)](../../templates/pitch/judge-drill-close-area.md) (mentions)

_Indexed by lane(s): samples_
