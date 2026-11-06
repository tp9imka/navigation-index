# Heightmap-gradient particle filter on real DEM (SPRIN-D CTU method) vs TERCOM

## Goal

The CTU MRS team won the SPRIN-D Fully Autonomous Flight challenge (9 km course, below
25 m AGL, no GNSS) with a localization module that matches gradients of a local LiDAR
heightmap against a prior elevation map and fuses the similarity with odometry in a
clustered particle filter ([arXiv 2510.01348](https://arxiv.org/abs/2510.01348), digest:
[ctu-sprind-terrain-nav](../../docs/paper-digests/ctu-sprind-terrain-nav.md)). They
published no code. This sample re-implements that pipeline as closely as the paper
allows, runs it on real Copernicus GLO-30 terrain with simulated flights, and compares
it against a classic radar-altimeter TERCOM baseline on the same flights.

Everything about the vehicle is simulated: truth trajectory, odometry drift, the local
heightmap sensor, the radar altimeter. The terrain is real.

## What the paper specifies and what this sample does

| Paper (Sec. III) | Here | Faithful? |
|---|---|---|
| Prior map: north-aligned heightmap, max height per 1 m bin, from LiDAR point clouds turned into height above ground with LAStools | Copernicus GLO-30 DSM reprojected to UTM at 30 m. Optional `prep="ndsm"`: DSM minus a 150 m morphological opening as a crude height-above-ground | Deviation: 30x coarser grid, radar DSM not LiDAR |
| Local heightmap from the onboard occupancy map, 30-60 m square, compass-rotated to north | Simulated noisy local DEM patch, 41x41 cells (1.23 km), only cells within a 600 m swath of the last 1.23 km of track are observed, rotated by the simulated compass error | Same structure, scaled to the 30 m grid |
| Gradients, binarized at abs > 5 m (strong edges = buildings, trees) | `feature="binary", grad_thr=5` (m per cell, central differences) => variant `pf_paper` | Faithful in form; at 30 m the 5 m threshold means a 9.5 deg slope, not a building edge |
| - | `feature="grad"`: continuous gradient magnitude => variant `pf_grad` | Deviation, added because binary edges fail at 30 m (see results) |
| Template matching with Eq. (1), non-normalized correlation coefficient (TM_CCOEFF) | `core.match_ccoeff` via FFT, checked against a direct loop over Eq. (1) incl. the patch-mean term; masked cells excluded | Faithful |
| Gaussian blur on the similarity map | `blur_cells=1` | Faithful (sigma not stated in paper) |
| Translational PF, heading from compass; particles shifted by odometry | `core.HeightmapPF`, state (east, north) only | Faithful |
| Weight = normalized similarity at particle; resample after every 10 m of odometry; jitter from empirical odometry covariance | Min-max normalized similarity, systematic resampling every 150 m (5 cells), jitter sigma = max(3 m, k * distance moved) with k = 0.05 (`pf_paper`) or 0.1 (`pf_grad`) | Paper-normalization not specified; `pf_grad` also raises weights to the power 3 (deviation) |
| K-means, centroid of largest cluster as estimate | `kmeans2`, k = 4 | k not stated in paper |
| Particle count, blur sigma, k, normalization | 2000, 1 cell, 4, min-max | Not stated in paper - our choices |

Not reproduced: VIO itself, LiDAR occupancy mapping, the waypoint planner, the 1 m
grid, building/tree edges (GLO-30 does not resolve single buildings), and compass bias
correction (the paper says its system corrected up to 30 deg compass bias when features
were present; this PF does not estimate heading at all).

## Simulation model (`sim.py`)

- Terrain: three 15 x 15 km GLO-30 windows (`fetch_dem.py`), see table below. The
  "world" the sensors see is the DEM plus correlated error (sigma 2 m, 60 m correlation),
  so the reference map is not the truth.
- Flight: 10 km at 20 m/s, 1 Hz, weaving path (two sinusoidal heading terms, +-55 deg).
- Odometry (VIO-like, compass-aligned): per-run scale error N(0, 2%), compass bias
  N(0, 3 deg) plus 0.05 deg/sqrt(s) random walk, 0.3 m/s white velocity noise. The same
  compass error rotates the local heightmap. Initial position guess error N(0, 100 m).
- Local heightmap sensor (stand-in for downward stereo/LiDAR/SfM): sampled at
  `obs_res_m` (30 m), white height noise 2 m, horizontal and vertical scale error 1%,
  random vertical offset N(0, 50 m) (gradients ignore it), 5% cell dropout, swath mask.
- Radar altimeter TERCOM: terrain height = baro (bias N(0, 20 m), noise 0.5 m) minus
  radar AGL (noise 1 m). Every 1 km, a 2 km profile is matched by mean-removed MAD over a
  +-600 m, 15 m grid of translations; the fix is accepted only if the best MAD is below
  0.9x the best MAD more than 3 cells away and not on the search border.

## Files

| File | What |
|---|---|
| `fetch_dem.py` | Reads only the needed windows of the public GLO-30 COGs over HTTPS (no login), reprojects to UTM 30 m, caches `data/*.npz` (~0.8 MB each, git-ignored) |
| `core.py` | Bilinear lookup, nDSM, gradient features, Eq. (1) matcher (FFT + reference loop), similarity map, systematic resampling, K-means estimate, `HeightmapPF`, `tercom_fix` |
| `sim.py` | World, trajectory, odometry, heightmap sensor, radar altimeter, one Monte Carlo run |
| `run_eval.py` | 20 runs per region x 3 navigators, convergence test, sensor-error sweep, plots, `out/results.json` |
| `test_core.py` | 14 unit tests of the core math |
| `out/` | `results.json`, `eval_output.txt` (full printed tables), `error_vs_distance.png`, `tracks.png` |

## Run

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python fetch_dem.py          # ~25 s, three windows
.venv/bin/python -m pytest -q test_core.py
.venv/bin/python run_eval.py           # ~105 s on an M2 Max; --no-sweep to skip the sweep
```

## Results (ran 2026-11-06, CPython 3.13.15, Apple M2 Max, single Python process)

Seeds: PF knobs for `pf_grad` (weight power 3, jitter 0.1) were picked on seeds 100-111;
the tables use seeds 0-19 (main) and 200-211 (sweep). Two full runs gave identical error
numbers; timings vary by tens of percent with machine load.

Terrain windows (from `terrain_stats`; local relief = std of DEM minus a 1 km low-pass):

| region | where | height range | local relief std | cells with gradient > 2 m/cell |
|---|---|---|---|---|
| hilly | Bavarian Forest foothills near Grafenau, DE | 332-816 m | 37.8 m | 88% |
| mixed | Erding, DE (the SPRIN-D area): town, airbase, forest patches | 433-533 m | 4.5 m | 10% |
| flat | Great Hungarian Plain, HU: farmland, villages, tree belts, river | 70-121 m | 3.0 m | 8% |
| flat_smooth | control: `flat` blurred with a 300 m Gaussian, i.e. bare gently rolling farmland | 83-102 m | 1.3 m | 0% |

![error vs distance](out/error_vs_distance.png)

Horizontal error, median / 90th percentile over 20 runs, in metres:

| region | navigator | @1 km | @2 km | @5 km | @10 km | RMSE (median) |
|---|---|---|---|---|---|---|
| hilly | odometry | 108/197 | 105/218 | 173/303 | 311/462 | 193 |
| hilly | PF paper (binary edges) | 53/114 | 36/81 | 45/79 | 51/119 | 58 |
| hilly | PF gradient magnitude | 33/54 | 23/31 | 27/39 | 26/37 | 41 |
| hilly | TERCOM | 108/197 | 32/64 | 33/46 | 32/53 | 74 |
| mixed | odometry | 122/177 | 127/213 | 188/308 | 404/643 | 240 |
| mixed | PF paper | 101/223 | 84/282 | 121/275 | 324/525 | 201 |
| mixed | PF gradient magnitude | 55/194 | 32/76 | 30/45 | 32/84 | 63 |
| mixed | TERCOM | 122/177 | 105/217 | 87/235 | 123/385 | 143 |
| flat | odometry | 116/242 | 132/269 | 224/299 | 334/557 | 236 |
| flat | PF paper | 44/227 | 30/122 | 47/97 | 171/319 | 108 |
| flat | PF gradient magnitude | 27/136 | 26/37 | 58/182 | 41/156 | 84 |
| flat | TERCOM | 116/242 | 42/103 | 56/134 | 210/342 | 123 |
| flat_smooth | odometry | 116/242 | 132/269 | 224/299 | 334/557 | 236 |
| flat_smooth | PF paper | 154/275 | 152/230 | 207/288 | 344/547 | 265 |
| flat_smooth | PF gradient magnitude | 166/337 | 218/476 | 381/647 | 539/808 | 387 |
| flat_smooth | TERCOM | 116/242 | 132/269 | 224/299 | 334/557 | 236 |

TERCOM fix acceptance rate: 99% hilly, 34% mixed, 33% flat, 0% flat_smooth.

### Convergence from a 300 m initial offset

Initial guess 300 m off in a random direction (plus the N(0, 100 m) draw), particle
cloud sigma 250 m. "Converged" = error stays below 75 m for the rest of the 10 km
flight; distance is the median over converged runs.

| region | PF paper | PF gradient magnitude | TERCOM |
|---|---|---|---|
| hilly | 75% runs, 3020 m (151 s) | 100%, 700 m (35 s) | 100%, 6000 m |
| mixed | 10%, 7260 m | 85%, 6540 m | 30%, 9000 m |
| flat | 25%, 8940 m | 75%, 8140 m | 25%, 10000 m |
| flat_smooth | 0% | 0% | 0% |

The "stays below 75 m" rule is strict: in mixed terrain `pf_grad` is at 35 m median by
2 km, but late excursions above 75 m in some runs push the converged distance out.
Medians at 2 km are in `out/eval_output.txt`.

### Sensor-error sweep (mixed region, `pf_grad`, 12 runs each, one parameter at a time)

| parameter | values => err@10 km median (p90) | odometry @10 km |
|---|---|---|
| height noise sigma | 0.5 m => 35 (151); 2 m => 56 (105); 5 m => 126 (224); 10 m => 266 (653) | 382 |
| horizontal+vertical scale error | 0 => 46 (92); 2% => 32 (125); 5% => 43 (95); 10% => 53 (131) | 382 |
| compass bias sigma | 0 => 45 (103); 3 deg => 56 (105); 10 deg => 83 (1463); 20 deg => 373 (3924) | 162 / 382 / 699 / 1332 |
| native heightmap resolution | 30 m => 56 (105); 60 m => 45 (120); 120 m => 91 (220) | 382 |
| patch size | 21 cells => 49 (203); 41 => 56 (105); 61 => 52 (136) | 382 |
| swath width | 300 m => 73 (144); 600 m => 56 (105); 1200 m => 35 (75) | 382 |

### Compute time per update (measured)

| step | median | p95 |
|---|---|---|
| PF update: template features + Eq. (1) over the search box + blur + weights + resample + K-means, 2000 particles, 41x41 template | 1.1 ms | 1.5-2.4 ms |
| TERCOM fix: 4489 candidate offsets x 100 profile samples | 20 ms | 29-41 ms |

Apple M2 Max, one Python process, numpy 2.5.4 / scipy 1.18.1, other agents' jobs
running on the same machine. The paper reports real-time on an Intel NUC i7 CPU but no
per-update timing.

![tracks](out/tracks.png)

## Findings

1. **Binary edges at 5 m do not transfer to a 30 m DEM.** `pf_paper` beats odometry in
   hilly terrain (51 vs 311 m at 10 km) but only marginally in mixed (324 vs 404 m).
   On tuning seeds 100-111, cutting heightmap noise and DEM error from 2 m to 0.3 m (no
   scale error) brought binary edges in hilly terrain to 55 m median final error with the
   paper's linear weights and 25 m with weight power 3, so the main failure is noise
   flipping cells across the threshold, not the PF. The paper's threshold works because at 1 m bins a building or
   tree edge is a 5-20 m step, far above LiDAR noise. On a 30 m grid, continuous gradient
   magnitude is the robust choice (26-41 m at 10 km in the three real regions).
2. **Gradient PF beats TERCOM where relief is low.** In hilly terrain both bound the error
   (26 vs 32 m median at 10 km). At Erding, TERCOM accepts a third of its fixes and ends at
   123 m median; the gradient PF stays at 32 m because a 2D patch carries more structure
   than a 1D profile.
3. **"Flat" real DSM is not featureless.** The Hungarian plain window has villages, tree
   belts and a river in GLO-30 (a radar DSM), and both methods still help there. Failure
   only appears once that is blurred away (`flat_smooth`).
4. **On truly flat terrain the PF fails worse than odometry; TERCOM fails safe.**
   `pf_grad` on `flat_smooth` reaches 539 m median at 10 km vs 334 m for raw odometry:
   min-max normalization stretches pure noise into a confident similarity map. TERCOM's
   ambiguity gate rejected every fix and left odometry untouched. A PF port needs an
   equivalent gate (e.g. skip updates when the similarity peak is not distinct, or use an
   absolute rather than min-max normalization). The paper notes the same regime
   qualitatively: "In open field areas, the system mostly relied on the odometry".
5. **Compass bias is the weak spot.** Above ~10 deg the translational PF diverges in some
   runs (p90 1.5 km at 10 deg) because the patch is rotated and the drift outruns the
   jitter. Adding heading to the state or a small rotation search in the matcher is the
   obvious next step.
6. **Wider swath helps more than a bigger patch.** 1200 m swath => 35 m at 10 km vs 73 m
   at 300 m; patch size 21-61 cells moves the median little once the swath is fixed,
   though 21 cells doubles the p90 (203 vs 105 m).
7. **Cheap.** About 1 ms per PF update on a laptop CPU, 20x cheaper than the brute-force
   TERCOM search used here.

Eq. (1) is unnormalized: a high-contrast region outscores an exact but low-contrast
match (`test_ccoeff_is_not_normalized_so_high_contrast_wins`). The paper argues the
binary maps are already normalized; with continuous gradients this bias is real and is
one reason for the weight power and blur.

## Limitations

- The flights, odometry and heightmap sensor are synthetic. The patch is built from the
  same DEM family as the map (with added correlated error), which is optimistic compared
  with real LiDAR/SfM vs a 30 m radar DSM: vegetation season, buildings, radar
  penetration in forest and SfM distortion are not modelled.
- The local map is assumed undistorted by odometry drift inside the patch (the paper makes
  the same assumption).
- Each navigator was tuned lightly on separate seeds; `pf_paper` uses the paper's
  literal threshold, not a threshold tuned for 30 m.
- TERCOM here is translation-only batch MAD, no recursive filter; the stdlib PF with a
  point radar altimeter is in [terrain-relative-nav-pf](../terrain-relative-nav-pf/).
- The Russian 2026 TERCOM hackathon solutions mentioned in the round brief were not found
  in `data/resources/ua-ru-sources.json` and were not compared.

## Related

- `res:sprind-heightmap-gradients-2025` - the paper this sample re-implements.
- `res:copernicus-dem-aws` - GLO-30 source, public COGs.
- `repo:rasterio/rasterio` - windowed COG read and reprojection.
- `repo:alti3/python-tercom` - another batch TERCOM implementation to cross-check against.
- [terrain-relative-nav-pf](../terrain-relative-nav-pf/) - stdlib radar-altimeter PF on a synthetic DEM.
