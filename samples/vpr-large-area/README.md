<!-- about: repo:anyloc/anyloc, res:anyloc-universal-vpr-2023, repo:cvg/lightglue -->

# Large-area visual place recognition: lost-GNSS recovery over 49 km2, no position prior

The missing first stage of [geoloc-license-clean](../geoloc-license-clean/). That sample matches a
drone frame to an orthophoto *when the rough position is known*. This one answers "where am I at
all" (kidnapped UAV, GNSS lost for long enough that the INS prior is useless): retrieve candidate
places from a geo-referenced tile database over a large map, then hand the top-k to the fine matcher.
Everything was **run** on an Apple M2 Max (DINOv2 on the MPS backend, LightGlue on CPU) against real
public imagery. License-clean parts only.

```
NAIP 49 km2 (5 vintages) --tiles 250 m / 100 m, stride 50 m, 8 rotations--> DINOv2 ViT-S/14 --> GeM | CLS | VLAD
query frame --centre square of tile size (GSD from AGL)--> same descriptor --cosine top-k (numpy / FAISS)-->
  candidates (east, north, heading) --geoloc.Localizer (ALIKED + LightGlue + MAGSAC), window = candidate +- 100 m-->
  fix if >= 25 inliers, else next candidate
```

## Components and licenses

| Part | License | Where checked |
|---|---|---|
| DINOv2 ViT-S/14 code and weights (`torch.hub`, pinned commit `7764ea0`) | Apache-2.0 | GitHub API for facebookresearch/dinov2; [license doc](../../docs/model-weights-licenses.md) |
| GeM, VLAD, ring histogram, tile DB, index (`vpr.py`, `index.py`, `geo.py`) | this repo | own code. VLAD follows the AnyLoc recipe (hard assignment, intra-norm) but no AnyLoc code is copied. AnyLoc itself is BSD-3-Clause (GitHub API) |
| FAISS (optional backend) | MIT | GitHub API for facebookresearch/faiss |
| Fine stage: `geoloc.py` imported from ../geoloc-license-clean (ALIKED, LightGlue, OpenCV) | BSD-3 / Apache-2.0 | see that README |
| NAIP 2015, 2017, 2019, 2021, 2023 (USDA) via Microsoft Planetary Computer | "Public Domain with Attribution" | [AWS Open Data registry](https://registry.opendata.aws/naip/) |
| USGS 3DEP 1/3 arc-second DEM (only to estimate eBee AGL) | public domain (USGS) | Planetary Computer collection `3dep-seamless` |
| eBee frames, `OpenDroneMap/odm_data_aukerman` | CC0-1.0 | repo `license.txt` |

DINOv2's training set (LVD-142M) is not released. No VPR-specific trained head is used, so the
GSV-Cities / SF-XL data caveats of MixVPR, SALAD, BoQ, EigenPlaces do not apply here.

## Files

| File | What |
|---|---|
| `download_data.py` | STAC search on Planetary Computer, reads a 7 km x 7 km window (centre -81.7505, 41.3036, UTM 17N) from the 4 NAIP quarter-quad COGs per year: 2023 at 0.6 m (native 0.3 m, read through GDAL overviews), 2019 and 2021 at 0.6 m, 2017 and 2015 at 1.0 m. Imports `get_json`, `fetch_frames` from ../geoloc-license-clean/download_data.py. Downloads 23 eBee frames (every 4th of the 77-frame survey) and samples 3DEP ground height under each one. |
| `geo.py` | stdlib only: tile grid, affine pixel <=> UTM, yaw convention, angle difference, haversine, recall@k |
| `vpr.py` | tile renderer (`render_tile`, area-filtered first), query crop, DINOv2 describer with CLS / GeM / VLAD heads masked to the inscribed circle, classic ring-histogram descriptor |
| `index.py` | exact cosine index (numpy, or FAISS `IndexFlatIP`), place-level de-duplication across rotations, multi-variant queries |
| `run_vpr.py` | builds and caches the DBs, synthetic queries (via `synth_frames.make_frame` of geoloc-license-clean) and real eBee queries, writes `out/vpr_*.json` |
| `run_chain.py` | VPR top-5 => fine matching => gate, and the known-prior baseline on the same queries, writes `out/chain_*.json` |
| `tests/` | `unittest`: geo math and index (stdlib parts always run; numpy / OpenCV / torch parts skip when missing) |

`data/` (1.2 GB with 5 vintages) and `out/` (4.2 GB of cached descriptor DBs) are git-ignored.

## Run

```bash
uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python download_data.py                         # 6-25 min per vintage here (HTTP range reads; 2021 needed 3 attempts)
.venv/bin/python run_vpr.py --skip-real                   # DBs 2023 at 250 m and 100 m x 8 rotations (~9 min each), 150 queries per source year
.venv/bin/python run_vpr.py --skip-synth                  # real eBee frames vs DBs of each vintage, 100 m and 70 m tiles
.venv/bin/python run_vpr.py --skip-synth --real-db-years 2023 --real-tiles 100 --real-yaws 8
.venv/bin/python run_chain.py --strategy gem/invariant8+hdg --synth-years 2023 2019 2017 --n 20
.venv/bin/python run_chain.py --real --tile 100 --strategy cls/invariant8+hdg --fine-year 2019
.venv/bin/python run_chain.py --real --tile 100 --strategy cls/invariant8+hdg --fine-year 2019 --skip-prior --cand-radius-m 50
python3 -m unittest discover -s tests
```

## Setup of the experiment

- **Map:** 7 km x 7 km = 49 km2 of mixed suburb, farmland, forest and parks around Medina, Ohio
  (Aukerman Park is inside). DB built from **NAIP 2023-05-26**, the newest vintage, as an operator would.
- **Tiles:** 250 m (stride 50 m, 18,496 tiles) and 100 m (stride 50 m, 19,321 tiles), each rendered to
  224 x 224 px at 8 yaws (0, 45, ... 315 deg). 70 m tiles (stride 35 m, 39,601) for the real frames only.
  With a 50 m stride, the nearest tile centre is at most 35 m from any point, so "R@k within 50 m"
  has a quantisation floor; the 100 m column is the more honest "right place" number.
- **Synthetic queries:** 150 per (tile size, source year), seed 7. 640 x 480 frames from `make_frame`
  (random centre, yaw 0-360, perspective jitter up to 6%, photometric change, blur, noise, JPEG).
  Frame GSD 0.55-0.8 m for the 250 m tiles (short side 264-384 m) and 0.22-0.3 m for 100 m tiles.
  GSD known to 5% (as from baro AGL + intrinsics). Query = centre square of the tile's ground size.
  Source years: 2023 (same imagery as the DB), 2021-06 (2 years, same season), 2019-10 (4 years,
  autumn vs late spring), 2017-06 and
  2015-07 (6 and 8 years, 1 m source, so the 100 m-tile queries are upsampled 3-4x and blurry).
- **Real queries:** 23 eBee frames (Sony WX220, 2016-06-29, EXIF GPS as truth). Heading unknown.
  AGL is ambiguous: EXIF altitude minus 3DEP ground is 64-74 m if the altitude is MSL, about 100 m
  if it is WGS84 ellipsoidal height (geoid about -34 m here, a table value I did not compute). Both
  hypotheses are reported. All 23 frames are inside one ~300 m x 150 m park, so they are far from 23
  independent places. Read real recall as "this park", not a rate.
- **Rotation strategies** (heading unknown):
  `none` = query as is vs north-up DB; `north-up-prior` = query rotated by true yaw + N(0, 5 deg) (a
  compass, the upper reference); `query-tta8` = 8 rotated queries vs north-up DB, best score wins;
  `db-aug8` = 1 query vs DB with all 8 rotations (8x index); `invariant8` = descriptor averaged over the
  8 rotations on both sides (1x index, 8 forward passes per tile and per query).
- **Classic baseline:** `ring/invariant`: Lab colour and gradient-magnitude histograms over 4 concentric
  rings (rotation-invariant by construction), Hellinger-normalised, 128-D.

## Measured results (ran 2026-11-06)

Machine: Apple M2 Max, DINOv2 ViT-S/14 on MPS, torch 2.15.0, numpy index; other agents were using the
machine at the same time, so timings are indicative. Recall cells are fractions of 150 queries.

### Retrieval, DB 2023, 250 m tiles, queries cut from the same 2023 imagery

DB build: 18,496 tiles x 8 rotations in 547 s (~270 tiles/s including rendering). Query descriptor:
18.6 ms for 1 crop, 38.7 ms for 9 crops (8 rotations + prior), MPS. Heading error is the median
over queries whose top-1 is within 100 m (n in brackets).

| Strategy | R@1 50m | R@5 50m | R@10 50m | R@1 100m | R@10 100m | R@1 250m | R@10 250m | heading err (n) | index MB | search ms |
|---|---|---|---|---|---|---|---|---|---|---|
| gem/north-up-prior | 0.50 | 0.80 | 0.86 | 0.73 | 0.90 | 0.79 | 0.94 | - | 27.1 | 0.77 |
| gem/none | 0.23 | 0.38 | 0.43 | 0.36 | 0.56 | 0.44 | 0.61 | - | 27.1 | 0.68 |
| gem/query-tta8 | 0.49 | 0.66 | 0.71 | 0.67 | 0.79 | 0.71 | 0.84 | 13.4 (100) | 27.1 | 2.25 |
| gem/db-aug8 | 0.65 | 0.89 | 0.91 | 0.85 | 0.95 | 0.90 | 0.98 | 12.4 (127) | 216.8 | 5.03 |
| **gem/invariant8** | **0.77** | **0.93** | **0.95** | **0.89** | **0.98** | **0.93** | **0.99** | - | 27.1 | 0.77 |
| cls/north-up-prior | 0.31 | 0.58 | 0.65 | 0.53 | 0.77 | 0.65 | 0.79 | - | 27.1 | 0.73 |
| cls/db-aug8 | 0.43 | 0.73 | 0.78 | 0.67 | 0.85 | 0.77 | 0.93 | 15.1 (100) | 216.8 | 5.25 |
| cls/invariant8 | 0.55 | 0.79 | 0.85 | 0.75 | 0.90 | 0.84 | 0.95 | - | 27.1 | 0.77 |
| vlad/north-up-prior | 0.69 | 0.88 | 0.91 | 0.87 | 0.95 | 0.90 | 0.97 | - | 433.5 | 10.28 |
| vlad/none | 0.25 | 0.44 | 0.53 | 0.39 | 0.63 | 0.51 | 0.71 | - | 433.5 | 10.22 |
| vlad/query-tta8 | 0.54 | 0.76 | 0.79 | 0.71 | 0.87 | 0.77 | 0.89 | 13.1 (106) | 433.5 | 16.26 |
| ring/invariant (classic) | 0.01 | 0.03 | 0.05 | 0.01 | 0.07 | 0.03 | 0.13 | - | 9.0 | 0.4 |

VLAD: 16 clusters x 384 = 6144-D, spherical k-means on 200k patch tokens from 1500 DB tiles.

### Retrieval by condition (map-vintage gap and tile size)

Each cell: R@1 within 50 m / R@10 within 100 m. DB is always NAIP 2023.

| DB / query source | gem/none | gem/query-tta8 | gem/db-aug8 | gem/invariant8 | cls/invariant8 | vlad/query-tta8 | vlad/north-up-prior | gem/north-up-prior | ring (classic) |
|---|---|---|---|---|---|---|---|---|---|
| 250 m, src 2023 (same) | 0.23 / 0.56 | 0.49 / 0.79 | 0.65 / 0.95 | **0.77 / 0.98** | 0.55 / 0.90 | 0.54 / 0.87 | 0.69 / 0.95 | 0.50 / 0.90 | 0.01 / 0.07 |
| 250 m, src 2021-06 | 0.12 / 0.39 | 0.13 / 0.47 | 0.17 / 0.57 | **0.29 / 0.73** | 0.23 / 0.59 | 0.21 / 0.56 | 0.25 / 0.73 | 0.19 / 0.63 | 0.00 / 0.01 |
| 250 m, src 2019-10 | 0.07 / 0.33 | 0.07 / 0.35 | 0.16 / 0.50 | **0.18 / 0.57** | 0.14 / 0.47 | 0.10 / 0.37 | 0.16 / 0.49 | 0.07 / 0.41 | 0.00 / 0.03 |
| 250 m, src 2017-06 | 0.07 / 0.33 | 0.15 / 0.43 | 0.19 / 0.49 | **0.24 / 0.55** | 0.14 / 0.41 | 0.17 / 0.44 | 0.25 / 0.56 | 0.19 / 0.52 | 0.00 / 0.02 |
| 250 m, src 2015-07 | 0.06 / 0.30 | 0.12 / 0.33 | 0.14 / 0.37 | **0.19 / 0.48** | 0.14 / 0.39 | 0.09 / 0.38 | 0.20 / 0.49 | 0.13 / 0.40 | 0.00 / 0.01 |
| 100 m, src 2023 (same) | 0.22 / 0.47 | 0.39 / 0.63 | 0.57 / 0.78 | **0.66 / 0.79** | 0.43 / 0.70 | 0.43 / 0.70 | 0.57 / 0.80 | 0.45 / 0.74 | 0.01 / 0.07 |
| 100 m, src 2021-06 | 0.06 / 0.26 | 0.05 / 0.27 | 0.09 / 0.29 | 0.11 / 0.35 | 0.06 / 0.20 | 0.08 / 0.28 | **0.13 / 0.37** | 0.07 / 0.27 | 0.01 / 0.04 |
| 100 m, src 2019-10 | 0.07 / 0.21 | 0.05 / 0.20 | 0.07 / 0.22 | **0.12 / 0.31** | 0.07 / 0.25 | 0.05 / 0.22 | 0.09 / 0.23 | 0.05 / 0.19 | 0.00 / 0.01 |
| 100 m, src 2017-06 | 0.03 / 0.16 | 0.04 / 0.15 | 0.05 / 0.24 | 0.05 / 0.21 | 0.01 / 0.11 | 0.05 / 0.20 | 0.08 / 0.28 | 0.05 / 0.23 | 0.00 / 0.02 |
| 100 m, src 2015-07 | 0.05 / 0.16 | 0.05 / 0.11 | 0.03 / 0.21 | 0.05 / 0.20 | 0.03 / 0.14 | 0.03 / 0.20 | 0.06 / 0.25 | 0.06 / 0.21 | 0.00 / 0.01 |

Full per-strategy tables (all k, all radii, heading error, sizes) are in `out/vpr_synth.json` after a run.

### Real eBee frames (2016) vs DBs of each vintage

23 frames, heading unknown. Cells: R@1 within 50 m / R@10 within 100 m. "y8" rows use the 8-rotation
DB, which is needed for `db-aug8` and `invariant8`.

| DB / tile / AGL hypothesis | gem/none | gem/query-tta8 | gem/invariant8 | cls/none | cls/query-tta8 | cls/db-aug8 | cls/invariant8 | vlad/query-tta8 | ring |
|---|---|---|---|---|---|---|---|---|---|
| 2023 / 100 m / AGL msl, y8 | 0.26 / 0.78 | 0.39 / 0.87 | 0.52 / 0.83 | 0.30 / 0.91 | 0.43 / 0.96 | 0.52 / 0.91 | **0.74 / 0.96** | 0.35 / 0.78 | 0.00 / 0.00 |
| 2023 / 100 m / AGL ellipsoid, y8 | 0.43 / 0.74 | 0.52 / 0.83 | 0.43 / 0.83 | 0.39 / 0.87 | 0.43 / 0.96 | 0.65 / 0.91 | **0.70 / 0.96** | 0.39 / 0.74 | 0.00 / 0.00 |
| 2023 / 70 m / AGL msl | 0.13 / 0.52 | 0.17 / 0.61 | - | 0.39 / 0.74 | 0.35 / 0.83 | - | - | 0.17 / 0.52 | 0.00 / 0.00 |
| 2021 / 100 m / AGL msl | 0.26 / 0.70 | 0.39 / 0.83 | - | 0.17 / 0.74 | 0.35 / 0.78 | - | - | 0.09 / 0.65 | 0.00 / 0.00 |
| 2021 / 100 m / AGL ellipsoid | 0.17 / 0.70 | 0.26 / 0.78 | - | 0.26 / 0.74 | 0.26 / 0.65 | - | - | 0.09 / 0.57 | 0.00 / 0.00 |
| 2019 / 100 m / AGL ellipsoid | 0.09 / 0.57 | 0.09 / 0.78 | - | 0.22 / 0.70 | 0.22 / 0.78 | - | - | 0.04 / 0.48 | 0.00 / 0.00 |
| 2019 / 100 m / AGL msl | 0.09 / 0.57 | 0.13 / 0.74 | - | 0.26 / 0.74 | 0.22 / 0.78 | - | - | 0.04 / 0.57 | 0.00 / 0.00 |
| 2017 / 100 m / AGL ellipsoid | 0.09 / 0.35 | 0.09 / 0.35 | - | 0.04 / 0.48 | 0.09 / 0.70 | - | - | 0.22 / 0.70 | 0.00 / 0.00 |
| 2015 / 100 m / AGL ellipsoid | 0.13 / 0.43 | 0.13 / 0.43 | - | 0.17 / 0.39 | 0.13 / 0.52 | - | - | 0.04 / 0.22 | 0.00 / 0.00 |

### Chain: VPR top-5 => fine matching => inlier gate, vs fine matching with a known prior

Fine stage: `geoloc.Localizer("aliked")` from geoloc-license-clean, CPU, gate 25 inliers. Chain: rank places
with `invariant8`, read each candidate's heading from its 8 stored rotated descriptors, then try
candidates in rank order, 3 headings each (estimate +- 20 deg), window = candidate +- 100 m; stop at the
first gated fix. Known prior: truth + 100 m in a random direction, radius 150 m, heading truth + N(0, 5 deg),
one call (the geoloc-license-clean protocol). Fine map = NAIP 2023 at 0.6 m unless stated. 20 synthetic
queries per row (seed 11, 250 m tile DB, `gem/invariant8+hdg`).

| Queries | VPR top-5 within 100 m | Chain fixes | Chain wrong (> 50 m) | Chain median err | Chain median time / tries | Known-prior fixes | Known-prior median err | Known-prior time |
|---|---|---|---|---|---|---|---|---|
| synthetic, src 2023 | 20/20 | **20/20** | 0 | 0.22 m | 7.1 s / 3 | 20/20 | 0.18 m | 2.0 s |
| synthetic, src 2017-06 | 7/20 | **8/20** | 0 | 4.7 m | 26.4 s / 15 | 20/20 | 4.5 m | 1.7 s |
| synthetic, src 2019-10 | 9/20 | **3/20** | 0 | 2.4 m | 23.1 s / 15 | 12/20 | 2.5 m | 1.5 s |
| real eBee, fine map 2019, window +- 100 m | 22/23 | 0/23 | 0 | - | 15.1 s / 30 | 0/23 (24 headings x 2 AGL) | - | 33.8 s |
| real eBee, fine map 2023, window +- 100 m | 22/23 | 0/23 | 0 | - | 17.0 s / 30 | not run | - | - |
| real eBee, fine map 2019, window +- 50 m | 22/23 | **1/23** (DSC00252, 26 inliers, rank 4) | 0 | 20.1 m | 10.2 s / 30 | not run | - | - |

Real-frame chain: `cls/invariant8+hdg` on the 2023 100 m DB, crop from the ellipsoid AGL hypothesis, fine
stage tries both AGL hypotheses (2 x 3 headings x 5 candidates = 30 calls max). VPR descriptor + search:
~0.09 s per query; everything else is the fine matcher.

Where the place was right, the heading read off the rotated descriptors was off by a median 9 deg (20
synthetic queries, src 2023). In two synthetic cases the gate accepted a fix from a candidate 150-175 m from
truth: the window is candidate +- 100 m plus the frame footprint, so the matcher reaches further than the
radius suggests. Those fixes were 2-8 m accurate.

**Real frames: VPR alone found the park, the fine stage did not close.** VPR top-1 was within 50 m for 16 of
23 frames (median top-1 distance 37.7 m, best of top-5 24.8 m) over 49 km2 with no prior and no heading.
The ALIKED + LightGlue stage then saw 4-12 inliers against the 2019 map with a 100 m window (the gate is 25),
the same failure geoloc-license-clean reported for these 2016 frames. A 50 m window gave 1 fix in 23,
20 m off. The gate held: no wrong fix was accepted in any chain or prior run.

## What the numbers say

- **Rotation-averaged descriptors won.** `gem/invariant8` (average the GeM vector over 8 rotations, on both
  DB and query sides) matched or beat rotation-augmenting the DB in every synthetic condition (clearly in
  8 of 10; within noise on the 100 m tiles with 2015 / 2017 sources), at 1/8 of the index size, and it beat even the north-up query with a compass-grade heading prior (0.77 vs 0.50 R@1 within 50 m
  on 250 m tiles). Averaging over rotations also smooths over the perspective and crop differences. Query
  TTA (rotate the query 8 times) was the weakest of the three; I did not isolate why. On real frames `cls/invariant8` was best
  (0.70-0.74 R@1 within 50 m), `gem/invariant8` was not, so try both heads.
- **The price of invariance is heading.** An invariant descriptor gives no heading. `db-aug8` and
  `query-tta8` do (median 12-15 deg error where the place is right), which cuts the fine matcher's cold
  heading sweep from 24 tries to 3. The chain uses both: rank places with `invariant8`, then read each
  candidate's heading off its 8 stored rotated descriptors (one dot product per rotation, no extra search).
  That needs the 8-rotation descriptors on disk, but only the averaged ones in the search index.
- **Map-vintage gap dominates everything.** Same imagery: 0.98 R@10 within 100 m on 250 m tiles (best
  strategy). 2 years, same season: 0.73. 4 to 8 years: 0.48-0.57. On 100 m tiles: 0.79 => 0.35 => 0.20-0.31.
  The 2021 to 2023 gap alone (same sensor class, both late spring) costs 25 points of R@10. The bigger tile carries more
  layout (road network, field boundaries) and survives time better. That suggests climbing (bigger
  footprint) before a recovery query; the synthetic frames also differ in GSD per tile size, so this is
  not a clean altitude experiment.
- **The newest map was best for real 2016 frames,** not the temporally closer 2015 / 2017 vintages (1 m,
  and upsampled for 100 m tiles, which is a confound) nor 2019 (October). That is the opposite of the fine
  stage, where geoloc-license-clean found the 2019 map gave its only fix. Retrieval wants sharp, leaf-on
  layout; fine matching wants the same texture.
- **The classic baseline is useless at this scale.** Ring colour / gradient histograms: R@10 within
  250 m of 0.13 at best, 0.00 on real frames. Colour statistics do not identify a place among 18k tiles.
- **Chain fix rate = retrieval hit rate x fine-match success.** Same imagery: both 100%, so the chain equals
  the known-prior result (0.22 vs 0.18 m) at 3.5x the time. Across 4-6 years the fine matcher alone fixed
  60-100% with a prior, but retrieval put the right place in the top 5 only 35-45% of the time, so the chain
  fixed 15-40%. On real 2016 frames the order flips: retrieval worked (22/23 in top 5), fine matching did not.
  Neither stage alone is the bottleneck in general; which one fails depends on the map gap.
- **Retrieval is cheap; verification is the bottleneck for time.** 20-40 ms per query descriptor on MPS and
  under 1 ms for a numpy search over 18k x 384 floats (5 ms with the 8x augmented index, 10-16 ms for
  6144-D VLAD). Each fine-matcher call is 1.5-2.5 s on CPU. Budget the top-k by the matcher, not the index.
- **VLAD did not pay for its size here.** 433 MB vs 27 MB for GeM, and `vlad/query-tta8` was at or below
  `gem/invariant8` in every synthetic row. AnyLoc-style VLAD shines with bigger backbones and domain vocabularies (not tested).

## Gotchas found while running

- **FAISS and torch in one process aborted** on macOS arm64 (`OMP: Error #15`, both pip wheels bundle
  libomp). The runners use the numpy backend; `tests/test_index.py` checks in a subprocess that FAISS
  `IndexFlatIP` returns the same top-5 ids as numpy. At 20-40k tiles exact numpy search is under 1 ms
  anyway. Use FAISS (IVF / PQ) when the DB is millions of tiles, in its own process.
- **Rotated tiles from a big map need area filtering first.** `render_tile` uses `warpAffine`, which has
  no area filter (the same aliasing bug geoloc-license-clean hit), so `run_vpr.build_db` downsamples the
  map with `INTER_AREA` to the tile GSD once, then warps at about 1:1.
- **A planetary-scale COG read can fail mid-way** (`TIFFFillTile ... got 0 bytes` after 20 min). The
  download retries each vintage 3 times with GDAL HTTP retries on.
- **Without place de-duplication a top-10 list from the 8x DB is the same place at several headings.**
  `TileIndex.search_places` keeps the best hit per place.

## Hackathon extensions

- Feed `out/` DBs to an EKF as a "global fix candidate" generator: VPR top-k + fine-match gate =>
  position measurement with covariance from inliers, as suggested in geoloc-license-clean.
- Multi-frame voting: consecutive frames + INS odometry, accumulate tile scores along the track (a
  particle filter over tile IDs). Single-frame recall at 4+ year gaps is 0.2-0.5; a sequence should do
  much better. Not tested here.
- Try ViT-B/14 (153 img/s vs 338 for ViT-S on this MPS) and 322 px input; both measured only for speed.
- Fine-tune nothing, but pick the map vintage: build DBs for 2 vintages and search both.
