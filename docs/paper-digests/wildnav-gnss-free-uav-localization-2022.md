# WildNav - paper digest
<!-- about: res:wildnav-gnss-free-uav-localization-2022, repo:tiers/wildnav -->
**Vision-based GNSS-Free Localization for UAVs in the Wild** - Gurgu, Pena Queralta, Westerlund (Univ. of Turku), ICMERR 2022 (venue per repo README DOI 10.1109/ICMERR56497.2022.10097798). [paper](https://arxiv.org/abs/2210.09727) | [code](https://github.com/TIERS/wildnav) | Read: full text via ar5iv rendering of arXiv 2210.09727, plus repo README

## Problem
Absolute position for a UAV flying long distance at ~120 m over non-urban terrain (fields, forest, few man-made landmarks) without GNSS. Visual odometry drifts and assumes low altitude, so the paper goes for absolute matching against open satellite imagery, with no pre-mapping flight.

## Method
- Reference map: Google Earth satellite tiles (~1400x1200 px, north-up), each tagged with lat/lon of its top-left and bottom-right corners; stored onboard for offline use.
- Drone photo is de-rotated using drone yaw + gimbal yaw so it is north-aligned like the tiles. The authors add a fixed 15 deg clockwise correction for a systematic compass error on their UAV.
- SuperGlue (SuperPoint features) matches the photo against every tile; template matching and SIFT were tried and dropped for "relatively high computation time and inaccuracy" (no numbers given).
- Tile with the most matches wins. RANSAC homography, needs at least 4 matches, otherwise no fix.
- Photo footprint is projected into the tile; the polygon center is converted to lat/lon by linear interpolation between the tile corners (Eq. 1, Eq. 2). No altitude or full 6-DoF pose, no filtering over time.

## Data and sensors
- DJI Matrice 300, manually piloted, Zenmuse H20T 12 MP RGB camera (82.9 deg FOV), ~120 m AGL, sunny weather, May flights one year after the satellite imagery (season matched).
- Ground truth: GNSS position from photo EXIF.
- Flight area near 60.403091 N, 22.461824 E (Finland), Fig. 3. Own dataset only, shared via a University of Turku SharePoint link in the README. No public benchmark used.
- Related dataset cards for a broader test: [UAV-VisLoc](../dataset-cards/uav-visloc.md), [AerialVL](../dataset-cards/aerialvl.md), [VPAIR](../dataset-cards/vpair.md).

## Headline results (as reported)
- Paper text (no tables; results in Figs. 4-6): 77 of 126 photos localized, success defined as error < 50 m; MAE 15.82 m.
- Fig. 6: per-photo error, "a few exceptions where the error exceeds 30 meters".
- Repo README results table (not in the arXiv text we read): Dataset 1 - 124 total, 77 localized (62%), MAE 15.82 m; Dataset 2 - 78 total, 44 localized (56%), MAE 26.58 m.
- No quantitative matcher comparison, no runtime, no onboard compute numbers reported.

## Limitations
- Stated by authors: accuracy not enough for precision maneuvers or low-altitude flight near obstacles; featureless surfaces (fields, forest, water) cause wrong-tile matches and large errors; lighting and season strongly affect matching; non-urban open imagery is lower resolution and updated less often; matcher is not rotation invariant so heading metadata is required; performance depends on the trajectory.
- Our read: brute-force matching against every tile does not scale beyond a small area - there is no retrieval stage to shortlist tiles. The "localized" rate counts only fixes under 50 m, so ~40% of frames give no usable fix and the paper does not show how wrong-tile matches could be detected online. Image count differs between paper (126) and README (124).
- Our read: the 15 deg compass fudge is tuned to one airframe; any team reusing this must estimate its own heading bias.

## Code, weights, license
- Repo TIERS/wildnav, BSD-3-Clause (GitHub API), last push 2025-06-12, ~286 stars, not archived. Python, tested on Ubuntu 20.04 / Python 3.10, CPU fallback via `force_cpu` flag.
- Matcher comes as a git submodule: magicleap/SuperGluePretrainedNetwork (GitHub reports license "Other" - Magic Leap's non-commercial research license). So the weights that do the work are not BSD.
- A few sample query/map images ship in the repo; full flight photos via SharePoint link.
- Integration card: [tiers__wildnav](../integration-cards/tiers__wildnav.md).

## Reproduction effort (estimate)
Estimate: one laptop with any CUDA GPU (CPU works, slower). Running the shipped samples: under 1 hour including venv setup (watch the torch 1.12.1 pin, see integration card). Reproducing the paper numbers depends on the SharePoint dataset staying online and on matching Google Earth tiles, which are not redistributable and change over time - treat the exact MAE as not reproducible. Building tiles for a new area: half a day.

## What a hackathon team can take from it
- The simplest end-to-end "visual GPS" loop: de-rotate by yaw => match against georeferenced tile => homography => footprint center => lat/lon. ~300 lines, easy to read in an hour.
- Swap SuperGlue for LightGlue ([cvg__lightglue](../integration-cards/cvg__lightglue.md)) to get a permissive license and more speed; or RoMa ([parskatt__roma](../integration-cards/parskatt__roma.md)) for harder appearance change.
- Add a retrieval front end (AnyLoc / SALAD style global descriptor over tiles) so you only match the top-k tiles - this is the missing piece for areas larger than a few tiles. See [anyloc__anyloc](../integration-cards/anyloc__anyloc.md).
- Use inlier count + homography sanity (area, convexity) as a gating score before feeding the fix into an EKF (e.g. [cra-ros-pkg__robot_localization](../integration-cards/cra-ros-pkg__robot_localization.md)) as an absolute position measurement; reject rather than trust low-inlier fixes.
- The "success = error < 50 m" protocol plus MAE is a quick evaluation recipe for your own flight logs with EXIF GNSS as ground truth.
