# Sentinel-1 GRD on Planetary Computer (with ESA RFI annotations)

<!-- about: repo:zephr-xyz/sentinel1-rfi-detection, sample:osint-jamming-map, repo:stac-utils/pystac-client -->

Copernicus Sentinel-1 C-band SAR, Level-1 Ground Range Detected scenes, mirrored by Microsoft Planetary Computer as Cloud-Optimized GeoTIFFs (VV, VH) plus the SAFE XML annotations, including ESA's per-swath RF interference report. Readable anonymously after URL signing, no Copernicus account. No index id for the dataset itself; the marker names the RFI-detection repo the sample ports, the sample and the STAC client.

| Field | Value |
|---|---|
| Platform | Sentinel-1 satellites; in 2026 S1C and S1D alternate (the sample's stack: relative orbit 51, descending, every 6 days) |
| Environment | Global land and coastal; repeat on one orbit track was 6 days in the sample's 2026 stack |
| Sensors and rates | C-band SAR, 5.405 GHz receive. IW mode, dual-pol VV + VH. ESA noise-sensing RFI report per swath roughly every 5.5 s (sample README) |
| Ground truth | None for RFI. ESA's `rfiDetected` flag and mitigation type per swath are processor outputs, not truth |
| Size | One IW GRDH VH COG (`S1D_IW_GRDH_1SDV_20261001T045103_..._0090AC`) = 494,365,368 B (HEAD with SAS token, 2026-11-06). The sample reads VH at 1/8 through COG overviews: 18 scenes => about 440 MB cache |
| License | Copernicus Sentinel data, free and open under the Copernicus data policy (STAC collection: `proprietary`, link to the Sentinel Data Legal Notice); credit "Contains modified Copernicus Sentinel data <year>". Planetary Computer terms apply to the hosting |
| Format | COG GeoTIFF per polarization (uint16 DN, geolocation via GCPs); XML assets `schema-product-vh/vv` (the href ends in `annotation/rfi/rfi-iw-vh.xml`), `schema-noise-*`, `schema-calibration-*` |
| Index | [sentinel1-rfi-detection](../../catalog/repos/zephr-xyz__sentinel1-rfi-detection.md), [pystac-client](../../catalog/repos/stac-utils__pystac-client.md), [osint-jamming-map sample](../../samples/osint-jamming-map/) |

## Download

```bash
# STAC search for a stack over a point, sign, read windows/overviews (pystac-client + planetary_computer + rasterio)
python3 samples/osint-jamming-map/s1_rfi.py                       # defaults: Kaliningrad, 2026-10-01, 18-scene stack
python3 samples/osint-jamming-map/s1_rfi.py --date 2026-08-14 --out out_0814
```

Collection `sentinel-1-grd` (STAC temporal extent from 2014-10-10, open-ended). Unsigned blob URLs answer HTTP 409 "Public access is not permitted"; sign with `planetary_computer.sign()` or a token from `https://planetarycomputer.microsoft.com/api/sas/v1/token/sentinel-1-grd`.

## Used in this repo

[samples/osint-jamming-map](../../samples/osint-jamming-map/) `s1_rfi.py`, run 2026-11-06, about 8 min:

- Stack 2026-07-15 to 2026-10-31, 18 scenes; 2026-10-13 is missing on Planetary Computer.
- ESA annotation flagged RFI on 9 of 18 passes, with time-frequency mitigation on exactly those; one IW3 slot NW of the Sambia peninsula flagged on 6 dates.
- Temporal z-score (port of zephr-xyz): nothing on the target date; 2026-08-14 lit up 38 hexes, mostly over sea, which a wind change also explains. Read as "unusual pass", not "jammer".
- GNSS is L-band; Sentinel-1 receives at C-band. It sees C-band radars, 5 GHz RLAN and broadband spurious emissions, not a GNSS jammer's intended signal.

## Loading and tooling

- pystac-client + `planetary_computer` for search and signing; rasterio overviews (`out_shape`) to read at 1/8.
- zephr-xyz/sentinel1-rfi-detection downloads full SAFE zips from Copernicus Data Space instead, which needs a free CDSE account.

## Hackathon fit

- Idea 2 / EW situational awareness: a C-band RF-activity layer next to an ADS-B GNSS-degradation layer, both free and no login.
- Not a GNSS jamming detector; pitch it as context.

## Pitfalls

- One snapshot per pass (about 25 s per frame), every 6 days on one orbit. Emitters that are off during the pass are invisible.
- The RFI strips are swath x time footprints; the exact IW1/2/3 split is not in the Planetary Computer assets, so locations are approximate.
- Full-resolution VH is about 0.5 GB per scene; read overviews.
- Some scenes in a stack can be missing from the mirror.

## Sources

- Planetary Computer STAC collection `sentinel-1-grd` JSON, one item's asset list, HEAD on a signed VH href, 2026-11-06
- samples/osint-jamming-map/README.md and `s1_rfi.py`
