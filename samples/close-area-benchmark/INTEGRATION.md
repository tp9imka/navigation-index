# Proposed hub wiring (text only, not applied)

The driver applies these. This sample edited no shared file except the
`world_glass.make_any_world` fix in close-area-arena. Links resolve from this file (samples/close-area-benchmark/); rewrite them relative to the target
file when applying.

## Decoder (docs/problem-statement-decoder.md)

Add to the "Start from" cell of row 31 (drone A=>B through obstacles in a close area):

[close-area-benchmark](./README.md) (every hub planner on 8 room
types x 2 range sensors, one table; pick the row that matches the venue)

Add to row 31's "Main risk": without a prior map and with only 4 horizontal beams (Crazyflie
Multi-ranger), the unknown-map A* reaches 35 % in offices, 0 % in warehouses and 5 % in a glass
office in the synthetic arena; get a floor plan or a denser range sensor.

Search keywords for the row: `close-area benchmark matrix`, `office warehouse maze planner`,
`crazyflie 4 beam unknown map`.

## Evidence matrix (docs/evidence-matrix.md), close-area section

| Sample | Method | Measured | Input | Runs | Caveat |
|---|---|---|---|---|---|
| [close-area-benchmark](./README.md) | 9 planners (straight, freest beam, APF + escape, VFH+, A* known, A* unknown with geofence prior, Informed RRT* 5000, A* + MPC, A* unknown + F2 PX4-CBF) on 8 arena families, ideal 72-ray and crazyflie 4-cone presets, true pose, truth scorer | Prior-map planners 100 % reached, 0 % collision everywhere. A* unknown: ideal 55-100 % reached, 0 % collision; crazyflie office 35 / 25, warehouse 0 / 50, glass_office 5 / 65 (reached / collision %). F2 on 72 beams: 0 % reached on narrow_gap, office, warehouse, maze, glass_office (stuck) | synthetic (2.5D point-mass arena) | 20 layouts per cell, seed 0, 2,880 flights | 120 s limit on maze and warehouse; unknown-map A* given the area geofence as its map prior (shipped prior: office 15 % vs 95 %); seed 0 partly a tuning seed |

## Cheat sheet (docs/cheatsheets/close-area-a-to-b.md), "which planner first"

Add one line:

- Room type known, map not: check the matching column of the
  [close-area-benchmark](./README.md) table first. With a
  floor plan any of A* known, Informed RRT* or A* + MPC reached 100 % in every family; with 4
  beams and no map, nothing in the hub passes warehouse or glass office.

## Showcase (site/)

`site/data/showcase/replays_v2/index.json` lists 112 replays grouped by family
(`schema close-area-replay-index/2`). Each replay has `world` in `close-area-world/1`, so the
playground loader can open it directly. The showcase page still reads `replays/` (old format);
pointing it at `replays_v2/` is a driver edit.
