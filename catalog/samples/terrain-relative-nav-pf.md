# Sample: Terrain-relative navigation with a particle filter

`sample:terrain-relative-nav-pf` - code and walkthrough in [samples/terrain-relative-nav-pf](../../samples/terrain-relative-nav-pf/)

A stdlib-only simulation of TERCOM/TRN: an aircraft with a biased INS and a radar altimeter matches its measured terrain profile against a seeded synthetic DEM with a particle filter that also estimates the INS velocity bias. Prints INS-only vs PF error over time, includes a flat-terrain control, and a rasterio loader for Copernicus GLO-30 tiles.

**Verification:** terrain.py and trn_pf.py ran with python3.14.7 stdlib on 2026-11-06, output shown in README; dem_rasterio.py is an unverified sketch: syntax-checked only, requires rasterio (the GLO-30 tile URL returned HTTP 200 on 2026-11-06).

**Concepts:** [Terrain-relative navigation](../concepts/terrain-nav.md), [Inertial navigation (INS/IMU)](../concepts/ins.md), [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [Assured / resilient PNT](../concepts/assured-pnt.md), [GIS, maps and geospatial data](../concepts/gis-mapping.md)

**Tags:** `tercom`, `trn`, `particle-filter`, `radar-altimeter`, `dem`, `copernicus-glo30`, `stdlib`, `python`

## Related

- explains: [python-tercom](../repos/alti3__python-tercom.md)
- explains: [TERCOM via particle filter](../repos/sotostrk__tercom-via-particle-filter-uav-state-estimation-mae6760-project-.md)
- explains: [tercom_nav (TERCOM + ESKF)](../repos/mzahana__tercom_nav.md)
- explains: [terrain-nav-preprocessing](../repos/hstm__terrain-nav-preprocessing.md)
- uses: [Rasterio](../repos/rasterio__rasterio.md)

_Indexed by lane(s): samples_
