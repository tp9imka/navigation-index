# Sample: Night / thermal UAV frame to RGB satellite geolocalization with a no-false-fix gate (ALIKED / DISK / SIFT + LightGlue, SGM baseline, Thermal-UAV)

`sample:thermal-geolocalization` - code and walkthrough in [samples/thermal-geolocalization](../../samples/thermal-geolocalization/)

Real nadir DJI M4T thermal frames (Thermal-UAV / SCC-Loc, Apache-2.0 card) matched against the dataset's 0.3 m RGB satellite GeoTIFF, by condition: city and village, day and night, day and night fog. Compares ALIKED, DISK and SIFT with LightGlue (license-clean) under three modality-bridging preprocessings (raw, CLAHE, gradient magnitude), fits a 4-DOF similarity and gates fixes on inliers, inlier ratio, scale, rotation and search radius. Reports fix rate, error, false-fix count and M2 runtime on CPU and MPS, checks the gate on held-out validation-split flights, and runs the IROS 2023 SGM thermal-to-satellite retrieval network (MIT code, unlicensed research-only weights) as an out-of-domain baseline. fetch_data.py pulls a 180-frame subset out of the 19.9 GB ZIP with HTTP range requests.

**Verification:** Ran 2026-11-06 on Apple M2 Max (torch 2.15.0, LightGlue git 5a650c4, OpenCV 5.0.0, Python 3.12.14): fetch_data.py pulled 180 Thermal-UAV frames (9 flights) and cropped the 0.3 m ref.tif (~2.8 GB transfer); run_eval.py on MPS, 120 frames from 6 flights (111 on the map), revised gate: ALIKED/grad 18/111 fixes (median 2.6 m), ALIKED/raw 16/111 (3.3 m), DISK/grad 15/111, SIFT 1/111; village-night best with ALIKED/grad 9/20, village-night-fog 0/14 for every method; 0 false fixes in 1080 attempts (84 accepted), and 0 in 540 attempts (37 accepted) on 3 held-out validation-split flights. The revised gate was chosen after the first run (a-priori gate: 32 accepted, 0 false). SGM retrieval (research-only weights): top-1 within 20 m on 26-29/111, 182 of 238 ungated fixes false. Median s/frame CPU vs MPS: ALIKED 1.26 / 0.18, DISK 2.42 / 0.29, SIFT 0.21 / 0.30. Tests: 11 pass in the venv; plain python3 9 pass, 2 skip. Boson-nighttime (gated, NC, 74 GB), STHN/UASTHN fine stages, MINIMA and RoMa were not run.

**Concepts:** [Visual geo-localization (image-to-map)](../../catalog/concepts/visual-geolocalization.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md), [Feature detection and matching](../../catalog/concepts/feature-matching.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md)

**Tags:** `thermal`, `night`, `infrared`, `lightglue`, `aliked`, `disk`, `sift`, `clahe`, `cross-modal`, `integrity`, `false-fix`, `geotiff`, `mps`, `gnss-denied`, `uav`

## Related

- uses: [License-clean drone frame to orthophoto geolocalization (ALIKED / DISK / SIFT + LightGlue)](../../catalog/samples/geoloc-license-clean.md)
- uses: [SCC-Loc](../../catalog/repos/floralhercules__scc-loc.md)
- uses: [Satellite-thermal geo-localization](../../catalog/repos/arplaboratory__satellite-thermal-geo-localization.md)
- explains: [Long-range UAV Thermal Geo-localization with Satellite Imagery](../../catalog/resources/thermal-geolocalization-iros-2023.md)
- explains: [STHN](../../catalog/repos/arplaboratory__sthn.md)
- explains: [UASTHN](../../catalog/repos/arplaboratory__uasthn.md)
- explains: [UASTHN: Uncertainty-Aware Deep Homography Estimation for UAV Satellite-Thermal Geo-localization](../../catalog/resources/uasthn-uncertainty-thermal-2025.md)
- explains: [ScalLoc](../../catalog/repos/floralhercules__scalloc.md)
- explains: [CART - Caltech Aerial RGB-Thermal](../../catalog/repos/aerorobotics__caltech-aerial-rgbt-dataset.md)
- uses: [LightGlue](../../catalog/repos/cvg__lightglue.md)
- uses: [Rasterio](../../catalog/repos/rasterio__rasterio.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [Fixed-wing golden demo: ArduPlane 4.6.3 SITL on a 27.6 km route, coherent GPS drag, golden-demo monitor, EKF3 switch to ExternalNav fed by measured day (VPAIR) and night (thermal) geoloc fix models vs airspeed dead reckoning only](../../catalog/samples/golden-demo-fixedwing.md) (uses)

_Indexed by lane(s): samples_
