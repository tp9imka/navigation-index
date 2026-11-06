# RoMa - integration card
<!-- about: repo:parskatt/roma -->
One-line: dense matcher (DINOv2 coarse features + learned refinement) that still finds correspondences across season, lighting and sensor gaps where sparse matchers fail - use it as the slow, accurate verifier on the top retrieval hit, on a CUDA GPU.

| | |
|---|---|
| Install | `uv pip install romatch` (PyPI) or from a clone `uv pip install -e .` / `uv sync` (README, "tested on Linux python 3.12"). Optional fused kernel: `uv pip install romatch[fused-local-corr]` - Linux only per `pyproject.toml` marker. Latest GitHub release `v0.1.1` (2025-10-06); `pyproject.toml` on main says `0.1.2`. Requires `torch>=2.5.1`, `poselib>=2.0.4`, `timm`, `kornia`, `wandb`, others. |
| Runs on | Linux + NVIDIA GPU is the working path. In `romatch/utils/utils.py` `get_autocast_params`, AMP is enabled only for CUDA; any other device runs without autocast and the code comments "mps is not supported". CPU is possible but slow (vismatch `model_details.md` "s/img" columns: 18.950 on CPU vs 0.453 on an RTX A4000, 512x512 example pairs). Maintainer: ~1 s per pair at paper settings, "about 0.1 seconds" batched at lower resolution (issue #42). No official ONNX/TensorRT; a third-party coarse-pass ONNX export is described in issue #151 (fork `ilanmotiei/RoMa`, not checked). |
| Inputs | Two images as file paths or PIL images (`match(im_A_input, im_B_input, ...)`); 8-bit RGB only - `check_not_i16` raises on 16-bit, `check_rgb` on non-RGB. Default coarse resolution 560x560, upsampled to 864x864 (README, `roma_outdoor` kwargs `coarse_res`, `upsample_res`). |
| Outputs | `warp` (dense correspondence field in normalized [-1,1] coords) and `certainty` per pixel. `sample(warp, certainty)` => sparse `matches`, `certainty`; `to_pixel_coordinates(matches, H_A, W_A, H_B, W_B)` => `kptsA`, `kptsB` in pixels. |
| Key API / entry points | `romatch/__init__.py` exports `roma_outdoor`, `roma_indoor`, `tiny_roma_v1_outdoor`. `roma_outdoor(device, weights=None, dinov2_weights=None, coarse_res=560, upsample_res=864, amp_dtype=torch.float16, symmetric=True, use_custom_corr=True, upsample_preds=True, with_padding=False, do_compile=False)`. `RegressionMatcher.match(...)`, `.sample(...)`, `.to_pixel_coordinates(...)`, `.match_keypoints(...)`, `.visualize_warp(...)` (all in `romatch/models/matcher.py`). Attributes `w_resized`, `h_resized`, `upsample_res`, `sample_thresh`. Demos: `demo/demo_match.py`, `demo/demo_fundamental.py`, `demo/demo_match_tiny.py`. |
| Time to first result | Estimate: 20-40 min on a Linux CUDA box with internet (RoMa weights from `Parskatt/storage` releases plus DINOv2 ViT-L/14 from `dl.fbaipublicfiles.com` on first call). Longer on macOS/CPU because of the issues below. |
| License | Code: MIT (GitHub metadata, LICENSE). README: "All our code except DINOv2 is MIT license. DINOv2 has an Apache 2 license"; GitHub metadata for facebookresearch/dinov2 is Apache-2.0. Weights: outdoor model trained on MegaDepth; indoor weights trained on ScanNet - maintainer (issue #17): "Scannet has a non-commercial license", cannot say what that means for the weights. Weights license otherwise not stated. |

## Minimal usage
Not run. Adapted from README.

```python
import cv2, torch
from PIL import Image
from romatch import roma_outdoor

dev = "cuda"
roma = roma_outdoor(device=dev, coarse_res=560, upsample_res=864)
a, b = "drone_frame.jpg", "map_tile.png"
W_A, H_A = Image.open(a).size
W_B, H_B = Image.open(b).size

warp, certainty = roma.match(a, b, device=dev)
matches, certainty = roma.sample(warp, certainty)
kA, kB = roma.to_pixel_coordinates(matches, H_A, W_A, H_B, W_B)
H, inl = cv2.findHomography(kA.cpu().numpy(), kB.cpu().numpy(), cv2.USAC_MAGSAC, 3.0)
```

## Wiring it into a nav stack
- Second-stage verifier: retrieval ([AnyLoc](./anyloc__anyloc.md), [SALAD](../../catalog/repos/serizba__salad.md)) => fast sparse match ([LightGlue](./cvg__lightglue.md) or [XFeat](./verlab__accelerated_features.md)) on top-k => RoMa only on the top-1 or when the sparse inlier count is marginal. Output homography => tile georeference => lat/lon, same hand-off as the LightGlue card.
- `certainty` is a useful quality signal: gate fixes on mean certainty of sampled matches as well as RANSAC inliers before sending to an EKF or MAVLink.
- Thermal-to-RGB or night imagery: RoMa is the dense candidate to try first; compare with [satellite-thermal-geo-localization](../../catalog/repos/arplaboratory__satellite-thermal-geo-localization.md). Convert 16-bit radiometric frames to 8-bit RGB first (see Gotchas).
- Edge: `tiny_roma_v1_outdoor` builds on XFeat (pulled via `torch.hub.load("verlab/accelerated_features", "XFeat", ...)`), README table shows it ahead of XFeat* on MegaDepth-1500 AUC.

## Gotchas
- `roma_outdoor` / `roma_indoor` raise `RuntimeError` unless `torch.get_float32_matmul_precision()` is `"highest"` (source). If another library in your process sets it to `"high"` (common with TF32 tweaks), RoMa refuses to build.
- CPU/macOS fp16 errors: issues #26 ("LayerNormKernelImpl not implemented for 'Half'") and #100 (CPU precision mismatch) are open. Current source disables autocast off CUDA, but this was not verified here; if it still fails, pass `amp_dtype=torch.float32`.
- macOS arm64 install failed on missing `fused-local-corr` wheels (issue #124); maintainer made it Linux-only and added: "be a bit careful with MacOS inference, have had issues before with MPS".
- 16-bit images are rejected (`check_not_i16`), which bites with raw thermal frames.
- DINOv2 weights URL is hardcoded with the comment "hopefully this doesnt change :D". For offline/air-gapped use, download `dinov2_vitl14_pretrain.pth` and the RoMa `.pth` in advance and pass `weights=` / `dinov2_weights=`.
- Results are stochastic (README "Reproducibility": RANSAC and sampled correspondences vary) - average several runs when benchmarking.
- RoMa v2 exists as a separate repo (Parskatt/RoMaV2, MIT per GitHub metadata); it is not in the index - check it before committing to v1.

## Alternatives
- [LightGlue](./cvg__lightglue.md) - 10x+ faster sparse matching; good enough when imagery is same-season, same-sensor.
- [MASt3R](../../catalog/repos/naver__mast3r.md) - dense 3D-aware matching, but CC BY-NC-SA 4.0 (its LICENSE) - research only.
- [vismatch](./gmberton__vismatch.md) - runs `roma`, `tiny-roma`, `romav2` and dozens of others behind one call for a quick shoot-out on your own frames.

Sources: Parskatt/RoMa README.md, pyproject.toml, LICENSE, romatch/__init__.py, romatch/models/model_zoo/__init__.py, romatch/models/matcher.py, romatch/utils/utils.py, demo/ listing; issues #9, #17, #26, #42, #100, #124, #151; releases/latest; gmberton/vismatch docs/source/model_details.md; naver/mast3r LICENSE; GitHub metadata for Parskatt/RoMa, Parskatt/RoMaV2, facebookresearch/dinov2 via `gh api` (2026-11-06).
