# Sentinel-1 RFI detection

`repo:zephr-xyz/sentinel1-rfi-detection` - <https://github.com/zephr-xyz/sentinel1-rfi-detection>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 30 | Python | MIT | 2026-03-25 | False | active-research | high |

Pipeline that flags radio-frequency interference in Sentinel-1 C-band SAR scenes using temporal z-scores and DEM slope masking, run over Iran, the Persian Gulf and Jammertest 2025.

**Why it matters:** Free satellite data as a wide-area RFI sensor, complementing ADS-B based maps - but Sentinel-1 is C-band, and the authors' own Jammertest analysis could not tie detections to L-band GNSS jammers.

**Hackathon notes:** Needs a free Copernicus Data Space account. Pull Sentinel-1 scenes for a region and produce an RFI heatmap; present it as an RFI map, not a proven jamming map. MIT.

## Deep dives

- [sentinel-1-grd](../../docs/dataset-cards/sentinel-1-grd.md) (dataset-cards)

**Concepts:** [Jamming and spoofing](../../catalog/concepts/gnss-interference.md), [Situational awareness and C2 interop](../../catalog/concepts/situational-awareness.md), [GIS, maps and geospatial data](../../catalog/concepts/gis-mapping.md)

**Tags:** `sentinel-1`, `sar`, `rfi`, `osint`

**Domains:** space, multi

## Referenced by

- [Sentinel-1 Level-1 GRD on Microsoft Planetary Computer](../../catalog/resources/sentinel-1-grd-planetary-computer.md) (has_code)
- [OSINT interference map from free data: ADS-B NACp hexes and Sentinel-1 C-band RFI over Kaliningrad / the SE Baltic](../../catalog/samples/osint-jamming-map.md) (uses)

_Indexed by lane(s): round3-expansion_

_GitHub metadata fetched 2026-11-06._
