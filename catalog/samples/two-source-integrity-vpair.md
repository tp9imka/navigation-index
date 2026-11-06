# Sample: Two independent absolute sources on one real flight: visual fixes + terrain-relative navigation with solution-separation integrity (VPAIR over NRW 1 m LiDAR)

`sample:two-source-integrity-vpair` - code and walkthrough in [samples/two-source-integrity-vpair](../../samples/two-source-integrity-vpair/)

Adds terrain-relative navigation as a second absolute source to the real VPAIR flight (8.53 km after GNSS loss, Rhine valley between Bad Honnef and Koenigswinter, east of Bonn). VO and visual fixes are the cached real-imagery front end of e2e-visual-nav-vpair (imported, no GPU). TRN sensors are simulated from real terrain at the real VPAIR poses: a downward heightmap (scanning LiDAR / stereo stand-in) from the Geobasis NRW 1 m DSM matched by terrain-heightmap-pf's v2 particle filter against a 5 m NRW map or a Copernicus GLO-30 map, and a 40 deg radar altimeter (blind-flight-bench beam model, noise, dropouts) matched by batch TERCOM against the DSM's leading-edge beam map. Fusion and integrity reuse altpnt-integrity v2 (heading/scale EKF, chi-square gate, solution separation, protection level, per-source fault priors), with TRN R from the TRN's own no-truth sigma. Reports error, PL availability at AL 25/50/100 m, HMI/MI with each source alone vs both over 10 TRN seeds, and injects a visual map misregistration and a TRN ambiguity (secondary match peak), with the monitor order swapped as a control and a three-source variant.

**Verification:** Ran 2026-11-06 on Apple M2 Max, CPython 3.12.14, numpy 2.5.4, scipy 1.18.1, rasterio 1.5.2: fetch_terrain.py (46 NRW DOM1 tiles, GLO-30 window, 125 s), run_two_source.py with 10 TRN seeds (107 s), screenshot.sh at frames 130 and 198. Map stride 8 (360 m tiles), heading +2 deg, 188 frames after GNSS loss: VO + visual fixes alone 9.7 m RMS but solution-separation PL median 1.2 km (1.6 % available at AL 50); + LiDAR-heightmap TRN 2.6 m RMS, PL median 30.5 m, available 14.4 / 84.4 / 100 % at AL 25 / 50 / 100 m; GLO-30-map TRN 55.6 % at AL 100 only; radar-altimeter TERCOM 10.9 % at AL 100 with 6 false detections. 0 HMI in every fault-free run. Faults: misregistration and TRN ambiguity detected 10/10 with the LiDAR TRN, no HMI, but two-source attribution of the misregistration follows the monitor's source order (control: swapped order flips it), and the three-source variant mis-excludes and gives 19 HMI epochs at AL 50 under TRN ambiguity. Tests: venv 14 pass; plain python3 7 pass, 7 skip. Altimeter and heightmap are simulated from real terrain at real poses, not recorded; LiDAR map and sensor share one DSM.

**Concepts:** [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [Terrain-relative navigation](../../catalog/concepts/terrain-nav.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Visual geo-localization (image-to-map)](../../catalog/concepts/visual-geolocalization.md), [Visual(-inertial) odometry](../../catalog/concepts/vio.md)

**Tags:** `vpair`, `integrity`, `protection-level`, `solution-separation`, `fde`, `chi-square-gate`, `trn`, `tercom`, `radar-altimeter`, `lidar`, `heightmap`, `particle-filter`, `geobasis-nrw`, `glo-30`, `fault-injection`, `map-misregistration`, `navdash`

## Related

- uses: [End-to-end GNSS-denied visual navigation on one real flight: nadir VO + DINOv2 retrieval + LightGlue fixes + multi-frame voting + altpnt integrity (VPAIR)](../../catalog/samples/e2e-visual-nav-vpair.md)
- uses: [Integrity monitoring for alt-PNT: solution-separation FDE, protection levels and a Stanford diagram](../../catalog/samples/altpnt-integrity.md)
- uses: [Heightmap-gradient particle filter on real DEM and 1 m LiDAR (SPRIN-D CTU method) vs TERCOM](../../catalog/samples/terrain-heightmap-pf.md)
- uses: [Blind-flight bench: radar altimeter + Copernicus GLO-30 TRN, six navigators on one harness](../../catalog/samples/blind-flight-bench.md)
- uses: [VPAIR - Aerial Visual Place Recognition and Localization in Large-scale Outdoor Environments](../../catalog/resources/vpair-dataset-2022.md)
- uses: [VPAIR](../../catalog/repos/aervisloc__vpair.md)
- uses: [Geobasis NRW DOM1 / DGM1 1 m airborne LiDAR surface and terrain models](../../catalog/resources/geobasis-nrw-dom1-dgm1.md)
- uses: [Copernicus DEM on AWS Open Data](../../catalog/resources/copernicus-dem-aws.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Multi-source fault detection and exclusion on one real flight: ARAIM-style subset exclusion across GNSS, visual fixes and two TRNs (VPAIR)](../../catalog/samples/multi-source-fde.md) (uses)

_Indexed by lane(s): samples_
