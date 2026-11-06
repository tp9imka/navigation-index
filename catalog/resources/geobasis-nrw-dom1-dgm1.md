# Geobasis NRW DOM1 / DGM1 1 m airborne LiDAR surface and terrain models

`res:geobasis-nrw-dom1-dgm1` - dataset - <https://www.opengeodata.nrw.de/produkte/geobasis/hm/>

**By:** Geobasis NRW (Bezirksregierung Koeln) - **Year:** ? - **Level:** intermediate - **Access:** open

North Rhine-Westphalia's open-data 1 m digital surface model (DOM1, buildings and vegetation included) and 1 m bare-earth terrain model (DGM1) for the whole state, delivered as 1 x 1 km GeoTIFF tiles in ETRS89 / UTM 32N with no login. Licensed dl-de/zero-2.0, so no attribution is required.

## Key takeaways

- A real high-resolution prior map for terrain or heightmap navigation in a European setting
- In the terrain-heightmap sample, edge-based matching that failed on 30 m GLO-30 worked on the 1 m surface model
- Tile names carry the flight year, which differs by area; list the directory if a name 404s
- NRW only; DOM1 vegetation changes with season

## Deep dives

- [geobasis-nrw-lidar](../../docs/dataset-cards/geobasis-nrw-lidar.md) (dataset-cards)

**Concepts:** [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md), [Terrain-relative navigation](../../catalog/concepts/terrain-nav.md), [GIS, maps and geospatial data](../../catalog/concepts/gis-mapping.md)

**Tags:** `lidar`, `dsm`, `dtm`, `dem`, `germany`, `geotiff`, `dl-de-zero`

## Related

- dataset_for: [Heightmap-gradient particle filter on real DEM and 1 m LiDAR (SPRIN-D CTU method) vs TERCOM](../../catalog/samples/terrain-heightmap-pf.md)
- has_code: [Rasterio](../../catalog/repos/rasterio__rasterio.md)

## Referenced by

- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Multi-source fault detection and exclusion on one real flight: ARAIM-style subset exclusion across GNSS, visual fixes and two TRNs (VPAIR)](../../catalog/samples/multi-source-fde.md) (uses)
- [Two independent absolute sources on one real flight: visual fixes + terrain-relative navigation with solution-separation integrity (VPAIR over NRW 1 m LiDAR)](../../catalog/samples/two-source-integrity-vpair.md) (uses)

_Indexed by lane(s): datasets-used_
