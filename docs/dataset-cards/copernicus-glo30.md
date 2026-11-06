# Copernicus DEM GLO-30 (AWS Open Data COGs)

<!-- about: res:copernicus-dem-aws, sample:terrain-heightmap-pf, sample:blind-flight-bench, sample:terrain-relative-nav-pf, sample:osint-jamming-map -->

The Copernicus global digital surface model at 1 arc-second (about 30 m), from TanDEM-X radar data, served by Sinergise on AWS as one Cloud-Optimized GeoTIFF per 1 x 1 degree tile. No login, plain HTTPS. The default terrain map for every terrain sample in this repo.

| Field | Value |
|---|---|
| Platform | Spaceborne InSAR (TanDEM-X mission), Copernicus DEM 2021 release (registry text) |
| Environment | Global land. "GLO-30 Public" leaves out a small list of country tiles not yet released; ocean has no tiles (assume 0 m) (registry text) |
| Sensors and rates | Gridded heights, 1 arc-second; a DSM, so it includes buildings, infrastructure and vegetation (registry text) |
| Ground truth | It is the reference map. Vertical accuracy not restated here (not read on the pages checked). The samples model map error explicitly (sigma 2-3 m correlated) rather than assuming a figure |
| Size | Per tile (HEAD Content-Length, 2026-11-06): `N48_00_E013_00` 42,759,871 B, `N47_00_E008_00` 41,746,914 B. Windowed reads are far smaller: the heightmap sample caches about 0.8 MB per 15 x 15 km window, the blind-flight bench about 18 MB for four 36 x 35 km windows |
| License | Free for the general public under the Copernicus DEM licence (AWS registry entry, linking the licence on dataspace.copernicus.eu); use the attribution text given there |
| Format | COG GeoTIFF, float32, EPSG:4326, heights orthometric on EGM2008 (per the terrain-relative-nav-pf README) |
| Index | [Copernicus DEM on AWS](../../catalog/resources/copernicus-dem-aws.md) |

## Download

```bash
# tile naming: Copernicus_DSM_COG_10_<N|S>yy_00_<E|W>xxx_00_DEM, one per 1 x 1 deg
T=Copernicus_DSM_COG_10_N47_00_E008_00_DEM
curl -O https://copernicus-dem-30m.s3.amazonaws.com/$T/$T.tif
# or read only a window over HTTPS (what the samples do)
python3 samples/terrain-heightmap-pf/fetch_dem.py
```

A STAC catalogue sits at `https://copernicus-dem-30m-stac.s3.amazonaws.com/` (HTTP 200, 2026-11-06). GLO-90 is the `copernicus-dem-90m` bucket with `_COG_30_` in tile names; `N47_00_E008_00` there is 5,112,967 B (HEAD).

## Used in this repo

| Sample | What it reads | Measured |
|---|---|---|
| [terrain-heightmap-pf](../../samples/terrain-heightmap-pf/) | `fetch_dem.py`: one window per region from one tile via `/vsicurl/`, reprojected to UTM at 30 m, NaN rim cropped; regions hilly (Bavarian Forest), flat (Hungarian Plain), mixed (Erding, the SPRIN-D area) | ~0.8 MB per cached window |
| [blind-flight-bench](../../samples/blind-flight-bench/) | imports the same `fetch_dem.py`; four windows (Khibiny, Middle Urals, Yenisei taiga, south of Moscow) | ~18 MB cache, fetch ~30 s |
| [terrain-relative-nav-pf](../../samples/terrain-relative-nav-pf/) | `dem_rasterio.py` loads a whole GLO-30 tile into its `Dem` class | syntax-checked only in that sample; not run on real data |
| [osint-jamming-map](../../samples/osint-jamming-map/) | `s1_rfi.py`: GLO-30 at reduced resolution through COG overviews, for the 15 deg slope mask (`eu-central-1` endpoint) | part of the ~440 MB S1 cache |

## Loading and tooling

- rasterio with `GDAL_DISABLE_READDIR_ON_OPEN=EMPTY_DIR` and `/vsicurl/` for windowed reads; `rasterio.warp.reproject` to UTM.
- `repo:bopen/elevation` also wraps Copernicus / SRTM downloads (not used here).

## Hackathon fit

- Idea 11 (terrain-relative navigation over a real DEM) and radar-altimeter TERCOM-style benches: global, no login, quick.
- Slope / layover masks for SAR work, line-of-sight for RF sensor siting.

## Pitfalls

- It is a surface model from radar: forest canopy and buildings are partly in it. A radar altimeter over forest reads somewhere between canopy and ground; the blind-flight bench models 2-8 m canopy penetration as an assumption, not a measured GLO-30 property.
- 30 m smooths away single buildings and tree edges; the heightmap sample's edge-based method failed at 30 m and worked on the 1 m [Geobasis NRW](geobasis-nrw-lidar.md) surface model.
- Lat/lon grid: reprojecting to UTM leaves a NaN rim; crop it.
- Heights are orthometric (EGM2008); GNSS and many baro setups use ellipsoid height. Convert before comparing.

## Sources

- awslabs/open-data-registry `datasets/copernicus-dem.yaml` (description, licence pointer, buckets), 2026-11-06
- HEAD on two tiles and an anonymous bucket listing, 2026-11-06
- READMEs and fetch code of the four samples above
