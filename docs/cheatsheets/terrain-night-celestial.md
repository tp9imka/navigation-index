# Cheat sheet: terrain, night and celestial absolute fixes

Briefs like "fixed-wing by terrain (TERCOM)", "blind flight", "navigate at night / through
smoke", "magnetic anomaly navigation", "heading backup at sea", "no RF at all". Decoder rows 15,
16, 18, 25, and the absolute-fix half of 27.

## 1. What judges likely want (30 s)

Absolute position from something that cannot be jammed (terrain, the magnetic field, stars,
thermal imagery), measured on real terrain or real sensor data, with the conditions where it
fails shown next to the ones where it works. "The condition vendors skip in their brochures."

## 2. The demo in 24-48 h

Pick one source by the brief, not all four. Terrain is the safest: heightmap particle filter vs
TERCOM vs odometry on real GLO-30 windows, with an information gate on flat terrain.

| Sample | Status | Deps | Setup / download | First commands (from `samples/<name>/`) |
|---|---|---|---|---|
| [terrain-heightmap-pf](../../samples/terrain-heightmap-pf/) | ran | venv | GLO-30 fetch ~25 s; v1 ~105 s, v2 ~6 min | `.venv/bin/python fetch_dem.py && .venv/bin/python run_eval.py` |
| [blind-flight-bench](../../samples/blind-flight-bench/) | ran | venv (unpinned numpy scipy rasterio; imports terrain-heightmap-pf) | ~6 min + ~30 s fetch | `.venv/bin/python regions.py && .venv/bin/python run_bench.py` |
| [celestial-star-tracker](../../samples/celestial-star-tracker/) | ran | venv + cedar-solve v0.6.0 `--no-deps` | fetch ~5 min (~190 MB); solve ~10 s; sim ~5 s | `python3 fetch_data.py && .venv/bin/python plate_solve_eval.py && .venv/bin/python position_fix_sim.py` |
| [thermal-geolocalization](../../samples/thermal-geolocalization/) | ran | venv | ~2.8 GB transfer (1.7 GB disk), ~7 min; eval ~4 min MPS, ~25 min CPU | `.venv/bin/python fetch_data.py --heldout && PYTORCH_ENABLE_MPS_FALLBACK=1 .venv/bin/python run_eval.py --device mps --gate revised --tag main_revised` |
| [magnav-quickstart](../../samples/magnav-quickstart/) | ran | docker (`julia:1.11`) | ~10 min install + precompile, 5.8 GB Julia depot; run 43 s | see the sample's `docker exec magnav ...` command |

In a flight loop: [golden-demo-fixedwing](../../samples/golden-demo-fixedwing/) (ArduPlane SITL,
27.6 km, day / night fix models).

## 3. First 2 hours (3-5 people)

| Who | 0:00-1:00 | 1:00-2:00 |
|---|---|---|
| Lead | Altitude, distance, terrain type, sensors (radar altimeter? heading source? camera?) | ADR-001: error at N km, % diverged, fix rate |
| Nav | terrain-heightmap-pf v1 run | Swap in the brief's region and altimeter model |
| Platform | GLO-30 windows for the brief's area; celestial / thermal fetch if relevant | Heading source (compass bias state, stars) wired in |
| Viz (4-5) | Error vs distance per terrain class | Particle cloud on the DEM, spread as confidence |
| Pitch (5) | Read the [blind-flight teardown](../landscape/blind-flight-teardown.md) | Failure-case slide: flat, sea, turns without heading, clouds |

## 4. Numbers you can cite

- Heightmap PF v2 at 10 km: median 12 m hilly, 27 m mixed, 25 m flat vs odometry 311-404 m.
  Real GLO-30 terrain, **synthetic** flights and sensors, 20 runs.
- Real thermal frames vs RGB satellite: best config 18 of 111 frames fixed (median 2.6 m), night
  fog 0 of 14; 0 false fixes in 1620 gated attempts. **Real** (Thermal-UAV / SCC-Loc subset).
- Star plate solve: 40 / 40 real cutouts solved, pointing median 5.2 arcsec (12 deg FOV);
  position budget: 1 arcmin of level error = 1,896 m (theory 1.85 km), 1 mg accel bias = 6.4 km.
  **Real** star images for the solve, **synthetic** for the budget.

MagNav if asked: EKF DRMS 31.2 m vs INS-only final error 218.8 m on one 14 min line. **Real**
SGL 2020 flight data, 1 line.

## 5. Top traps

1. Flat terrain or sea gives TRN nothing to match; with turns and no heading sensor 80-100 % of
   blind-flight flights diverged (real terrain, simulated). Bring a heading source.
2. GLO-30 is a DSM, not bare earth; elevation 2.0 breaks 1.x commands; the 1 m LiDAR result
   (0.4 m) uses the same DSM for map and sensor, a best case.
3. Thermal fixes are rare even with position and heading priors; learned retrieval (SGM)
   ungated gave 182 of 238 false fixes and has research-only weights. Clouds block stars; on a
   moving platform the vertical is the whole position budget, so heading is the realistic win.
   MagNav needs the AFRL data agreement and long Julia compiles.

## 6. Stretch goal

TRN as a second absolute source next to visual fixes on a real flight:
[two-source-integrity-vpair](../../samples/two-source-integrity-vpair/) took PL availability at
AL 50 m from 1.6 % to 84.4 % (mixed: real VPAIR poses, simulated TRN sensor from real 1 m LiDAR).
Or the night case in the ArduPlane loop: night alarm 19-31 s and 33-50 m max cross-track with
15 % thermal fixes (SITL, statistical fix draws).

## 7. Links

- Decoder: [rows 15, 16, 18, 25, 27](../problem-statement-decoder.md#the-table); evidence:
  [section 4](../evidence-matrix.md#4-absolute-alt-pnt-position-error),
  [section 3](../evidence-matrix.md#3-integrity-metrics-protection-level-misleading-information).
- Cards: [Rasterio](../integration-cards/rasterio__rasterio.md),
  [elevation](../integration-cards/bopen__elevation.md),
  [tercom_nav](../integration-cards/mzahana__tercom_nav.md),
  [python-tercom](../integration-cards/alti3__python-tercom.md),
  [cedar-solve](../integration-cards/smroid__cedar-solve.md), [tetra3](../integration-cards/esa__tetra3.md),
  [Skyfield](../integration-cards/skyfielders__python-skyfield.md),
  [satellite-thermal](../integration-cards/arplaboratory__satellite-thermal-geo-localization.md),
  [MagNav.jl](../integration-cards/mit-ai-accelerator__magnav.jl.md).
- Datasets: [Copernicus GLO-30](../dataset-cards/copernicus-glo30.md),
  [Geobasis NRW LiDAR](../dataset-cards/geobasis-nrw-lidar.md),
  [thermal sets](../dataset-cards/thermal-datasets.md),
  [MagNav challenge](../dataset-cards/magnav-challenge-data.md),
  [AFIT example](../dataset-cards/afit-magnav-example-data.md).
