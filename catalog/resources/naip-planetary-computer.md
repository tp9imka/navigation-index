# NAIP aerial imagery on Microsoft Planetary Computer

`res:naip-planetary-computer` - dataset - <https://planetarycomputer.microsoft.com/dataset/naip>

**By:** USDA Farm Service Agency, Microsoft Planetary Computer - **Year:** ? - **Level:** intermediate - **Access:** open

USDA National Agriculture Imagery Program leaf-on orthophotos (RGB + NIR) of the contiguous US, re-flown per state every few years, served as Cloud-Optimized GeoTIFFs behind a STAC API. Windows of a few square km can be read straight from the COGs after fetching a free SAS token. Resolution depends on state and year (0.3-1 m in the Ohio scenes the samples use).

## Key takeaways

- Public-domain-with-attribution reference map you can redistribute, unlike most satellite basemaps
- Several epochs of the same area make map-age experiments for visual geolocalization easy
- Unsigned blob URLs return HTTP 409; sign with planetary_computer or the SAS token endpoint
- US only; quarter-quad files are 0.4-1.4 GB, so read windows or overviews

## Deep dives

- [naip-planetary-computer](../../docs/dataset-cards/naip-planetary-computer.md) (dataset-cards)

**Concepts:** [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md), [Visual geo-localization (image-to-map)](../../catalog/concepts/visual-geolocalization.md), [GIS, maps and geospatial data](../../catalog/concepts/gis-mapping.md), [Place recognition and loop closure](../../catalog/concepts/place-recognition.md)

**Tags:** `naip`, `orthophoto`, `stac`, `cog`, `planetary-computer`, `aerial-imagery`, `usa`

## Related

- dataset_for: [License-clean drone frame to orthophoto geolocalization (ALIKED / DISK / SIFT + LightGlue)](../../catalog/samples/geoloc-license-clean.md)
- dataset_for: [Golden demo: GPS drag (position-only or coherent) on an ArduCopter SITL AUTO mission, integrity monitoring with solution separation + protection level, real visual geolocalization, EKF3 switch to ExternalNav, Monte Carlo, dashboard replay](../../catalog/samples/golden-demo.md)
- dataset_for: [Large-area visual place recognition for lost-GNSS recovery (DINOv2 GeM / VLAD over a 49 km2 NAIP tile DB, chained to LightGlue fine matching)](../../catalog/samples/vpr-large-area.md)
- has_code: [pystac-client](../../catalog/repos/stac-utils__pystac-client.md)
- has_code: [Rasterio](../../catalog/repos/rasterio__rasterio.md)

## Referenced by

- [OpenDroneMap Aukerman Park eBee image set](../../catalog/resources/odm-aukerman-ebee-dataset.md) (uses)
- [USGS 3DEP seamless DEMs on Microsoft Planetary Computer](../../catalog/resources/usgs-3dep-planetary-computer.md) (same_author)

_Indexed by lane(s): datasets-used_
