# Sample: Drone frame to orthophoto geolocalization with LightGlue

`sample:visual-geolocalization-lightglue` - code and walkthrough in [samples/visual-geolocalization-lightglue](../../samples/visual-geolocalization-lightglue/)

Matches a nadir drone frame against a georeferenced satellite or orthophoto tile with SuperPoint + LightGlue, fits a MAGSAC homography with OpenCV, and maps the frame centre through the GeoTIFF geotransform to lat/lon. The geometry (affine geotransform, homography mapping, WGS84 UTM, haversine) is a stdlib module with unit tests; the pipeline points at UAV-VisLoc, VPAIR and University-1652 for imagery and at hloc / AnyLoc for retrieval over large maps.

**Verification:** geo_math.py and 12 unit tests ran with python3.14.7 stdlib on 2026-11-06. geolocalize.py ran on 2026-11-06 with torch 2.15.0 (CPU), LightGlue git 5a650c4, opencv-python 5.0.0.93, rasterio 1.5.2 on Python 3.12.14 against synthetic pairs cut from one public OpenAerialMap orthophoto (Tbilisi, CC-BY 4.0): 0.04-0.21 m error for yaw 0/60/135 deg, tilt and 60-150 m priors; 30.7 m error with 162 inliers when 40% of the frame was nodata at the ortho edge; a frame from a different city gave no fix (5 inliers). Frame and map come from the same survey, so this is a pipeline/geometry check, not a cross-season or real-UAV result; UAV-VisLoc/VPAIR/University-1652 were not run.

## Practical readiness

| Compute | Hardware | Offline | Setup | Dataset download | Tested platforms | Validation |
|---|---|---|---|---|---|---|
| unknown | unknown | unknown | unknown | unknown | unknown | unverified |

**Main limitation:** Read the sample verification; readiness has not been curated.

## Deep dives

- [openaerialmap](../../docs/dataset-cards/openaerialmap.md) (dataset-cards)

**Concepts:** [Visual geo-localization (image-to-map)](../../catalog/concepts/visual-geolocalization.md), [Feature detection and matching](../../catalog/concepts/feature-matching.md), [Place recognition and loop closure](../../catalog/concepts/place-recognition.md), [Geodesy and coordinate frames](../../catalog/concepts/geodesy.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md)

**Tags:** `lightglue`, `superpoint`, `homography`, `geotiff`, `rasterio`, `opencv`, `gnss-denied`, `uav`

## Related

- uses: [LightGlue](../../catalog/repos/cvg__lightglue.md)
- uses: [Rasterio](../../catalog/repos/rasterio__rasterio.md)
- explains: [SuperPoint (pretrained)](../../catalog/repos/magicleap__superpointpretrainednetwork.md)
- uses: [UAV-VisLoc dataset](../../catalog/repos/intellisensing__uav-visloc.md)
- uses: [VPAIR](../../catalog/repos/aervisloc__vpair.md)
- explains: [University-1652 baseline](../../catalog/repos/layumi__university1652-baseline.md)
- explains: [hloc](../../catalog/repos/cvg__hierarchical-localization.md)
- explains: [AnyLoc](../../catalog/repos/anyloc__anyloc.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Learning paths](../../docs/learning-paths.md) (mentions)
- [5. Absolute alternative PNT](../../docs/primer/05-absolute-alt-pnt.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [OpenAerialMap](../../catalog/resources/openaerialmap.md) (dataset_for)

_Indexed by lane(s): samples_
