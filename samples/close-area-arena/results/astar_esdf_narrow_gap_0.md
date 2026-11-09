`python -m planners.astar_esdf --layouts 50 --seed 0` from samples/close-area-arena (synthetic: simulated layouts, vehicle and sensor)

| planner | family | layouts | reached % | collision % | stuck % | timeout % | median time to goal s | median min clearance m | replans | plan median ms | plan p95 ms | fallback replans | no-path replans | wall s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| straight | narrow_gap | 50 | 0.0 | 0.0 | 100.0 | 0.0 | - | 0.371 | 0 | - | - | 0 | 0 | 3.1 |
| astar_esdf known_map | narrow_gap | 50 | 100.0 | 0.0 | 0.0 | 0.0 | 24.23 | 0.276 | 3115 | 3.85 | 39.08 | 272 | 0 | 37.5 |
| astar_esdf unknown_map | narrow_gap | 50 | 80.0 | 0.0 | 14.0 | 6.0 | 27.79 | 0.264 | 4664 | 37.18 | 64.54 | 128 | 0 | 181.9 |

Per run (outcome, min clearance m):

| run | straight | astar_esdf known_map | astar_esdf unknown_map |
|---|---|---|---|
| 0 | stuck 0.384 | reached 0.3252 | reached 0.2533 |
| 1 | stuck 0.3831 | reached 0.2388 | reached 0.1936 |
| 2 | stuck 0.3745 | reached 0.2404 | reached 0.2749 |
| 3 | stuck 0.3687 | reached 0.2691 | reached 0.2579 |
| 4 | stuck 0.3686 | reached 0.3522 | reached 0.292 |
| 5 | stuck 0.2417 | reached 0.3857 | reached 0.2669 |
| 6 | stuck 0.3613 | reached 0.2923 | reached 0.252 |
| 7 | stuck 0.2814 | reached 0.2752 | reached 0.2593 |
| 8 | stuck 0.3632 | reached 0.2752 | reached 0.2632 |
| 9 | stuck 0.3774 | reached 0.3049 | reached 0.2376 |
| 10 | stuck 0.3676 | reached 0.3001 | reached 0.2594 |
| 11 | stuck 0.3698 | reached 0.3432 | stuck 0.5816 |
| 12 | stuck 0.3801 | reached 0.2392 | reached 0.2867 |
| 13 | stuck 0.3677 | reached 0.3292 | reached 0.2419 |
| 14 | stuck 0.3706 | reached 0.2687 | reached 0.2651 |
| 15 | stuck 0.3697 | reached 0.2764 | reached 0.2718 |
| 16 | stuck 0.3705 | reached 0.2781 | reached 0.239 |
| 17 | stuck 0.383 | reached 0.2469 | stuck 0.2259 |
| 18 | stuck 0.3729 | reached 0.3108 | reached 0.2433 |
| 19 | stuck 0.3721 | reached 0.231 | reached 0.2651 |
| 20 | stuck 0.3756 | reached 0.3999 | reached 0.2321 |
| 21 | stuck 0.378 | reached 0.212 | timeout 0.2748 |
| 22 | stuck 0.3757 | reached 0.2859 | reached 0.2548 |
| 23 | stuck 0.3678 | reached 0.279 | reached 0.2761 |
| 24 | stuck 0.3688 | reached 0.2844 | reached 0.2745 |
| 25 | stuck 0.3844 | reached 0.2538 | reached 0.2808 |
| 26 | stuck 0.3802 | reached 0.3262 | stuck 0.6232 |
| 27 | stuck 0.3777 | reached 0.2328 | reached 0.2145 |
| 28 | stuck 0.3958 | reached 0.2965 | reached 0.2542 |
| 29 | stuck 0.2442 | reached 0.3137 | reached 0.3109 |
| 30 | stuck 0.3697 | reached 0.2536 | reached 0.2484 |
| 31 | stuck 0.3618 | reached 0.2695 | stuck 0.5468 |
| 32 | stuck 0.3795 | reached 0.1839 | reached 0.2035 |
| 33 | stuck 0.232 | reached 0.221 | timeout 0.3688 |
| 34 | stuck 0.3668 | reached 0.1992 | reached 0.2602 |
| 35 | stuck 0.4068 | reached 0.2843 | reached 0.277 |
| 36 | stuck 0.3691 | reached 0.2223 | stuck 0.2687 |
| 37 | stuck 0.3258 | reached 0.2836 | reached 0.291 |
| 38 | stuck 0.3698 | reached 0.2532 | reached 0.2615 |
| 39 | stuck 0.3812 | reached 0.3058 | reached 0.3054 |
| 40 | stuck 0.3698 | reached 0.2042 | stuck 0.2605 |
| 41 | stuck 0.3696 | reached 0.2342 | reached 0.2101 |
| 42 | stuck 0.3812 | reached 0.3232 | reached 0.2451 |
| 43 | stuck 0.3786 | reached 0.2599 | reached 0.2746 |
| 44 | stuck 0.3801 | reached 0.1911 | stuck 0.2528 |
| 45 | stuck 0.3819 | reached 0.2891 | reached 0.2823 |
| 46 | stuck 0.3831 | reached 0.2371 | timeout 0.1955 |
| 47 | stuck 0.3813 | reached 0.2803 | reached 0.2683 |
| 48 | stuck 0.3808 | reached 0.2757 | reached 0.2676 |
| 49 | stuck 0.2645 | reached 0.3044 | reached 0.3273 |

Plot: [astar_esdf_narrow_gap_0_run11.png](astar_esdf_narrow_gap_0_run11.png), run 11 (first run the unknown-map mode did not reach B, else run 0). Panels left to right: straight, astar_esdf known_map, astar_esdf unknown_map. Blue = truth path, green = last planned path, grey band = 0.15 m inflation, orange = stuck, magenta = collision, purple = timeout.


Notes (written by hand after the run, synthetic):

- Unknown-map failures: 7 stuck (runs 11, 17, 26, 31, 36, 40, 44) and 3 timeout (21, 33, 46), 0 collisions. No replan ended without a path. The planner treats the unseen wall as traversable, flies along it looking for a way through, sees more wall and turns back.
- "stuck" here is the scorer's displacement rule (< 0.2 m from the position 10 s earlier), not standstill. Re-running the 7 stuck layouts (same outcomes) gave 2.61-11.68 m of truth path in the last 10 s of each run: the vehicle had come back to where it was 10 s earlier. Timeouts are the same loops without an exact return.
- Fallback replans (no path at RADIUS + TRACK_MARGIN = 0.25 m, path found at RADIUS = 0.15 m) happen when the gap is narrower than about 0.6 m on the grid.
- The carrot pull-back (CARROT_CLEAR_M) was added after the first 5-layout trial collided on narrow_gap layouts 1, 2 and 4 (known map: layout 1). Tuning used layouts 0-9 of this same seed-0 set, so these numbers are not held-out.
