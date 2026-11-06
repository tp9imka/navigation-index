# Sample: Drone frame to orthophoto geolocalization with LightGlue

`sample:visual-geolocalization-lightglue` - code and walkthrough in [samples/visual-geolocalization-lightglue](../../samples/visual-geolocalization-lightglue/)

Matches a nadir drone frame against a georeferenced satellite or orthophoto tile with SuperPoint + LightGlue, fits a MAGSAC homography with OpenCV, and maps the frame centre through the GeoTIFF geotransform to lat/lon. The geometry (affine geotransform, homography mapping, WGS84 UTM, haversine) is a stdlib module with unit tests; the pipeline points at UAV-VisLoc, VPAIR and University-1652 for imagery and at hloc / AnyLoc for retrieval over large maps.

**Verification:** geo_math.py and test_geo_math.py ran with python3.14.7 stdlib on 2026-11-06 (12 tests OK), output shown in README; geolocalize.py is an unverified sketch: syntax-checked only, requires torch, lightglue, opencv-python, rasterio and numpy.

**Concepts:** [Visual geo-localization (image-to-map)](../concepts/visual-geolocalization.md), [Feature detection and matching](../concepts/feature-matching.md), [Place recognition and loop closure](../concepts/place-recognition.md), [Geodesy and coordinate frames](../concepts/geodesy.md), [Assured / resilient PNT](../concepts/assured-pnt.md)

**Tags:** `lightglue`, `superpoint`, `homography`, `geotiff`, `rasterio`, `opencv`, `gnss-denied`, `uav`

## Related

- uses: [LightGlue](../repos/cvg__lightglue.md)
- uses: [Rasterio](../repos/rasterio__rasterio.md)
- explains: [SuperPoint (pretrained)](../repos/magicleap__superpointpretrainednetwork.md)
- uses: [UAV-VisLoc dataset](../repos/intellisensing__uav-visloc.md)
- uses: [VPAIR](../repos/aervisloc__vpair.md)
- explains: [University-1652 baseline](../repos/layumi__university1652-baseline.md)
- explains: [hloc](../repos/cvg__hierarchical-localization.md)
- explains: [AnyLoc](../repos/anyloc__anyloc.md)

_Indexed by lane(s): samples_
