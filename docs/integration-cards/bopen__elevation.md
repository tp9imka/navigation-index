# elevation - integration card
<!-- about: repo:bopen/elevation -->
One-line: one command (`eio clip --bounds ...`) gets you a clipped, cached 30 m or 90 m global DEM GeoTIFF for an AOI - the map half of terrain-relative navigation.

| | |
|---|---|
| Install | `pip install elevation` (latest release v2.0.1, 2026-10-21). Requires GDAL command line tools on PATH (`gdal_translate`, `gdalbuildvrt`, `gdalinfo`, `ogrinfo`); check with `eio selfcheck --verbose`. |
| Runs on | Linux and macOS are the target platforms; Windows "only lightly tested" (README). Python >= 3.11. No GPU. Needs internet on first access to an area. |
| Inputs | Bounds as `left bottom right top` in WGS84 lon/lat degrees, or `--reference` any GDAL/OGR raster or vector file whose extent is used. Product choice: `MAPZEN` (default), `GLO-30`, `GLO-90`, `AW3D30`, `SRTM1_GEOID`, `SRTM1_ELLIP`, `SRTM3` (`GEDTM30` only in unreleased 2.1.0). |
| Outputs | A GeoTIFF (default creation options `TILED=YES COMPRESS=DEFLATE`) in the product's native geographic CRS; heights in metres on the product's vertical datum (EGM96, EGM2008, or WGS84 ellipsoid for `SRTM1_ELLIP`). Local tile cache under the user cache dir or `EIO_CACHE_DIR`. |
| Key API / entry points | CLI: `eio [--product P] [--cache_dir D] clip -o out.tif --bounds L B R T [--margin M] [--max_download_tiles N]`, `eio seed`, `eio info`, `eio dataset [ID]` (STAC metadata), `eio clean`, `eio distclean`, `eio selfcheck`. Python: `elevation.clip(bounds, output="out.tif", margin="0", product=..., *, cache_dir=None, gdal_options=..., max_download_tiles=25)`, `elevation.seed(cache_dir=None, product=..., bounds=None, ...)`, `elevation.info()`, `elevation.dataset()`. |
| Time to first result | Estimate: 10 min for a small AOI with GDAL already installed (pip + one `eio clip`). Assumes network access to AWS / OpenTopography; `GLO-30`/`GLO-90` additionally need an Earth Data Hub account. |
| License | Apache-2.0 (code). Each DEM product keeps its provider's download policy and attribution terms (README). |

## Minimal usage

Not run. From the README, adapted to an AOI:

```bash
pip install elevation
eio selfcheck --verbose
eio clip -o aoi-MAPZEN.tif --bounds 8.40 47.30 8.70 47.45
eio --product SRTM1_ELLIP clip -o aoi-SRTM1_ELLIP.tif --bounds 8.40 47.30 8.70 47.45
```

```python
import elevation
elevation.clip(bounds=(8.40, 47.30, 8.70, 47.45), output="aoi.tif", product="AW3D30")
```

`SRTM1_ELLIP` is worth knowing about: its heights are on the WGS84 ellipsoid, so they compare directly with GNSS or INS ellipsoidal height without a geoid model.

## Wiring it into a nav stack

- Terrain-relative nav pipeline: `eio clip` => [GDAL](./osgeo__gdal.md) `gdalwarp -t_srs EPSG:<utm>` to metres => [rasterio](./rasterio__rasterio.md) read => particle filter measurement model ([samples/terrain-relative-nav-pf](../../samples/terrain-relative-nav-pf/), whose `dem_rasterio.py` reads GLO-30 tiles).
- Classic TERCOM demos such as [python-tercom](../../catalog/repos/alti3__python-tercom.md) and DEM noise sweeps such as [terrain-nav-preprocessing](../../catalog/repos/hstm__terrain-nav-preprocessing.md) need exactly this kind of clipped GeoTIFF as input.
- Simulation: the same AOI DEM can become a heightmap for [Gazebo](./gazebosim__gz-sim.md) worlds, so the simulated radar altimeter and the filter's map share a source (watch the datum).
- Display: hillshade the clip with `gdaldem hillshade` and overlay in [MapLibre GL JS](./maplibre__maplibre-gl-js.md), or serve terrain to [CesiumJS](./cesiumgs__cesium.md) via quantized mesh.
- Pre-seed before going offline: `eio seed --bounds ...` caches tiles so later clips do not hit the network - do it before the event, hackathon Wi-Fi is not a data source.

Catalog page: [catalog/repos/bopen__elevation.md](../../catalog/repos/bopen__elevation.md). Concepts: [terrain-nav](../../catalog/concepts/terrain-nav.md), [gis-mapping](../../catalog/concepts/gis-mapping.md).

## Gotchas

- Version 2.0 (2026-10-21) is not fully backward compatible with 1.x: the old Makefile/curl/unzip pipeline was replaced by GDAL `/vsicurl/` reads, and retired product names raise `ProductRetiredError`. Old blog posts and Stack Overflow answers show 1.x commands (`SRTM1`, `SRTM3` with make). Read the migration guide linked from the README.
- `GEDTM30` appears in the README but CHANGELOG lists it under 2.1.0 (unreleased); the PyPI 2.0.1 build will not have it.
- `GLO-30` / `GLO-90` read a cloud-hosted Zarr store from Earth Data Hub: needs an account, an API key in `~/.netrc` for `data.earthdatahub.destine.eu`, and GDAL >= 3.8.
- Download cap: `clip` and `seed` refuse more than 25 tiles by default (`--max_download_tiles`) - large AOIs fail until you raise it, and providers ask for their own bulk channels.
- Datums differ per product (EGM96, EGM2008, ellipsoid). Mixing products, or comparing against GNSS height, without a geoid correction biases a terrain filter by the local geoid undulation.
- Surface vs terrain: AW3D30 and GLO-30 are surface models (buildings, canopy), `GEDTM30` is bare-earth. A radar altimeter over forest sees something in between.
- Output stays in geographic EPSG:4326 pixels (non-square metres); reproject before using as a metric grid.
- Issue #62 (closed) reported the SRTM3 CGIAR source unreachable at one point; upstream hosts change, have a fallback product.

## Alternatives

- [GDAL](./osgeo__gdal.md) with `/vsicurl/` directly on the Copernicus COG tiles - no extra dependency, more typing; prefer if you already have a tile URL list.
- [stac-utils/pystac-client](../../catalog/repos/stac-utils__pystac-client.md) - search DEM and imagery assets in STAC catalogs when you need sources elevation does not ship.
- [hstm/terrain-nav-preprocessing](../../catalog/repos/hstm__terrain-nav-preprocessing.md) - when you need DEM tiles with controlled noise for evaluation rather than a raw clip.

Sources: `gh api repos/bopen/elevation` (license Apache-2.0, release v2.0.1), README.md, CHANGELOG.rst, pyproject.toml, elevation/__init__.py, elevation/datasource.py (signatures of clip/seed/info/dataset, ProductRetiredError), elevation/datasets/AW3D30.yaml, issue list (latest 10 issues).
