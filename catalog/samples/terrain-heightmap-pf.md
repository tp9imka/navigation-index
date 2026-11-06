# Sample: Heightmap-gradient particle filter on real Copernicus DEM (SPRIN-D CTU method) vs TERCOM

`sample:terrain-heightmap-pf` - code and walkthrough in [samples/terrain-heightmap-pf](../../samples/terrain-heightmap-pf/)

Re-implementation of the CTU SPRIN-D winner's localization (arXiv 2510.01348): local heightmap gradients matched to a prior DEM with the unnormalized correlation coefficient, Gaussian-blurred similarity maps weighting a translational particle filter resampled every fixed odometry distance, K-means largest-cluster estimate. Runs 10 km simulated flights with VIO-like drift over three real Copernicus GLO-30 windows (Bavarian Forest hills, Erding where SPRIN-D was flown, Hungarian plain) plus a smoothed-flat control, and compares against a radar-altimeter batch TERCOM baseline. Reports error vs distance, convergence from a 300 m initial offset, flat-terrain failure, a sensor-error sweep and measured CPU time per update.

**Verification:** ran 2026-11-06 with CPython 3.13.15 + numpy 2.5.4 / scipy 1.18.1 / rasterio 1.5.2 / matplotlib 3.11.2 on an Apple M2 Max: fetch_dem.py downloaded the three GLO-30 windows over public HTTPS, run_eval.py produced every number and plot in README (results deterministic across two full runs, timings vary with machine load), test_core.py 14 passed and fails when the correlation flip or similarity-map origin is mutated. The flights, odometry and heightmap sensor are simulated; no real UAV, LiDAR or SfM data was used. The paper's own numbers are quoted from the paper, not reproduced.

**Concepts:** [Terrain-relative navigation](../concepts/terrain-nav.md), [Inertial navigation (INS/IMU)](../concepts/ins.md), [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [Assured / resilient PNT](../concepts/assured-pnt.md), [GIS, maps and geospatial data](../concepts/gis-mapping.md), [Simulation and HIL/SITL](../concepts/simulation.md)

**Tags:** `trn`, `tercom`, `particle-filter`, `heightmap`, `gradient-matching`, `template-matching`, `dem`, `copernicus-glo30`, `sprind`, `kmeans`, `python`, `numpy`, `scipy`

## Related

- explains: [Kilometer-Scale GNSS-Denied UAV Navigation via Heightmap Gradients: A Winning System from the SPRIN-D Challenge](../resources/sprind-heightmap-gradients-2025.md)
- uses: [Copernicus DEM on AWS Open Data](../resources/copernicus-dem-aws.md)
- uses: [Rasterio](../repos/rasterio__rasterio.md)
- explains: [python-tercom](../repos/alti3__python-tercom.md)

_Indexed by lane(s): samples_
