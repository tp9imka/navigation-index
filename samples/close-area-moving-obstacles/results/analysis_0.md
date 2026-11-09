Source: results/moving_0.json (`python run_moving.py --layouts 50 --seed 0 --workers 14`, synthetic). Written by `python analyze.py`.

## Stuck layouts

| arm | mover speed m/s | stuck layouts |
|---|---|---|
| astar | 0.0 | - |
| astar | 0.5 | - |
| astar | 1.0 | - |
| astar_5hz | 0.0 | - |
| astar_5hz | 0.5 | - |
| astar_5hz | 1.0 | - |
| astar_f2 | 0.0 | 2, 5, 8, 11, 13, 17, 20, 27, 42, 44 |
| astar_f2 | 0.5 | 2, 5, 8, 11, 13, 20, 27, 42 |
| astar_f2 | 1.0 | 2, 5, 8, 11, 13, 20, 27, 42 |
| apf | 0.0 | 26, 28 |
| apf | 0.5 | 26 |
| apf | 1.0 | 6, 40 |

close-area-safety-filter kill_a_unsensed_off_0.json, F2, truth pose, no movers, layouts 0-49: stuck on 2, 5, 8, 11, 13, 20, 27, 42, 44 (9 of 50).
- astar_f2 at 0.0 m/s: 10 stuck, 9 of them also stuck there; new: [17]
- astar_f2 at 0.5 m/s: 8 stuck, 8 of them also stuck there; new: none
- astar_f2 at 1.0 m/s: 8 stuck, 8 of them also stuck there; new: none

## F2 intervention fraction (share of 50 Hz steps with eta > 0)

| mover speed m/s | median | max |
|---|---|---|
| 0.0 | 0.383 | 0.941 |
| 0.5 | 0.376 | 0.941 |
| 1.0 | 0.409 | 0.941 |

## Mover collisions: vehicle speed and closing speed at contact

| arm | mover speed m/s | mover collisions | vehicle speed median m/s | min | max | closing speed median m/s | min | max | closing < 0.1 m/s |
|---|---|---|---|---|---|---|---|---|---|
| astar | 0.5 | 7 | 0.303 | 0.282 | 0.305 | -0.051 | -0.198 | 0.057 | 7 |
| astar | 1.0 | 18 | 0.39 | 0.172 | 0.577 | -0.017 | -0.285 | 0.209 | 14 |
| astar_5hz | 0.5 | 6 | 0.3 | 0.297 | 0.302 | -0.017 | -0.227 | 0.014 | 6 |
| astar_5hz | 1.0 | 18 | 0.345 | 0.259 | 0.42 | 0.003 | -0.226 | 0.151 | 15 |
| apf | 1.0 | 1 | 0.27 | 0.27 | 0.27 | 0.07 | 0.07 | 0.07 | 1 |
