`python run_stalemap.py --layouts 100 --seed 2 --workers 14` (synthetic), wall 303.2 s, 14 workers, arm64 CPython 3.11.15 numpy 2.4.6 scipy 1.17.1

| rung | layouts flown | obstacles removed / added (total) | median changed map cells | other |
|---|---|---|---|---|
| a_exact | 100 | 0 / 0 | 0 | - |
| b_removed | 100 | 145 / 0 | 286 | - |
| c_added | 100 | 0 / 152 | 115 | - |
| d_shift01 | 100 | 0 / 0 | 348 | resampled for a free path: 0 layouts |
| d_shift02 | 100 | 0 / 0 | 675 | resampled for a free path: 0 layouts |
| e_selfmap | 99 | 0 / 0 | - | outbound {'reached': 59, 'collision': 0, 'stuck': 41, 'timeout': 0}; used 99 of 100; outbound end est err median 0.339 m, run max median 0.417 m; map occupied cells >0.2 m from a real surface: median 0.142 of cells |

| rung | fault | arm | runs | reached % | collision % | of which: move into unmapped / other unmapped / mapped | stuck % | relocs accepted | wrong commits (> 0.5 m) truth / map frame | runs with a wrong commit (map frame) | still hovering at end | recover s median / p95 / max | moves flown |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| a_exact | none | truth | 100 | 100.0 | 0.0 | 0 / 0 / 0 | 0.0 | - | - | - | - | - | - |
| a_exact | dropout | (b) single | 100 | 100.0 | 0.0 | 0 / 0 / 0 | 0.0 | 462 | 8 / 8 | 5 | 2 | 0.2 / 0.2 / 0.2 | - |
| a_exact | dropout | (c) multi | 100 | 84.0 | 0.0 | 0 / 0 / 0 | 16.0 | 413 | 0 / 0 | 0 | 18 | 0.4 / 0.4 / 5.9 | - |
| a_exact | dropout | (f) multi_ig | 100 | 100.0 | 0.0 | 0 / 0 / 0 | 0.0 | 457 | 0 / 0 | 0 | 3 | 0.4 / 0.82 / 9.5 | 27 |
| a_exact | jump | (b) single | 100 | 100.0 | 0.0 | 0 / 0 / 0 | 0.0 | 399 | 7 / 7 | 5 | 0 | 0.2 / 0.2 / 0.2 | - |
| a_exact | jump | (c) multi | 100 | 94.0 | 0.0 | 0 / 0 / 0 | 6.0 | 330 | 0 / 0 | 0 | 7 | 0.4 / 0.4 / 3.4 | - |
| a_exact | jump | (f) multi_ig | 100 | 100.0 | 0.0 | 0 / 0 / 0 | 0.0 | 347 | 0 / 0 | 0 | 2 | 0.4 / 0.4 / 7.7 | 11 |
| b_removed | none | truth | 100 | 100.0 | 0.0 | 0 / 0 / 0 | 0.0 | - | - | - | - | - | - |
| b_removed | dropout | (b) single | 100 | 100.0 | 0.0 | 0 / 0 / 0 | 0.0 | 469 | 8 / 8 | 7 | 1 | 0.2 / 0.2 / 0.2 | - |
| b_removed | dropout | (c) multi | 100 | 71.0 | 0.0 | 0 / 0 / 0 | 29.0 | 394 | 1 / 1 | 1 | 29 | 0.4 / 0.5 / 8.6 | - |
| b_removed | dropout | (f) multi_ig | 100 | 99.0 | 0.0 | 0 / 0 / 0 | 1.0 | 483 | 0 / 0 | 0 | 0 | 0.4 / 2.29 / 14.0 | 47 |
| b_removed | jump | (b) single | 100 | 100.0 | 0.0 | 0 / 0 / 0 | 0.0 | 394 | 6 / 6 | 5 | 5 | 0.2 / 0.2 / 0.2 | - |
| b_removed | jump | (c) multi | 100 | 85.0 | 0.0 | 0 / 0 / 0 | 15.0 | 303 | 0 / 0 | 0 | 17 | 0.4 / 0.4 / 5.5 | - |
| b_removed | jump | (f) multi_ig | 100 | 99.0 | 0.0 | 0 / 0 / 0 | 1.0 | 346 | 0 / 0 | 0 | 2 | 0.4 / 1.22 / 12.8 | 25 |
| c_added | none | truth | 100 | 100.0 | 0.0 | 0 / 0 / 0 | 0.0 | - | - | - | - | - | - |
| c_added | dropout | (b) single | 100 | 98.0 | 2.0 | 0 / 0 / 2 | 0.0 | 592 | 57 / 57 | 19 | 2 | 0.2 / 0.2 / 0.2 | - |
| c_added | dropout | (c) multi | 100 | 65.0 | 0.0 | 0 / 0 / 0 | 35.0 | 396 | 4 / 4 | 4 | 36 | 0.4 / 0.4 / 6.7 | - |
| c_added | dropout | (f) multi_ig | 100 | 89.0 | 7.0 | 2 / 4 / 1 | 3.0 | 501 | 16 / 16 | 8 | 9 | 0.4 / 3.5 / 12.1 | 91 |
| c_added | jump | (b) single | 100 | 99.0 | 1.0 | 0 / 0 / 1 | 0.0 | 571 | 62 / 62 | 14 | 4 | 0.2 / 0.2 / 0.2 | - |
| c_added | jump | (c) multi | 100 | 73.0 | 0.0 | 0 / 0 / 0 | 27.0 | 337 | 7 / 7 | 6 | 29 | 0.4 / 0.6 / 9.0 | - |
| c_added | jump | (f) multi_ig | 100 | 88.0 | 7.0 | 2 / 4 / 1 | 5.0 | 417 | 21 / 21 | 10 | 12 | 0.4 / 3.12 / 17.4 | 80 |
| d_shift01 | none | truth | 100 | 100.0 | 0.0 | 0 / 0 / 0 | 0.0 | - | - | - | - | - | - |
| d_shift01 | dropout | (b) single | 100 | 100.0 | 0.0 | 0 / 0 / 0 | 0.0 | 489 | 4 / 4 | 4 | 1 | 0.2 / 0.2 / 0.2 | - |
| d_shift01 | dropout | (c) multi | 100 | 80.0 | 0.0 | 0 / 0 / 0 | 20.0 | 419 | 0 / 0 | 0 | 25 | 0.4 / 0.4 / 1.3 | - |
| d_shift01 | dropout | (f) multi_ig | 100 | 100.0 | 0.0 | 0 / 0 / 0 | 0.0 | 478 | 0 / 0 | 0 | 5 | 0.4 / 0.71 / 9.3 | 25 |
| d_shift01 | jump | (b) single | 100 | 100.0 | 0.0 | 0 / 0 / 0 | 0.0 | 426 | 6 / 6 | 5 | 2 | 0.2 / 0.2 / 0.2 | - |
| d_shift01 | jump | (c) multi | 100 | 97.0 | 0.0 | 0 / 0 / 0 | 3.0 | 391 | 3 / 3 | 3 | 5 | 0.4 / 0.4 / 3.1 | - |
| d_shift01 | jump | (f) multi_ig | 100 | 100.0 | 0.0 | 0 / 0 / 0 | 0.0 | 400 | 2 / 2 | 2 | 2 | 0.4 / 0.4 / 2.9 | 7 |
| d_shift02 | none | truth | 100 | 100.0 | 0.0 | 0 / 0 / 0 | 0.0 | - | - | - | - | - | - |
| d_shift02 | dropout | (b) single | 100 | 100.0 | 0.0 | 0 / 0 / 0 | 0.0 | 558 | 16 / 16 | 12 | 1 | 0.2 / 0.2 / 0.2 | - |
| d_shift02 | dropout | (c) multi | 100 | 65.0 | 0.0 | 0 / 0 / 0 | 35.0 | 416 | 9 / 9 | 6 | 35 | 0.4 / 0.6 / 8.3 | - |
| d_shift02 | dropout | (f) multi_ig | 100 | 97.0 | 0.0 | 0 / 0 / 0 | 3.0 | 524 | 10 / 10 | 7 | 3 | 0.4 / 2.28 / 13.2 | 57 |
| d_shift02 | jump | (b) single | 100 | 100.0 | 0.0 | 0 / 0 / 0 | 0.0 | 526 | 17 / 17 | 13 | 2 | 0.2 / 0.2 / 0.2 | - |
| d_shift02 | jump | (c) multi | 100 | 82.0 | 0.0 | 0 / 0 / 0 | 18.0 | 424 | 7 / 7 | 5 | 18 | 0.4 / 0.5 / 6.5 | - |
| d_shift02 | jump | (f) multi_ig | 100 | 97.0 | 0.0 | 0 / 0 / 0 | 3.0 | 468 | 6 / 6 | 5 | 2 | 0.4 / 1.56 / 12.1 | 39 |
| e_selfmap | none | truth | 99 | 92.9 | 6.1 | 0 / 6 / 0 | 1.0 | - | - | - | - | - | - |
| e_selfmap | dropout | (b) single | 99 | 98.0 | 0.0 | 0 / 0 / 0 | 2.0 | 469 | 118 / 71 | 12 | 0 | 0.2 / 0.2 / 0.2 | - |
| e_selfmap | dropout | (c) multi | 99 | 71.7 | 1.0 | 0 / 0 / 1 | 27.3 | 332 | 54 / 10 | 6 | 25 | 0.4 / 0.4 / 2.5 | - |
| e_selfmap | dropout | (f) multi_ig | 99 | 93.9 | 2.0 | 0 / 1 / 1 | 4.0 | 387 | 60 / 13 | 9 | 1 | 0.4 / 2.67 / 15.8 | 51 |
| e_selfmap | jump | (b) single | 99 | 97.0 | 0.0 | 0 / 0 / 0 | 2.0 | 526 | 202 / 166 | 14 | 1 | 0.2 / 0.2 / 0.2 | - |
| e_selfmap | jump | (c) multi | 99 | 81.8 | 0.0 | 0 / 0 / 0 | 18.2 | 278 | 39 / 11 | 7 | 16 | 0.4 / 0.4 / 3.1 | - |
| e_selfmap | jump | (f) multi_ig | 99 | 92.9 | 2.0 | 0 / 1 / 1 | 5.1 | 303 | 43 / 14 | 11 | 4 | 0.4 / 1.69 / 8.5 | 35 |
