`python -m planners.astar_esdf --layouts 50 --seed 0` from samples/close-area-arena (synthetic: simulated layouts, vehicle and sensor)

| planner | family | layouts | reached % | collision % | stuck % | timeout % | median time to goal s | median min clearance m | replans | plan median ms | plan p95 ms | fallback replans | no-path replans | wall s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| straight | random | 50 | 26.0 | 0.0 | 74.0 | 0.0 | 17.06 | 0.38 | 0 | - | - | 0 | 0 | 3.4 |
| astar_esdf known_map | random | 50 | 100.0 | 0.0 | 0.0 | 0.0 | 18.81 | 0.635 | 2379 | 1.22 | 10.62 | 0 | 0 | 11.2 |
| astar_esdf unknown_map | random | 50 | 100.0 | 0.0 | 0.0 | 0.0 | 18.72 | 0.622 | 2389 | 21.01 | 57.53 | 0 | 0 | 69.7 |

Per run (outcome, min clearance m):

| run | straight | astar_esdf known_map | astar_esdf unknown_map |
|---|---|---|---|
| 0 | stuck 0.3666 | reached 0.5647 | reached 0.6432 |
| 1 | reached 1.2574 | reached 1.2564 | reached 1.2511 |
| 2 | reached 0.3789 | reached 0.6739 | reached 0.68 |
| 3 | stuck 0.3656 | reached 0.6144 | reached 0.6164 |
| 4 | stuck 0.3802 | reached 0.5976 | reached 0.6254 |
| 5 | stuck 0.3837 | reached 0.6517 | reached 0.5921 |
| 6 | stuck 0.3806 | reached 0.6146 | reached 0.6298 |
| 7 | stuck 0.3829 | reached 0.6847 | reached 0.5587 |
| 8 | stuck 0.3796 | reached 0.6308 | reached 0.6158 |
| 9 | reached 0.7689 | reached 0.7522 | reached 0.7639 |
| 10 | reached 0.9253 | reached 0.9321 | reached 0.9254 |
| 11 | stuck 0.3787 | reached 0.5861 | reached 0.6024 |
| 12 | stuck 0.4068 | reached 0.622 | reached 0.6168 |
| 13 | stuck 0.3667 | reached 0.6261 | reached 0.4987 |
| 14 | reached 1.1604 | reached 1.1604 | reached 1.1604 |
| 15 | reached 0.4707 | reached 0.6046 | reached 0.5849 |
| 16 | stuck 0.3736 | reached 0.6347 | reached 0.63 |
| 17 | reached 0.7313 | reached 0.7632 | reached 0.7624 |
| 18 | reached 1.1991 | reached 1.1991 | reached 1.1991 |
| 19 | stuck 0.4045 | reached 0.6074 | reached 0.6797 |
| 20 | stuck 0.3832 | reached 0.6222 | reached 0.5614 |
| 21 | stuck 0.383 | reached 0.6462 | reached 0.5491 |
| 22 | stuck 0.3681 | reached 0.628 | reached 0.587 |
| 23 | stuck 0.254 | reached 0.6163 | reached 0.6709 |
| 24 | reached 1.1526 | reached 1.1526 | reached 1.1526 |
| 25 | stuck 0.4034 | reached 0.6051 | reached 0.6247 |
| 26 | stuck 0.3842 | reached 0.6376 | reached 0.6197 |
| 27 | stuck 0.4031 | reached 0.5997 | reached 0.643 |
| 28 | stuck 0.3694 | reached 0.6403 | reached 0.6267 |
| 29 | reached 0.8428 | reached 0.8434 | reached 0.8287 |
| 30 | stuck 0.3602 | reached 0.6407 | reached 0.5929 |
| 31 | reached 0.789 | reached 0.8186 | reached 0.8203 |
| 32 | stuck 0.3185 | reached 0.595 | reached 0.5938 |
| 33 | stuck 0.38 | reached 0.6303 | reached 0.6517 |
| 34 | stuck 0.3744 | reached 0.6757 | reached 0.688 |
| 35 | stuck 0.3789 | reached 0.5757 | reached 0.5821 |
| 36 | stuck 0.3731 | reached 0.6667 | reached 0.566 |
| 37 | reached 0.2558 | reached 0.6005 | reached 0.5971 |
| 38 | stuck 0.3775 | reached 0.6402 | reached 0.6217 |
| 39 | stuck 0.2387 | reached 0.6387 | reached 0.5357 |
| 40 | stuck 0.3673 | reached 0.6176 | reached 0.5929 |
| 41 | stuck 0.3729 | reached 0.6235 | reached 0.6159 |
| 42 | stuck 0.3601 | reached 0.6662 | reached 0.6324 |
| 43 | stuck 0.4033 | reached 0.5447 | reached 0.6014 |
| 44 | reached 0.383 | reached 0.6173 | reached 0.5774 |
| 45 | stuck 0.3735 | reached 0.6361 | reached 0.6077 |
| 46 | stuck 0.3856 | reached 0.6522 | reached 0.6213 |
| 47 | stuck 0.3689 | reached 0.6478 | reached 0.6754 |
| 48 | stuck 0.3859 | reached 0.5968 | reached 0.622 |
| 49 | stuck 0.3866 | reached 0.6606 | reached 0.646 |

Plot: [astar_esdf_random_0_run0.png](astar_esdf_random_0_run0.png), run 0 (first run the unknown-map mode did not reach B, else run 0). Panels left to right: straight, astar_esdf known_map, astar_esdf unknown_map. Blue = truth path, green = last planned path, grey band = 0.15 m inflation, orange = stuck, magenta = collision, purple = timeout.


Notes (written by hand after the run, synthetic): pass line known_map reached >= 90 % on random => PASS (100 %). The straight planner reaches 26 % on these 50 layouts (40 % on the first 20 in straight_random_0.md). Planner constants were tuned on layouts 0-9 of seed 0 (part of this set), so the numbers are not held-out. Planning ms are wall time on one machine and move with load.
