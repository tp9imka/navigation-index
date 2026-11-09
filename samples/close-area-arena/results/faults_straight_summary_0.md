`python run_faults.py --planner straight --layouts 50 --seed 0` (synthetic). Planner sees the estimate; ranges and scores are on truth.

| case | layouts | reached % | collision % | stuck % | timeout % | median min clearance m | est err median m | est err max m | median of run max err m | err > 2 sigma % | fault fired runs |
|---|---|---|---|---|---|---|---|---|---|---|---|
| truth | 50 | 26.0 | 0.0 | 74.0 | 0.0 | 0.38 | - | - | - | - | - |
| none_nodark | 50 | 22.0 | 0.0 | 78.0 | 0.0 | 0.376 | 0.095 | 0.4759 | 0.1578 | 1.1 | 0 |
| none | 50 | 16.0 | 0.0 | 84.0 | 0.0 | 0.377 | 0.1434 | 0.9388 | 0.2508 | 1.8 | 0 |
| jump | 50 | 14.0 | 0.0 | 86.0 | 0.0 | 0.38 | 0.3985 | 1.1608 | 0.577 | 32.4 | 44 |
| bias | 50 | 16.0 | 0.0 | 84.0 | 0.0 | 0.379 | 0.271 | 1.3576 | 0.5326 | 23.0 | 50 |
| dropout | 50 | 16.0 | 0.0 | 84.0 | 0.0 | 0.378 | 0.1854 | 1.0428 | 0.3575 | 13.8 | 50 |
| overconfident | 50 | 16.0 | 0.0 | 84.0 | 0.0 | 0.377 | 0.1434 | 0.9388 | 0.2508 | 99.5 | 50 |

Drift calibration (none_nodark, 50 runs, origin-anchored final error): fitted C = 0.0423 m/sqrt(m) vs target 0.0474; => 0.1338 m RMS at 10 m vs 0.15 m target (samples/relative-nav-benchmark/README.md: OpenVINS UZH-FPV indoor_forward_3, RPE over 10 m 1.5 % (real data)).
