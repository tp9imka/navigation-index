# UAV-VisLoc

<!-- about: repo:intellisensing/uav-visloc, res:uav-visloc-dataset-2024 -->

Real nadir UAV imagery from 11 sites in China paired with large orthorectified satellite
maps, for absolute visual localization (drone image => lat/lon on the map). Xu et al.,
arXiv 2405.11936, 2024.

| Field | Value |
|---|---|
| Platform | Fixed-wing and multirotor UAVs (README; models not named) |
| Environment | 11 locations in China: cities, towns, farms, rivers, hills |
| Sensors and rates | Downward RGB camera only; still images (not video), roughly 0.1-0.2 m/px. No IMU stream |
| Ground truth | Per-image center lat/lon, height, date and heading (Phi) in `<site>.csv`. Source and accuracy of the per-image coordinates not stated; README calls the example subset "minimal coordinate error", implying the full set has some |
| Size | Full: 16.4 GB (README); Google Drive reports `UAV_VisLoc_dataset.zip (16G)`. Example subset: 2.04 GB (README), Drive reports `UAV_VisLoc_example.zip (2.0G)` (checked 2026-11-06) |
| License | Not stated in the repo README or dataset files list. Treat as research use, ask before redistribution |
| Format | JPG drone frames, GeoTIFF satellite maps (0.3 m/px, from Google Maps), CSV metadata |
| Index | [UAV-VisLoc repo](../../catalog/repos/intellisensing__uav-visloc.md), [paper](../../catalog/resources/uav-visloc-dataset-2024.md) |

## What's in it

- 6,742 drone images, 11 satellite maps, 11 sites, 7 terrain categories (README table).
- One satellite map per flight, covering all images of that flight.
- `satellite_coordinates_range.csv` gives the lat/lon bounds of each map.
- Example subset = site 03 only, hand-picked for good coordinates and terrain variety.

## Download

```bash
# gdown handles the Drive virus-scan confirm page; install into a project venv
VENV=.venv; uv venv "$VENV"
uv pip install --python "$VENV/bin/python" gdown
# example subset, 2.0 GB, site 03 only
"$VENV/bin/gdown" 16tY7tPZiNIoyAhknvyXnp0jAfccIcHtL -O UAV_VisLoc_example.zip
# full set, 16 GB
"$VENV/bin/gdown" 1xYODANyilEMM3CfWh85APwkTHQeLTcCT -O UAV_VisLoc_dataset.zip
# Baidu mirrors (code rsai): https://pan.baidu.com/s/13zgbP3Kjk1FDfZ47fBaC0g (full)
```

## Loading and tooling

```python
import csv, rasterio
meta = list(csv.DictReader(open("UAV-VisLoc/03/03.csv")))
sat = rasterio.open("UAV-VisLoc/03/satellite03.tif")
print(meta[0], sat.width, sat.height, sat.transform)
```

- The [visual-geolocalization-lightglue sample](../../samples/visual-geolocalization-lightglue/README.md)
  is written against this layout (`--frame .../drone/03_0001.JPG --tile .../satellite03.tif`).
- Matchers: [LightGlue](../../catalog/repos/cvg__lightglue.md), [RoMa](../../catalog/repos/parskatt__roma.md).
  Retrieval: [AnyLoc](../../catalog/repos/anyloc__anyloc.md),
  [VPR methods evaluation](../../catalog/repos/gmberton__vpr-methods-evaluation.md).
- Score with plain haversine error per frame; trajectory tools like evo are not needed (no
  continuous trajectory).

## Hackathon fit

- Idea 18 (visual geolocalization fused with VO) and idea 20 (Jetson geolocalization):
  the cheapest real-flight drone-to-satellite set with lat/lon labels. Pick one site, crop
  satellite tiles around a prior, match, report meters of error per frame.
- Idea 11 (terrain-relative nav) as a visual stand-in when no DEM-based sensor is available.

## Pitfalls

- Satellite GeoTIFFs may not carry a usable geotransform; the sample README notes you may
  have to build it from `satellite_coordinates_range.csv`.
- Images are sparse stills; no IMU, so "fused with VO" needs synthetic odometry from GT deltas.
- Drone heading is given; most matchers fail on large rotations unless you rotate the query
  first. Using GT heading is a pose prior - say so when reporting.
- Images are 1-2 orders of magnitude larger than a Jetson wants; downsample before matching.
- Google Drive quota errors on the 16 GB file are common; use Baidu or retry later.

## Sources

- https://github.com/IntelliSensing/UAV-VisLoc README (counts, sizes, layout, links), read 2026-11-06.
- arXiv 2405.11936 abstract (11 locations, fixed-wing, metadata fields).
- Google Drive download pages for both file ids (file names and sizes), 2026-11-06.
