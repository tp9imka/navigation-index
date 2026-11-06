# XFeat - integration card
<!-- about: repo:verlab/accelerated_features -->
One-line: tiny CNN keypoint detector/descriptor (64-D) with built-in sparse, semi-dense and LighterGlue matching that runs real time on a laptop CPU - the "no GPU onboard" matching option, Apache-2.0 including weights in the repo.

| | |
|---|---|
| Install | No pip package. `git clone https://github.com/verlab/accelerated_features.git && cd accelerated_features`, install PyTorch (>=1.10), then `pip install opencv-contrib-python tqdm` for demos (README). Or `torch.hub.load('verlab/accelerated_features', 'XFeat', pretrained=True, top_k=4096)` (`hubconf.py`; `dependencies = ['torch']`). LighterGlue needs `pip install kornia` (`modules/xfeat.py` raises otherwise). Weights ship in-repo: `weights/xfeat.pt`, `weights/xfeat-lighterglue.pt`. Latest release `v0.1` (2024-06-22); last push 2025-01-15. |
| Runs on | CPU or CUDA: `XFeat.__init__` sets `self.dev = cuda if available else cpu`; no MPS selection in source. README: "Real-time sparse inference on CPU for VGA images (tested on laptop with an i5 CPU and vanilla pytorch)"; "about 1,400 FPS using an RTX 4090" batched VGA sparse; "over 150 FPS" single-batch GPU VGA. README lists Jetson / Raspberry Pi as intended targets but ships no ONNX/TensorRT export ("it would be nice to have an export script" - README Contributing). |
| Inputs | `torch.Tensor (B,C,H,W)` grayscale or RGB, or `np.ndarray (H,W,C)` uint8 for `match_xfeat` (`parse_input` divides by 255). Input is bilinearly resized down to multiples of 32 (`preprocess_tensor`) and keypoints are scaled back; there is no other downscaling, so cost grows with input size. |
| Outputs | `detectAndCompute` => list of dicts per batch item: `keypoints` (N,2) x,y, `scores` (N,), `descriptors` (N,64). `match_xfeat` / `match_xfeat_star` => `mkpts_0, mkpts_1` as numpy (N,2) pixel matches. `match_lighterglue` => matched indices/keypoints via kornia LightGlue. |
| Key API / entry points | `modules.xfeat.XFeat(weights=..., top_k=4096, detection_threshold=0.05)`; methods (source): `detectAndCompute(x, top_k=None, detection_threshold=None)`, `detectAndComputeDense(x, top_k=None, multiscale=True)`, `match_xfeat(img1, img2, top_k=None, min_cossim=-1)`, `match_xfeat_star(im_set1, im_set2, top_k=None)`, `match_lighterglue(d0, d1, min_conf=0.1)`, `match(feats1, feats2, min_cossim=0.82)`. `modules.lighterglue.LighterGlue`. Scripts: `minimal_example.py`, `realtime_demo.py --method XFeat|SIFT|ORB`, `python3 -m modules.eval.megadepth1500 ...`. |
| Time to first result | Estimate: 10-20 min on any laptop (CPU torch wheel, clone, `python3 minimal_example.py`). Assumes PyTorch installs cleanly. |
| License | Apache-2.0 (GitHub metadata, LICENSE badge in README). Weights are committed in the repo under that license; no separate weights license stated. Training used MegaDepth and a COCO subset (README points to COCO terms of use for the data). LighterGlue runs through kornia (Apache-2.0 per its GitHub metadata, not re-checked here). |

## Minimal usage
Not run. Adapted from README and `minimal_example.py`.

```python
import cv2, numpy as np, torch
xfeat = torch.hub.load("verlab/accelerated_features", "XFeat", pretrained=True, top_k=4096)

a = cv2.imread("drone_frame.jpg")[:, :, ::-1].copy()   # RGB uint8 HxWx3
b = cv2.imread("map_tile.png")[:, :, ::-1].copy()
p0, p1 = xfeat.match_xfeat(a, b)                       # sparse + mutual NN
# p0, p1 = xfeat.match_xfeat_star(...)                 # semi-dense, more matches
H, inl = cv2.findHomography(p0, p1, cv2.USAC_MAGSAC, 3.5)
print(int(inl.sum()), "inliers")
```

## Wiring it into a nav stack
- Onboard visual geolocalization with no GPU: [MixVPR](../../catalog/repos/amaralibey__mixvpr.md) or another small retrieval model picks candidate tiles, XFeat matches frame-to-tile, homography => lat/lon => [MAVROS](../../catalog/repos/mavlink__mavros.md) / [non-GPS MAVLink position](../../catalog/resources/ardupilot-dev-mavlink-nongps-position.md). This is the Jetson row in [reference stacks](../reference-stacks.md).
- Frame-to-frame tracking front end for a VO prototype: `detectAndCompute` per frame + `match` between consecutive frames, then essential matrix/PnP in OpenCV; fuse with IMU in an EKF.
- Extraction cost is the same per image, so precompute and cache tile features (`keypoints` + 64-D `descriptors`) offline; only the query frame runs live.
- `tiny_roma_v1_outdoor` in [RoMa](./parskatt__roma.md) and `xfeat`, `xfeat-star`, `xfeat-lightglue`, `xfeat-steerers` in [vismatch](./gmberton__vismatch.md) reuse XFeat.

## Gotchas
- Embedded timings are user-reported only: issue #77 - ~700 ms per image on Jetson Orin NX (setup not stated), ~60 ms per frame on an RK3562 by another user. Not reproduced here; benchmark your own board.
- No official ONNX / TensorRT / C++ path (issues #9, #17, #78, #100 open). Community LighterGlue ONNX exports are linked in #100 (`stschake/accelerated_features` fork, `noahzhy/xfeat_lightglue_onnx`); a user there asks whether accuracy matches the original - unverified.
- `realtime_demo.py` uses a homography: README warns it "only works correctly for planar scenes and rotation-only motion".
- Not rotation invariant out of the box; rotation work lives in steerers variants (issue #32) and in vismatch's `xfeat-steerers-*` models. Rotate nadir frames to north-up from heading.
- LighterGlue mutates kornia's `LightGlue.default_conf` at class level (`modules/lighterglue.py`), which can surprise other kornia LightGlue users in the same process.
- Accuracy cost vs SuperPoint+LightGlue, README MegaDepth-1500 AUC@5/10/20 (Accurate setup, 1024 px, 4096 kpts): XFeat+LighterGlue 0.564/0.710/0.819 vs SP+LG 0.591/0.738/0.841.
- Low maintenance since 2025-01; pin a ref for torch.hub (`torch.hub.load("verlab/accelerated_features:<ref>", ...)`) or vendor the clone so the hub load does not change under you.

## Alternatives
- [LightGlue](./cvg__lightglue.md) with ALIKED - more accurate, needs a GPU for real time; [LightGlue-ONNX](./fabio-sim__lightglue-onnx.md) for TensorRT on Jetson.
- [ORB-SLAM3](../../catalog/repos/uz-slamlab__orb_slam3.md) features (ORB) - classical, CPU, but much weaker under illumination/viewpoint change (XFeat README comparison).
- [RoMa](./parskatt__roma.md) - when robustness matters more than speed (ground station, not onboard).

Sources: verlab/accelerated_features README.md, hubconf.py, minimal_example.py, modules/xfeat.py, modules/lighterglue.py, .gitmodules, directory listings of modules/ and weights/; issues #9, #32, #77, #100 (plus search hits #17, #78); releases/latest; GitHub metadata via `gh api` (2026-11-06).
