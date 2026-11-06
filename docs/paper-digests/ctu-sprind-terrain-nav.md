# CTU SPRIN-D heightmap-gradient localization - paper digest
<!-- about: res:sprind-heightmap-gradients-2025, res:sprind-fully-autonomous-flight -->
**Kilometer-Scale GNSS-Denied UAV Navigation via Heightmap Gradients: A Winning System from the SPRIN-D Challenge** - Werner, Capek, Musil, Franek, Baca, Saska (Czech Technical University in Prague, MRS group), arXiv 2510.01348 v2 (25 May 2026). [paper](https://arxiv.org/abs/2510.01348) | code: none published | Read: full text of the arXiv HTML v2 | Re-implementation: [samples/terrain-heightmap-pf](../../samples/terrain-heightmap-pf/)

## Problem
SPRIN-D Funke Fully Autonomous Flight: a UAV under 25 kg flies a 9 km waypoint course below 25 m AGL with no GNSS and no prior reconnaissance or dense mapping flights, avoiding obstacles, and must find red-flag waypoints that are given on a paper map with ~20 m uncertainty. Venue: Erding airbase, Bavaria - urban blocks, open fields, semi-open forest. Odometry drift over kilometres is the core problem; loop closures are unavailable.

## Method
- Platform: multirotor with Livox Mid-360 LiDAR, RealSense D435, Bluefox global-shutter camera + ICM42688 IMU on a vibration-decoupled battery mount, magnetometer, Intel NUC i7 (16 GB), no GPU.
- Odometry: monocular VIO from OpenVINS, compass-aligned. Authors tested RTAB-Map and ORB-SLAM3 in simulation and dropped them beyond 1 km (memory/compute growth, tracking loss).
- Prior map: north-aligned heightmap, max height per 1 m bin, built from open airborne LiDAR point clouds turned into height above terrain with LAStools. Where no LiDAR existed (test flights 60, 61) they estimated object heights from aerial RGB with monocular depth models.
- Local map: from the onboard OctoMap occupancy map, square of 30-60 m side, same 1 m max-height binning, rotated to north with the compass. Assumes drift inside the local map is negligible.
- Matching: gradients instead of absolute heights, because baro altitude is too noisy and the ground may not be visible or flat. Gradients with abs value > 5 m are kept as a binary edge map - effectively edges of buildings and trees, discarding fences, cars, bushes. Edge maps are matched with the non-normalized correlation coefficient (OpenCV TM_CCOEFF, Eq. 1), found empirically better than squared difference or normalized correlation when the local map is incomplete. A Gaussian blur smooths the similarity map.
- Filter: translational particle filter, heading taken from the compass. Particles shift with odometry; every 10 m of odometry each particle is weighted by the normalized similarity at its position, resampled, and perturbed with Gaussian noise from an empirical odometry covariance. K-means on particles, centroid of the largest cluster is the estimate (multimodality from aliasing was common).
- Guidance: the planner gets a virtual goal at a fixed distance along the direction from the corrected position to the next waypoint.

## Data and sensors
- Own flights only: two pre-competition test flights with GNSS ground truth (IDs 60, 61) and six competition flights where ground truth was reconstructed by hand from VIO plus camera/LiDAR footage at identifiable places (stated precision 0-5 m).
- A digital twin of the area in FlightForge (DEM, LoD2 buildings, procedurally generated vegetation from satellite masks) was used for development and for synthetic YOLOv8 training data. Not released.

## Headline results (as reported)
- Table I, RMSE odometry => method: flight 60 (830 m, forest/open) 8 => 5 m; 61 (495 m) 36 => 13 m; 205 (939 m, urban) 31 => 10 m; 206 (1023 m, urban) 27 => 6 m; 208 (872 m, urban/open) 14 => 11 m; 232 (1256 m, forest) 53 => 7 m; 239 (1371 m, forest) 8 => 9 m; 242 (939 m, urban/open) 9 => 11 m.
- Text: competition flights had localization RMSE below 11 m while compass-aligned odometry reached up to 53 m. Flight 61 was deliberately initialized ~32 m off and ended at ~4 m error.
- Flights over 1 km ended on battery or hardware faults (WiFi card reboot), not on localization. Waypoints detected per flight: from 1/2 to 4/4.
- Only three of nine teams flew autonomously beyond 100 m; the other two did not reach more than 2 waypoints. RGB satellite matching by other teams was "highly unreliable" at these altitudes.
- No per-update compute time, particle count, blur sigma, K-means k or weight normalization formula is given.

## Limitations
- Stated by authors: works best in urban areas; in open fields the system "mostly relied on the odometry"; the compass had slowly varying bias up to 30 deg near buildings and runways, corrected only when enough features were present; local map size capped flight speed and hence range; IMU vibration isolation was essential.
- Our read: ground truth for six of eight flights is manual and has 0-5 m stated precision, close to the reported RMSE, so the competition numbers are indicative. Flights 239 and 242 show no gain over odometry. The longest flight is 1.37 km, not 9 km in one go.
- Our read: the method depends on a 1 m height-above-ground prior from airborne LiDAR (or a learned stand-in). A 30 m global DSM does not resolve the building and tree edges the 5 m threshold is built for. In our re-implementation on Copernicus GLO-30 the literal binary 5 m threshold gave little gain in the Erding window, while continuous gradient magnitude did (see sample README).
- Our read: min-max-normalized similarity has no notion of "no information"; on featureless terrain it can pull particles toward noise. The paper's "relied on odometry" in open fields suggests the real system's maps were simply flat there; our re-implementation on a smoothed-flat control did worse than odometry, while a gated TERCOM did not.
- The index record's takeaway "gradients beat raw height matching at low altitude" is the authors' design reasoning (no reliable absolute height on board), not a measured comparison in the paper.

## Code, weights, license
- No code, maps or flight logs released. Paper is CC BY 4.0. Builds on the open CTU MRS UAV System (`repo:ctu-mrs/mrs_uav_system`) and OpenVINS, but the localization module itself is not public as far as the paper says.
- Independent re-implementation of Sec. III on real GLO-30 terrain with simulated flights, with a TERCOM baseline and measured timings: [samples/terrain-heightmap-pf](../../samples/terrain-heightmap-pf/).

## Reproduction effort (estimate)
- Algorithm only, on simulated flights over open DEMs: about a day (the sample took that route; ~1 ms per update on a laptop CPU at 41x41 cells).
- Faithful reproduction needs 1 m airborne LiDAR of the area (e.g. German state open geodata, as the authors used), a LiDAR UAV with good VIO and compass, and an occupancy-mapping stack: weeks, plus flight permissions. The competition numbers themselves are not reproducible without their logs.
