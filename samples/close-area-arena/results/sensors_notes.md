# Sensor presets x glass family: notes on sensors_0

Source: [sensors_0.md](sensors_0.md) and [sensors_0.json](sensors_0.json), made by
`.venv/bin/python run_sensors.py --layouts 50 --seed 0 --parity` in samples/close-area-arena.
Input: synthetic (simulated layouts, vehicle and sensor). Scored on truth. Sensor values and
their basis: [presets.py](../presets.py), from
[doc 08](../../../docs/research/close-area-nav/08-crazyflie-sensing-limits.md) sections 2 and 6.

## Result

| planner | family | ideal reached / collision % | crazyflie reached / collision % | crazyflie_bright reached / collision % |
|---|---|---|---|---|
| freest_beam | random | 86 / 0 | 54 / 2 | 58 / 0 |
| freest_beam | glass | 82 / 4 | 0 / 90 | 0 / 96 |
| astar_esdf known_map=False | random | 100 / 0 | 98 / 2 | 62 / 38 |
| astar_esdf known_map=False | glass | 90 / 10 | 0 / 100 | 0 / 100 |

- The glass family with the crazyflie preset produces collisions: 90 % (freest_beam) and 100 %
  (astar_esdf unknown map) of 50 layouts. 39 and 40 of those runs hit a glass panel; the rest hit
  a thin pole or, once, a dark box.
- With the ideal fan the same glass layouts give 4 % and 10 % collisions, all on poles. Single
  rays 5 deg apart also miss 0.02-0.05 m poles, so the current arena already has a thin-pole gap.
- crazyflie_bright (0.73 m range) breaks the map-building planner on the random family too:
  38 % collisions, all on matte obstacles. The 4 beams see an obstacle late and only on the beam
  axes.
- Parity: this loop and run.evaluate gave identical outcome and min clearance on 50/50 random
  layouts with the ideal preset, for both planners.

## Limits

- Glass panels sit on or within 0.6 m of the A-B line by design, so any planner without a map of
  the glass hits one. The family measures the cost of the unsensed class, not a typical room.
- The cone fill rule (min_fill 0.15 of 11 sub-rays), dropout, dark range and the 3.0 m range are
  proposals, not measured (marked in presets.py). With them a 0.02 m pole is seen only within
  about 0.2 m and a 0.05 m pole within about 0.4 m (synthetic check, not saved to a file).
- The minimum range (0.04 m) never fires in a run: the vehicle radius is 0.15 m.
- Inside 3.0 m the zranger noise term is below the 0.02 m floor, so range-dependent noise adds
  at most about 0.004 m to the std.
- Nothing here was flown. No real Multi-ranger data was used.
