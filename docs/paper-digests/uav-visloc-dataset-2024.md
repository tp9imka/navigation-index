# UAV-VisLoc - paper digest
<!-- about: res:uav-visloc-dataset-2024, repo:intellisensing/uav-visloc -->
**UAV-VisLoc: A Large-scale Dataset for UAV Visual Localization** - Xu, Yao, Cao, Wei, Liu, Wang, Peng, arXiv technical report 2024. [paper](https://arxiv.org/abs/2405.11936) | [code](https://github.com/IntelliSensing/UAV-VisLoc) | Read: full text, arXiv HTML v1; repo README

## Problem
A UAV that loses GNSS should recover lat/lon by matching its downward image against a large satellite map. Earlier cross-view datasets (University-1652, SUES-200, DenseUAV) cover small areas, are mostly urban, and frame the task as tile retrieval rather than locating the UAV on a large map.

## Method
Dataset paper only - no new localization method and no baselines.
- Task definition (Sec. I): drone takes a down-looking image => match against an orthorectified satellite map in which every pixel has coordinates => output current coordinates.
- Collection: sequences of images along real flight tracks, one satellite map per flight covering the whole track.
- Per-image metadata: center lat/lon, flight height, date, heading Phi (relative to North).
- Future perspectives (Sec. IV): also proposes using earlier frames of the flight for return-to-home style navigation. Not evaluated.

## Data and sensors
- Dataset card: [UAV-VisLoc](../dataset-cards/uav-visloc.md).
- Sensors: downward RGB camera only, still images (roughly 0.1-0.2 m/px per README). Multi-rotor and fixed-wing UAVs; models and cameras not named. No IMU, no video, no intrinsics in the paper.
- Size: 6,742 drone images, 11 satellite maps, 11 sites in China (Abstract, Sec. III); 16.4 GB full, 2.04 GB example subset (README).
- Satellite maps: Google Earth, 0.3 m GSD (Sec. II-B). Map sizes from 3000x170 to 44800x33280 px (Table II).
- Altitude: text says 400-2,000 m (Sec. II-A); Table II lists 405-840 m where given. The paper does not reconcile the two.
- Terrain: villages, towns, farms, cities, rivers, hills, forests. Seasons: summer and autumn.
- Image size: 3976x2652 for most sites, 3000x2000 for three (Table II).

## Headline results (as reported)
- None. The paper reports no baseline evaluation, no metric and no numbers for any method. Table I only compares dataset sizes.
- For actual numbers on this kind of data, see AnyVisLoc (different dataset) or third-party papers that later used UAV-VisLoc (not checked here).

## Limitations
- Stated by authors: no limitations section.
- Our read: no evaluation protocol, no official train/test split, no metric. A team must invent its own, which makes "we beat X on UAV-VisLoc" claims hard to compare.
- Our read: ground-truth source and accuracy for per-image coordinates are not stated; README calls the example subset "minimal coordinate error", implying the rest has some.
- Our read: high altitude (hundreds of metres) and near-nadir - easier geometry than low-altitude oblique flight. Results here will be optimistic for a small quadrotor at 50-120 m.
- Our read: no attitude other than heading, so no full 6-DoF ground truth.

## Code, weights, license
- Repo IntelliSensing/UAV-VisLoc: data-only (README + images). GitHub API reports no license. Last push 2024-05-22 - static since release.
- No code, no weights.
- Dataset license: not stated anywhere we looked (README, paper). The arXiv paper itself is CC0, which does not cover the data. Satellite tiles are Google Earth imagery under Google's terms. Treat as research use, ask before redistributing.

## Reproduction effort (estimate)
Estimate:
- Nothing to reproduce - it is a dataset.
- Data: 16.4 GB zip from Google Drive (or Baidu). Start with the 2.04 GB example (site 03) to build a loader in under an hour.
- Hardware: any laptop for loading; matching experiments need a GPU like any matcher.
- Time to first result: 2-4 h to crop map tiles around each GT center, run an off-the-shelf matcher, and compute position error. Most of that is writing the cropping and pixel=>lat/lon code from the GeoTIFF.

## What a hackathon team can take from it
- A ready test set for the "satellite map + downward camera => lat/lon" loop, across non-urban terrain (farms, rivers, forest) where city-trained models usually fail.
- Sequential flight tracks: you can simulate a flight, feed consecutive frames, and test temporal filtering of fixes (not possible with shuffled tile datasets like University-1652).
- GeoTIFF maps already georeferenced: pair with [rasterio](../integration-cards/rasterio__rasterio.md) or [GDAL](../integration-cards/osgeo__gdal.md) for pixel <=> lat/lon.
- Define your own metric up front (e.g. error in m and success within 25/50 m) and state it; the paper gives none.
- Matchers to try first: [LightGlue](../integration-cards/cvg__lightglue.md), [RoMa](../integration-cards/parskatt__roma.md); for retrieval of the candidate region, [AnyLoc](../integration-cards/anyloc__anyloc.md).
