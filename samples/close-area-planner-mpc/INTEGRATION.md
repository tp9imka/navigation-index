# Proposed hub wiring (text only, not applied)

The driver applies these; this sample did not edit any shared file. Links below resolve from
this file (samples/close-area-planner-mpc/); re-base them when pasting into docs/ (for example
`./` => `../samples/close-area-planner-mpc/`).

## Decoder (docs/problem-statement-decoder.md)

Add to the "Start from" cell of row 31 (close-area A=>B):

[close-area-planner-mpc](./) (linear MPC with OSQP in an ESDF half-plane corridor on the arena
A*; measured against the carrot follower, solve time 0.22 ms median)

Add to that row's "Main risk": a corridor MPC on a known map tracks no better than a tuned
carrot follower in the synthetic arena (both 100 % reached, p95 tracking error 0.053-0.054 m);
pitch it for constraints and speed through gaps, not for success rate.

Search keywords for the row: `linear mpc osqp corridor`, `safe flight corridor half-plane`,
`mpc solve time warm start`.

## Evidence matrix (docs/evidence-matrix.md), close-area section

| Sample | Method | Measured | Input | Runs | Caveat |
|---|---|---|---|---|---|
| [close-area-planner-mpc](./README.md#results-ran-2026-11-09-apple-m3-max-cpython-31115-numpy-246-scipy-1171-osqp-113) | Arena A* (known map) + linear MPC: velocity-setpoint input with the exact tau = 0.15 s lag model, N = 20 x 0.1 s, per-axis v and a boxes, soft half-plane corridor from the grid (nearest-point planes, 0.20 m offset), OSQP warm start; vs the arena carrot follower | Both 100 % reached, 0 % collision on random and narrow_gap; median min clearance 0.637 vs 0.635 m (random), 0.304 vs 0.276 m (narrow_gap); tracking error p95 0.054 vs 0.053 m; median time to goal on narrow_gap 21.97 vs 24.23 s; QP 0.222 ms median / 0.464 ms p95 warm, 0.733 / 1.036 ms cold (M3 Max, Python); obstacle planes active in 163 of 11161 narrow_gap steps; planes off => identical outcomes | synthetic (2.5D point-mass arena, known map) | 50 layouts per family, seed 0 | Seed 0 not held out; known map only; truth pose; laptop timing, not a flight computer; the corridor changed one outcome only in a constant-1.4 m/s ablation (1 run) |

## Cheat sheet (docs/cheatsheets/README.md)

Extend the close-area line's "Sheet" cell:

"MPC", "corridor", "OSQP", "solve time": [close-area-planner-mpc](./) (corridor MPC matches the carrot follower on outcomes and passes gaps faster; 0.22 ms per QP on a laptop)

## guidance-planning.md G5

Add one line under G5 (MPC tracking): measured MPC number for close-area A=>B is in
[close-area-planner-mpc](./README.md) (synthetic arena, laptop): same outcomes as a carrot
follower, QP 0.22 ms median / 0.46 ms p95 with warm start.
