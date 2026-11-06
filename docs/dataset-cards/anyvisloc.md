# AnyVisLoc

<!-- about: repo:uav-avl/benchmark, res:anyvisloc-uav-localization-benchmark-2025 -->

Benchmark for UAV absolute visual localization at low altitude with oblique views, with
2.5D aerial and satellite reference maps (orthophoto + DSM) and a retrieval => matching =>
PnP baseline. Ye et al., arXiv 2503.10692, CVPR 2026 Findings. Copyright holder per the
dataset license: National University of Defense Technology.

| Field | Value |
|---|---|
| Platform | DJI Mavic 2, Mavic 3, Mavic 3 Pro, Phantom 3, Phantom 4, Phantom 4 RTK, Mini 4 Pro (README) |
| Environment | 24 scenes across China: dense urban, towns, villages, landmarks, campuses, parks, grassland, farmland, mountains; several weathers, seasons, illuminations |
| Sensors and rates | RGB stills, 20,077 images; heights about 6-500 m, pitch about 5-90 deg (nadir and oblique) |
| Ground truth | Per-image 6-DoF pose (`pose_c2w`, `xyz`, `euler_deg`) in a scene-local metric frame. Raw poses from RTK (cm-level) or standard GPS (~10 m), refined by SfM against the aerial orthomosaic; manual PnP check within 0.5 m (docs/GROUND_TRUTH.md). Authors pitch it for 3/5/10 m success thresholds |
| Size | Not verified (Baidu / OneDrive only; no size in README) |
| License | AnyVisLoc Dataset License v1.0: research-only, non-commercial, no redistribution, no public derived subsets. Third-party satellite/DSM data under their own terms |
| Format | Per-scene folder: `Lxx_reference.json`, `aerial_map.png`, `aerial_dsm.npy`, `satellite_map.png`, `satellite_dsm.npy`, one `.npz` per UAV image (image, K, dist, poses) |
| Index | [Benchmark repo](../../catalog/repos/uav-avl__benchmark.md), [paper](../../catalog/resources/anyvisloc-uav-localization-benchmark-2025.md) |

## What's in it

- Two reference types per scene: high-res aerial orthophoto + DSM (for precise PnP) and a
  satellite image + DSM (the realistic, widely available reference).
- Reference coverage per scene from 10,000 m2 to 9,000,000 m2.
- Pose-prior protocols: `yp` (coarse yaw, pitch, altitude used; map yaw-aligned), `p`
  (no yaw alignment), `unknown`.

## Download

```bash
git clone https://github.com/UAV-AVL/Benchmark.git && cd Benchmark
# Dataset: Baidu https://pan.baidu.com/s/14vSQDydkmiTj2U1JpQH-Hg?pwd=fcw8
#          OneDrive https://1drv.ms/f/c/fef40436afe2e5bb/IgC0Zat90dsgTY-2lNlDliGXAfuTZOYEeKcllr7VPD_F3eY?e=LJ5fAD
# both are browser downloads; put scenes under ./Data/AnyVisLoc/
# Weights: RoMa + DINOv2 (direct URLs in README), CAMP (Google Drive), GIM/MINIMA LightGlue
curl -LO https://github.com/Parskatt/storage/releases/download/roma/roma_outdoor.pth
```

## Loading and tooling

The repo ships the runner and an `AnyVisLocNPZDataset` loader (`avl_data.py`). Tested by the
authors on Python 3.10, PyTorch 2.5.1, CUDA 12.1, RTX 4090 (README; not run here).

```bash
python run_avl.py --dataset_root ./Data/AnyVisLoc --yaml config_selectable_matchers.yaml \
  --reference_mode satellite --pose_priori yp --limit 20 --device cuda
```

Matchers it wraps: [LightGlue](../../catalog/repos/cvg__lightglue.md),
[RoMa](../../catalog/repos/parskatt__roma.md), GIM, MINIMA, ALIKED, DISK. Related:
[U2S-CVGL](../../catalog/repos/uav-avl__u2s-cvgl.md) from the same group for unknown-scale matching.

## Hackathon fit

- Idea 18 (visual geolocalization + VO) when the demo flies a small multirotor at low
  altitude with a gimballed, tilted camera: this is the only indexed set with oblique views
  and a DSM, so PnP gives full 6-DoF, not just lat/lon.
- Idea 20 (Jetson): use `--limit` and the satellite reference to time per-frame latency.

## Pitfalls

- License forbids redistribution, including sharing within a team via a public bucket.
  Each person downloads, or keep it on one machine.
- No verified size; Baidu needs an account and client for large files; OneDrive works from a browser.
- `yp` prior uses GT-derived yaw/pitch/altitude; a demo claiming "no prior" must use `unknown`.
- Aerial reference maps have ghosting/blur around buildings (authors' note).
- Defence-affiliated copyright holder; check your event's rules on dataset provenance.

## Sources

- https://github.com/UAV-AVL/Benchmark README, docs/GROUND_TRUTH.md, docs/LICENSE_DATASET.md, read 2026-11-06.
