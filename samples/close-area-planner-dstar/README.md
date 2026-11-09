# D* Lite vs A* from scratch on unknown maps

Use this when the map is built from range returns during flight and you need to know whether
incremental replanning (D* Lite) is worth it over re-running A* every replan.

D* Lite on the same inflated grid and cost model as the arena's
[astar_esdf](../close-area-arena/README.md) unknown-map mode, reusing its follower. Only cells that
changed since the last replan are updated. All inputs are synthetic (simulated layouts, vehicle and
range sensor). The job that built this hit its time limit before writing a README; the loop driver
wrote this page from the files in [results/](results/).

## Run

```sh
uv venv .venv && uv pip install --python .venv -r requirements.txt
.venv/bin/python compare.py run --layouts 50 --seed 0      # outcomes and planning time
.venv/bin/python compare.py verify --layouts 50 --seed 0   # A* on every frozen D* map, same cost?
.venv/bin/python compare.py scale --tiles 1,2,4,8 --replans 25   # search time vs map side
```

## Results (seed 0, 50 layouts per family)

From [compare_0.md](results/compare_0.md). Plan = whole replan (ESDF + cost arrays + search +
shortcut).

| family | search | reached % | collision % | plan ms median / p95 | search ms median / p95 |
|---|---|---|---|---|---|
| random | A* from scratch | 100 | 0 | 22.8 / 65.0 | 20.6 / 62.5 |
| random | D* Lite | 100 | 0 | 5.1 / 10.6 | 3.2 / 7.3 |
| u_trap | A* from scratch | 100 | 0 | 37.9 / 70.5 | 35.1 / 67.4 |
| u_trap | D* Lite | 100 | 0 | 5.3 / 14.4 | 3.3 / 11.1 |
| narrow_gap | A* from scratch | 80 | 0 | 39.2 / 67.7 | 36.2 / 61.7 |
| narrow_gap | D* Lite | 84 | 0 | 7.7 / 24.4 | 4.4 / 19.1 |

- **Correct:** at every one of 10,017 replans, A* on the same frozen map found a path exactly when
  D* Lite did, and never a cheaper one (max relative difference 8.6e-16):
  [correctness_0.md](results/correctness_0.md). Outcomes match on random and u_trap (50/50); on
  narrow_gap 41/50 match (the 9 differing runs were not traced; equal-cost ties are a likely cause).
- **Faster, but not needed at this size:** 4-7x less search time per replan; A* already fits a
  2-5 Hz budget on a 20 x 20 m arena.
- **Where it matters:** on tiled maps ([scale_stdout.txt](results/scale_stdout.txt), 25 replans
  each), median A* search grows from 36 ms (1 tile) to 261 ms (2x2), 1.24 s (4x4) and 5.8 s (8x8),
  while D* Lite incremental replans stay at 2.5-7 ms. Its first search costs as much as A*.
  Beyond about a 40 x 40 m area at 0.1 m cells, re-running A* misses a 2 Hz replan budget here.

## Limits

- Synthetic 2.5D arena, truth pose, one seed. Timings are Python on an Apple M3 Max under heavy
  machine load.
- The scale test times search only on tiled copies of arena maps, not full flights.
- Fuzz checks of the incremental updates: [fuzz.md](results/fuzz.md),
  [fuzz_strict.md](results/fuzz_strict.md).

## Sources

- Koenig and Likhachev, "D* Lite", AAAI 2002 (not re-read for this sample).
