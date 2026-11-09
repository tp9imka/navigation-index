`python compare.py run --layouts 50 --seed 0` (synthetic: simulated layouts, vehicle and sensor; arm64, CPython 3.12.10, numpy 2.5.4, scipy 1.18.1)

Planning time = whole replan (ESDF + cost arrays + search + shortcut). Search = the search call only.

| family | search | reached % | collision % | stuck % | timeout % | median time to goal s | replans | plan ms median | plan ms p95 | search ms median | search ms p95 | plan s per run median | plan s per run max | wall s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| random | A* from scratch | 100.0 | 0.0 | 0.0 | 0.0 | 18.72 | 2389 | 22.83 | 64.97 | 20.62 | 62.53 | 1.32 | 2.13 | 77.9 |
| random | D* Lite | 100.0 | 0.0 | 0.0 | 0.0 | 18.66 | 2391 | 5.14 | 10.6 | 3.19 | 7.33 | 0.32 | 0.43 | 24.9 |
| u_trap | A* from scratch | 100.0 | 0.0 | 0.0 | 0.0 | 22.11 | 2826 | 37.86 | 70.54 | 35.05 | 67.35 | 2.03 | 2.59 | 113.0 |
| u_trap | D* Lite | 100.0 | 0.0 | 0.0 | 0.0 | 21.94 | 2822 | 5.32 | 14.38 | 3.27 | 11.12 | 0.39 | 0.53 | 29.3 |
| narrow_gap | A* from scratch | 80.0 | 0.0 | 14.0 | 6.0 | 27.79 | 4664 | 39.22 | 67.68 | 36.15 | 61.69 | 2.57 | 9.16 | 191.4 |
| narrow_gap | D* Lite | 84.0 | 0.0 | 12.0 | 4.0 | 29.9 | 4651 | 7.65 | 24.38 | 4.39 | 19.06 | 0.71 | 2.23 | 62.9 |

| family | same outcome A* vs D* (runs) | A* backend identical to arena results (runs) | D* first search pops median | D* incremental: changed cells / updated vertices / pops median | pops p95 |
|---|---|---|---|---|---|
| random | 50 / 50 | 50 / 50 | 24862.5 | 1057.0 / 2342.0 / 192.0 | 1317.0 |
| u_trap | 50 / 50 | 50 / 50 | 24625.0 | 874.5 / 2044.5 / 425.0 | 1739.0 |
| narrow_gap | 41 / 50 | 50 / 50 | 24825.0 | 645.5 / 1506.0 / 980.5 | 4968.8 |

Per run (outcome A* / D*):

| run | random | u_trap | narrow_gap |
|---|---|---|---|
| 0 | reached / reached | reached / reached | reached / reached |
| 1 | reached / reached | reached / reached | reached / reached |
| 2 | reached / reached | reached / reached | reached / reached |
| 3 | reached / reached | reached / reached | reached / reached |
| 4 | reached / reached | reached / reached | reached / stuck |
| 5 | reached / reached | reached / reached | reached / reached |
| 6 | reached / reached | reached / reached | reached / reached |
| 7 | reached / reached | reached / reached | reached / reached |
| 8 | reached / reached | reached / reached | reached / reached |
| 9 | reached / reached | reached / reached | reached / reached |
| 10 | reached / reached | reached / reached | reached / reached |
| 11 | reached / reached | reached / reached | stuck / stuck |
| 12 | reached / reached | reached / reached | reached / reached |
| 13 | reached / reached | reached / reached | reached / reached |
| 14 | reached / reached | reached / reached | reached / reached |
| 15 | reached / reached | reached / reached | reached / reached |
| 16 | reached / reached | reached / reached | reached / reached |
| 17 | reached / reached | reached / reached | stuck / timeout |
| 18 | reached / reached | reached / reached | reached / reached |
| 19 | reached / reached | reached / reached | reached / reached |
| 20 | reached / reached | reached / reached | reached / reached |
| 21 | reached / reached | reached / reached | timeout / stuck |
| 22 | reached / reached | reached / reached | reached / reached |
| 23 | reached / reached | reached / reached | reached / reached |
| 24 | reached / reached | reached / reached | reached / reached |
| 25 | reached / reached | reached / reached | reached / reached |
| 26 | reached / reached | reached / reached | stuck / reached |
| 27 | reached / reached | reached / reached | reached / reached |
| 28 | reached / reached | reached / reached | reached / reached |
| 29 | reached / reached | reached / reached | reached / reached |
| 30 | reached / reached | reached / reached | reached / reached |
| 31 | reached / reached | reached / reached | stuck / reached |
| 32 | reached / reached | reached / reached | reached / reached |
| 33 | reached / reached | reached / reached | timeout / reached |
| 34 | reached / reached | reached / reached | reached / reached |
| 35 | reached / reached | reached / reached | reached / reached |
| 36 | reached / reached | reached / reached | stuck / timeout |
| 37 | reached / reached | reached / reached | reached / reached |
| 38 | reached / reached | reached / reached | reached / reached |
| 39 | reached / reached | reached / reached | reached / reached |
| 40 | reached / reached | reached / reached | stuck / stuck |
| 41 | reached / reached | reached / reached | reached / reached |
| 42 | reached / reached | reached / reached | reached / stuck |
| 43 | reached / reached | reached / reached | reached / reached |
| 44 | reached / reached | reached / reached | stuck / stuck |
| 45 | reached / reached | reached / reached | reached / reached |
| 46 | reached / reached | reached / reached | timeout / reached |
| 47 | reached / reached | reached / reached | reached / reached |
| 48 | reached / reached | reached / reached | reached / reached |
| 49 | reached / reached | reached / reached | reached / reached |
