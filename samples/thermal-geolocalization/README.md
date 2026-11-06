# Thermal UAV frame => RGB satellite map => lat/lon, day and night, with an integrity gate

Night operations take away the RGB camera. This sample runs the
[geoloc-license-clean](../geoloc-license-clean/) idea on **real thermal frames**: a nadir
DJI Matrice 4T thermal image, a position prior and a heading prior are matched against a
visible-light satellite GeoTIFF, and a geometric gate decides whether the fix is trusted.
Everything below was run on 2026-11-06 on an Apple M2 Max (MPS and CPU).

```
thermal frame --rotate north-up by yaw prior, resample to map GSD (laser AGL)--> query
satellite window around position prior --> reference
both --preproc raw | CLAHE | gradient magnitude-->
ALIKED | DISK | SIFT --LightGlue--> matches --RANSAC 4-DOF similarity--> frame centre in map px
--GeoTIFF affine (UTM 49N)--> lat/lon
gate: inliers, inlier ratio, scale ~1, rotation ~0, inside search radius  => fix or no fix
```

## Data: Thermal-UAV (SCC-Loc), a subset

| Item | Value | Source |
|---|---|---|
| Dataset | Thermal-UAV, 11,890 nadir thermal frames around Changsha, DJI M4T, day / night / fog flights at 250-340 m AGL | [HF dataset card](https://huggingface.co/datasets/FloralHercules/Thermal-UAV), [SCC-Loc repo](https://github.com/FloralHercules/SCC-Loc) |
| Licence | HF card: **Apache-2.0**, "intended for academic research purposes". Not gated. | HF API `cardData.license`, README |
| Reference map | `ref.tif`, 40961 x 27770 px RGB, EPSG:32649, 0.30 m/px, georeferenced. Card says "Google Maps satellite imagery". Capture date not stated. | read with rasterio |
| GT per frame | `Thermal_info.csv`: GNSS lat/lon, laser-rangefinder AGL, gimbal pitch/roll/yaw | in the ZIP |
| Archive | one 19.9 GB ZIP (`NUDT.zip`) with frames, maps, DSM (4.5 GB) and third-party checkpoints | HF API |
| What we fetch | 20 evenly spaced frames from each of 6 flights (4 test-split, 2 train-split fog flights) + 3 validation-split flights for the held-out gate check = 180 frames; one map crop per flight | `fetch_data.py` |
| Transfer / disk | ~2.8 GB transferred (the 2.8 GB deflated `ref.tif` dominates), 1.7 GB kept in `data/` (1.4 GB map crops, 242 MB frames) | measured |

The Google imagery inside an Apache-2.0 card is a licence conflict we cannot resolve: the
dataset authors cannot relicense Google's imagery. Treat the map as research-only, do not
redistribute it, and swap in an open orthophoto for anything public. No map pixels are
committed here.

`fetch_data.py` reads the ZIP's central directory with HTTP range requests
(`remote_zip.py`, stdlib) and pulls single members. The 2.8 GB map member is fetched in 64 MB
ranges and inflated locally (CRC checked), then cropped to a 700 m margin around each flight
and deleted. zipfile's own streaming reader ran at about 1 MB/s here, so the large ranges are
what make it a 7 minute fetch.

### Datasets we did not use, and why

| Candidate | Why not |
|---|---|
| Boson-nighttime / satellite-thermal-dataset (arplaboratory, the repo named in the task) | HF dataset is **gated**: requires an HF account and accepting "non-commercial research and educational purposes only". Delivered as a ~74 GB split `tar.gz` (v1: 3 x 20 GB + 9.8 GB), which cannot be partially extracted. Accepting terms on the user's behalf is not something an agent should do. |
| CART, Caltech Aerial RGB-Thermal | Caltech data record: CC BY-NC 4.0 (README says CC BY-SA 4.0 non-commercial). Raw data is ROS bags on S3; the labeled zips (4.1 / 4.3 GB) carry no per-frame georeference without joining the bags. |
| Thermal-Oblique (ScalLoc) | Gated "auto", 22 GB single ZIP, oblique views. Same authors as Thermal-UAV. |

## Components and licences

| Part | Licence | Use here |
|---|---|---|
| LightGlue + `aliked/disk/sift_lightglue` weights | Apache-2.0 | matcher |
| ALIKED / DISK / OpenCV SIFT | BSD-3 / Apache-2.0 (kornia copy: MIT card) / Apache-2.0 | extractors |
| SGM (STGL, Xiao et al. IROS 2023), code | MIT (`arplaboratory/satellite-thermal-geo-localization`, demo branch) | network rebuilt in `sgm_baseline.py` |
| SGM weights `xjh19972/SGM` `model.safetensors` | **no licence stated** on the HF card; trained on the gated non-commercial Boson-nighttime set | **research-only** baseline, downloaded at run time, not redistributed |
| Thermal-UAV frames | Apache-2.0 card, academic research | eval data |
| Thermal-UAV `ref.tif` | Google imagery, see above | research-only |

SuperPoint is not used anywhere (Magic Leap non-commercial terms; see
[docs/model-weights-licenses.md](../../docs/model-weights-licenses.md)). The ZIP also ships
MINIMA, RoMa and CAMP checkpoints; we did not download or evaluate them.

## Files

| File | What |
|---|---|
| `fetch_data.py`, `remote_zip.py` | range-request subset fetch, map crop, `data/manifest.json` |
| `geom.py` | stdlib: GSD from AGL + intrinsics, haversine, similarity scale/rotation, the `Gate`, summary stats |
| `thermal_geoloc.py` | preprocessing (raw / CLAHE / gradient), north-up resampling, `Localizer` (extractor + LightGlue + RANSAC + gate) |
| `sgm_baseline.py` | SGM retrieval over a grid of satellite squares around the prior |
| `run_eval.py` | runs configs x frames, writes `out/<tag>.jsonl` (git-ignored) and calls `report.py` |
| `report.py` | per config x condition tables, inlier sweep, SGM margin table => `out/<tag>_summary.md` |
| `test_thermal_geoloc.py` | 11 unittest cases; 9 need nothing but `python3` |
| `out/*_summary.md`, `out/*.log` | the numbers quoted below |

## Run

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt   # we used uv venv, Python 3.12.14
.venv/bin/python fetch_data.py --heldout          # ~7 min, ~2.8 GB transfer, 1.7 GB on disk
export PYTORCH_ENABLE_MPS_FALLBACK=1
.venv/bin/python run_eval.py --device mps --gate revised --tag main_revised      # ~4 min
.venv/bin/python run_eval.py --device mps --gate revised --split heldout --tag heldout_revised
.venv/bin/python run_eval.py --device mps --features --sgm 512 110 --tag sgm     # ~9 min
python3 -m unittest discover
```

## Protocol

- **Prior:** truth + 100 m in a random direction (seed 7), search radius 150 m. Heading prior =
  GT gimbal yaw + 180 deg + N(0, 5 deg). AGL from the laser rangefinder in the metadata.
  The **+180 deg** was found by probing 8 day frames with offsets 0 / 90 / -90 / 180:
  only 180 produced fits within 20 m (6 of 8). The frames are stored with gimbal roll 180.
- **Work resolution:** window side = footprint + 2 x radius => about 0.53 m/px, query about
  390 x 310 px, reference 1024 px. Max 2048 keypoints.
- **Fix error:** distance from the mapped frame centre to the GT GNSS position. It includes
  GNSS error, map georeferencing error and the small offset between camera centre and
  antenna.
- **Correct** = accepted and within 20 m. **False fix** = accepted and more than 20 m off.
- **Frames outside the map:** 9 of 120 main frames and 5 of 60 held-out frames have their GT
  position on empty `ref.tif` pixels (the flights run off the reference map). They are not
  counted in the fix-rate denominator, but any fix accepted on them would count as false.
- **Conditions** come from the flight names: `city-day`, `city-night`, `village-day`,
  `village-night`, `village-day-fog`, `village-night-fog`.

## Results

### Fix rate and error per condition (revised gate, MPS, 6 main flights)

Cell = correct fixes / frames on the map (median error of the correct ones). **No accepted fix
was wrong in any cell**, so "accepted" equals "correct" everywhere.

| Config | city-day | city-night | village-day | village-day-fog | village-night | village-night-fog | All |
|---|---|---|---|---|---|---|---|
| aliked/raw | 7/19 (4.1 m) | 2/19 (5.1 m) | 6/19 (1.3 m) | 0/20 | 1/20 (1.6 m) | 0/14 | 16/111 (3.3 m) |
| aliked/clahe | 5/19 (4.8 m) | 3/19 (4.1 m) | 3/19 (2.6 m) | 1/20 (8.2 m) | 1/20 (3.1 m) | 0/14 | 13/111 (3.7 m) |
| **aliked/grad** | 4/19 (3.7 m) | 0/19 | 5/19 (0.7 m) | 0/20 | **9/20 (2.6 m)** | 0/14 | **18/111 (2.6 m)** |
| disk/raw | 5/19 (3.4 m) | 1/19 (4.8 m) | 3/19 (1.5 m) | 1/20 (0.6 m) | 1/20 (1.9 m) | 0/14 | 11/111 (1.8 m) |
| disk/clahe | 5/19 (3.3 m) | 2/19 (4.8 m) | 3/19 (1.6 m) | 0/20 | 0/20 | 0/14 | 10/111 (3.4 m) |
| disk/grad | 4/19 (3.6 m) | 2/19 (4.5 m) | 2/19 (1.5 m) | 1/20 (1.1 m) | 6/20 (2.9 m) | 0/14 | 15/111 (3.2 m) |
| sift/raw | 0/19 | 0/19 | 1/19 (3.1 m) | 0/20 | 0/20 | 0/14 | 1/111 (3.1 m) |
| sift/clahe | 0/19 | 0/19 | 0/19 | 0/20 | 0/20 | 0/14 | 0/111 |
| sift/grad | 0/19 | 0/19 | 0/19 | 0/20 | 0/20 | 0/14 | 0/111 |

Using two configs per frame (ALIKED raw, then ALIKED grad, keep the accepted one with more
inliers) gives 27/111 main frames and 12/55 held-out frames fixed, still 0 false fixes.
Full tables with p90 error: [out/main_revised_summary.md](out/main_revised_summary.md).

**Ungated ceiling.** The best similarity fit lands within 20 m of truth on 55/111 frames for
ALIKED/raw and 45/111 for ALIKED/grad (column "Best fit within 20 m, ungated" in the summary).
The gate gives up about two thirds of those to keep the false-fix count at zero.

### Integrity: false fixes

| Run | Matcher attempts | Wrong or no fit (err > 20 m) | Accepted | False fixes |
|---|---|---|---|---|
| main, a-priori gate | 1080 | 810 | 32 | **0** |
| main, revised gate | 1080 | 810 | 84 | **0** |
| held-out flights, a-priori gate | 540 | 399 | 14 | **0** |
| held-out flights, revised gate | 540 | 399 | 37 | **0** |
| SGM retrieval, no gate | 240 | 184 | 238 | **182** |

Zero observed is not zero rate. With 84 accepted and 0 false, the 95 % upper bound on the
false-fix rate is about 3.6 % (rule of three). In the revised-gate runs the best wrong fit had
16 inliers (main) and 7 (held-out), and the scale check rejected the 16-inlier one; correct
fits reached up to 95 inliers. 3 of 1080 main attempts hit a LightGlue SIFT exception on a
degenerate keypoint set and are logged as no fix.

**How the gate was set, honestly.** The a-priori gate (30 inliers, inlier ratio 0.25, scale
1 +- 0.25, rotation +- 15 deg, inside the search radius) was fixed before the first full run.
That run showed correct fits rejected for two reasons: 15-29 inliers, and a systematic
rotation of -4 to -10 deg between the north-up query and the map (median per flight from
correct ALIKED fits: city-day -3.8, city-night -9.2, village-day -5.9, village-night -10.5
deg). That is a heading-prior bias in the GT yaw, larger than the injected 5 deg noise.
The revised gate (15 inliers, ratio 0.15, rotation +- 30 deg) was chosen from that run and
then checked on three **validation-split flights** that were not looked at before
(`city7` night, `village5` day and night, 20 frames each): 37 accepted, 0 false.

**Similarity instead of homography.** The first version fitted a MAGSAC homography. On correct
but small inlier clusters it picked up a spurious perspective term (relative scale change
across the query above 0.15 on 125 of 215 correct fits), so a perspective check rejected
most good fixes. The query is already north-up at map GSD from the priors, so a 4-DOF
similarity (`cv2.estimateAffinePartial2D`) is the right model; it is the default now and the
homography path is kept as `--model homography`.

### Held-out flights (validation split, revised gate)

| Config | city-night | village-day | village-night | All |
|---|---|---|---|---|
| aliked/raw | 1/16 (0.9 m) | 4/19 (1.9 m) | 2/20 (2.9 m) | 7/55 (2.2 m) |
| aliked/clahe | 1/16 (1.2 m) | 3/19 (2.1 m) | 1/20 (2.7 m) | 5/55 (2.1 m) |
| aliked/grad | 0/16 | 6/19 (2.2 m) | 2/20 (6.4 m) | 8/55 (2.3 m) |
| disk/raw | 0/16 | 4/19 (2.2 m) | 2/20 (2.4 m) | 6/55 (2.2 m) |
| disk/clahe | 1/16 (3.6 m) | 4/19 (2.9 m) | 2/20 (2.7 m) | 7/55 (3.0 m) |
| disk/grad | 0/16 | 3/19 (2.6 m) | 1/20 (8.7 m) | 4/55 (5.1 m) |
| sift/* | 0/16 | 0/19 | 0/20 | 0/55 |

### SGM (the repo's learned thermal-to-satellite retrieval), research-only weights

SGM embeds the thermal query and satellite squares of the same ground size (110 m) on a 15 m
grid around the prior, and the nearest descriptor gives the position. Two input scales:
`sgm512` resizes every square to 512 px as the demo does; `sgm110` feeds about 1 m/px,
closer to the scale of its training data.

| Config | Frames on map | Top-1 within 20 m | Median err of those | t/frame (MPS) |
|---|---|---|---|---|
| sgm512 | 111 | 26 (23 %) | 7.5 m | 3.6 s |
| sgm110 | 111 | 29 (26 %) | 11.0 m | 0.52 s |

The SGM rows come from an earlier invocation (`--sgm 512 110` alongside a homography-model
LightGlue run, same priors and seed); SGM code was unchanged since, apart from tagging every
top-1 as accepted, which we applied to that output.

Retrieval has no geometric check, so every top-1 is a fix: 182 of 238 were false. A
distinctiveness margin (best distance vs best distance more than 40 m away) helps a bit:
`sgm512` with margin >= 1.1 keeps 11 correct and 1 false, `sgm110` with margin >= 1.3 keeps
2 correct and 0 false ([out/results_sgm_summary.md](out/results_sgm_summary.md)). Those
thresholds were read off the test data. SGM was trained on Boson thermal at a different
altitude, sensor and region, so this is an out-of-domain check, not a reproduction of the
paper. Its use here would be a coarse candidate generator in front of the gated matcher.

### Runtime on M2 Max (4 frames x 6 flights, same frames on both devices)

| Extractor | CPU (8 threads) median s/frame | MPS median s/frame |
|---|---|---|
| ALIKED + LightGlue | 1.26 | 0.18 |
| DISK + LightGlue | 2.42 | 0.29 |
| SIFT + LightGlue | 0.21 | 0.30 |

Model loading and one warm-up frame are excluded; map window cut, preprocessing, both
extractions, matching and RANSAC are included. Accepted fixes and errors were identical on
CPU and MPS for these 24 frames. Other agents were using the machine during the runs, so read
the timings as indicative. SIFT gains nothing on MPS: OpenCV SIFT runs on the CPU either way.

## Failure analysis

- **Fog and featureless vegetation: 0 fixes in `village-night-fog` for every method.** The
  frames are mostly tree canopy and fields with low thermal contrast (one sample frame: std 23
  grey levels vs 39 for a city-night frame). Nothing the extractors find there has a counterpart in the day RGB map.
  The gate correctly returned nothing.
- **City at night is harder than village at night for gradient preprocessing** (0/19 vs 9/20
  with ALIKED/grad). At night building roofs, roads and parked cars swap relative intensity in
  ways that are not just a sign flip, and the 0.53 m/px work resolution drops the fine road
  markings. Raw and CLAHE do slightly better in the city.
- **Gradient maps help most where thermal and RGB disagree in sign** (village-night 9/20 vs
  1/20 raw). Gradient magnitude is invariant to that inversion; CLAHE is not. Daytime results
  barely move with preprocessing.
- **SIFT is not usable across modalities here:** 1 accepted fix in 540 SIFT attempts
  (3 preprocessings x 180 frames, revised gate). LightGlue's SIFT
  weights match SIFT descriptors that differ too much between thermal and RGB.
- **Heading bias.** GT yaw is off by -4 to -10 deg against the map in most flights. A real
  system will see the same from a magnetometer. ALIKED and DISK descriptors are not rotation
  invariant, so a heading search of a few steps or a rotation-robust first pass should raise
  the fix rate (not measured here).
- **Coarse work resolution.** A 150 m search radius forces about 0.53 m/px. For ALIKED/raw,
  20 of the 39 frames between "accepted" (16) and "ungated within 20 m" (55) are fits with
  8-14 inliers that pass every other check (inlier sweep in the summary). A tighter prior
  from an EKF (30-60 m) would let the matcher run near the 0.3 m map GSD. Not run here.
- **Off-map flights.** 14 of 180 frames are outside the reference map. A deployed system needs
  map coverage checks before trusting any "no fix" as a sensor failure.

## Not verified

- No full-dataset numbers: 180 of 11,890 frames, 9 of the dataset's flights.
- Boson-nighttime (the arplaboratory dataset) was not downloaded (gated, NC terms, 74 GB).
- STHN / UASTHN fine homography stages, MINIMA, RoMa and SCC-Loc's own pipeline were not run.
- The SGM numbers use our torchvision rebuild of the network; it loads the checkpoint with
  strict key matching and GeM p = 3.07 (trained value), but the original repo code was not
  executed.
- Map capture date vs flight date (Dec 2025 - Mar 2026) is unknown.
