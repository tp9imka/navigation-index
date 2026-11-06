# GDAL - integration card
<!-- about: repo:osgeo/gdal -->
One-line: the format and reprojection layer under every DEM, orthophoto and tile pipeline - clip, warp, hillshade, viewshed, point-sample and convert geodata from the command line or Python.

| | |
|---|---|
| Install | Docker (least pain): `docker pull ghcr.io/osgeo/gdal:ubuntu-small-latest` (~385 MB, has Python) or `ghcr.io/osgeo/gdal:ubuntu-full-latest` (~1.48 GB, all drivers). Conda: `conda install -c conda-forge gdal`. Python bindings over a system libgdal: `pip install gdal[numpy]=="$(gdal-config --version).*"` (swig/python/README.rst). Latest release at time of writing: v3.13.3. |
| Runs on | Linux, macOS, Windows, Android (CI badges in README). No GPU. Docker images are Alpine or Ubuntu based (26.04 for GDAL 3.13). |
| Inputs | Raster: GeoTIFF/COG, DTED, HGT, VRT, JPEG2000, netCDF, HDF5, PMTiles raster, MBTiles, Zarr (driver set depends on build). Vector: Shapefile, GeoJSON, GeoPackage, KML, MVT/PMTiles, PostGIS. Remote via `/vsicurl/`, `/vsis3/`. Any CRS PROJ knows. |
| Outputs | Same formats (write support varies per driver), plus derived rasters: hillshade, slope, aspect, roughness (`gdaldem`), viewshed (`gdal_viewshed`), tiles (`gdal raster tile`, XYZ or TMS). |
| Key API / entry points | Classic CLI: `gdal_translate`, `gdalwarp`, `gdalbuildvrt`, `gdaldem`, `gdal_viewshed`, `gdallocationinfo [-wgs84] [-valonly] <ds> x y`, `ogr2ogr`. New unified CLI (since 3.11): `gdal raster info|clip|reproject|hillshade|viewshed|tile|convert`. Python: `from osgeo import gdal`; `gdal.Open(path)`, `ds.GetGeoTransform()`, `ds.GetRasterBand(1).ReadAsArray()`, `gdal.Warp(dst, src, dstSRS=..., outputBounds=...)`, `gdal.Translate(...)`. |
| Time to first result | Estimate: 10-15 min with the Docker image and a DEM tile already on disk (pull + one `gdaldem` command). Assumes Docker present; a from-source build is hours. |
| License | MIT for GDAL itself (README; GitHub metadata says NOASSERTION because LICENSE.TXT aggregates many licenses). Builds that link GPL libraries (e.g. the `alpine-normal` image, per docker/README.md) are copyleft overall. |

## Minimal usage

Not run. Clip a Copernicus GLO-30 tile to an AOI in UTM, derive a hillshade, and read terrain height under one lon/lat (the TRN measurement-model lookup).

```bash
docker run --rm -v "$PWD:/data" -w /data ghcr.io/osgeo/gdal:ubuntu-small-latest bash -c '
  gdalwarp -t_srs EPSG:32632 -te 450000 5200000 470000 5220000 -tr 30 30 -r bilinear \
           Copernicus_DSM_COG_10_N47_00_E008_00_DEM.tif aoi_utm.tif
  gdaldem hillshade aoi_utm.tif aoi_hillshade.tif
  gdallocationinfo -valonly -wgs84 Copernicus_DSM_COG_10_N47_00_E008_00_DEM.tif 8.55 47.37
'
```

Python equivalent of the last step:

```python
from osgeo import gdal
gdal.UseExceptions()
ds = gdal.Open("aoi_utm.tif")
x0, dx, _, y0, _, dy = ds.GetGeoTransform()
z = ds.GetRasterBand(1).ReadAsArray()
```

## Wiring it into a nav stack

- Terrain-relative nav: GDAL prepares the map, the filter consumes it. Reproject the DEM to the metric CRS your estimator uses (`gdalwarp -t_srs`), then load it with [rasterio](./rasterio__rasterio.md) as in [samples/terrain-relative-nav-pf](../../samples/terrain-relative-nav-pf/) (`dem_rasterio.py`).
- DEM acquisition: [elevation](./bopen__elevation.md) shells out to `gdal_translate`, `gdalbuildvrt`, `gdalinfo` and `ogrinfo`; GDAL must be on PATH for it.
- Visual geolocalization: orthophoto reference tiles for matchers need a known geotransform; `gdal_translate -of COG` plus `gdalwarp` to a common CRS keeps pixel => world conversion consistent ([samples/visual-geolocalization-lightglue](../../samples/visual-geolocalization-lightglue/)).
- Situational-awareness display: `gdal raster tile` produces XYZ tile pyramids; the PMTiles driver (vector since 3.8, also raster) and `ogr2ogr out.pmtiles in.mbtiles` hand off to [PMTiles](./protomaps__pmtiles.md) and [MapLibre GL JS](./maplibre__maplibre-gl-js.md). For 3D, quantized-mesh terrain for [CesiumJS](./cesiumgs__cesium.md) is built by [cesium-terrain-builder](../../catalog/repos/geo-data__cesium-terrain-builder.md), which links GDAL.
- Coordinate glue: CRS math lives in [PROJ](../../catalog/repos/osgeo__proj.md); for pure point conversions in a filter loop, [pymap3d](./geospace-code__pymap3d.md) avoids the GDAL dependency entirely.

Catalog page: [catalog/repos/osgeo__gdal.md](../../catalog/repos/osgeo__gdal.md). Concepts: [gis-mapping](../../catalog/concepts/gis-mapping.md), [terrain-nav](../../catalog/concepts/terrain-nav.md).

## Gotchas

- Python bindings must match libgdal exactly. `pip install gdal` without a matching system GDAL fails or builds without numpy support; the README's fix is `pip install --no-cache --force-reinstall gdal[numpy]=="$(gdal-config --version).*"`. Use Docker or conda to sidestep this.
- `osgeo.gdal_array` (numpy arrays) needs numpy at build time; installing numpy afterwards does not fix it (swig/python/README.rst).
- `gdallocationinfo -wgs84` takes longitude first, then latitude. The `-te` of `gdalwarp` is `xmin ymin xmax ymax` in the target CRS.
- Vertical datum: GDAL reports what the file says. GLO-30 is on EGM2008, SRTM/AW3D30 on EGM96, GNSS gives ellipsoidal height. Mixing them without a geoid correction is tens of metres of bias in a TRN measurement model.
- Exceptions: older code relies on `gdal.UseExceptions()` being off by default; call it explicitly (see issue #10010 on toggling it).
- Two CLIs now coexist: the classic `gdal_*` programs and the `gdal <noun> <verb>` CLI added in 3.11. Tutorials older than 2025 only show the classic ones; some `gdal raster tile` options need 3.11.1 or 3.12.
- Licensing of a build depends on linked drivers: the docker README warns its license summaries are best effort.

## Alternatives

- [Rasterio](./rasterio__rasterio.md) - Pythonic API on top of GDAL, pip wheels bundle libgdal. Prefer it for Python-only pipelines.
- [QGIS](../../catalog/repos/qgis__qgis.md) - GUI on top of GDAL; prefer for one-off inspection and digitizing, not for pipelines.
- [pymap3d](./geospace-code__pymap3d.md) - when you only need coordinate transforms, not raster IO.

Sources: `gh api repos/osgeo/gdal` (license, release v3.13.3), README.md, LICENSE.TXT, docker/README.md, swig/python/README.rst, doc/source/programs/{gdal.rst, gdal_raster_tile.rst, gdallocationinfo.rst}, doc/source/drivers/vector/pmtiles.rst, issue search (UseExceptions).
