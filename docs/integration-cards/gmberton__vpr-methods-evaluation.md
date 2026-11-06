# VPR-methods-evaluation - integration card
<!-- about: repo:gmberton/vpr-methods-evaluation -->
One-line: one CLI that runs ~20 pretrained place-recognition models (NetVLAD to MegaLoc/AnyLoc/SALAD) on two folders of images and gives you recall@k plus top-k prediction images - the quickest way to choose a retrieval model for your drone-to-satellite tiles.

| | |
|---|---|
| Install | `git clone --recursive https://github.com/gmberton/VPR-methods-evaluation && cd VPR-methods-evaluation && pip install -r requirements.txt` (unpinned: faiss_cpu, torch, torchvision, huggingface_hub, safetensors, gdown, loguru, scikit_learn, ...). `--recursive` is required (submodule `third_party/deep-image-retrieval` for AP-GeM; `vpr_models/__init__.py` raises a hint if missing). No releases; last push 2026-08. |
| Runs on | Any OS with PyTorch. `--device` choices are `cuda` or `cpu` only (parser.py) - no MPS. README: the toy CosPlace/ResNet18 run "will take a few seconds even running on a CPU of a laptop". Heavy DINOv2 models (AnyLoc ViT-G, SALAD, MegaLoc) want a GPU. Search is `faiss.IndexFlatL2` on CPU (exhaustive). No ONNX/TensorRT export. |
| Inputs | `--database_folder`, `--queries_folder` (recursive glob of .jpg/.jpeg/.png, or a `<folder>_images_paths.txt` list). Labelled mode needs UTM in the filename: `path/@UTM_east@UTM_north@whatever@.jpg`; positives are within `--positive_dist_threshold` (default 25 m). `--no_labels` for plain retrieval. `--image_size H W` or a single int for shortest edge. |
| Outputs | Log dir `logs/<log_dir>/<timestamp>/` with `info.log` (recall line e.g. `R@1: 98.8, R@5: 99.7, ...` per README for CosPlace on St Lucia), optional `queries_descriptors.npy` / `database_descriptors.npy` (`--save_descriptors`), optional prediction images (`--num_preds_to_save N`, `--save_only_wrong_preds`). |
| Key API / entry points | `main.py` (CLI, `main(args)`); `parser.parse_arguments()` (method list + per-method dim validation); `vpr_models.get_model(method, backbone=None, descriptors_dimension=None)` returns a `torch.nn.Module` mapping `[B,3,H,W]` => `[B,D]`; `test_dataset.TestDataset(database_folder, queries_folder, positive_dist_threshold=25, image_size=None, use_labels=True)`; `vpr_models.resizing_wrapper.ResizingWrapper(model, resize_type="dino_v2_resize")` snaps H, W to multiples of 14. |
| Time to first result | Estimate: 10-15 min to the toy-dataset run on a laptop CPU (pip install dominates). 1-2 h to a recall table on your own tiles, assuming you can write UTM coordinates into filenames. |
| License | Wrapper code: MIT (GitHub metadata, LICENSE file). README: "each wrapped model (its code and weights) is subject to its own license". Upstream code licenses from GitHub metadata (2026-11-06): CosPlace, EigenPlaces, MegaLoc, BoQ, CricaVPR, SuperVLAD, DINO-Mix, EDTformer, OpenIBL (SFRS), Relja/netvlad: MIT; naver/deep-image-retrieval (AP-GeM): BSD-3-Clause; AnyLoc: BSD-3-Clause (vocabulary license not stated); serizba/salad and serizba/cliquemining: GPL-3.0; amaralibey/MixVPR and gsv-cities (Conv-AP): no license detected (all rights reserved by default); QAA upstream (xjh19972/QAA, linked in README) returned 404. Weight-file licenses are not stated separately by this repo. |

## Minimal usage
Not run. From the README, then adapted to aerial tiles.

```bash
# toy smoke test, CPU
python3 main.py --method=cosplace --backbone=ResNet18 --descriptors_dimension=512 \
  --database_folder=toy_dataset/database --queries_folder=toy_dataset/queries \
  --no_labels --image_size 200 200 --num_preds_to_save 3 --log_dir toy_experiment --device cpu

# your data: tiles/@<east>@<north>@tileid@.png, frames/@<east>@<north>@frameid@.jpg
for m in megaloc salad anyloc-aerial eigenplaces; do
  python3 main.py --method=$m --database_folder=tiles --queries_folder=frames \
    --image_size 322 322 --positive_dist_threshold 50 --save_descriptors --log_dir aerial_$m
done
```

## Wiring it into a nav stack
- Model selection bench, not a runtime: use it to pick the retrieval model for the coarse stage, then take `vpr_models.get_model(...)` directly into your node and keep the FAISS index built from tile descriptors.
- Data prep: tile an orthophoto (e.g. from [OpenDroneMap](../../catalog/repos/opendronemap__odm.md) or a STAC download via [pystac-client](../../catalog/repos/stac-utils__pystac-client.md)), compute each tile-centre UTM with [rasterio](../../catalog/repos/rasterio__rasterio.md), write it into the filename. Drone frames get their GNSS-truth UTM the same way - that is your evaluation label.
- Top-k tiles go to a local matcher ([LightGlue](../../catalog/repos/cvg__lightglue.md), [vismatch](../../catalog/repos/gmberton__vismatch.md) for the same "many models, one interface" idea on the matching side) and then to a homography => lat/lon fix, as in [WildNav](./tiers__wildnav.md).
- [hloc](../../catalog/repos/cvg__hierarchical-localization.md) is the alternative if you need retrieval + 6-DoF pose against an SfM map instead of 2D tiles.

## Gotchas
- `anyloc-*` methods hardcode `device="cuda"` inside `get_model` (`vpr_models/__init__.py`), so `--device cpu` still fails for AnyLoc on a CPU-only box. Other hub models load on CPU and are then moved by `.to(args.device)`.
- Default `--method` is `megaloc`; `--descriptors_dimension` is validated per method (e.g. NetVLAD only 4096 or 32768, CosPlace/ResNet18 only 32-512). Wrong combos raise at parse time.
- `--batch_size` default 4 requires same-size database images; README help says set 1 if resolutions differ, or pass `--image_size`.
- All descriptors are held in one dense float32 array in RAM before FAISS; with AnyLoc (49152 dims) that is ~192 KB per image (computed) - tens of thousands of tiles will need RAM planning or PCA.
- Recall uses UTM distance only; heading/scale mismatch between nadir frames and north-up tiles is your problem. Rotate frames to north-up first.
- Issue #8: "GET was unable to find an engine to execute this computation" with MixVPR on GPU (closed) - typical torch/CUDA mismatch; pin a torch build that matches your driver.
- Licensing trap: the MIT badge covers only the wrapper. SALAD/CliqueMining are GPL-3.0, MixVPR/Conv-AP have no license, AnyLoc vocabularies are unclarified. Pick MIT/BSD upstreams if the demo may become a product.

## Alternatives
- [AnyLoc](./anyloc__anyloc.md) - use directly if you have already decided on DINOv2+VLAD and want the "aerial" vocabulary without the wrapper.
- [VPR-Bench](../../catalog/repos/mubarizzaffar__vpr-bench.md) - broader evaluation framework (IJCV paper) with more datasets/metrics; heavier to set up.
- [hloc](../../catalog/repos/cvg__hierarchical-localization.md) - when you want retrieval + local matching + pose in one maintained toolbox rather than a retrieval-only bench.

Sources: gmberton/VPR-methods-evaluation README.md, main.py, parser.py, test_dataset.py, requirements.txt, .gitmodules, vpr_models/__init__.py, vpr_models/resizing_wrapper.py; issues #1, #8, #18; GitHub license metadata of each upstream repo listed (via `gh api`, 2026-11-06).
