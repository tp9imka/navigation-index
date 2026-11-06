# Rasterio - integration card
<!-- about: repo:rasterio/rasterio -->
One-line: pip-installable GeoTIFF/DEM reader that turns a map tile into a numpy array plus an affine transform, so a nav filter can look up terrain height or orthophoto pixels by world coordinate.

| | |
|---|---|
| Install | `pip install rasterio` (wheels bundle libgdal; latest release 1.5.2). Conda alternative: `conda install -c conda-forge rasterio` for more format drivers. Source build against system GDAL: `GDAL_CONFIG=/path/to/gdal-config python -m pip install --no-binary rasterio rasterio`. |
| Runs on | Linux, macOS, Windows (official wheels per README). Rasterio 1.5+ needs Python >= 3.12, numpy >= 2, GDAL >= 3.8. No GPU. |
| Inputs | Any GDAL raster the bundled build supports: GeoTIFF/COG, VRT, JPEG2000, HDF5, netCDF (wheels include these per README); remote via `/vsicurl/` or `s3://` URLs. |
| Outputs | `numpy` arrays (optionally masked), `Affine` transforms, `CRS` objects, written GeoTIFFs. |
| Key API / entry points | `rasterio.open(path, mode="r")`; `DatasetReader.read(indexes=None, window=None, masked=False, ...)`; `DatasetReader.sample(xy, indexes=None, masked=False)`; `rasterio.windows.from_bounds(left, bottom, right, top, transform=None, ...)`; `rasterio.transform.xy(transform, rows, cols, offset="center")` / `rowcol(transform, xs, ys)`; `rasterio.warp.transform(src_crs, dst_crs, xs, ys)`, `reproject(...)`, `calculate_default_transform(...)`; `rasterio.vrt.WarpedVRT(src, crs=..., resampling=...)`; CLI `rio info`, `rio insp`. |
| Time to first result | Estimate: 5 min (`pip install` + open a GeoTIFF + `sample`). Assumes Python 3.12+ and a DEM file already downloaded. |
| License | BSD-3-Clause (LICENSE.txt, copyright Mapbox 2013-2021); GitHub metadata reports NOASSERTION. |

## Minimal usage

Not run. Crop a DEM window around a vehicle position and sample terrain height at particle positions, both in the DEM's CRS.

```python
import rasterio
from rasterio.windows import from_bounds
from rasterio.warp import transform

with rasterio.open("aoi_utm.tif") as src:
    e, n = 460000.0, 5210000.0
    win = from_bounds(e - 2000, n - 2000, e + 2000, n + 2000, transform=src.transform)
    patch = src.read(1, window=win, masked=True)
    heights = [v[0] for v in src.sample([(e, n), (e + 30, n)])]
    lon, lat = transform(src.crs, "EPSG:4326", [e], [n])
```

The index already has a fuller loader: [samples/terrain-relative-nav-pf/dem_rasterio.py](../../samples/terrain-relative-nav-pf/dem_rasterio.py) reprojects a geographic GLO-30 tile to UTM through `WarpedVRT` and hands it to the particle filter (syntax-checked only, per that sample's README).

## Wiring it into a nav stack

- Terrain-relative nav: DEM from [elevation](./bopen__elevation.md) (`eio clip` => GeoTIFF) => rasterio window read => measurement model of a particle filter ([samples/terrain-relative-nav-pf](../../samples/terrain-relative-nav-pf/)). Keep the DEM in a metric CRS so the filter state is in metres.
- Visual geolocalization: orthophoto crop around the INS-predicted position via `from_bounds`, match with a feature matcher, convert matched pixels back with the affine transform ([samples/visual-geolocalization-lightglue](../../samples/visual-geolocalization-lightglue/)).
- Geodetic frames: for ECEF/ENU/NED conversions of the resulting fix use [pymap3d](./geospace-code__pymap3d.md); rasterio only does CRS-to-CRS via PROJ.
- Heavy preprocessing (mosaics, COG conversion, hillshade) is often faster with [GDAL](./osgeo__gdal.md) CLI, then rasterio for the runtime lookups.

Catalog page: [catalog/repos/rasterio__rasterio.md](../../catalog/repos/rasterio__rasterio.md). Concepts: [gis-mapping](../../catalog/concepts/gis-mapping.md), [terrain-nav](../../catalog/concepts/terrain-nav.md).

## Gotchas

- Half-pixel convention: the affine transform points at the top-left corner of pixel (0, 0); `xy()` returns centres by default (`offset="center"`). The TRN and LightGlue samples both add 0.5 explicitly. Issue #3277 (open) is a user confused by exactly this.
- `sample()` expects coordinates in the dataset CRS, not lon/lat, unless the file is EPSG:4326. Transform first.
- Python floor: 1.5+ needs Python >= 3.12; older interpreters silently resolve to an older rasterio.
- Wheels are "mainly intended to make installation easy for simple applications, not so much for production" and omit many GDAL optional drivers (docs/installation.rst). Mixing rasterio wheels with a conda GDAL or the `gdal` pip package in one env can load two libgdal copies.
- `masked=True` returns a numpy masked array; filling nodata (sea, voids) with 0 m is a silent bias in a terrain filter. Decide the fill policy explicitly.
- Mac Arm: open issue #2868 about netCDF URL paths on Apple Silicon wheels.

## Verified in this hub
Measured by hub samples that ran this code on 2026-11-06, unless a bullet says otherwise. The linked sample README holds the commands and raw output.

- rasterio 1.5.2 (Python 3.12-3.13, macOS arm64 wheels) read windows of public Copernicus GLO-30 COGs and NAIP COGs over HTTPS and reprojected them without a local GDAL install - [terrain-heightmap-pf](../../samples/terrain-heightmap-pf/README.md), [geoloc-license-clean](../../samples/geoloc-license-clean/README.md).
- Half-pixel trap: LightGlue keypoints put integers on pixel centres, the rasterio affine on pixel corners; add 0.5 before applying the transform - [visual-geolocalization-lightglue](../../samples/visual-geolocalization-lightglue/README.md).

## Alternatives

- [GDAL](./osgeo__gdal.md) Python bindings (`osgeo.gdal`) - same engine, lower level, harder install; prefer when you need a driver the wheels omit.
- [elevation](./bopen__elevation.md) - not a reader, but if you only need a clipped DEM file, `eio clip` gets you there without code.
- [stac-utils/pystac-client](../../catalog/repos/stac-utils__pystac-client.md) - for discovering imagery/DEM assets by AOI before reading them with rasterio.

Sources: `gh api repos/rasterio/rasterio` (license, release 1.5.2), README.rst, docs/installation.rst, LICENSE.txt, rasterio/{windows.py, warp.py, transform.py, sample.py, _io.pyx} function signatures, issues #3277, #2868, #3446 (search for wheel/macos), samples/terrain-relative-nav-pf in this index.
