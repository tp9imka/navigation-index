# pystac-client

`repo:stac-utils/pystac-client` - <https://github.com/stac-utils/pystac-client>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 211 | Python | NOASSERTION | 2026-11-03 | False | production | high |

Python client for searching STAC APIs (Earth Search, Planetary Computer and others) by area, time and properties.

**Why it matters:** Credential-free path to Sentinel-2, Landsat and Copernicus DEM tiles via public STAC catalogs.

**Hackathon notes:** Search Earth Search (AWS) without a key and read COGs directly with rasterio.

## Deep dives

- [naip-planetary-computer](../../docs/dataset-cards/naip-planetary-computer.md) (dataset-cards)
- [sentinel-1-grd](../../docs/dataset-cards/sentinel-1-grd.md) (dataset-cards)

**Concepts:** [GIS, maps and geospatial data](../../catalog/concepts/gis-mapping.md), [Visual geo-localization (image-to-map)](../../catalog/concepts/visual-geolocalization.md)

**Tags:** `stac`, `satellite-imagery`, `cog`

**Domains:** multi

## Related

- integrates_with: [odc-stac](../../catalog/repos/opendatacube__odc-stac.md)
- integrates_with: [Rasterio](../../catalog/repos/rasterio__rasterio.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [5. Absolute alternative PNT](../../docs/primer/05-absolute-alt-pnt.md) (mentions)
- [7. Maps, geodesy and planning](../../docs/primer/07-maps-geodesy-planning.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [odc-stac](../../catalog/repos/opendatacube__odc-stac.md) (integrates_with)
- [sentinelhub-py](../../catalog/repos/sentinel-hub__sentinelhub-py.md) (alternative_to)
- [NAIP aerial imagery on Microsoft Planetary Computer](../../catalog/resources/naip-planetary-computer.md) (has_code)
- [Sentinel-1 Level-1 GRD on Microsoft Planetary Computer](../../catalog/resources/sentinel-1-grd-planetary-computer.md) (has_code)
- [SpatioTemporal Asset Catalog (STAC) specification](../../catalog/resources/stac-spec.md) (has_code)
- [USGS 3DEP seamless DEMs on Microsoft Planetary Computer](../../catalog/resources/usgs-3dep-planetary-computer.md) (has_code)
- [OSINT interference map from free data: ADS-B NACp hexes and Sentinel-1 C-band RFI over Kaliningrad / the SE Baltic](../../catalog/samples/osint-jamming-map.md) (uses)

_Indexed by lane(s): planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
