# OpenDroneMap (ODM)

`repo:opendronemap/odm` - <https://github.com/opendronemap/odm>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 6,584 | Python | AGPL-3.0 | 2026-10-29 | False | production | high |

Photogrammetry toolkit that turns aerial images into orthophotos, point clouds, 3D models and DEMs.

**Why it matters:** Build your own up-to-date reference orthophoto and DSM from a survey flight for visual and terrain navigation.

**Hackathon notes:** docker run opendronemap/odm on a folder of images; WebODM gives a GUI. Processing time scales with image count.

**Concepts:** [GIS, maps and geospatial data](../../catalog/concepts/gis-mapping.md), [Terrain-relative navigation](../../catalog/concepts/terrain-nav.md), [Visual geo-localization (image-to-map)](../../catalog/concepts/visual-geolocalization.md)

**Tags:** `photogrammetry`, `orthophoto`, `dsm`

**Domains:** air

## Related

- depends_on: [GDAL](../../catalog/repos/osgeo__gdal.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [7. Maps, geodesy and planning](../../docs/primer/07-maps-geodesy-planning.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [OpenDroneMap Aukerman Park eBee image set](../../catalog/resources/odm-aukerman-ebee-dataset.md) (has_code)
- [License-clean drone frame to orthophoto geolocalization (ALIKED / DISK / SIFT + LightGlue)](../../catalog/samples/geoloc-license-clean.md) (explains)

_Indexed by lane(s): planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
