# Natural Earth vector data

`res:natural-earth-vectors` - dataset - <https://www.naturalearthdata.com/downloads/10m-physical-vectors/>

**By:** Natural Earth (NACIS volunteers) - **Year:** ? - **Level:** intro - **Access:** open

Public-domain world vector layers (land, coastline, countries) at 1:10m, 1:50m and 1:110m scales. Samples use the 10 m land polygon as an 'is this position on land' mask for AIS plausibility checks and the 50 m country borders as a basemap for interference maps.

## Key takeaways

- Public domain, small downloads, no login
- At 1:10m, canals, fjord heads and harbours are drawn as land: most 'on land' AIS alerts in the sample were coastline resolution
- Use a large-scale water mask for harbour-level checks

**Concepts:** [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md), [GIS, maps and geospatial data](../../catalog/concepts/gis-mapping.md), [Maritime navigation](../../catalog/concepts/maritime-nav.md)

**Tags:** `natural-earth`, `coastline`, `basemap`, `public-domain`, `shapefile`

## Related

- dataset_for: [GNSS spoofing signatures in real AIS tracks: detectors, injected ground truth, GeoJSON and CoT](../../catalog/samples/maritime-ais-spoofing.md)
- dataset_for: [OSINT interference map from free data: ADS-B NACp hexes and Sentinel-1 C-band RFI over Kaliningrad / the SE Baltic](../../catalog/samples/osint-jamming-map.md)

_Indexed by lane(s): datasets-used_
