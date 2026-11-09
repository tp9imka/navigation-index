`python run_kill.py --layouts 50 --seed 1 --family u_trap --workers 14 --tag kill_e_u_trap --arms F2,F3,F4@eps_m=0.2,F5 --cases none,jump,bias,dropout --unsensed on` (synthetic), wall 81.0 s, 900 runs, 14 workers

## Unsensed obstacles on

Unsensed obstacles placed: 100 in 50 layouts (per layout min 2, max 2).

| arm | case | layouts | collision % | of which unsensed | reached % | stuck % | of which in hover | timeout % | intervention fraction | median min clearance m | median time to goal s | median max pose err m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F2 | none | 50 | 0.0 | 0 of 0 | 78.0 | 22.0 | - | 0.0 | 0.2239 | 0.744 | 21.32 | 0.314 |
| F2 | jump | 50 | 8.0 | 4 of 4 | 34.0 | 58.0 | - | 0.0 | 0.1793 | 0.556 | 21.54 | 0.641 |
| F2 | bias | 50 | 6.0 | 3 of 3 | 34.0 | 60.0 | - | 0.0 | 0.2196 | 0.712 | 21.1 | 0.602 |
| F2 | dropout | 50 | 2.0 | 1 of 1 | 76.0 | 22.0 | - | 0.0 | 0.2068 | 0.704 | 21.37 | 0.364 |
| F3 | none | 50 | 0.0 | 0 of 0 | 78.0 | 22.0 | - | 0.0 | 0.2588 | 0.731 | 21.32 | 0.313 |
| F3 | jump | 50 | 4.0 | 2 of 2 | 32.0 | 64.0 | - | 0.0 | 0.221 | 0.562 | 21.48 | 0.633 |
| F3 | bias | 50 | 6.0 | 3 of 3 | 32.0 | 62.0 | - | 0.0 | 0.2467 | 0.712 | 21.25 | 0.603 |
| F3 | dropout | 50 | 2.0 | 1 of 1 | 74.0 | 24.0 | - | 0.0 | 0.2408 | 0.708 | 21.46 | 0.351 |
| F4@eps_m=0.2 | none | 50 | 0.0 | 0 of 0 | 76.0 | 24.0 | - | 0.0 | 0.4353 | 0.875 | 22.09 | 0.319 |
| F4@eps_m=0.2 | jump | 50 | 0.0 | 0 of 0 | 40.0 | 60.0 | - | 0.0 | 0.4077 | 0.802 | 23.34 | 0.613 |
| F4@eps_m=0.2 | bias | 50 | 0.0 | 0 of 0 | 36.0 | 64.0 | - | 0.0 | 0.4626 | 0.853 | 21.9 | 0.651 |
| F4@eps_m=0.2 | dropout | 50 | 0.0 | 0 of 0 | 74.0 | 26.0 | - | 0.0 | 0.4346 | 0.874 | 22.12 | 0.363 |
| F5 | none | 50 | 0.0 | 0 of 0 | 76.0 | 24.0 | 0 | 0.0 | 0.3045 | 0.734 | 21.44 | 0.305 |
| F5 | jump | 50 | 0.0 | 0 of 0 | 10.0 | 90.0 | 22 | 0.0 | 0.4782 | 0.693 | 22.7 | 0.645 |
| F5 | bias | 50 | 0.0 | 0 of 0 | 32.0 | 68.0 | 7 | 0.0 | 0.3474 | 0.737 | 21.24 | 0.607 |
| F5 | dropout | 50 | 0.0 | 0 of 0 | 76.0 | 24.0 | 2 | 0.0 | 0.3582 | 0.756 | 21.96 | 0.366 |
| F5 | uwb_nlos | 50 | 0.0 | 0 of 0 | 74.0 | 26.0 | 3 | 0.0 | 0.5039 | 0.798 | 24.0 | 0.301 |
| F5 | both | 50 | 0.0 | 0 of 0 | 28.0 | 72.0 | 14 | 0.0 | 0.5649 | 0.804 | 23.64 | 0.629 |

Map-barrier diagnostics (F3, F4, F5; for F5 the margin column is the PL):

| arm | case | map row active, fraction of steps | slack used, fraction of steps | runs with slack | mean k*sigma + gamma at nearest obstacle m | max k*sigma + gamma m | max gamma m |
|---|---|---|---|---|---|---|---|
| F3 | none | 0.0434 | 0.0 | 0 | 0.3474 | 0.7844 | 0.009 |
| F3 | jump | 0.0506 | 0.0 | 0 | 0.3744 | 0.7688 | 0.0084 |
| F3 | bias | 0.0397 | 0.0 | 0 | 0.3689 | 0.8217 | 0.009 |
| F3 | dropout | 0.0408 | 0.0 | 0 | 0.3336 | 0.7516 | 0.0721 |
| F4@eps_m=0.2 | none | 0.3697 | 0.0076 | 48 | - | - | - |
| F4@eps_m=0.2 | jump | 0.3261 | 0.0099 | 49 | - | - | - |
| F4@eps_m=0.2 | bias | 0.3314 | 0.0072 | 47 | - | - | - |
| F4@eps_m=0.2 | dropout | 0.3663 | 0.0062 | 48 | - | - | - |
| F5 | none | 0.0465 | 0.0 | 0 | 0.439 | 0.7129 | 0.0 |
| F5 | jump | 0.0373 | 0.0 | 0 | 0.465 | 0.6986 | 0.0 |
| F5 | bias | 0.0504 | 0.0 | 0 | 0.4571 | 0.7117 | 0.0 |
| F5 | dropout | 0.0469 | 0.0 | 0 | 0.429 | 0.6922 | 0.0 |
| F5 | uwb_nlos | 0.1034 | 0.0 | 0 | 0.543 | 1.7017 | 0.0 |
| F5 | both | 0.095 | 0.0 | 0 | 0.5513 | 2.0209 | 0.0 |

Integrity monitor and hover diagnostics (F5), scored on truth at every monitor epoch:

| arm | case | monitor epochs | PL available % | PL breaches (true err > PL) | max err / PL | wrong-exclusion epochs (runs) | ambiguous epochs % | hover steps % | runs with hover | speed-cap steps % | mean PL m | max PL m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F5 | none | 11882 | 100.0 | 0 | 0.4908 | 0 (0) | 0.0 | 0.0 | 0 | 4.21 | 0.4349 | 0.7129 |
| F5 | jump | 12783 | 83.86 | 0 | 0.7459 | 0 (0) | 16.14 | 22.14 | 32 | 3.28 | 0.4541 | 0.6986 |
| F5 | bias | 13589 | 95.21 | 0 | 0.5544 | 0 (0) | 4.79 | 5.47 | 8 | 3.17 | 0.4505 | 0.7117 |
| F5 | dropout | 11787 | 98.69 | 0 | 0.729 | 0 (0) | 1.31 | 1.74 | 3 | 9.31 | 0.4245 | 0.6922 |
| F5 | uwb_nlos | 13077 | 96.2 | 0 | 0.6241 | 0 (0) | 3.8 | 6.04 | 12 | 25.92 | 0.5337 | 1.7017 |
| F5 | both | 14770 | 89.17 | 64 | 1.3317 | 85 (5) | 10.83 | 15.31 | 23 | 21.87 | 0.54 | 2.0209 |
