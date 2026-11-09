`python run_kill.py --layouts 100 --seed 1 --workers 14 --tag kill_e --arms F2,F3,F4@eps_m=0.2,F5 --cases none,jump,bias,dropout --unsensed on` (synthetic), unsensed on, wall 137.8 s for the whole command

Unsensed obstacles placed: 200 in 100 layouts (per layout min 2, max 2).

| arm | case | layouts | collision % | of which unsensed | reached % | stuck % | of which in hover | timeout % | intervention fraction | median min clearance m | median time to goal s | median max pose err m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F2 | none | 100 | 2.0 | 2 of 2 | 64.0 | 34.0 | - | 0.0 | 0.2201 | 0.635 | 20.22 | 0.347 |
| F2 | jump | 100 | 12.0 | 12 of 12 | 34.0 | 54.0 | - | 0.0 | 0.2138 | 0.492 | 20.7 | 0.685 |
| F2 | bias | 100 | 5.0 | 5 of 5 | 32.0 | 63.0 | - | 0.0 | 0.2519 | 0.597 | 20.07 | 0.605 |
| F2 | dropout | 100 | 1.0 | 1 of 1 | 59.0 | 40.0 | - | 0.0 | 0.2267 | 0.6 | 20.38 | 0.422 |
| F3 | none | 100 | 0.0 | 0 of 0 | 64.0 | 36.0 | - | 0.0 | 0.3129 | 0.663 | 20.28 | 0.348 |
| F3 | jump | 100 | 7.0 | 7 of 7 | 32.0 | 61.0 | - | 0.0 | 0.306 | 0.608 | 20.54 | 0.684 |
| F3 | bias | 100 | 2.0 | 2 of 2 | 32.0 | 66.0 | - | 0.0 | 0.323 | 0.65 | 20.1 | 0.615 |
| F3 | dropout | 100 | 1.0 | 1 of 1 | 57.0 | 42.0 | - | 0.0 | 0.2972 | 0.651 | 20.06 | 0.422 |
| F4@eps_m=0.2 | none | 100 | 0.0 | 0 of 0 | 60.0 | 40.0 | - | 0.0 | 0.5014 | 0.883 | 20.86 | 0.333 |
| F4@eps_m=0.2 | jump | 100 | 3.0 | 3 of 3 | 39.0 | 58.0 | - | 0.0 | 0.5237 | 0.842 | 20.8 | 0.649 |
| F4@eps_m=0.2 | bias | 100 | 0.0 | 0 of 0 | 32.0 | 68.0 | - | 0.0 | 0.5122 | 0.867 | 20.66 | 0.595 |
| F4@eps_m=0.2 | dropout | 100 | 0.0 | 0 of 0 | 59.0 | 41.0 | - | 0.0 | 0.5143 | 0.889 | 21.24 | 0.414 |
| F5 | none | 100 | 0.0 | 0 of 0 | 67.0 | 33.0 | 0 | 0.0 | 0.3594 | 0.681 | 21.16 | 0.354 |
| F5 | jump | 100 | 3.0 | 3 of 3 | 15.0 | 82.0 | 42 | 0.0 | 0.5212 | 0.687 | 21.24 | 0.654 |
| F5 | bias | 100 | 0.0 | 0 of 0 | 31.0 | 69.0 | 13 | 0.0 | 0.3787 | 0.687 | 20.98 | 0.607 |
| F5 | dropout | 100 | 0.0 | 0 of 0 | 57.0 | 43.0 | 8 | 0.0 | 0.4234 | 0.696 | 21.18 | 0.423 |
| F5 | uwb_nlos | 100 | 0.0 | 0 of 0 | 56.0 | 44.0 | 7 | 0.0 | 0.5803 | 0.722 | 25.06 | 0.352 |
| F5 | both | 100 | 0.0 | 0 of 0 | 24.0 | 76.0 | 30 | 0.0 | 0.6007 | 0.786 | 23.93 | 0.59 |

Map-barrier diagnostics (F3, F4, F5; for F5 the margin column is the PL):

| arm | case | map row active, fraction of steps | slack used, fraction of steps | runs with slack | mean k*sigma + gamma at nearest obstacle m | max k*sigma + gamma m | max gamma m |
|---|---|---|---|---|---|---|---|
| F3 | none | 0.1005 | 0.0001 | 1 | 0.3962 | 0.9426 | 0.0088 |
| F3 | jump | 0.1015 | 0.0 | 0 | 0.4096 | 0.9426 | 0.0091 |
| F3 | bias | 0.097 | 0.0001 | 1 | 0.417 | 0.9263 | 0.0089 |
| F3 | dropout | 0.08 | 0.0001 | 1 | 0.3718 | 0.9201 | 0.0707 |
| F4@eps_m=0.2 | none | 0.4114 | 0.0128 | 94 | - | - | - |
| F4@eps_m=0.2 | jump | 0.3941 | 0.0156 | 91 | - | - | - |
| F4@eps_m=0.2 | bias | 0.3798 | 0.0159 | 95 | - | - | - |
| F4@eps_m=0.2 | dropout | 0.4112 | 0.0133 | 94 | - | - | - |
| F5 | none | 0.0677 | 0.0 | 0 | 0.4418 | 0.7232 | 0.0 |
| F5 | jump | 0.0502 | 0.0 | 0 | 0.4592 | 0.7199 | 0.0 |
| F5 | bias | 0.0526 | 0.0 | 0 | 0.4644 | 0.7223 | 0.0 |
| F5 | dropout | 0.0666 | 0.0 | 0 | 0.4398 | 0.7125 | 0.0 |
| F5 | uwb_nlos | 0.1012 | 0.0037 | 1 | 0.5421 | 1.8345 | 0.0 |
| F5 | both | 0.0774 | 0.0001 | 1 | 0.551 | 1.9541 | 0.0 |

Integrity monitor and hover diagnostics (F5), scored on truth at every monitor epoch:

| arm | case | monitor epochs | PL available % | PL breaches (true err > PL) | max err / PL | wrong-exclusion epochs (runs) | ambiguous epochs % | hover steps % | runs with hover | speed-cap steps % | mean PL m | max PL m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F5 | none | 23753 | 100.0 | 0 | 0.48 | 0 (0) | 0.0 | 0.0 | 0 | 7.49 | 0.4396 | 0.7232 |
| F5 | jump | 23074 | 83.32 | 0 | 0.7776 | 0 (0) | 16.68 | 21.91 | 68 | 5.17 | 0.4549 | 0.7199 |
| F5 | bias | 26430 | 96.24 | 0 | 0.6485 | 0 (0) | 3.76 | 4.4 | 15 | 6.26 | 0.4609 | 0.7223 |
| F5 | dropout | 24121 | 97.0 | 0 | 0.7074 | 0 (0) | 3.0 | 4.0 | 10 | 11.24 | 0.4368 | 0.7125 |
| F5 | uwb_nlos | 27091 | 92.53 | 0 | 0.8294 | 0 (0) | 7.47 | 11.15 | 45 | 23.79 | 0.5496 | 1.8422 |
| F5 | both | 28532 | 87.23 | 92 | 1.4013 | 134 (10) | 12.77 | 17.16 | 53 | 21.87 | 0.5494 | 1.9578 |
