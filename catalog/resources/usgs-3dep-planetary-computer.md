# USGS 3DEP seamless DEMs on Microsoft Planetary Computer

`res:usgs-3dep-planetary-computer` - dataset - <https://planetarycomputer.microsoft.com/dataset/3dep-seamless>

**By:** U.S. Geological Survey, Microsoft Planetary Computer - **Year:** ? - **Level:** intro - **Access:** open

The USGS 3D Elevation Program seamless bare-earth DEMs for the US, served as Cloud-Optimized GeoTIFFs through Planetary Computer's STAC API with the same SAS signing as NAIP. Licensed PDDL-1.0 per the STAC collection; the vpr-large-area sample uses it to get ground elevation under each drone frame.

## Key takeaways

- Same STAC search and signing flow as NAIP, so one helper covers imagery and terrain
- Gives ground height under a frame to turn barometric or GNSS altitude into height above ground
- US only; outside the US use Copernicus GLO-30

**Concepts:** [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md), [Terrain-relative navigation](../../catalog/concepts/terrain-nav.md), [GIS, maps and geospatial data](../../catalog/concepts/gis-mapping.md)

**Tags:** `3dep`, `dem`, `usgs`, `stac`, `cog`, `planetary-computer`

## Related

- dataset_for: [Large-area visual place recognition for lost-GNSS recovery (DINOv2 GeM / VLAD over a 49 km2 NAIP tile DB, chained to LightGlue fine matching)](../../catalog/samples/vpr-large-area.md)
- has_code: [pystac-client](../../catalog/repos/stac-utils__pystac-client.md)
- same_author: [NAIP aerial imagery on Microsoft Planetary Computer](../../catalog/resources/naip-planetary-computer.md)

_Indexed by lane(s): datasets-used_
