# License-clean visual geolocalization: drone frame => NAIP orthophoto => lat/lon

The same task as [visual-geolocalization-lightglue](../visual-geolocalization-lightglue/),
built only from parts whose licenses allow redistribution and commercial use, and **run** on
CPU against real public imagery. SuperPoint and SuperGlue are left out on purpose. Their Magic
Leap license is noncommercial internal research only: see
[docs/model-weights-licenses.md](../../docs/model-weights-licenses.md).

```
frame --rotate north-up by heading prior, resample to map GSD--> query
map window around position prior --resample--> reference
ALIKED | DISK | SIFT --LightGlue--> matches --MAGSAC homography (OpenCV)--> frame centre in map px
--GeoTIFF affine--> UTM 17N --rasterio.warp--> WGS84 lat/lon      (gate: >= 25 inliers or no fix)
```

## Components and licenses

| Part | License | Where checked |
|---|---|---|
| LightGlue code + `aliked/disk/sift_lightglue` weights | Apache-2.0 | LightGlue README "License" |
| ALIKED code + `aliked-n16.pth` | BSD-3-Clause | GitHub API for Shiaoming/ALIKED; LightGlue README |
| DISK `depth-save.pth` (downloaded by kornia from `huggingface.co/kornia/disk`) | HF card: MIT; original cvlab-epfl repo: Apache-2.0 | HF API, GitHub API |
| OpenCV (SIFT, MAGSAC), kornia, rasterio | Apache-2.0 / Apache-2.0 / BSD-3-Clause | GitHub API |
| NAIP imagery (USDA), via Microsoft Planetary Computer | "Public Domain with Attribution" | [AWS Open Data registry](https://registry.opendata.aws/naip/) |
| eBee frames, `OpenDroneMap/odm_data_aukerman` | CC0-1.0 | repo `license.txt` |

Training data of the weights (MegaDepth, CC BY 4.0, whose images keep their Flickr licenses)
is the remaining caveat. See the license doc.

## Files

| File | What |
|---|---|
| `download_data.py` | STAC search on Planetary Computer, SAS token, reads a 2 km x 2 km window straight from the NAIP COGs (mosaics 2 quarter-quads) for 2023 (0.3 m) and 2019 (0.6 m). Downloads 5 eBee JPEGs. |
| `geoloc.py` | `OrthoMap` (GeoTIFF + CRS helpers) and `Localizer` (prior window, north-up query, extractor + LightGlue, MAGSAC, inlier gate, pixel => lat/lon) |
| `synth_frames.py` | Synthetic 640x480 frames: random centre, yaw 0-360, scale 1.1-1.8x source GSD, corner jitter up to 6% (perspective), gamma / contrast / colour cast / blur / noise / JPEG 60-90. Truth = frame centre through the generating homography. |
| `run_eval.py` | Synthetic eval + real eBee frames, writes `out/results*.json` |
| `thumbs/` | 4 small JPEGs (public domain / CC0 sources) |

`data/` (159 MB) and `out/` are git-ignored.

## Run

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt   # we used uv venv, Python 3.12.14
.venv/bin/python download_data.py          # ~7 min here; GDAL range reads over HTTPS
.venv/bin/python run_eval.py --n 20        # all extractors, synthetic + real, ~60 min on CPU
.venv/bin/python run_eval.py --features aliked sift --skip-synth \
    --prior-offset-m 30 --search-radius-m 60 --out results_real_tight.json
```

Weights download on first use into `~/.cache/torch/hub/checkpoints/`: ALIKED from
github.com/Shiaoming/ALIKED, LightGlue weights from cvg/LightGlue releases v0.1_arxiv, and DISK
from huggingface.co/kornia/disk.

## Measured results (ran 2026-11-06)

Machine: Apple M2 Max, CPU only, torch 2.15.0 with 8 threads, OpenCV 5.0.0. Other agents were
using the same machine during the runs, so timings are indicative and probably a bit pessimistic.
"t/frame" is one extractor + match + homography call (query and reference extraction included,
model loading and warm-up excluded). Map: NAIP 2023-05-26, 0.3 m, 6667 x 6667 px, EPSG:26917.
Position prior = truth + 100 m in a random direction. Search radius 150 m. Heading prior =
truth + N(0, 5 deg). Scale prior = truth x (1 + N(0, 0.05)). Max 2048 keypoints. Same 20 frames
(seed 7) for every extractor.

**Synthetic, frames cut from the same 2023 map** (photometric + perspective change only):

| Extractor | Fixes | <= 5 m | Median err | Max err | Median t/frame |
|---|---|---|---|---|---|
| ALIKED + LightGlue | 20/20 | 20 | 0.11 m | 0.29 m | 1.43 s |
| DISK + LightGlue | 20/20 | 20 | 0.11 m | 1.06 m | 2.79 s |
| SIFT + LightGlue | 20/20 | 20 | 0.10 m | 0.28 m | 0.28 s |

**Synthetic, frames cut from NAIP 2019-10-12 (0.6 m), matched against the 2023 map**
(different season, sensor and orthorectification):

| Extractor | Fixes | <= 5 m | Median err | Max err | Median t/frame |
|---|---|---|---|---|---|
| ALIKED + LightGlue | 20/20 | 19 | 3.88 m | 6.38 m | 1.67 s |
| DISK + LightGlue | 16/20 | 10 | 4.82 m | 15.63 m | 3.14 s |
| SIFT + LightGlue | 13/20 | 13 | 1.90 m | 3.26 m | 0.46 s |

The 2-5 m floor in the cross-season case is consistent with co-registration offsets between NAIP
vintages: errors are measured against the 2019 geotransform, and the fix uses the 2023 one. I did
not measure that offset separately. No wrong fix passed the gate in any synthetic run: the worst
accepted fix was 15.6 m off.

**Real eBee frames (Sony WX220, 2016-06-29, ~3 cm GSD) with EXIF GPS as truth.** Heading and
AGL are unknown. The cold search sweeps 24 headings x 3 AGL guesses (80/100/120 m) and keeps the
max-inlier result. After one fix it reuses that camera-vs-track offset and AGL ("warm", 9 tries).

| Config | Map | ALIKED | SIFT | DISK |
|---|---|---|---|---|
| prior +100 m, radius 150 m | 2023 | 0/5 fixes (best 6-8 inliers), ~90 s/frame search | 0/5, ~16 s | 0/5, ~290 s |
| prior +100 m, radius 150 m | 2019 | 0/5 (best 10 inliers) | 0/5 | 0/5 |
| prior +30 m, radius 60 m | 2023 | 0/5 (best 12 inliers) | 0/5 | not run |
| prior +30 m, radius 60 m | 2019 | **1/5: DSC00255, 47 inliers, 11.0 m error**, 105 s cold search | 0/5 | not run |

Real output for the one fix (`out/run_real_tight.log`):

```
aliked/real-vs-2019 {"n": 5, "fixes": 1, "within_5m": 0, "within_20m": 1, "median_err_m": 11.02, ...}
   DSC00229.JPG cold tries 72 inliers 8 err_m None agl 100 hdg 165.0 search_s 112.38
   DSC00240.JPG cold tries 72 inliers 10 err_m None agl 120 hdg 75.0 search_s 96.43
   DSC00255.JPG cold tries 72 inliers 47 err_m 11.02 agl 120 hdg 315.0 search_s 104.97
   DSC00270.JPG warm tries 9 inliers 7 err_m None agl 120 hdg 119.2 search_s 12.71
   DSC00285.JPG warm tries 9 inliers 7 err_m None agl 110 hdg 139.2 search_s 6.68
```

`thumbs/real_DSC00255.jpg` is the frame. `thumbs/real_DSC00255_naip2019_fix.jpg` is the 2019 NAIP
around the fix (red cross). The 11 m error includes the eBee's uncorrected GPS and the
off-nadir tilt of a fixed-wing airframe. Neither was measured.

### What the real-frame result says

- **The synthetic numbers overstate real performance by a lot.** Seven years between flight
  (2016) and map (2023), mown-trail patterns that changed, tree canopy at 3 cm vs 30 cm, and
  unknown heading and scale together took the clean stack from 100% to 0-20% fixes on these
  5 frames. 5 frames from one park is a tiny sample. Read it as a warning, not a rate.
- **The temporally closer map won.** The 2019 0.6 m map gave the only fix. The newer, sharper
  2023 0.3 m map gave none. Map date matters more than map resolution.
- **A tight prior matters.** The same frame failed with a 100 m / 150 m window and fixed with
  30 m / 60 m. Feed the EKF's position and covariance into the window size.
- **Heading is the expensive unknown.** A cold 360 deg sweep costs 72 matcher calls (~100 s with
  ALIKED on this CPU). A compass or INS yaw cuts that to 1-3 calls.
- **The inlier gate held.** No wrong fix (> 20 m) was accepted on real frames in any config. Best
  rejected candidates had 6-12 inliers against the gate of 25.

## Bug found while running

The first version rotated and downsampled the query in one `cv2.warpAffine` call. warpAffine
has no area filter, so shrinking a 3 cm frame to 0.3-0.6 m aliased the texture away. The fix,
now in `geoloc.prepare_query`, is a `cv2.resize(INTER_AREA)` first and the rotation after.
Synthetic frames hid the bug, because their scale change was only 1-2x. Real frames exposed it
(10-20x).

## Hackathon extensions

- Retrieval first: DINOv2 (Apache-2.0) + GeM/VLAD over map tiles to find the window, then this
  matcher. See the license doc for which VPR heads are clean.
- Use `res["inliers"]` as the measurement-noise driver in an EKF update. Keep the inlier gate.
- Retrain LightGlue on aerial pairs with glue-factory (Apache-2.0), with frames from a map
  vintage different from the reference, to close the cross-season gap with clean provenance.
- Pre-cache the weights and record their SHA256 for an offline demo.
