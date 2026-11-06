# Sentinel-1 Level-1 GRD on Microsoft Planetary Computer

`res:sentinel-1-grd-planetary-computer` - dataset - <https://planetarycomputer.microsoft.com/dataset/sentinel-1-grd>

**By:** ESA / Copernicus, Microsoft Planetary Computer - **Year:** ? - **Level:** advanced - **Access:** open

Copernicus Sentinel-1 C-band SAR Ground Range Detected scenes mirrored as Cloud-Optimized GeoTIFFs (VV, VH) together with the SAFE XML annotations, which include ESA's per-swath RF interference report. Readable anonymously after URL signing, no Copernicus account needed. Free and open under the Copernicus data policy.

## Key takeaways

- ESA's rfiDetected annotation plus a temporal z-score over a stack gives a C-band RF-activity context layer
- C-band, not L-band: it sees radars and broadband emissions, not a GNSS jammer's intended signal
- One snapshot per pass, every 6 days per orbit track in the 2026 stack; read COG overviews, full VH is about 0.5 GB
- Some scenes can be missing from the mirror

## Deep dives

- [sentinel-1-grd](../../docs/dataset-cards/sentinel-1-grd.md) (dataset-cards)

**Concepts:** [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md), [Electronic warfare resilience](../../catalog/concepts/ew-resilience.md), [Situational awareness and C2 interop](../../catalog/concepts/situational-awareness.md), [Jamming and spoofing](../../catalog/concepts/gnss-interference.md)

**Tags:** `sentinel-1`, `sar`, `rfi`, `copernicus`, `stac`, `cog`, `planetary-computer`

## Related

- dataset_for: [OSINT interference map from free data: ADS-B NACp hexes and Sentinel-1 C-band RFI over Kaliningrad / the SE Baltic](../../catalog/samples/osint-jamming-map.md)
- has_code: [Sentinel-1 RFI detection](../../catalog/repos/zephr-xyz__sentinel1-rfi-detection.md)
- has_code: [pystac-client](../../catalog/repos/stac-utils__pystac-client.md)
- same_author: [Copernicus DEM on AWS Open Data](../../catalog/resources/copernicus-dem-aws.md)

_Indexed by lane(s): datasets-used_
