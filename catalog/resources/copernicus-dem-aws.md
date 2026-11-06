# Copernicus DEM on AWS Open Data

`res:copernicus-dem-aws` - dataset - <https://registry.opendata.aws/copernicus-dem/>

**By:** ESA / Copernicus, AWS Open Data - **Year:** 2026 - **Level:** intro - **Access:** open

Registry entry for the Copernicus global DEM (GLO-30/GLO-90) hosted as cloud-optimized GeoTIFFs on AWS, freely accessible without an account.

## Key takeaways

- Global 30 m DEM as COGs - sample directly with rasterio
- Good default terrain for terrain-referenced nav and planning

**Concepts:** [Terrain-relative navigation](../concepts/terrain-nav.md), [GIS, maps and geospatial data](../concepts/gis-mapping.md), [Datasets and benchmarks](../concepts/datasets-benchmarks.md)

**Tags:** `dem`, `copernicus`, `cog`

## Related

- uses: [elevation](../repos/bopen__elevation.md)
- uses: [Rasterio](../repos/rasterio__rasterio.md)

## Referenced by

- [OSINT interference map from free data: ADS-B NACp hexes and Sentinel-1 C-band RFI over Kaliningrad / the SE Baltic](../samples/osint-jamming-map.md) (uses)
- [Heightmap-gradient particle filter on real Copernicus DEM (SPRIN-D CTU method) vs TERCOM](../samples/terrain-heightmap-pf.md) (uses)

_Indexed by lane(s): planning-gis-c2_
