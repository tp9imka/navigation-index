`python run_kill.py --layouts 50 --seed 1 --family narrow_gap --workers 14 --tag kill_e_narrow_gap --arms F2,F3,F4@eps_m=0.2,F5 --cases none,jump,bias,dropout --unsensed on` (synthetic), unsensed on, wall 168.0 s for the whole command

Unsensed obstacles placed: 100 in 50 layouts (per layout min 2, max 2).

| arm | case | layouts | collision % | of which unsensed | reached % | stuck % | of which in hover | timeout % | intervention fraction | median min clearance m | median time to goal s | median max pose err m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F2 | none | 50 | 0.0 | 0 of 0 | 0.0 | 100.0 | - | 0.0 | 0.614 | 0.481 | - | 0.205 |
| F2 | jump | 50 | 14.0 | 6 of 7 | 0.0 | 86.0 | - | 0.0 | 0.5324 | 0.466 | - | 0.648 |
| F2 | bias | 50 | 8.0 | 4 of 4 | 0.0 | 92.0 | - | 0.0 | 0.5815 | 0.492 | - | 0.552 |
| F2 | dropout | 50 | 6.0 | 3 of 3 | 0.0 | 94.0 | - | 0.0 | 0.5873 | 0.487 | - | 0.29 |
| F3 | none | 50 | 0.0 | 0 of 0 | 0.0 | 100.0 | - | 0.0 | 0.6533 | 0.52 | - | 0.205 |
| F3 | jump | 50 | 12.0 | 6 of 6 | 0.0 | 88.0 | - | 0.0 | 0.5972 | 0.498 | - | 0.648 |
| F3 | bias | 50 | 4.0 | 2 of 2 | 0.0 | 96.0 | - | 0.0 | 0.6448 | 0.53 | - | 0.549 |
| F3 | dropout | 50 | 4.0 | 2 of 2 | 0.0 | 96.0 | - | 0.0 | 0.6275 | 0.518 | - | 0.289 |
| F4@eps_m=0.2 | none | 50 | 0.0 | 0 of 0 | 0.0 | 100.0 | - | 0.0 | 0.8239 | 0.891 | - | 0.238 |
| F4@eps_m=0.2 | jump | 50 | 2.0 | 1 of 1 | 0.0 | 98.0 | - | 0.0 | 0.8221 | 0.839 | - | 0.64 |
| F4@eps_m=0.2 | bias | 50 | 0.0 | 0 of 0 | 0.0 | 100.0 | - | 0.0 | 0.823 | 0.883 | - | 0.555 |
| F4@eps_m=0.2 | dropout | 50 | 0.0 | 0 of 0 | 0.0 | 100.0 | - | 0.0 | 0.825 | 0.895 | - | 0.277 |
| F5 | none | 50 | 0.0 | 0 of 0 | 0.0 | 100.0 | 0 | 0.0 | 0.6797 | 0.568 | - | 0.21 |
| F5 | jump | 50 | 4.0 | 2 of 2 | 0.0 | 96.0 | 26 | 0.0 | 0.6832 | 0.6 | - | 0.636 |
| F5 | bias | 50 | 0.0 | 0 of 0 | 0.0 | 100.0 | 12 | 0.0 | 0.6807 | 0.552 | - | 0.573 |
| F5 | dropout | 50 | 0.0 | 0 of 0 | 0.0 | 100.0 | 2 | 0.0 | 0.6986 | 0.571 | - | 0.282 |
| F5 | uwb_nlos | 50 | 0.0 | 0 of 0 | 0.0 | 100.0 | 4 | 0.0 | 0.7825 | 0.63 | - | 0.214 |
| F5 | both | 50 | 0.0 | 0 of 0 | 0.0 | 100.0 | 16 | 0.0 | 0.7877 | 0.637 | - | 0.565 |

Map-barrier diagnostics (F3, F4, F5; for F5 the margin column is the PL):

| arm | case | map row active, fraction of steps | slack used, fraction of steps | runs with slack | mean k*sigma + gamma at nearest obstacle m | max k*sigma + gamma m | max gamma m |
|---|---|---|---|---|---|---|---|
| F3 | none | 0.1094 | 0.0 | 0 | 0.2959 | 0.6955 | 0.0092 |
| F3 | jump | 0.1479 | 0.0014 | 1 | 0.3052 | 0.6983 | 0.0092 |
| F3 | bias | 0.14 | 0.0 | 0 | 0.3009 | 0.6986 | 0.01 |
| F3 | dropout | 0.1106 | 0.0 | 0 | 0.2767 | 0.7541 | 0.0728 |
| F4@eps_m=0.2 | none | 0.5565 | 0.0146 | 49 | - | - | - |
| F4@eps_m=0.2 | jump | 0.6297 | 0.025 | 47 | - | - | - |
| F4@eps_m=0.2 | bias | 0.5527 | 0.0126 | 48 | - | - | - |
| F4@eps_m=0.2 | dropout | 0.5637 | 0.0125 | 47 | - | - | - |
| F5 | none | 0.1028 | 0.0 | 0 | 0.3676 | 0.5211 | 0.0 |
| F5 | jump | 0.0529 | 0.0 | 0 | 0.3789 | 0.6421 | 0.0 |
| F5 | bias | 0.091 | 0.0 | 0 | 0.3707 | 0.5202 | 0.0 |
| F5 | dropout | 0.0953 | 0.0 | 0 | 0.3625 | 0.5204 | 0.0 |
| F5 | uwb_nlos | 0.1725 | 0.0 | 0 | 0.4771 | 1.6707 | 0.0 |
| F5 | both | 0.1721 | 0.0003 | 1 | 0.4794 | 1.6754 | 0.0 |

Integrity monitor and hover diagnostics (F5), scored on truth at every monitor epoch:

| arm | case | monitor epochs | PL available % | PL breaches (true err > PL) | max err / PL | wrong-exclusion epochs (runs) | ambiguous epochs % | hover steps % | runs with hover | speed-cap steps % | mean PL m | max PL m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F5 | none | 11319 | 100.0 | 0 | 0.4668 | 0 (0) | 0.0 | 0.0 | 0 | 2.16 | 0.3664 | 0.5211 |
| F5 | jump | 10112 | 78.24 | 0 | 0.6547 | 0 (0) | 21.76 | 29.96 | 37 | 2.34 | 0.3778 | 0.6421 |
| F5 | bias | 11379 | 93.69 | 0 | 0.5821 | 0 (0) | 6.31 | 8.25 | 18 | 3.38 | 0.369 | 0.5202 |
| F5 | dropout | 11342 | 98.47 | 0 | 0.6811 | 0 (0) | 1.53 | 2.38 | 4 | 5.86 | 0.3615 | 0.5204 |
| F5 | uwb_nlos | 12531 | 95.44 | 0 | 0.6552 | 0 (0) | 4.56 | 6.47 | 14 | 15.32 | 0.4755 | 1.6707 |
| F5 | both | 12455 | 86.85 | 90 | 1.3322 | 111 (7) | 13.15 | 16.85 | 27 | 15.44 | 0.4791 | 1.6754 |
