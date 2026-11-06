# WildNav - integration card
<!-- about: repo:tiers/wildnav -->
One-line: ~300 lines of Python that match nadir drone photos against georeferenced satellite tiles with SuperPoint+SuperGlue and turn the best homography into lat/lon - the smallest readable "visual GPS" baseline, but its matcher is non-commercial.

| | |
|---|---|
| Install | `python3 -m venv env && source env/bin/activate && git clone git@github.com:TIERS/wildnav.git && cd wildnav && git submodule update --init --recursive && pip3 install -r requirements.txt`. Pins: `torch==1.12.1`, `opencv_python==4.5.5.64`, `pandas==1.4.2`, `scikit_learn==1.1.2`, `haversine==2.5.1`. Submodule `src/superglue_lib` = magicleap/SuperGluePretrainedNetwork (ships `superpoint_v1.pth`, `superglue_outdoor.pth`, `superglue_indoor.pth`). One GitHub release `wildnav_v1.0` (2022-10-18, no assets); last push 2025-06. |
| Runs on | README: "tested on Ubuntu 20.04 with Python 3.10". CUDA if available, else CPU via `force_cpu = True` in `src/superglue_utils.py` (README: "much slower"). torch 1.12.1 has no wheels for Python 3.11+, so stay on <=3.10 or unpin. Opens an OpenCV GUI window by default (`no_display = False`), so headless/SSH runs need that flag flipped. No MPS, ONNX or TensorRT path in the repo. |
| Inputs | Query photos in `assets/query/` + `assets/query/photo_metadata.csv` (`Filename,Latitude,Longitude,Altitude,Gimball_Roll,Gimball_Yaw,Gimball_Pitch,Flight_Roll,Flight_Yaw,Flight_Pitch`; produced from EXIF by `src/extract_image_meta_exif.py`; lat/lon only used for error reporting). Map tiles in `assets/map/` + `assets/map/map.csv` (`Filename,Top_left_lat,Top_left_lon,Bottom_right_lat,Bottom_right_long`, WGS84 degrees). Images resized to max side 800 px before matching (`resize = [800]`). |
| Outputs | Per query: printed calculated lat/lon, `results/<photo>_located.png` (match visualisation), match images `results/matches_*.png`, and a row appended to `results/calculated_coordinates.csv` (truth, calculated, lat/lon error, haversine metres error, matched flag). |
| Key API / entry points | `src/wildnav.py` is a script (runs on import): `csv_read_sat_map(filename)`, `csv_read_drone_images(filename)`, `calculate_geo_pose(geo_photo, center, features_mean, shape)`, classes `GeoPhoto`, `GeoPhotoDrone`. `src/superglue_utils.py`: `match_image()` returns `(satellite_map_index, center, located_image, features_mean, last_frame, max_matches)`, uses `superglue_lib.models.matching.Matching(config)` + `cv2.findHomography(..., cv2.RANSAC, 5.0)`. `src/build_map.py`: downloads a tile grid from Google Static Maps (zoom 18, 640x640, scale 2) and writes `map.csv`. |
| Time to first result | Estimate: 30-45 min to run on the bundled sample query/map images with a CUDA GPU and Python 3.10 available. Half a day for your own area (tile download + CSVs + EXIF). |
| License | WildNav code: BSD-3-Clause (GitHub metadata, LICENSE "Copyright (c) 2022, TIERS"). Hard dependency SuperGlue (code AND the bundled SuperPoint/SuperGlue weights) is under Magic Leap's "ACADEMIC OR NON-PROFIT ORGANIZATION NONCOMMERCIAL RESEARCH USE ONLY" license agreement (submodule LICENSE). Map imagery: `build_map.py` pulls Google Static Maps tiles; those are governed by Google Maps Platform terms, not by this repo. |

## Minimal usage
Not run. From the README.

```bash
cd wildnav
git submodule update --init --recursive
pip3 install -r requirements.txt
cd src
# headless box: set force_cpu / no_display in superglue_utils.py first if needed
python3 wildnav.py           # uses the sample tiles + queries already in assets/
cat ../results/calculated_coordinates.csv
```

## Wiring it into a nav stack
- What it is: a single-shot absolute fix per image, no filter, no time. `wildnav.py` loops every query against every tile in `assets/map/` (brute force), keeps the tile with most matches, and maps the homography centre linearly into the tile's lat/lon box.
- Put a retrieval stage in front ([AnyLoc](./anyloc__anyloc.md), or pick a model with [VPR-methods-evaluation](./gmberton__vpr-methods-evaluation.md)) so only top-k tiles are matched.
- Swap the matcher for a permissive one: [LightGlue](../../catalog/repos/cvg__lightglue.md) with a non-SuperPoint extractor such as DISK or ALIKED (check each weight file's license before relying on it), or [XFeat](../../catalog/repos/verlab__accelerated_features.md); for Jetson, [LightGlue-ONNX](../../catalog/repos/fabio-sim__lightglue-onnx.md) provides ONNX/TensorRT export. The interface is just "two images => matched keypoints", so `match_image()` is the only function to replace.
- Feed the output as an absolute position measurement with a covariance into an EKF/ESKF (the pattern [tercom_nav](./mzahana__tercom_nav.md) uses for terrain fixes), not straight to the autopilot. Gate on inlier count and on the README-reported localisation rate (62% / 56% of photos localised on its two datasets).
- Map tiles from your own source: any georeferenced orthophoto cut into tiles with corner coordinates works ([rasterio](../../catalog/repos/rasterio__rasterio.md) for the cut, [OpenDroneMap](../../catalog/repos/opendronemap__odm.md) for a fresh orthomosaic).

## Gotchas
- SuperGlue dependency answers the lane question: yes, WildNav depends on SuperGlue via the `src/superglue_lib` submodule, and the license forbids commercial use, redistribution and sublicensing; derivatives become Magic Leap's property. Fine for a hackathon demo, a blocker for anything shipped.
- Sample dataset link (UTU SharePoint) is dead - issue #3 open since 2024-12 with no replacement. Only the few sample images in `assets/` remain.
- `build_map.py` contains a hardcoded Google API key (comment says IP-restricted, "you need to get your own") and its `MAP_PATH` is `../assets/maps/map_2/`, not the `../assets/map/` that `wildnav.py` reads.
- Pose model is crude: `calculate_geo_pose` linearly interpolates lat/lon from the homography centre in the tile; it ignores altitude, camera tilt and lens model, and only one rotation (`rotations = [20]`) is tried. Off-nadir or heading-flipped frames fail to match.
- The query image is written into the map folder as `1_query_image.png` and relies on alphabetical sort to be frame 0 of the SuperGlue `VideoStreamer`. Tile filenames that sort before "1_" break the index mapping silently.
- Relative paths everywhere (`../assets/...`, `../results/`): must run from `src/`. Issue #4 (2025-09): "codebase is quite unorganized and hard to work with".
- CUDA capability mismatch with the pinned torch on RTX 30xx (README "Common problems" #1) - reinstall torch for your CUDA.

## Alternatives
- [terbouchehacene/visual_localization](../../catalog/repos/terbouchehacene__visual_localization.md) - cleaner reimplementation of the same idea; check its matcher license too.
- [hmf21/uavlocalization](../../catalog/repos/hmf21__uavlocalization.md) - adds the retrieval-then-match structure WildNav lacks.
- [UAV-VisLoc](../../catalog/repos/intellisensing__uav-visloc.md) - not code to replace WildNav, but a real UAV-imagery + satellite-map dataset to replace its dead sample link.

Sources: TIERS/wildnav README.md, .gitmodules, requirements.txt, LICENSE, src/wildnav.py, src/superglue_utils.py, src/build_map.py, assets/map/map.csv, assets/query/photo_metadata.csv; issues #1, #3, #4; magicleap/SuperGluePretrainedNetwork LICENSE and models/weights listing (via `gh api`, 2026-11-06).
