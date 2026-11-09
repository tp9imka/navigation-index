`python run_kill.py --layouts 100 --seed 2 --workers 14 --tag kill_e --arms F2,F3,F4@eps_m=0.2,F5 --cases none,jump,bias,dropout --unsensed on` (synthetic), wall 157.7 s, 1800 runs, 14 workers

## Unsensed obstacles on

Unsensed obstacles placed: 200 in 100 layouts (per layout min 2, max 2).

| arm | case | layouts | collision % | of which unsensed | reached % | stuck % | of which in hover | timeout % | intervention fraction | median min clearance m | median time to goal s | median max pose err m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F2 | none | 100 | 0.0 | 0 of 0 | 63.0 | 37.0 | - | 0.0 | 0.247 | 0.634 | 20.82 | 0.354 |
| F2 | jump | 100 | 14.0 | 14 of 14 | 41.0 | 45.0 | - | 0.0 | 0.2714 | 0.533 | 21.12 | 0.646 |
| F2 | bias | 100 | 3.0 | 3 of 3 | 33.0 | 64.0 | - | 0.0 | 0.2563 | 0.597 | 20.28 | 0.606 |
| F2 | dropout | 100 | 1.0 | 1 of 1 | 63.0 | 36.0 | - | 0.0 | 0.2556 | 0.619 | 20.68 | 0.376 |
| F3 | none | 100 | 0.0 | 0 of 0 | 62.0 | 38.0 | - | 0.0 | 0.3351 | 0.65 | 20.52 | 0.35 |
| F3 | jump | 100 | 9.0 | 8 of 9 | 42.0 | 49.0 | - | 0.0 | 0.362 | 0.56 | 21.01 | 0.648 |
| F3 | bias | 100 | 0.0 | 0 of 0 | 32.0 | 68.0 | - | 0.0 | 0.3381 | 0.618 | 20.3 | 0.589 |
| F3 | dropout | 100 | 1.0 | 1 of 1 | 65.0 | 34.0 | - | 0.0 | 0.3321 | 0.643 | 20.6 | 0.376 |
| F4@eps_m=0.2 | none | 100 | 0.0 | 0 of 0 | 57.0 | 43.0 | - | 0.0 | 0.526 | 0.9 | 20.9 | 0.35 |
| F4@eps_m=0.2 | jump | 100 | 0.0 | 0 of 0 | 36.0 | 64.0 | - | 0.0 | 0.5419 | 0.827 | 20.65 | 0.628 |
| F4@eps_m=0.2 | bias | 100 | 0.0 | 0 of 0 | 32.0 | 68.0 | - | 0.0 | 0.5282 | 0.896 | 20.65 | 0.579 |
| F4@eps_m=0.2 | dropout | 100 | 0.0 | 0 of 0 | 57.0 | 43.0 | - | 0.0 | 0.5257 | 0.894 | 20.98 | 0.386 |
| F5 | none | 100 | 0.0 | 0 of 0 | 63.0 | 37.0 | 0 | 0.0 | 0.3541 | 0.653 | 21.08 | 0.371 |
| F5 | jump | 100 | 2.0 | 2 of 2 | 26.0 | 72.0 | 39 | 0.0 | 0.5494 | 0.678 | 21.72 | 0.635 |
| F5 | bias | 100 | 0.0 | 0 of 0 | 34.0 | 66.0 | 13 | 0.0 | 0.4036 | 0.683 | 20.84 | 0.586 |
| F5 | dropout | 100 | 0.0 | 0 of 0 | 66.0 | 34.0 | 6 | 0.0 | 0.4237 | 0.654 | 21.79 | 0.372 |
| F5 | uwb_nlos | 100 | 0.0 | 0 of 0 | 53.0 | 47.0 | 7 | 0.0 | 0.5593 | 0.728 | 24.98 | 0.374 |
| F5 | both | 100 | 0.0 | 0 of 0 | 31.0 | 69.0 | 27 | 0.0 | 0.6139 | 0.717 | 26.54 | 0.658 |

Map-barrier diagnostics (F3, F4, F5; for F5 the margin column is the PL):

| arm | case | map row active, fraction of steps | slack used, fraction of steps | runs with slack | mean k*sigma + gamma at nearest obstacle m | max k*sigma + gamma m | max gamma m |
|---|---|---|---|---|---|---|---|
| F3 | none | 0.096 | 0.0 | 0 | 0.397 | 0.9205 | 0.0103 |
| F3 | jump | 0.1021 | 0.0004 | 1 | 0.4003 | 0.926 | 0.0094 |
| F3 | bias | 0.0955 | 0.0002 | 1 | 0.4158 | 0.9466 | 0.0103 |
| F3 | dropout | 0.0895 | 0.0 | 0 | 0.3692 | 0.8634 | 0.0698 |
| F4@eps_m=0.2 | none | 0.4145 | 0.0169 | 97 | - | - | - |
| F4@eps_m=0.2 | jump | 0.4108 | 0.0231 | 97 | - | - | - |
| F4@eps_m=0.2 | bias | 0.397 | 0.016 | 93 | - | - | - |
| F4@eps_m=0.2 | dropout | 0.415 | 0.0161 | 98 | - | - | - |
| F5 | none | 0.0553 | 0.0 | 0 | 0.4445 | 0.7297 | 0.0 |
| F5 | jump | 0.0552 | 0.0 | 0 | 0.4473 | 0.727 | 0.0 |
| F5 | bias | 0.0601 | 0.0 | 0 | 0.4583 | 0.7273 | 0.0 |
| F5 | dropout | 0.0552 | 0.0 | 0 | 0.4291 | 0.7022 | 0.0 |
| F5 | uwb_nlos | 0.0868 | 0.0 | 0 | 0.5343 | 1.8219 | 0.0 |
| F5 | both | 0.1024 | 0.0 | 0 | 0.5423 | 1.7503 | 0.0 |

Integrity monitor and hover diagnostics (F5), scored on truth at every monitor epoch:

| arm | case | monitor epochs | PL available % | PL breaches (true err > PL) | max err / PL | wrong-exclusion epochs (runs) | ambiguous epochs % | hover steps % | runs with hover | speed-cap steps % | mean PL m | max PL m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F5 | none | 24405 | 100.0 | 0 | 0.5059 | 0 (0) | 0.0 | 0.02 | 1 | 6.43 | 0.4427 | 0.7297 |
| F5 | jump | 22562 | 83.25 | 0 | 0.8123 | 0 (0) | 16.75 | 20.62 | 62 | 5.64 | 0.4435 | 0.727 |
| F5 | bias | 26575 | 96.86 | 0 | 0.731 | 0 (0) | 3.14 | 4.17 | 16 | 6.05 | 0.4558 | 0.7273 |
| F5 | dropout | 23754 | 98.03 | 0 | 0.6744 | 0 (0) | 1.97 | 3.66 | 12 | 10.3 | 0.4266 | 0.7022 |
| F5 | uwb_nlos | 28330 | 93.83 | 0 | 0.8604 | 0 (0) | 6.17 | 10.32 | 50 | 21.18 | 0.538 | 1.8979 |
| F5 | both | 29392 | 87.54 | 42 | 1.1664 | 82 (6) | 12.46 | 17.58 | 63 | 20.59 | 0.5484 | 1.9241 |
