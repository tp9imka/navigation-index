# NAIP aerial orthophotos on Microsoft Planetary Computer

<!-- about: res:naip-planetary-computer, sample:geoloc-license-clean, sample:golden-demo, repo:stac-utils/pystac-client -->

USDA National Agriculture Imagery Program: leaf-on aerial orthophotos of the contiguous US, each state re-flown every 2-3 years, RGB + NIR. Planetary Computer serves them as Cloud-Optimized GeoTIFFs behind a STAC API, so a few km2 can be read as windows without downloading whole tiles. This is the license-clean map source for the visual geolocalization samples. No index id of its own; the marker names the samples and the STAC client.

| Field | Value |
|---|---|
| Platform | Crewed survey aircraft (USDA contract flights) |
| Environment | Contiguous US only. The samples use Aukerman Park, Ohio (41.30 N, 81.75 W) |
| Sensors and rates | 4-band (R, G, B, NIR) orthophoto. GSD varies by year and state: Ohio 2023 0.3 m, 2019 and 2021 0.6 m, 2015 and 2017 1 m (item ids and sample metadata) |
| Ground truth | Orthorectified and georeferenced; absolute accuracy not stated on the pages read. The geoloc sample saw a 2-5 m floor between the 2019 and 2023 epochs, consistent with co-registration offsets (not measured separately) |
| Size | Per quarter-quad COG (HEAD with SAS token, 2026-11-06): `m_4108143_sw_17_030_20230526` (0.3 m) 1,368,266,409 B; `m_4108143_sw_17_060_20191012` (0.6 m) 425,760,978 B. Windows the samples wrote: 2 x 2 km at 0.3 m 94.2 MB, at 0.6 m 27.2 MB; 7 x 7 km at 0.6 m 292-329 MB, at 1 m 108 MB |
| License | "Public Domain with Attribution" per the [AWS Open Data registry](https://registry.opendata.aws/naip/) entry the sample cites. The Planetary Computer STAC collection lists `license: other`; Planetary Computer's own terms of use apply to the hosting |
| Format | COG GeoTIFF, UTM (EPSG:269xx per zone), uint8 4-band; STAC collection `naip` (temporal extent 2010-2023 per the collection JSON) |
| Index | [pystac-client](../../catalog/repos/stac-utils__pystac-client.md), [geoloc-license-clean sample](../../samples/geoloc-license-clean/), [golden-demo sample](../../samples/golden-demo/), [vpr-large-area sample](../../samples/vpr-large-area/) |

## Download

```bash
# STAC search, a SAS token, then windowed reads straight from the COGs (rasterio)
python3 samples/geoloc-license-clean/download_data.py      # 2 x 2 km, 2023 (0.3 m) + 2019 (0.6 m), plus 5 CC0 eBee frames
python3 samples/vpr-large-area/download_data.py             # 7 x 7 km, several years, read from COG overviews
```

The pattern in `download_data.py`: POST `https://planetarycomputer.microsoft.com/api/stac/v1/search` with `collections: ["naip"]` and a point, GET `https://planetarycomputer.microsoft.com/api/sas/v1/token/naip`, append the token to each `assets.image.href`, then `rasterio.merge` with bounds. An unsigned blob URL answers HTTP 409 ("Public access is not permitted"). `planetary_computer.sign()` does the same signing.

## Used in this repo

- [samples/geoloc-license-clean](../../samples/geoloc-license-clean/): map NAIP 2023-05-26, 0.3 m, 6667 x 6667 px; cross-season frames cut from NAIP 2019-10-12 (0.6 m). `data/` is 159 MB (README; 151 MiB by du). Result worth knowing: on real eBee frames the 2019 0.6 m map gave the only fix and the 2023 0.3 m map none; map date mattered more than resolution.
- [samples/golden-demo](../../samples/golden-demo/): reuses those two GeoTIFFs (94 MB + 27 MB) for a real-image visual geoloc leg (frame rendered from 2019 at the SITL truth position, matched against 2023).
- [samples/vpr-large-area](../../samples/vpr-large-area/) (still being written in this round; no README yet): `download_data.py` mosaics the 4 quarter-quads around the park for 2023, 2021, 2019 (0.6 m) and 2017, 2015 (1 m) in UTM 17N, and samples USGS 3DEP (`3dep-seamless`, PDDL-1.0) under each eBee frame. On disk on 2026-11-06: `naip_2023.tif` 292 MB, `naip_2019.tif` 329 MB, `naip_2017.tif` 108 MB; `data/` 855 MiB in all (du).

## Loading and tooling

- rasterio (windowed COG reads, `merge`, `warp.transform`); set `GDAL_DISABLE_READDIR_ON_OPEN=EMPTY_DIR` so GDAL does not list the container.
- [pystac-client](../../catalog/repos/stac-utils__pystac-client.md) or plain `urllib` POST for search, as the samples do.

## Hackathon fit

- Idea 18 / 20 (visual geolocalization): a reference map you can redistribute and pitch commercially, unlike most satellite basemaps.
- Map-age experiments: the same area in up to 5 epochs, so you can show how much a 4-7 year old map costs.

## Pitfalls

- US only. Outside the US use OpenAerialMap (CC BY 4.0, patchy), national orthophoto portals, or the UAV-VisLoc / VPAIR maps.
- SAS tokens expire; fetch a new one per session.
- Different years differ in GSD and season (leaf-on, but May vs October). Downsampling a 3 cm drone frame to 0.3-0.6 m without an area filter aliases the texture away (the geoloc sample hit this).
- Full quarter-quads are 0.4-1.4 GB each; read windows, not whole files.

## Sources

- Planetary Computer STAC: collection JSON for `naip`, `sentinel-1-grd`, `3dep-seamless`; SAS token endpoint; HEAD on two signed item hrefs, 2026-11-06
- samples/geoloc-license-clean/README.md and `download_data.py`; samples/golden-demo/README.md; samples/vpr-large-area/download_data.py and data JSONs
