# Sample: Terrain-relative navigation with a particle filter

`sample:terrain-relative-nav-pf` - code and walkthrough in [samples/terrain-relative-nav-pf](../../samples/terrain-relative-nav-pf/)

A stdlib-only simulation of TERCOM/TRN: an aircraft with a biased INS and a radar altimeter matches its measured terrain profile against a seeded synthetic DEM with a particle filter that also estimates the INS velocity bias. Prints INS-only vs PF error over time, includes a flat-terrain control, and a rasterio loader for Copernicus GLO-30 tiles.

**Verification:** terrain.py and trn_pf.py ran with python3.14.7 stdlib on 2026-11-06, output shown in README; dem_rasterio.py is an unverified sketch: syntax-checked only, requires rasterio (the GLO-30 tile URL returned HTTP 200 on 2026-11-06).

## Practical readiness

| Compute | Hardware | Offline | Setup | Dataset download | Tested platforms | Validation |
|---|---|---|---|---|---|---|
| unknown | unknown | unknown | unknown | unknown | unknown | unverified |

**Main limitation:** Read the sample verification; readiness has not been curated.

## Deep dives

- [copernicus-glo30](../../docs/dataset-cards/copernicus-glo30.md) (dataset-cards)
- [blind-flight-teardown](../../docs/landscape/blind-flight-teardown.md) (landscape)

**Concepts:** [Terrain-relative navigation](../../catalog/concepts/terrain-nav.md), [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [GIS, maps and geospatial data](../../catalog/concepts/gis-mapping.md)

**Tags:** `tercom`, `trn`, `particle-filter`, `radar-altimeter`, `dem`, `copernicus-glo30`, `stdlib`, `python`

## Related

- explains: [python-tercom](../../catalog/repos/alti3__python-tercom.md)
- explains: [TERCOM via particle filter](../../catalog/repos/sotostrk__tercom-via-particle-filter-uav-state-estimation-mae6760-project-.md)
- explains: [tercom_nav (TERCOM + ESKF)](../../catalog/repos/mzahana__tercom_nav.md)
- explains: [terrain-nav-preprocessing](../../catalog/repos/hstm__terrain-nav-preprocessing.md)
- uses: [Rasterio](../../catalog/repos/rasterio__rasterio.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- ["Polyot vslepuyu" (Blind flight) 2026: problem teardown and seven public solutions](../../docs/landscape/blind-flight-teardown.md) (mentions)
- [Learning paths](../../docs/learning-paths.md) (mentions)
- [5. Absolute alternative PNT](../../docs/primer/05-absolute-alt-pnt.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Docs map](../../docs/README.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)

_Indexed by lane(s): samples_
