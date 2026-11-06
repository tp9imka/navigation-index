# hloc - integration card
<!-- about: repo:cvg/hierarchical-localization -->
One-line: ready-made retrieval => local matching => PnP plumbing against a COLMAP/pycolmap SfM model, with HDF5 hand-off files between stages - the fastest way to a 6-DoF "where is this camera in my pre-built map" answer.

| | |
|---|---|
| Install | `git clone --recursive https://github.com/cvg/Hierarchical-Localization/ && cd Hierarchical-Localization/ && python -m pip install -e .` (README). Submodules are required (`git submodule update --init --recursive`): d2net, SuperGluePretrainedNetwork, deep-image-retrieval, r2d2. Docker: `docker build -t hloc:latest .`, add `--runtime=nvidia` for GPU. `hloc/__init__.py` `__version__ = "1.5"`; latest GitHub release is `v1.4` (2023-07-20). `requirements.txt` pins `pycolmap>=3.13.0` and pulls `lightglue @ git+https://github.com/cvg/LightGlue`. |
| Runs on | Python >=3.7, PyTorch >=1.1 (README). `extract_features.py` and `match_features.py` pick `"cuda" if torch.cuda.is_available() else "cpu"` - no MPS path in source. COLMAP binary not needed since v1.3 (pycolmap is enough). No ONNX/TensorRT export provided; issue #391 (Jetson Orin TensorRT conversion) is open. |
| Inputs | Image directory (`image_dir`), image list or pairs file (text, one `name0 name1` per line). Optional known intrinsics as COLMAP camera model strings (`camera_model='SIMPLE_RADIAL'`, `camera_params`). Preprocessing confs set `resize_max` (1024 for most, 1600 for `superpoint_max`/`superpoint_inloc`). |
| Outputs | HDF5 feature files (keys = relative image path; `keypoints` Nx2, `descriptors` DxN; global: `global_descriptor` D), HDF5 match files (`matches0`, -1 = unmatched), pairs text files, a pycolmap/COLMAP SfM model, and per-query 6-DoF poses in a results text file plus a pickle log of inliers per query (README "Debugging"). |
| Key API / entry points | `hloc.extract_features.main(conf, image_dir, export_dir=None, as_half=True, image_list=None, feature_path=None, overwrite=False)` with `extract_features.confs[...]` (`superpoint_aachen`, `superpoint_max`, `superpoint_inloc`, `sift`, `sosnet`, `disk`, `netvlad`, `openibl`, `megaloc`, `dir`, ...). `hloc.match_features.main(conf, pairs, features, export_dir=None, matches=None, ...)` with confs `superpoint+lightglue`, `disk+lightglue`, `aliked+lightglue`, `superglue`, `NN-mutual`, `NN-ratio`, `adalam`. `hloc.pairs_from_retrieval.main(descriptors, output, num_matched, ...)`, `pairs_from_exhaustive`, `reconstruction.main(...)`, `localize_sfm.main(reference_sfm, queries, retrieval, features, matches, results, ransac_thresh=12, ...)`. CLI: `python -m hloc.<script> --args`. |
| Time to first result | Estimate: 1-2 h to run `pipeline_SfM.ipynb` on your own few hundred images with a CUDA GPU (or the Colab demo, which README says runs with GPU for free). Most time goes to pycolmap/submodule install and SfM. |
| License | Code: Apache-2.0 (GitHub metadata). Bundled third-party submodules keep their own licenses - see Gotchas. NetVLAD checkpoints are fetched from `cvg-data.inf.ethz.ch` (`hloc/extractors/netvlad.py`); weights license not stated in hloc. MegaLoc is loaded via `torch.hub.load("gmberton/MegaLoc", ...)`; its license not checked here. |

## Minimal usage
Not run. Retrieval + matching only (no SfM), adapted from README and the module signatures; uses DISK + LightGlue to avoid the SuperPoint/SuperGlue licenses.

```python
from pathlib import Path
from hloc import extract_features, match_features, pairs_from_retrieval

images = Path("data/")             # contains tiles/*.png and query/*.jpg
out = Path("outputs/")
ret_conf = extract_features.confs["netvlad"]
feat_conf = extract_features.confs["disk"]
match_conf = match_features.confs["disk+lightglue"]

g = extract_features.main(ret_conf, images, out)
pairs = out / "pairs-netvlad.txt"
pairs_from_retrieval.main(g, pairs, num_matched=5, query_prefix="query", db_prefix="tiles")
f = extract_features.main(feat_conf, images, out)
m = match_features.main(match_conf, pairs, feat_conf["output"], out)
# f, m: HDF5 files; read keypoints/matches0 with h5py and run cv2.findHomography per pair
```

## Wiring it into a nav stack
- Map-relative relocalization: build an SfM model of the operating area beforehand (`reconstruction.main`), then `localize_sfm.main` gives a camera pose in the model frame. Georeference the model (GPS-tagged mapping images or surveyed points) to get poses in a world frame, then feed as an absolute pose measurement into [robot_localization](./cra-ros-pkg__robot_localization.md) or a [GTSAM](./borglab__gtsam.md) factor graph.
- Without SfM, use it as a batch harness: retrieval to pairs file => matching to HDF5 => your own homography to tile georeference ([rasterio](./rasterio__rasterio.md)). The HDF5 layout is documented in README, so other tools can read it.
- Retrieval swaps: `netvlad`, `openibl`, `megaloc`, `dir` are built-in confs; [VPR-methods-evaluation](./gmberton__vpr-methods-evaluation.md) is better for choosing among VPR models first.
- Matcher internals come from [LightGlue](./cvg__lightglue.md) (dependency) and [SuperGlue](../../catalog/repos/magicleap__supergluepretrainednetwork.md) (submodule).

## Gotchas
- License trap: the `superpoint_*` extractor confs import `SuperGluePretrainedNetwork.models.superpoint` from the submodule (`hloc/extractors/superpoint.py`), and `superglue` matcher confs import the same submodule. That repo's LICENSE is "ACADEMIC OR NON-PROFIT ORGANIZATION NONCOMMERCIAL RESEARCH USE ONLY". The README's showcase pipelines and result tables are SuperPoint+SuperGlue / SuperPoint+NN. Issue #452 asks for per-method licenses; no answer at time of reading. Use `disk`/`aliked` + LightGlue, or `sift` + NN, for non-research work.
- pycolmap version churn is the main breakage source: 72 issues mention pycolmap (e.g. #370 SIFT broken by a pycolmap update, #393 `Camera` has no attribute `id`). Pin pycolmap to what `hloc/__init__.py` expects (>=3.13.0, warns otherwise).
- Apple Silicon: issue #491 (open) - SIGSEGV from an OpenMP conflict with pycolmap 3.13; a commenter reports pycolmap 3.11 avoids it. No MPS device selection in source anyway, so it runs on CPU there.
- Jetson/TensorRT: nothing provided (issue #391 open). For an onboard deployment, take only the ideas and use [LightGlue-ONNX](./fabio-sim__lightglue-onnx.md) for the matcher.
- Pipelines target ground-level benchmarks (Aachen, InLoc, CMU Seasons, RobotCar, Cambridge, 7-Scenes); no aerial pipeline. GPS-guided retrieval is still on the README's wishlist.
- `ransac_thresh=12` px default in `localize_sfm.main` is tuned for those benchmarks; retune for your resolution.

## Alternatives
- [LightGlue](./cvg__lightglue.md) alone + OpenCV RANSAC - less plumbing if you only need 2D tile registration, not 6-DoF in an SfM model.
- [vismatch](./gmberton__vismatch.md) - one-call access to many more matchers, but no retrieval/SfM/PnP stages.
- [GTSfM](../../catalog/repos/borglab__gtsfm.md) or [VGGT](../../catalog/repos/facebookresearch__vggt.md) - when the hard part is building the reference 3D model, not localizing against it.

Sources: cvg/Hierarchical-Localization README.md, requirements.txt, .gitmodules, setup.py, hloc/__init__.py, hloc/extract_features.py, hloc/match_features.py, hloc/pairs_from_retrieval.py, hloc/localize_sfm.py, hloc/extractors/superpoint.py, hloc/extractors/netvlad.py, hloc/extractors/megaloc.py, hloc/matchers/superglue.py, directory listings of hloc/extractors and hloc/matchers; issues #370, #391, #393, #452, #491; magicleap/SuperGluePretrainedNetwork LICENSE; releases/latest; GitHub metadata via `gh api` (2026-11-06).
