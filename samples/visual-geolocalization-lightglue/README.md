# Visual geolocalization: drone frame to orthophoto with LightGlue

## Goal

Get an absolute lat/lon fix for a drone without GNSS by matching a nadir camera frame
against a georeferenced satellite map or orthophoto:

```
drone frame =SuperPoint+LightGlue=> matches =MAGSAC homography H=> frame centre in tile pixels
            =GeoTIFF affine geotransform=> map coords (UTM or lon/lat) =rasterio.warp=> WGS84 lat/lon
```

The frame centre of a nadir camera is (to first order) the point under the aircraft,
so the mapped centre is the position fix. The camera is passive: nothing is emitted.

## Files

| File | What | Verified |
|---|---|---|
| `geo_math.py` | Stdlib: affine pixel<->world, homography point mapping, WGS84 UTM forward/inverse, haversine, `frame_center_to_world` | ran, 12 unit tests |
| `test_geo_math.py` | `unittest` suite for the above | ran |
| `geolocalize.py` | Full pipeline with torch + LightGlue + OpenCV + rasterio | ran on synthetic pairs (below) |
| `make_test_pair.py` | Cuts a map tile and a warped "drone frame" from one public OpenAerialMap orthophoto, writes truth + prior | ran |
| `run_cases.sh` | 7 cases + a negative control through `make_test_pair.py` and `geolocalize.py` | ran |
| `requirements.txt` | pinned torch 2.15.0, LightGlue git `5a650c4`, opencv-python 5.0.0.93, rasterio 1.5.2 | resolved and installed |

## Repos used and why

- `repo:cvg/lightglue` - the matcher. API used exactly as its README shows:
  `SuperPoint(max_num_keypoints=...)`, `LightGlue(features="superpoint")`,
  `extractor.extract(img)`, `matcher({"image0": f0, "image1": f1})`, `rbd(...)`,
  `out["matches"]`, `feats["keypoints"]`, plus `lightglue.utils.read_image` and
  `numpy_image_to_torch` (checked in `lightglue/utils.py` on 2026-11-06).
- `repo:magicleap/superpointpretrainednetwork` - original SuperPoint. LightGlue ships its
  own SuperPoint weights; you do not need this repo to run the sample.
- `repo:rasterio/rasterio` - reads the GeoTIFF, its affine `transform`, windowed crops,
  and reprojects map coords to WGS84.
- `repo:cvg/hierarchical-localization` (hloc) and `repo:anyloc/anyloc` - retrieval-first
  pipelines, see "Large maps" below.

## Test imagery

- `repo:intellisensing/uav-visloc` - real UAV flights with satellite maps over 11 sites
  (6,742 frames, 16.4 GB, Google Drive / Baidu links in its README). Each site folder has
  `drone/*.JPG`, `satelliteNN.tif` and `NN.csv` with per-frame centre lat/lon, height and
  heading. Best fit for this sample: use the CSV lat/lon as `--truth`.
- `repo:aervisloc/vpair` - aerial frames vs reference orthophotos, small, quick to evaluate.
- `repo:layumi/university1652-baseline` - drone/satellite/ground views of university
  buildings. Access via a request form (not instant). Building-centric, not wide-area,
  so it suits retrieval experiments more than metric fixes.

## Prerequisites

- Stdlib part: `python3` 3.10+ (verified with 3.14.7).
- Pipeline: `python3 -m pip install -r requirements.txt` (ran with Python 3.12.14, CPU
  torch on macOS arm64). LightGlue installs from git; on first use it downloads its
  SuperPoint and LightGlue weights from the LightGlue GitHub release into `~/.cache/torch`.
- Internet once, for the orthophoto (~70 s for the windowed reads here). `data/` is
  git-ignored (the map tile is ~9 MB).

## Run

Stdlib math and tests (no dependencies):

```bash
cd samples/visual-geolocalization-lightglue
python3 -m unittest -v test_geo_math
```

Observed (python3.14.7, 2026-11-06): `Ran 12 tests ... OK`. The UTM test anchors on the
WGS84 meridian arc to 45 deg (4,984,944.378 m, matched within 1 cm) plus 1 cm round trips
in both hemispheres.

Full pipeline on synthetic pairs:

```bash
python3 -m pip install -r requirements.txt
./run_cases.sh                       # PYTHON=... to pick the interpreter
# or one case by hand:
python3 make_test_pair.py --out data/base
python3 geolocalize.py --frame data/base/drone_frame.jpg --tile data/base/map_tile.tif \
    --prior <prior lat lon from data/base/pair.json> --truth <truth lat lon> --crop-px 1536
```

How a pair is made (`make_test_pair.py`): the source is the OpenAerialMap orthophoto
"Tbilisi (GE) - Saburtalo" (SJRC F22s Pro, 2023-10-08, CC-BY 4.0, EPSG:3857 COG, 8447 x
8926 px at 0.1 m in EPSG:3857 units, which is ~0.075 m on the ground at 41.7 N). The map
is the whole ortho at 1/4 resolution (2111 x 2231 px, 0.4 m units). The frame is a
1600 x 1200 window at 1/2 resolution (0.2 m units), rotated by `--yaw-deg`, given a
keystone `--tilt`, gain/offset change, Gaussian blur and noise, saved as JPEG. Truth is
the ground point under the frame centre; the prior is truth moved `--prior-offset-m` in a
random direction (INS drift stand-in).

Observed (`./run_cases.sh`, torch 2.15.0 CPU, LightGlue 5a650c4, 2026-11-06, ~25 s/case):

| Case | Settings | Inliers | Best rotation | Error vs truth |
|---|---|---|---|---|
| base | yaw 25 deg, tilt 0.08, prior 60 m off, crop 1536 px | 473 | 0 | 0.04 m |
| yaw60 | yaw 60 deg | 452 | 270 | 0.11 m |
| yaw135 | yaw 135 deg | 441 | 180 | 0.21 m |
| tilt20 | tilt 0.20 | 458 | 0 | 0.06 m |
| prior150 | prior 150 m off | 523 | 0 | 0.05 m |
| crop2048 | crop 2048 px (map downscaled more by the 1024 px extractor resize) | 342 | 0 | 0.08 m |
| edge | frame at the ortho edge, 40 % of it nodata, prior 250 m off | 162 | 0 | **30.67 m** |
| negative control | Batumi frame (other OAM survey) vs Tbilisi map | 5 | - | `no reliable fix (inliers=5, need 25)` |

How to read it:

- Same survey for map and frame, so this checks the pipeline and the geometry chain
  (rotation trials, homography, half-pixel convention, EPSG:3857 => WGS84), not
  cross-season or cross-sensor robustness. Real flights will do much worse than 0.1 m.
- 60 and 135 deg yaw were handled by the 4-rotation search (best at 270 and 180).
- The **edge** case is the useful failure: 162 inliers passed the 25-inlier gate with a
  30 m wrong fix. Nodata borders and partial overlap make an inlier count a weak
  integrity signal; check the inlier spatial spread or the homography's scale/shear
  against the expected GSD and attitude before trusting a fix.
- The cross-city frame was rejected, so the gate does reject unrelated imagery.

Real UAV frames (not run here; UAV-VisLoc is 16.4 GB):

```bash
python3 geolocalize.py --frame UAV-VisLoc/01/drone/01_0001.JPG \
    --tile UAV-VisLoc/01/satellite01.tif --prior <LAT> <LON> --truth <LAT> <LON>
```

Take `--truth` from `01.csv`; offset it by a few hundred metres for `--prior`.

## Large maps: retrieval first

Local matching against one crop works when you already know roughly where you are. For
a cold start over a whole region, tile the map and retrieve candidates first:

- AnyLoc (`repo:anyloc/anyloc`): DINOv2 features + VLAD. Precompute one descriptor per
  map tile offline, query with the drone frame, take the top-k tiles.
- hloc (`repo:cvg/hierarchical-localization`): retrieval (NetVLAD etc.) + SuperPoint /
  LightGlue matching as a configurable pipeline; use its retrieval and matching stages
  even without the SfM/PnP part.

Then run `geolocalize.py` on each top-k tile and keep the one with most inliers.

## Hackathon extensions

- Fuse fixes into an INS/EKF as position measurements, gated on inlier count. Feed the
  EKF prediction back as `--prior` so each crop stays small.
- Use the drone heading (compass / INS yaw) to pre-rotate the frame instead of trying
  4 rotations; 4x faster and handles arbitrary angles.
- Scale-match: resize the frame so its ground sample distance (altitude / focal length
  in px) is close to the map GSD. Big GSD mismatch is the most common failure.
- Swap SuperPoint for DISK or ALIKED (`LightGlue(features="disk")`) and compare inliers on
  seasonal changes.

## Pitfalls

- `extractor.extract` resizes to 1024 px on the long side by default and maps keypoints
  back to original pixels. A 10k px map is unusable at 1024 px: always crop with
  `--prior` (default 2048 px window) or tile it.
- Half-pixel convention: LightGlue keypoints put integers on pixel centres, a GDAL /
  rasterio affine puts integers on pixel corners. `frame_center_to_world` adds 0.5.
- Some datasets ship maps without an embedded geotransform (identity transform, no CRS).
  UAV-VisLoc lists map bounds in `satellite_coordinates_range.csv`; build the transform
  with `rasterio.transform.from_bounds(west, south, east, north, width, height)` if the
  TIFF has none. Check `src.crs` before trusting `src.transform`.
- Nadir assumption: with camera tilt or roll, the frame centre is not the point under the
  aircraft. Correct with attitude and altitude, or use the homography plus a ground plane.
- Homography assumes a planar scene. Tall buildings and steep terrain break it; prefer
  areas with flat ground texture (fields, roads) and keep the inlier gate.
- Seasonal and illumination change between map and flight drop matches sharply; a single
  good fix is not integrity, track inlier counts over time.
