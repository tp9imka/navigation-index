# python-tercom - integration card
<!-- about: repo:alti3/python-tercom -->
One-line: a two-file NumPy demo of TERCOM - simulate a noisy altimeter profile over a height grid, brute-force search position + heading by MSE, print the fix as a GPGGA sentence - the shortest path to a terrain-matching slide or notebook.

| | |
|---|---|
| Install | `git clone https://github.com/alti3/python-tercom && cd python-tercom && uv sync` (README; `pyproject.toml`: `requires-python >=3.12`, single dependency `numpy>=2.2.4`; `uv.lock` committed). Plain pip works too: `pip install "numpy>=2.2.4"`. No releases; last push 2025-04. |
| Runs on | Anything with Python 3.12+ and NumPy. CPU only, single-threaded pure-Python loops. No ROS, no GPU. |
| Inputs | Height grid as a NumPy `.npy` 2D array (metres) in `data/`, plus a JSON sidecar with `lat_top`, `lon_left`, `lat_bottom`, `lon_right`, `height`, `width` (rows/cols must equal the array shape, checked in `load_terrain_data`). No GeoTIFF/DEM reader: SRTM/Copernicus tiles must be converted to `.npy` + JSON yourself. If no files exist, `main.py` generates a synthetic 100x150 map (slope + 15 random Gaussian hills + noise) over lat 40.0-39.8, lon -74.0 to -73.7. Measured profile: 1D array of terrain heights, one sample per grid cell along a straight heading. |
| Outputs | Console: true vs estimated start cell, lat/lon, heading, MSE. A GPGGA string appended to `nmea_tercom_output.csv`. |
| Key API / entry points | `tercom.py`: `load_terrain_data(map_file="data/terrain_map.npy", metadata_file="data/map_metadata.json") -> (terrain_map, metadata)`; `simulate_observed_profile(terrain_map, metadata, true_y, true_x, length, heading_deg, noise_stddev=1.0)`; `find_best_match(terrain_map, observed_profile, possible_headings_deg=None) -> (best_y, best_x, best_heading, min_error)`; `indices_to_latlon(y, x, metadata)`; `create_gpgga_sentence(lat, lon, altitude=0)`. `main.py`: `generate_example_data(...)`, `main()`. |
| Time to first result | Estimate: 5 min (`uv run main.py` on the synthetic map). 1-2 h to run on a real DEM crop, mostly the GeoTIFF => `.npy` + JSON conversion. |
| License | GitHub metadata: none detected, and there is no LICENSE file in the repo. No license means all rights reserved by default: you may read it, but copying or redistributing code needs the author's permission. For a hackathon, reimplementing the ~30-line matching idea yourself is cleaner than vendoring it. |

## Minimal usage
Not run. From the README, plus a DEM conversion sketch using [rasterio](../../catalog/repos/rasterio__rasterio.md) (not part of this repo).

```bash
uv run main.py        # synthetic map, true heading 45 deg, searches every 30 deg
```

```python
import json, numpy as np, rasterio
with rasterio.open("srtm_crop.tif") as src:          # geographic (EPSG:4326) crop
    z = src.read(1).astype(float)
    w, s, e, n = src.bounds
np.save("data/my_map.npy", z)
json.dump({"lat_top": n, "lon_left": w, "lat_bottom": s, "lon_right": e,
           "height": z.shape[0], "width": z.shape[1]}, open("data/my_map_metadata.json", "w"))
# then: tercom.load_terrain_data("data/my_map.npy", "data/my_map_metadata.json")
```

## Wiring it into a nav stack
- DEM input: get SRTM / Copernicus DEM with [elevation](../../catalog/repos/bopen__elevation.md), crop around your prior position, convert as above. Keep the crop small (see cost below). [terrain-nav-preprocessing](../../catalog/repos/hstm__terrain-nav-preprocessing.md) is relevant if you want DEM tiles with controlled roughness.
- Real measurement model is yours: terrain height = baro/GNSS-free altitude AMSL minus radar/lidar AGL, sampled at fixed ground distance equal to the DEM cell size. The demo only samples the grid itself plus Gaussian noise.
- Output path: the GPGGA string is a demo artefact, not a safe GPS emulator (see Gotchas). For a real stack feed the lat/lon with an honest covariance into a filter, which is exactly what [tercom_nav](./mzahana__tercom_nav.md) does in ROS 2 with an ESKF.
- Pairs naturally with a visual fix ([WildNav](./tiers__wildnav.md)) for a "two independent non-GNSS position sources" demo.

## Gotchas
- Cost: `find_best_match` is three nested Python loops (heading x row x col) with an inner per-sample loop. On a full 1-arc-second SRTM tile (3601 x 3601 cells) with 12 headings and 25 samples that is ~3.9e9 inner steps (computed), i.e. impractical in Python. Crop to a few hundred cells around a prior or vectorise (tercom_nav's `match_profile` is a vectorised reference).
- Grid geometry is idealised: one profile sample per grid cell, cells assumed square, lat/lon from linear interpolation of the bounding box (`indices_to_latlon`; README "Linear Georeferencing"). Real DEMs in degrees have non-square cells away from the equator.
- Heading must be near one of the searched values; README example finds heading 60 for a true 45. Use INS heading to constrain the search (README "Heading Sensitivity").
- Mean-removed MSE only; no ambiguity/discrimination check, no rejection over flat terrain (README "Ambiguity"). A best match is always returned.
- `create_gpgga_sentence` hardcodes fix quality `1`, 8 satellites, HDOP 1.0, and puts terrain height (not vehicle altitude) in the altitude field. Never feed it to an autopilot as if it were GNSS.
- Uses `datetime.datetime.utcnow()`, deprecated since Python 3.12 (warning only).
- No license (see table).

## Alternatives
- [tercom_nav](./mzahana__tercom_nav.md) - vectorised matcher with MAD/discrimination/roughness gating, GeoTIFF loading and an ESKF, in ROS 2; the step up once the concept is clear.
- [tercom-python](../../catalog/repos/ayushmankumar7__tercom-python.md) - OpenCV demo that adds scene matching next to terrain contours.
- [rhymesg/particle_filter](../../catalog/repos/rhymesg__particle_filter.md) - MATLAB particle-filter terrain-referenced navigation; handles multimodal ambiguity that single best-match TERCOM cannot.

Sources: alti3/python-tercom README.md, tercom.py, main.py, pyproject.toml, data/map_metadata.json, repo tree; GitHub license metadata (via `gh api`, 2026-11-06).
