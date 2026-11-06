# OpenAerialMap

`res:openaerialmap` - dataset - <https://openaerialmap.org/>

**By:** Humanitarian OpenStreetMap Team, OpenAerialMap contributors - **Year:** ? - **Level:** intro - **Access:** open

An open catalogue of user-contributed aerial and drone orthomosaics, each stored as a Cloud-Optimized GeoTIFF on a public S3 bucket under CC BY 4.0. Coverage is patchy but global, which makes it a quick source of centimetre-level drone orthos outside the US with no login.

## Key takeaways

- Non-US, redistributable drone orthos for a visual-geolocalization demo map
- Scenes are EPSG:3857; convert units to ground metres (cos latitude) before quoting GSD
- Quality, date and georeference vary per uploader; check each scene
- Synthetic frames cut from the same ortho as the map are a best case, not a flight result

## Deep dives

- [openaerialmap](../../docs/dataset-cards/openaerialmap.md) (dataset-cards)

**Concepts:** [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md), [Visual geo-localization (image-to-map)](../../catalog/concepts/visual-geolocalization.md), [GIS, maps and geospatial data](../../catalog/concepts/gis-mapping.md)

**Tags:** `orthophoto`, `drone-imagery`, `cog`, `cc-by-4.0`, `hotosm`

## Related

- dataset_for: [Drone frame to orthophoto geolocalization with LightGlue](../../catalog/samples/visual-geolocalization-lightglue.md)
- uses: [LightGlue](../../catalog/repos/cvg__lightglue.md)

_Indexed by lane(s): datasets-used_
