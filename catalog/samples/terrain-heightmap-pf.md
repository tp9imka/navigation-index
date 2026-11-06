# Sample: Heightmap-gradient particle filter on real DEM and 1 m LiDAR (SPRIN-D CTU method) vs TERCOM

`sample:terrain-heightmap-pf` - code and walkthrough in [samples/terrain-heightmap-pf](../../samples/terrain-heightmap-pf/)

Re-implementation of the CTU SPRIN-D winner's localization (arXiv 2510.01348): local heightmap gradients matched to a prior DEM with the unnormalized correlation coefficient, Gaussian-blurred similarity maps weighting a translational particle filter resampled every fixed odometry distance, K-means largest-cluster estimate. Runs 10 km simulated flights with VIO-like drift over three real Copernicus GLO-30 windows (Bavarian Forest hills, Erding where SPRIN-D was flown, Hungarian plain) plus a smoothed-flat control, and compares against a radar-altimeter batch TERCOM baseline. Reports error vs distance, convergence from a 300 m initial offset, flat-terrain failure, a sensor-error sweep and measured CPU time per update. v2 adds a gain-fitted NCC likelihood with a Cramer-Rao information gate (falls back to odometry on featureless terrain: 336 vs 334 m at 10 km where v1 reached 539 m), compass bias as a particle state (8-53 m at 10 km for 0-20 deg bias where the translational filter loses lock above 10 deg), a no-truth confidence record (particle spread, ESS, CRB, NCC significance) checked against true error, and a test on real 1 m airborne LiDAR (Geobasis NRW DOM1/DGM1, dl-de/zero-2.0): the paper's literal binary edges reach 0.6 m median after 4 km at 1 m vs 19.9 m at 30 m reference resolution.

**Verification:** ran 2026-11-06 with CPython 3.13.15 + numpy 2.5.4 / scipy 1.18.1 / rasterio 1.5.2 / matplotlib 3.11.2 on an Apple M2 Max: fetch_dem.py downloaded the three GLO-30 windows over public HTTPS, run_eval.py produced every number and plot in README (results deterministic across two full runs, timings vary with machine load), test_core.py 14 passed and fails when the correlation flip or similarity-map origin is mutated. The flights, odometry and heightmap sensor are simulated; no real UAV, LiDAR or SfM data was used. The paper's own numbers are quoted from the paper, not reproduced. v2 (same date and machine): test_v2.py 8 passed (22 total with test_core.py); run_eval_v2.py re-ran v1 pf_grad and matched out/results.json exactly in all four regions, then produced every v2 table and plot in README; fetch_lidar.py downloaded 32 Geobasis NRW 1 m tiles over public HTTPS; run_lidar.py produced the 1 m vs 30 m table and gave identical error numbers on two runs. v2 gate thresholds were tuned on seeds 100-111 of the same regions. The LiDAR test simulates the onboard map from the same NRW DSM plus noise.

## Deep dives

- [copernicus-glo30](../../docs/dataset-cards/copernicus-glo30.md) (dataset-cards)
- [geobasis-nrw-lidar](../../docs/dataset-cards/geobasis-nrw-lidar.md) (dataset-cards)
- [blind-flight-teardown](../../docs/landscape/blind-flight-teardown.md) (landscape)

**Concepts:** [Terrain-relative navigation](../../catalog/concepts/terrain-nav.md), [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [GIS, maps and geospatial data](../../catalog/concepts/gis-mapping.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md)

**Tags:** `trn`, `tercom`, `particle-filter`, `heightmap`, `gradient-matching`, `template-matching`, `dem`, `copernicus-glo30`, `sprind`, `kmeans`, `python`, `numpy`, `scipy`, `information-gate`, `cramer-rao`, `heading-estimation`, `lidar-dsm`, `nrw-dom1`, `integrity`, `confidence`

## Related

- explains: [Kilometer-Scale GNSS-Denied UAV Navigation via Heightmap Gradients: A Winning System from the SPRIN-D Challenge](../../catalog/resources/sprind-heightmap-gradients-2025.md)
- uses: [Copernicus DEM on AWS Open Data](../../catalog/resources/copernicus-dem-aws.md)
- uses: [Rasterio](../../catalog/repos/rasterio__rasterio.md)
- explains: [python-tercom](../../catalog/repos/alti3__python-tercom.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Integrity monitoring for navigation and alt-PNT](../../docs/integrity-monitoring.md) (mentions)
- ["Polyot vslepuyu" (Blind flight) 2026: problem teardown and seven public solutions](../../docs/landscape/blind-flight-teardown.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Docs map](../../docs/README.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [Geobasis NRW DOM1 / DGM1 1 m airborne LiDAR surface and terrain models](../../catalog/resources/geobasis-nrw-dom1-dgm1.md) (dataset_for)
- [Integrity monitoring for alt-PNT: solution-separation FDE, protection levels and a Stanford diagram](../../catalog/samples/altpnt-integrity.md) (uses)
- [Two independent absolute sources on one real flight: visual fixes + terrain-relative navigation with solution-separation integrity (VPAIR over NRW 1 m LiDAR)](../../catalog/samples/two-source-integrity-vpair.md) (uses)

_Indexed by lane(s): samples_
