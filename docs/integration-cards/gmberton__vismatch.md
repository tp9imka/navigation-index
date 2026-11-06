# vismatch - integration card
<!-- about: repo:gmberton/vismatch -->
One-line: `get_matcher("<name>")` gives one interface (paths in, keypoints + RANSAC homography out) over 82 matcher names, so you can run a matcher shoot-out on your own drone/satellite pairs in an afternoon - then deploy the winner directly, after checking its own license.

| | |
|---|---|
| Install | `pip install vismatch` or `uv pip install vismatch` (PyPI). Dev: `git clone --recursive https://github.com/gmberton/vismatch && cd vismatch && uv pip install -e .` Extras: `uv pip install ".[all]"` for SphereGlue (torch-geometric) and OmniGlue/ZippyPoint (tensorflow/larq). Latest release `v1.4.0` (2026-10-15). `requires-python >= 3.10`. |
| Runs on | `get_matcher(..., device="cpu")` default; `cuda` asserted available; `mps` accepted with a warning below torch 2.11 ("several matchers hit missing Metal ops"), and `torch.linalg.inv` is routed through CPU on MPS to avoid NaNs in RoMa/DKM (source comment in `vismatch/__init__.py`). `model_details.md`: "MPS (Apple Silicon) is not tested"; some models are GPU-only or CPU-only (marked with a cross). No ONNX/TensorRT export - this is an evaluation/prototyping layer. |
| Inputs | Two images as path, PIL, numpy, or `torch.Tensor (3,H,W)` in [0,1] (`BaseMatcher.forward`). `matcher.load_image(path, resize=None, rot_angle=0)` helper. `max_num_keypoints=2048` default. CLI accepts images, folders, or files of pairs. |
| Outputs | Dict: `num_inliers`, `H` (3x3 homography img0 => img1 from `cv2.findHomography(..., cv2.USAC_MAGSAC, ...)`, None if <4 matches), `all_kpts0/1`, `all_desc0/1`, `matched_kpts0/1` (pre-RANSAC), `inlier_kpts0/1`, `matched_confidences`. `extract(img)` => `all_kpts0`, `all_desc0`. |
| Key API / entry points | `vismatch.get_matcher(matcher_name="sift-lightglue", device="cpu", max_num_keypoints=2048, *args, **kwargs)` - a list of names returns an `EnsembleMatcher`. `vismatch.available_models` (82 names in source). `BaseMatcher.__call__(img0, img1)`, `.extract(img)`, `.load_image(...)`. `vismatch.viz.plot_matches`, `plot_keypoints`. CLIs: `vismatch-match --matcher NAME --out-dir DIR --input A --input B`, `vismatch-extract`, plus repo scripts `vismatch_match.py`, `vismatch_extract.py`, `vismatch_test.py` (runtime benchmark). |
| Time to first result | Estimate: 15-30 min on a CUDA or CPU box with internet for the first matcher; each new matcher name triggers its own weight download. Assumes PyPI wheels resolve for your Python. |
| License | Wrapper code: BSD-3-Clause (GitHub metadata). README: "although VisMatch uses a BSD 3-Clause License, the matchers we wrap can have different licenses"; `model_details.md`: "Some are heavily restricted". There is no per-model license column in `model_details.md` despite the README saying there is - see Gotchas for the ones checked here. |

## Minimal usage
Not run. Adapted from README; compares three matchers on one pair.

```python
from vismatch import get_matcher

pair = ("drone_frame.jpg", "map_tile.png")
for name in ["aliked-lightglue", "xfeat-star", "roma"]:
    m = get_matcher(name, device="cuda", max_num_keypoints=2048)
    img0 = m.load_image(pair[0], resize=512)
    img1 = m.load_image(pair[1], resize=512)
    r = m(img0, img1)
    print(name, r["num_inliers"], r["H"] is not None)
```

## Wiring it into a nav stack
- Matcher selection, not runtime: build a small labelled set of frame/tile pairs from your target area (e.g. [UAV-VisLoc](../../catalog/repos/intellisensing__uav-visloc.md)), loop over candidate names, score inliers and reprojection error of the tile centre, then deploy the winner via its native repo ([LightGlue](./cvg__lightglue.md), [LightGlue-ONNX](./fabio-sim__lightglue-onnx.md), [XFeat](./verlab__accelerated_features.md), [RoMa](./parskatt__roma.md)).
- Because every matcher returns `H` from the same MAGSAC call, its output drops straight into a tile-georeference step ([rasterio](./rasterio__rasterio.md)) => lat/lon.
- Retrieval is out of scope; pair with [VPR-methods-evaluation](./gmberton__vpr-methods-evaluation.md) (same author) for the coarse stage, then vismatch for the fine stage.
- Rotation: `load_image(..., rot_angle=...)` lets you test north-up vs raw heading cheaply.

## Gotchas
- Mixed licenses, checked via GitHub metadata/LICENSE files on 2026-11-06 (not exhaustive): `superpoint-*` and `superglue` => Magic Leap non-commercial; `master` (MASt3R) and `duster` (DUSt3R) => naver repos report NOASSERTION, MASt3R LICENSE is CC BY-NC-SA 4.0; `eloftr` / `matchanything-eloftr` => zju3dv/EfficientLoFTR now uses a "Project Registration License" requiring registration for any organizational project use; `roma`/`tiny-roma`/`romav2`, `dedode`, `gim-*` => MIT; `loftr`, `omniglue`, `disk-*` => Apache-2.0; `aliked-*` => BSD-3-Clause; `ufm` => BSD-3-Clause. Re-check the specific model you ship.
- Network on every `get_matcher` call: source calls `snapshot_download(f"vismatch/{name}")` from Hugging Face first (comment: "Track usage via HF"); failures print a banner and continue. Pre-populate the HF cache (`HF_HUB_OFFLINE=1` after a warm run) for air-gapped or field use; not tested here.
- `[all]` extra was unsatisfiable on CPython 3.12 because ZippyPoint pins TensorFlow <2.16 (issue #70, closed). Install only the extras you need.
- Import-path issues from vendored third-party code: issues #32 / #56 ("No module named src", MatchAnything import fails when CWD contains `src/`), both closed.
- Runtime numbers in `model_details.md` are 512x512 example pairs on an RTX A4000, averaged over 5 iterations (doc footer), e.g. LightGlue SIFT/SuperPoint/DISK/ALIKED GPU 0.417/0.093/0.184/0.128 s, XFeat 0.027 s GPU / 0.048 s CPU, RoMa 0.453 s GPU / 18.950 s CPU. The wrapper adds overhead; use native repos for latency claims.
- `H` assumes a planar scene; for oblique frames over relief, use the `matched_kpts` and your own model (fundamental/PnP with DEM).

## Alternatives
- [hloc](./cvg__hierarchical-localization.md) - fewer matchers but adds retrieval, SfM and PnP stages.
- [LightGlue](./cvg__lightglue.md) directly - once you have chosen, drop the wrapper and its HF calls.
- [Glue Factory](../../catalog/repos/cvg__glue-factory.md) - when no off-the-shelf matcher works on your imagery and you need to train/evaluate your own.

Sources: gmberton/vismatch README.md, pyproject.toml, docs/source/model_details.md, vismatch/__init__.py, vismatch/base_matcher.py, vismatch/im_models/lightglue.py, vismatch/im_models/roma.py, directory listings; issues #32, #56, #70; releases/latest; naver/mast3r LICENSE, zju3dv/EfficientLoFTR LICENSE; GitHub metadata (license field) for gmberton/vismatch, naver/mast3r, naver/dust3r, zju3dv/LoFTR, zju3dv/EfficientLoFTR, xuelunshen/gim, google-research/omniglue, Parskatt/DeDoDe, Parskatt/RoMaV2, Shiaoming/ALIKED, cvlab-epfl/disk, UniFlowMatch/UFM, magicleap/SuperGluePretrainedNetwork via `gh api` (2026-11-06).
