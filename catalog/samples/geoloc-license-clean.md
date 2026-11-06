# Sample: License-clean drone frame to orthophoto geolocalization (ALIKED / DISK / SIFT + LightGlue)

`sample:geoloc-license-clean` - code and walkthrough in [samples/geoloc-license-clean](../../samples/geoloc-license-clean/)

Drone frame => NAIP orthophoto => lat/lon using only permissively licensed parts: ALIKED (BSD-3), DISK and LightGlue weights (Apache-2.0), OpenCV SIFT and MAGSAC (Apache-2.0), rasterio, public-domain NAIP from Microsoft Planetary Computer and CC0 eBee frames from OpenDroneMap. Generates synthetic frames with known truth (rotation, scale, perspective, photometric change, cross-season source) and runs real UAV frames with EXIF GPS as truth. Measured error and CPU runtime per frame are in the README.

**Verification:** Ran 2026-11-06 on Apple M2 Max CPU (torch 2.15.0, Python 3.12.14): download_data.py fetched NAIP 2023/2019 windows from Planetary Computer and 5 CC0 eBee frames; run_eval.py on 20 synthetic frames per case: same-map median error 0.10-0.11 m for ALIKED/DISK/SIFT+LightGlue (0.28-2.8 s/frame), cross-season 1.9-4.8 m with 13-20/20 fixes; real eBee frames vs NAIP: 1 fix out of 5 (ALIKED, 2019 map, tight prior, 11.0 m error), 0/5 in all other configs. Numbers and logs in README.

## Deep dives

- [naip-planetary-computer](../../docs/dataset-cards/naip-planetary-computer.md) (dataset-cards)

**Concepts:** [Visual geo-localization (image-to-map)](../../catalog/concepts/visual-geolocalization.md), [Feature detection and matching](../../catalog/concepts/feature-matching.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [GIS, maps and geospatial data](../../catalog/concepts/gis-mapping.md)

**Tags:** `lightglue`, `aliked`, `disk`, `sift`, `naip`, `planetary-computer`, `geotiff`, `rasterio`, `opencv`, `license`, `gnss-denied`, `uav`

## Related

- uses: [LightGlue](../../catalog/repos/cvg__lightglue.md)
- uses: [Rasterio](../../catalog/repos/rasterio__rasterio.md)
- explains: [OpenDroneMap (ODM)](../../catalog/repos/opendronemap__odm.md)
- explains: [Glue Factory](../../catalog/repos/cvg__glue-factory.md)
- explains: [SuperPoint (pretrained)](../../catalog/repos/magicleap__superpointpretrainednetwork.md)
- explains: [UAV-VisLoc dataset](../../catalog/repos/intellisensing__uav-visloc.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Integrity monitoring for navigation and alt-PNT](../../docs/integrity-monitoring.md) (mentions)
- [Model weights licenses: code vs weights vs training data](../../docs/model-weights-licenses.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [NAIP aerial imagery on Microsoft Planetary Computer](../../catalog/resources/naip-planetary-computer.md) (dataset_for)
- [OpenDroneMap Aukerman Park eBee image set](../../catalog/resources/odm-aukerman-ebee-dataset.md) (dataset_for)
- [Integrity monitoring for alt-PNT: solution-separation FDE, protection levels and a Stanford diagram](../../catalog/samples/altpnt-integrity.md) (uses)
- [End-to-end GNSS-denied visual navigation on one real flight: nadir VO + DINOv2 retrieval + LightGlue fixes + multi-frame voting + altpnt integrity (VPAIR)](../../catalog/samples/e2e-visual-nav-vpair.md) (uses)
- [Large-area visual place recognition for lost-GNSS recovery (DINOv2 GeM / VLAD over a 49 km2 NAIP tile DB, chained to LightGlue fine matching)](../../catalog/samples/vpr-large-area.md) (uses)

_Indexed by lane(s): samples_
