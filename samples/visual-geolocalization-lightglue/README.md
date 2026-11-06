# Visual geolocalization: drone frame to orthophoto with LightGlue

## Goal

Get an absolute lat/lon fix for a drone without GNSS by matching a nadir camera frame
against a georeferenced satellite map or orthophoto:

```
drone frame --SuperPoint+LightGlue--> matches --MAGSAC homography H--> frame centre in tile pixels
            --GeoTIFF affine geotransform--> map coords (UTM or lon/lat) --rasterio.warp--> WGS84 lat/lon
```

The frame centre of a nadir camera is (to first order) the point under the aircraft,
so the mapped centre is the position fix. The camera is passive: nothing is emitted.

## Files

| File | What | Verified |
|---|---|---|
| `geo_math.py` | Stdlib: affine pixel<->world, homography point mapping, WGS84 UTM forward/inverse, haversine, `frame_center_to_world` | ran, 12 unit tests |
| `test_geo_math.py` | `unittest` suite for the above | ran |
| `geolocalize.py` | Full pipeline with torch + LightGlue + OpenCV + rasterio | syntax-checked only |

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
- Pipeline (not installed or run here): Python 3.10+, `torch>=2.0`, `opencv-python>=4.5`
  (for `cv2.USAC_MAGSAC`), `rasterio`, `numpy`, and LightGlue from source:

```bash
git clone https://github.com/cvg/LightGlue.git && python -m pip install -e LightGlue
python -m pip install opencv-python rasterio
```

## Run

Stdlib math and tests (no dependencies):

```bash
cd samples/visual-geolocalization-lightglue
python3 -m unittest -v test_geo_math
```

Observed output (python3.14.7, 2026-11-06), trimmed:

```
test_rotated_scaled_frame_centre_lands_on_expected_ground_point ... ok
test_corner_and_centre ... ok
test_from_gdal ... ok
test_round_trip_with_rotation_terms ... ok
test_one_degree_latitude ... ok
test_degenerate ... ok
test_identity ... ok
test_projective_divide ... ok
test_similarity ... ok
test_central_meridian_at_45n ... ok
test_round_trip_north_and_south ... ok
test_symmetry_about_central_meridian ... ok
----------------------------------------------------------------------
Ran 12 tests in 0.000s

OK
```

The UTM test anchors on the WGS84 meridian arc to 45 deg (4,984,944.378 m, matched within
1 cm) plus 1 cm round trips in both hemispheres.

Full pipeline (unverified, needs the dependencies above), on a UAV-VisLoc site:

```bash
python3 geolocalize.py --frame UAV-VisLoc/01/drone/01_0001.JPG \
    --tile UAV-VisLoc/01/satellite01.tif \
    --prior <LAT> <LON> --truth <LAT> <LON>
```

Take `<LAT> <LON>` for `--truth` from `01.csv`; for `--prior` add a few hundred metres of
offset to emulate INS drift. Expected output shape (not observed):

```
fix lat=... lon=... inliers=<N> frame_rotation=<0|90|180|270>deg
error vs truth: <metres> m
```

If inliers < 25 it prints `no reliable fix` instead of a guess.

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
