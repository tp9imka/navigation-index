# VPAIR

<!-- about: repo:aervisloc/vpair -->

Aerial visual place recognition and localization from a light aircraft above 300 m AGL,
with each query paired to a rendered reference image with dense depth and a 6-DoF pose.
Schleiss, Rouatbi, Cremers, arXiv 2205.11567 (2022).

| Field | Value |
|---|---|
| Platform | Light aircraft, downward-facing camera |
| Environment | >100 km trajectory from Bonn to the Eifel mountains, Germany: urban, farmland, forest |
| Sensors and rates | Nadir RGB camera; sensor setup shown as a figure in README (camera model and rates not stated in text) |
| Ground truth | 6-DoF reference pose per query: position from GPS, orientation in a local NED frame (README). Accuracy not stated |
| Size | Full: 20,489,436,499 bytes (HEAD Content-Length on `vpair.zip`, 2026-11-06; README says 20.5 GB). Sample: 861,249,439 bytes (Zenodo API record 6473989; README 0.86 GB) |
| License | README: academic use only, commercial use prohibited. The Zenodo sample record is tagged CC-BY-4.0, which conflicts; follow the stricter README |
| Format | Query / reference image pairs, reference depth, pose files, distractor images |
| Index | [VPAIR](../../catalog/repos/aervisloc__vpair.md) |

## What's in it

- 2,706 query/reference pairs. References are rendered from public geodata (orthophoto +
  elevation), so they are not raw satellite crops.
- 10,000 distractor renders from a geographically similar area to make retrieval harder.

## Download

```bash
# sample, 0.86 GB
curl -L -o vpair_sample.zip "https://zenodo.org/records/6473989/files/vpair_sample.zip?download=1"
# full, 20.5 GB (TUM server; supports HEAD, resumable)
curl -L -C - -o vpair.zip https://ltc.cvg.cit.tum.de/vpair/vpair.zip
```

## Loading and tooling

- Lay queries and references out as `database/` and `queries/` folders and run
  [VPR methods evaluation](../../catalog/repos/gmberton__vpr-methods-evaluation.md) to compare
  NetVLAD, CosPlace, EigenPlaces, SALAD, etc. with one flag. That tool expects UTM in file
  names; convert from the pose file.
- [AnyLoc](../../catalog/repos/anyloc__anyloc.md) reports results on VPAIR in its paper
  (aerial domain), a good zero-shot baseline.
- Depth on the reference enables 2D-3D PnP with [LightGlue](../../catalog/repos/cvg__lightglue.md)
  matches for full pose, not just place.

## Hackathon fit

- Idea 18 (geolocalization + VO) for fixed-wing / high-altitude scenarios; the small
  sample is enough for a retrieval + PnP demo on a laptop.
- Idea 11 (terrain-relative nav) visual variant: references come with depth.

## Pitfalls

- Bird's-eye queries have arbitrary in-plane rotation (paper highlights this); many VPR
  models trained on street view fail without rotation augmentation.
- References are renders, not photographs, so appearance gap is synthetic vs real.
- License conflict between README and Zenodo tag.

## Sources

- https://github.com/AerVisLoc/vpair README (description, counts, links, license), read 2026-11-06.
- HEAD on https://ltc.cvg.cit.tum.de/vpair/vpair.zip; Zenodo API record 6473989.
- arXiv 2205.11567 abstract.
