# Sample: Large-area visual place recognition for lost-GNSS recovery (DINOv2 GeM / VLAD over a 49 km2 NAIP tile DB, chained to LightGlue fine matching)

`sample:vpr-large-area` - code and walkthrough in [samples/vpr-large-area](../../samples/vpr-large-area/)

The coarse first stage that geoloc-license-clean lacks: no position prior, unknown heading. Builds a geo-referenced tile DB over 49 km2 of public-domain NAIP (Planetary Computer, 5 vintages 2015-2023) at 250 m and 100 m tile sizes, 8 rotations. Global descriptors from DINOv2 ViT-S/14 (Apache-2.0): CLS, GeM, AnyLoc-style hard VLAD (own implementation), plus a classic rotation-invariant ring-histogram baseline. Compares four rotation strategies (none, query TTA, rotation-augmented DB, rotation-averaged invariant descriptor). Reports recall@1/5/10 within 50/100/250 m, latency and index size per map-vintage gap, then chains top-5 retrieval into ALIKED+LightGlue fine matching with the inlier gate and compares with fine matching given a known prior. Real CC0 eBee frames (2016) are also run.

**Verification:** Ran 2026-11-06 on Apple M2 Max (DINOv2 ViT-S/14 on MPS, LightGlue on CPU, torch 2.15.0, Python 3.12.14): download_data.py fetched 49 km2 of NAIP 2015/2017/2019/2021/2023 from Planetary Computer, 23 CC0 eBee frames and 3DEP heights; run_vpr.py built 250 m and 100 m tile DBs (18.5k / 19.3k tiles x 8 rotations, ~9 min each) and scored 150 synthetic queries per source year: same imagery R@1 within 50 m 0.77 and R@10 within 100 m 0.98 (gem/invariant8, 250 m tiles), 2-8 year vintage gap 0.18-0.29 / 0.48-0.73; rotation-averaged GeM matched or beat an 8x rotation-augmented DB at 1/8 the index size; classic ring histogram R@10 within 250 m <= 0.13. Real eBee frames vs 2023 DB: cls/invariant8 R@1 within 50 m 0.70-0.74 (23 frames in one park). run_chain.py (VPR top-5 => ALIKED+LightGlue, 25-inlier gate): synthetic 20/20 fixes (same imagery, 0.22 m median), 8/20 and 3/20 at 6 and 4 year gaps vs 20/20 and 12/20 with a known prior; real eBee 0/23 with 100 m windows, 1/23 (20 m) with 50 m windows; no wrong fix accepted. Tests: 23 unittest cases pass in the venv; with plain python3 12 pass and 11 skip (numpy/OpenCV/torch absent).

**Concepts:** [Visual geo-localization (image-to-map)](../../catalog/concepts/visual-geolocalization.md), [Place recognition and loop closure](../../catalog/concepts/place-recognition.md), [Feature detection and matching](../../catalog/concepts/feature-matching.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [GIS, maps and geospatial data](../../catalog/concepts/gis-mapping.md)

**Tags:** `dinov2`, `gem`, `vlad`, `anyloc`, `faiss`, `vpr`, `naip`, `planetary-computer`, `kidnapped-robot`, `lightglue`, `aliked`, `gnss-denied`, `uav`, `license`

## Related

- uses: [License-clean drone frame to orthophoto geolocalization (ALIKED / DISK / SIFT + LightGlue)](../../catalog/samples/geoloc-license-clean.md)
- explains: [AnyLoc](../../catalog/repos/anyloc__anyloc.md)
- explains: [AnyLoc: Towards Universal Visual Place Recognition](../../catalog/resources/anyloc-universal-vpr-2023.md)
- uses: [LightGlue](../../catalog/repos/cvg__lightglue.md)
- uses: [Rasterio](../../catalog/repos/rasterio__rasterio.md)
- explains: [EigenPlaces](../../catalog/repos/gmberton__eigenplaces.md)
- explains: [BoQ](../../catalog/repos/amaralibey__bag-of-queries.md)
- explains: [UAVLocalization (map retrieval + alignment)](../../catalog/repos/hmf21__uavlocalization.md)
- explains: [AnyVisLoc benchmark](../../catalog/repos/uav-avl__benchmark.md)
- explains: [VPR methods evaluation](../../catalog/repos/gmberton__vpr-methods-evaluation.md)

## Referenced by

- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [NAIP aerial imagery on Microsoft Planetary Computer](../../catalog/resources/naip-planetary-computer.md) (dataset_for)
- [OpenDroneMap Aukerman Park eBee image set](../../catalog/resources/odm-aukerman-ebee-dataset.md) (dataset_for)
- [USGS 3DEP seamless DEMs on Microsoft Planetary Computer](../../catalog/resources/usgs-3dep-planetary-computer.md) (dataset_for)

_Indexed by lane(s): samples_
