# LightGlue - integration card
<!-- about: repo:cvg/lightglue -->
One-line: sparse learned matcher that turns two images into point correspondences in a few lines of PyTorch - the default fine stage for drone-frame-to-map-tile registration, if you pick the extractor with its license in mind.

| | |
|---|---|
| Install | `git clone https://github.com/cvg/LightGlue.git && cd LightGlue && python -m pip install -e .` (README). No GitHub releases/tags (releases endpoint 404); `pyproject.toml` version `0.0`. Deps (`requirements.txt`): `torch>=1.9.1`, `torchvision>=0.3`, `numpy`, `opencv-python`, `matplotlib`, `kornia>=0.6.11`. Also exposed via Hugging Face `transformers` and `kornia.feature.LightGlue` (README "Other links"). |
| Runs on | Any OS with PyTorch. README benchmarks: GPU (RTX 3080) "150 FPS @ 1024 keypoints and 50 FPS @ 4096 keypoints per image" with compilation and adaptivity; CPU (i7 10700K) "20 FPS @ 512 keypoints". Source has a `pruning_keypoint_thresholds` entry for `"mps"` (pruning disabled, like CPU), so MPS is anticipated; no MPS benchmark stated. FlashAttention used automatically with `torch>=2.0`. No ONNX/TensorRT export in this repo - see [LightGlue-ONNX](./fabio-sim__lightglue-onnx.md). |
| Inputs | Per image: `torch.Tensor` (3,H,W) in [0,1] (`load_image`). Extractors resize to longest side 1024 by default (`preprocess_conf = {"resize": 1024}` in `superpoint.py`); disable with `resize=None`. Matcher input dict: `{'image0': feats0, 'image1': feats1}` with `keypoints`, `descriptors`, `image_size`. |
| Outputs | `matches` (K,2) index pairs, `scores`, plus per-image keypoints (pixel coords, rescaled back to the original image). No geometry - you run RANSAC yourself. |
| Key API / entry points | `lightglue/__init__.py` exports `SuperPoint`, `DISK`, `ALIKED`, `SIFT`, `DoGHardNet`, `LightGlue`, `match_pair`. `LightGlue(features="superpoint", **conf)` - `features` keys in source: `superpoint`, `disk`, `aliked`, `raco-aliked`, `sift`, `doghardnet`; conf: `n_layers`, `flash`, `mp`, `depth_confidence`, `width_confidence`, `filter_threshold`. `Extractor.extract(img, **conf)`. `match_pair(extractor, matcher, image0, image1, device="cpu", **preprocess)`. `lightglue.utils.load_image(path, resize=None)`, `rbd(dict)`. `LightGlue.compile(mode=...)`. `benchmark.py [--device cuda] [--num_keypoints ...] [--compile]`. |
| Time to first result | Estimate: 15-30 min on a CUDA or CPU box with internet (weights pulled from GitHub release `v0.1_arxiv` on first construct). Assumes a working PyTorch install. |
| License | Code and LightGlue weights: Apache-2.0 (GitHub metadata, README). Extractors differ - see Gotchas. SuperPoint weights + `lightglue/superpoint.py`: Magic Leap non-commercial research license. DISK: Apache-2.0 per README. ALIKED: BSD-3-Clause (README, file header of `aliked.py`). |

## Minimal usage
Not run. Adapted from README; ALIKED chosen instead of the SuperPoint default for licensing reasons.

```python
import cv2, torch
from lightglue import LightGlue, ALIKED, match_pair
from lightglue.utils import load_image

dev = "cuda" if torch.cuda.is_available() else "cpu"
extractor = ALIKED(max_num_keypoints=2048).eval().to(dev)
matcher = LightGlue(features="aliked").eval().to(dev)

img0 = load_image("drone_frame.jpg").to(dev)
img1 = load_image("map_tile.png").to(dev)
f0, f1, m = match_pair(extractor, matcher, img0, img1)
idx = m["matches"]
p0 = f0["keypoints"][idx[:, 0]].cpu().numpy()
p1 = f1["keypoints"][idx[:, 1]].cpu().numpy()
H, inl = cv2.findHomography(p0, p1, cv2.USAC_MAGSAC, 3.0)
```

## Wiring it into a nav stack
- Stage 2 of visual geolocalization: retrieval ([AnyLoc](./anyloc__anyloc.md), [SALAD](../../catalog/repos/serizba__salad.md), [MixVPR](../../catalog/repos/amaralibey__mixvpr.md)) returns top-k georeferenced tiles => LightGlue + RANSAC homography per tile => project the frame centre through H into tile pixels => tile geotransform ([GDAL](./osgeo__gdal.md) / [rasterio](./rasterio__rasterio.md)) => lat/lon. The index sample [visual-geolocalization-lightglue](../../samples/visual-geolocalization-lightglue/) does exactly this (with SuperPoint - see license gotcha).
- Gate on inlier count before publishing a fix; feed the fix to an EKF ([robot_localization](./cra-ros-pkg__robot_localization.md)) or to ArduPilot as an external position via [MAVROS](../../catalog/repos/mavlink__mavros.md) / the [non-GPS MAVLink messages](../../catalog/resources/ardupilot-dev-mavlink-nongps-position.md).
- [hloc](./cvg__hierarchical-localization.md) wraps LightGlue as `superpoint+lightglue` / `disk+lightglue` / `aliked+lightglue` match configs if you want retrieval, matching and PnP against an SfM model in one toolbox.
- For Jetson/TensorRT, export through [LightGlue-ONNX](./fabio-sim__lightglue-onnx.md); for a CPU-only edge story, [XFeat + LighterGlue](./verlab__accelerated_features.md).

## Gotchas
- License trap, read from source: `LightGlue(features=...)` defaults to `"superpoint"`, and the README example uses SuperPoint. `lightglue/superpoint.py` carries a Magic Leap "CONFIDENTIAL ... reproduction ... strictly prohibited" header, and the linked SuperPointPretrainedNetwork LICENSE is "ACADEMIC OR NON-PROFIT ORGANIZATION NONCOMMERCIAL RESEARCH USE ONLY". Maintainer (issue #38): Apache-2.0 covers LightGlue weights and code "except for files whose header declares a different license"; issue #120 notes the file header and the external LICENSE disagree, maintainer declines to say which applies. For anything beyond research, use `aliked` or `disk`.
- No drop-in "open SuperPoint": LightGlue-ONNX issue #39 reports zero matches when feeding SuperPoint-Open features to the SuperPoint-trained LightGlue weights.
- Not rotation invariant with default extractors: open issues #64 (90/180 deg) and #74. For nadir drone frames, rotate to north-up from heading or try 4 rotations (the index sample does `ROTATIONS_K = (0, 1, 2, 3)`).
- Runtime depends on keypoint count, not resolution (issue #151 comment); huge images are resized to 1024 by the extractor anyway, so small ground features can vanish - raise `resize` for high-altitude tiles.
- Pruning thresholds are tuned for RTX 30xx (README); rerun `benchmark.py` on Jetson/other hardware and adjust `LightGlue.pruning_keypoint_thresholds['cuda']`.
- ONNX export issues upstream (#112 GridSample on NXP i.MX 93 NPU, #66 TensorRT in C++) are open - another reason to start from LightGlue-ONNX.

## Alternatives
- [XFeat](./verlab__accelerated_features.md) - Apache-2.0 end to end, real-time sparse on CPU; slightly lower accuracy than SP+LG per its own MegaDepth table.
- [RoMa](./parskatt__roma.md) - dense, more robust to season/sensor change, much slower; use as a top-1 verifier.
- [LoFTR](../../catalog/repos/zju3dv__loftr.md) - detector-free semi-dense; or compare all of them on your imagery with [vismatch](./gmberton__vismatch.md).

Sources: cvg/LightGlue README.md, requirements.txt, pyproject.toml, lightglue/__init__.py, lightglue/lightglue.py, lightglue/superpoint.py, lightglue/aliked.py, lightglue/disk.py, lightglue/utils.py; issues #38, #64, #66, #74, #112, #120, #151; magicleap/SuperPointPretrainedNetwork LICENSE; fabio-sim/LightGlue-ONNX issue #39; GitHub metadata via `gh api` (2026-11-06).
