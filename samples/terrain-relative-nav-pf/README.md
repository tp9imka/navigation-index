# Terrain-relative navigation with a particle filter

## Goal

Show the core TERCOM / TRN idea in about 200 lines of stdlib Python: an aircraft
with a drifting INS and a radar altimeter can bound its position error by matching
the measured terrain profile against a DEM. Nothing here is GNSS-dependent or
jammable in the RF-navigation sense; the only emitter is the aircraft's own radar
altimeter.

What the simulation does, per 1 s step:

1. Truth flies at 60 m/s, constant 1200 m MSL, weaving +-20 deg around a 45 deg heading.
2. The INS integrates velocity with a constant bias (0.8 E, -0.6 N m/s) plus noise and
   starts 180 m off truth, so its error grows without bound.
3. Measured terrain height = baro altitude - radar AGL (noise 2 m and 3 m).
4. The particle filter holds 2000 hypotheses of (east, north, bias_e, bias_n),
   propagates them with the INS velocity minus each particle's bias, weights each by a
   gaussian on (measured terrain - DEM height under the particle), and does systematic
   resampling when the effective sample size drops below half.

## Files

| File | What | Verified |
|---|---|---|
| `terrain.py` | `Dem` grid with bilinear lookup; seeded synthetic DEM (60 gaussian hills + 4 octaves of value noise) | ran |
| `trn_pf.py` | Simulation + particle filter, prints the error table | ran |
| `dem_rasterio.py` | Loads a real GeoTIFF DEM (Copernicus GLO-30) into the same `Dem` class via rasterio | syntax-checked only |

## Related repos in the index

- `repo:alti3/python-tercom` - classic batch TERCOM (profile correlation) in Python. Compare
  its batch correlation against the recursive PF here.
- `repo:sotostrk/tercom-via-particle-filter-uav-state-estimation-mae6760-project-` - the
  same SIR-PF idea in MATLAB; useful cross-check of tuning.
- `repo:mzahana/tercom_nav` - ROS 2 terrain matching + error-state Kalman filter, the next
  step if you need this on a real vehicle stack.
- `repo:hstm/terrain-nav-preprocessing` - DEM tile preparation with controlled noise for
  evaluation sweeps.
- `repo:rasterio/rasterio` - used by `dem_rasterio.py` to read real DEMs.

## Prerequisites

- `python3` 3.10+ (verified with 3.14.7). Stdlib only for the simulation.
- Optional, for real DEMs: `rasterio` (`pip install rasterio`, ships GDAL wheels).

## Run

```bash
cd samples/terrain-relative-nav-pf
python3 trn_pf.py                       # defaults: --seed 7 --particles 2000 --duration 200
python3 trn_pf.py --seed 3 --particles 500
python3 trn_pf.py --terrain-scale 0.02  # near-flat terrain: watch TRN lose observability
```

Runtime is about 1.5 s on a laptop.

## Observed output (python3.14.7, 2026-11-06)

`python3 trn_pf.py`:

```
seed=7 particles=2000 duration=200.0s terrain_scale=1.0 meas_sigma=5.4m
 t[s]  INS err[m]  PF err[m]  PF 1-sigma[m]  bias est e/n [m/s]
   20       200.3       16.5           41.6      0.28/0.39
   40       219.8        9.9           25.5     -0.23/0.31
   60       240.1       24.9           22.8      0.07/0.24
   80       260.3        4.2           17.0      0.53/0.06
  100       280.6        4.5           21.6      0.55/0.02
  120       300.6       12.4           22.9      0.55/-0.00
  140       320.4       12.8           28.6      0.58/-0.04
  160       340.5       10.4           31.9      0.59/-0.10
  180       360.1       20.0           26.5      0.52/-0.12
  200       380.3       13.0           32.9      0.62/-0.15
resamples=20 terrain_std_along_track=266.1m true_bias e/n=0.80/-0.60 m/s
```

`python3 trn_pf.py --seed 3 --particles 500` (last lines): PF error 9-11 m at t=160-200 s,
bias estimate 0.60/-0.57 vs true 0.80/-0.60.

`python3 trn_pf.py --terrain-scale 0.02` (terrain std along track 5.3 m, same as the
measurement noise):

```
 t[s]  INS err[m]  PF err[m]  PF 1-sigma[m]  bias est e/n [m/s]
   20       200.1      171.9          301.2      0.05/-0.01
  100       279.8       48.0          228.9      0.26/-0.15
  200       379.7      151.5          294.4      0.16/-0.39
resamples=1 terrain_std_along_track=5.3m true_bias e/n=0.80/-0.60 m/s
```

How to read it: INS error grows linearly (about 1 m/s of bias). Over rough terrain the PF
locks within 20 s and stays at 4-25 m. The bias estimate converges slowly and only
partly in 200 s (it is observable only through accumulated position change), which is
normal. Over flat terrain the PF does not converge, and its 1-sigma (about 230-300 m)
correctly says so. Use the 1-sigma column as the integrity signal, not the error column
(you do not have truth in flight).

## Swap in a real DEM (Copernicus GLO-30)

GLO-30 is free, global, 30 m, and hosted as Cloud Optimized GeoTIFFs on AWS open data.
Tile naming is `Copernicus_DSM_COG_10_<N|S>yy_00_<E|W>xxx_00_DEM`, one tile per 1x1 deg.

```bash
cd samples/terrain-relative-nav-pf
curl -O https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N47_00_E008_00_DEM/Copernicus_DSM_COG_10_N47_00_E008_00_DEM.tif
pip install rasterio                    # your environment, not done by this sample
python3 dem_rasterio.py Copernicus_DSM_COG_10_N47_00_E008_00_DEM.tif 32632   # UTM 32N
```

The URL above returned HTTP 200 on 2026-11-06; `dem_rasterio.py` itself has not been
run. To use it in the filter, replace the `synthetic_dem(...)` call in `trn_pf.run` with
`load_dem(path, epsg)`, and set `START_XY_M` to a UTM coordinate inside the tile. A full
tile is about 3600x2400 cells as Python lists (heavy, but works); crop with a rasterio
`window=` read if memory matters.

## Swap in real logs

Replace the simulated block at the top of the loop in `trn_pf.run` (truth, INS, baro,
radalt) with rows from a log, one row per step:

| Column | Units | Used for |
|---|---|---|
| `t` | s | step `dt` (do not assume 1 s) |
| `ins_ve`, `ins_vn` | m/s | particle propagation |
| `baro_alt_msl` | m | measured terrain = baro - radalt |
| `radalt_agl` | m | same |
| `truth_e`, `truth_n` (optional) | m, UTM | error column only |

ArduPilot and PX4 dataflash / ulog files carry baro, rangefinder and EKF velocity;
convert lat/lon to the DEM's UTM zone first. If the log has no truth, print only the
PF estimate and its 1-sigma.

## Hackathon extensions

- Batch TERCOM vs PF: run `repo:alti3/python-tercom` on the same DEM and profile, compare
  time to lock and robustness to a 300 m initial error.
- Integrity flag: raise a "TRN unreliable" alarm when 1-sigma exceeds a threshold or the
  terrain std over the last N samples drops below about 3x the measurement sigma.
- Feed the PF fix as a position measurement into an EKF (see `repo:mzahana/tercom_nav`)
  instead of using the PF as the whole navigator.
- Speed: replace the per-particle Python loop with numpy (vectorised bilinear lookup);
  10-50x faster, needed for 10k+ particles.

## Pitfalls

- Vertical datum: GLO-30 heights are orthometric (EGM2008 geoid). Baro altitude is
  pressure altitude; GNSS altitude is ellipsoidal. A constant offset between them looks
  like a terrain mismatch and drags the filter. Estimate a bias state or calibrate on
  the ground.
- Radar altimeter footprint: real units measure the nearest return in a beam several
  tens of metres wide, not the point under the aircraft. Over cliffs or forests the
  error is not gaussian. Inflate `DEM_ERROR_M` rather than trusting nominal noise.
- Over-confident likelihood: with a tiny `meas_sigma` most particles die each step
  (sample impoverishment). Watch `resamples` and the 1-sigma; if it collapses to near 0
  while the error grows, increase `DEM_ERROR_M` or `PROCESS_POS_SIGMA_M`.
- Repetitive terrain (parallel ridges) gives multi-modal posteriors; the weighted mean
  can sit between two modes. Report modes, not just the mean, for real use.
- The radar altimeter is an emitter. It is the standard TRN sensor, but if emission
  control matters, look at passive alternatives (`concept:visual-geolocalization`,
  `concept:magnetic-nav`).
