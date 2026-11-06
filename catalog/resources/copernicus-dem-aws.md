# Copernicus DEM on AWS Open Data

`res:copernicus-dem-aws` - dataset - <https://registry.opendata.aws/copernicus-dem/>

**By:** ESA / Copernicus, AWS Open Data - **Year:** 2026 - **Level:** intro - **Access:** open

Registry entry for the Copernicus global DEM (GLO-30/GLO-90) hosted as cloud-optimized GeoTIFFs on AWS, freely accessible without an account.

## Key takeaways

- Global 30 m DEM as COGs - sample directly with rasterio
- Good default terrain for terrain-referenced nav and planning

## Deep dives

- [copernicus-glo30](../../docs/dataset-cards/copernicus-glo30.md) (dataset-cards)
- [blind-flight-teardown](../../docs/landscape/blind-flight-teardown.md) (landscape)

**Concepts:** [Terrain-relative navigation](../../catalog/concepts/terrain-nav.md), [GIS, maps and geospatial data](../../catalog/concepts/gis-mapping.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md)

**Tags:** `dem`, `copernicus`, `cog`

## Related

- uses: [elevation](../../catalog/repos/bopen__elevation.md)
- uses: [Rasterio](../../catalog/repos/rasterio__rasterio.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- ["Polyot vslepuyu" (Blind flight) 2026: problem teardown and seven public solutions](../../docs/landscape/blind-flight-teardown.md) (mentions)
- [5. Absolute alternative PNT](../../docs/primer/05-absolute-alt-pnt.md) (mentions)
- [7. Maps, geodesy and planning](../../docs/primer/07-maps-geodesy-planning.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Docs map](../../docs/README.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [Sentinel-1 Level-1 GRD on Microsoft Planetary Computer](../../catalog/resources/sentinel-1-grd-planetary-computer.md) (same_author)
- [Blind-flight bench: radar altimeter + Copernicus GLO-30 TRN, six navigators on one harness](../../catalog/samples/blind-flight-bench.md) (uses)
- [OSINT interference map from free data: ADS-B NACp hexes and Sentinel-1 C-band RFI over Kaliningrad / the SE Baltic](../../catalog/samples/osint-jamming-map.md) (uses)
- [Heightmap-gradient particle filter on real DEM and 1 m LiDAR (SPRIN-D CTU method) vs TERCOM](../../catalog/samples/terrain-heightmap-pf.md) (uses)

_Indexed by lane(s): planning-gis-c2_
