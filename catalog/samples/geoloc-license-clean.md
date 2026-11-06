# Sample: License-clean drone frame to orthophoto geolocalization (ALIKED / DISK / SIFT + LightGlue)

`sample:geoloc-license-clean` - code and walkthrough in [samples/geoloc-license-clean](../../samples/geoloc-license-clean/)

Drone frame => NAIP orthophoto => lat/lon using only permissively licensed parts: ALIKED (BSD-3), DISK and LightGlue weights (Apache-2.0), OpenCV SIFT and MAGSAC (Apache-2.0), rasterio, public-domain NAIP from Microsoft Planetary Computer and CC0 eBee frames from OpenDroneMap. Generates synthetic frames with known truth (rotation, scale, perspective, photometric change, cross-season source) and runs real UAV frames with EXIF GPS as truth. Measured error and CPU runtime per frame are in the README.

**Verification:** PLACEHOLDER

**Concepts:** [Visual geo-localization (image-to-map)](../concepts/visual-geolocalization.md), [Feature detection and matching](../concepts/feature-matching.md), [Assured / resilient PNT](../concepts/assured-pnt.md), [GIS, maps and geospatial data](../concepts/gis-mapping.md)

**Tags:** `lightglue`, `aliked`, `disk`, `sift`, `naip`, `planetary-computer`, `geotiff`, `rasterio`, `opencv`, `license`, `gnss-denied`, `uav`

## Related

- uses: [LightGlue](../repos/cvg__lightglue.md)
- uses: [Rasterio](../repos/rasterio__rasterio.md)
- explains: [OpenDroneMap (ODM)](../repos/opendronemap__odm.md)
- explains: [Glue Factory](../repos/cvg__glue-factory.md)
- explains: [SuperPoint (pretrained)](../repos/magicleap__superpointpretrainednetwork.md)
- explains: [UAV-VisLoc dataset](../repos/intellisensing__uav-visloc.md)

_Indexed by lane(s): samples_
