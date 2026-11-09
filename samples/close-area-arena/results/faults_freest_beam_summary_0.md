`python run_faults.py --planner freest_beam --layouts 50 --seed 0` (synthetic). Planner sees the estimate; ranges and scores are on truth.

| case | layouts | reached % | collision % | stuck % | timeout % | median min clearance m | est err median m | est err max m | median of run max err m | err > 2 sigma % | fault fired runs |
|---|---|---|---|---|---|---|---|---|---|---|---|
| truth | 50 | 86.0 | 0.0 | 14.0 | 0.0 | 0.467 | - | - | - | - | - |
| none_nodark | 50 | 74.0 | 0.0 | 26.0 | 0.0 | 0.467 | 0.112 | 0.4771 | 0.2291 | 0.9 | 0 |
| none | 50 | 58.0 | 0.0 | 42.0 | 0.0 | 0.466 | 0.1647 | 1.0918 | 0.3812 | 4.0 | 0 |
| jump | 50 | 42.0 | 0.0 | 58.0 | 0.0 | 0.465 | 0.3878 | 1.1637 | 0.6567 | 25.5 | 43 |
| bias | 50 | 40.0 | 0.0 | 60.0 | 0.0 | 0.469 | 0.406 | 1.2832 | 0.7225 | 28.2 | 50 |
| dropout | 50 | 46.0 | 0.0 | 54.0 | 0.0 | 0.475 | 0.2913 | 1.2241 | 0.4933 | 19.5 | 50 |
| overconfident | 50 | 58.0 | 0.0 | 42.0 | 0.0 | 0.466 | 0.1647 | 1.0918 | 0.3812 | 99.6 | 50 |

Drift calibration (none_nodark, 50 runs, origin-anchored final error): fitted C = 0.0439 m/sqrt(m) vs target 0.0474; => 0.1389 m RMS at 10 m vs 0.15 m target (samples/relative-nav-benchmark/README.md: OpenVINS UZH-FPV indoor_forward_3, RPE over 10 m 1.5 % (real data)).
