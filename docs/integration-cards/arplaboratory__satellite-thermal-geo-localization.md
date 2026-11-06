# Satellite-thermal geo-localization (STGL) - integration card
<!-- about: repo:arplaboratory/satellite-thermal-geo-localization -->
One-line: pretrained thermal-query => satellite-RGB retrieval (SGM) plus a satellite => synthetic-thermal generator (TGM), with demo scripts that pull weights from Hugging Face - the quickest way to show night-time map matching.

| | |
|---|---|
| Install | `git clone https://github.com/arplaboratory/satellite-thermal-geo-localization && cd satellite-thermal-geo-localization && conda env create -f env.yml` (env.yml pins python=3.9, pytorch=1.12.0, torchvision=0.13.0, cudatoolkit=11.3, faiss-gpu, h5py, torchscan=0.1.1). For inference use the `demo` branch: `git checkout demo` (README: aligns with STHN/global_pipeline "for pretrained model compatibility"). Demos also import `huggingface_hub` and `safetensors`. No releases. |
| Runs on | env.yml is Linux + NVIDIA (cudatoolkit 11.3, faiss-gpu). Demo scripts select `"cuda" if torch.cuda.is_available() else "cpu"`, so inference should work on CPU with a hand-built env (not tried). Training scripts are SLURM `sbatch` files (README: change suffix to `.sh` for bash). No MPS, ONNX or TensorRT path. |
| Inputs | Thermal query: 8-bit image, contrast-adjusted (factor 3), grayscale => 3 channels, resized to 512x512 (`SGM_demo.py`). Database: 512x512 RGB satellite crops, ImageNet-normalized; demo crops them from a 1536x1536 map with stride 35 px. Training/eval data: HDF5 files (`train/val/test/extended_database.h5`, `*_queries.h5`) from the Boson-nighttime dataset. |
| Outputs | SGM: one global descriptor per image (HF `config.json`: backbone `resnet50conv4`, aggregation `gem`, `fc_output_dim` 4096). Demo prints top-5 patch centres (pixel row, col) with L2 distance and writes `examples/sgm/sgm_retrieval.png`. TGM: synthetic thermal PNGs `examples/tgm/tgm_patch_*.png`. Eval scripts report R@1, R@5 and R_512@1, R_512@5, L^512_2 (README). |
| Key API / entry points | `SGM_demo.py` (demo branch): `download_sgm_model()` => `hf_hub_download(repo_id="xjh19972/SGM", filename="model.safetensors")`, `load_sgm_model(path)` => `model.network.GeoLocalizationNet(args)`. `TGM_demo.py`: `hf_hub_download(repo_id="xjh19972/TGM", ...)`, `load_tgm_model(path)` => `model.network.pix2pix(args, 3, 1)`, `crop_patches(map_np, crop_size=512, stride=35, max_patches=20, region=None)`. Training/eval: `train.py`, `train_extended.py`, `train_pix2pix.py`, `eval.py`, `eval_pix2pix.py`, `scripts/*.sbatch`. |
| Time to first result | Estimate: 30-60 min to `python SGM_demo.py` output on a CUDA Linux box with conda (env solve + ~two HF weight downloads). Retraining TGM+SGM is multi-day GPU work (issue #33 asks about epoch time, unanswered in what I read). |
| License | Code: MIT (GitHub metadata; LICENSE "Copyright (c) 2022 ARPL"; `LICENSE_FOR_REFERENCE` carries MIT for gmberton's deep-visual-geo-localization-benchmark; `model/pix2pix_networks/LICENSE` for the pix2pix code). HF weights `xjh19972/SGM`, `xjh19972/TGM`: weights license not stated (no license field in model card metadata). Dataset `xjh19972/boson-nighttime`: HF metadata `license: mit`, gated (auto-approve, login required). Satellite imagery provenance/terms: not stated in README (training scripts are named `train_bing_*`). |

## Minimal usage
Not run. From the README "Simple Inference Demo".

```bash
git clone https://github.com/arplaboratory/satellite-thermal-geo-localization
cd satellite-thermal-geo-localization
conda env create -f env.yml && conda activate VTL
pip install huggingface_hub safetensors
git checkout demo
python SGM_demo.py   # thermal examples/thermal_512.png vs crops of examples/satellite_1536.png
python TGM_demo.py   # satellite crops => synthetic thermal
```

## Wiring it into a nav stack
- Same coarse-retrieval role as [AnyLoc](./anyloc__anyloc.md), but for a thermal (night) camera: pre-crop a georeferenced satellite map into 512x512 patches with known centres, embed them once, embed each thermal frame, nearest neighbour => candidate centre. Patch pixel centre => lat/lon via the map's geotransform ([rasterio](../../catalog/repos/rasterio__rasterio.md)).
- Refine with the same lab's [STHN](../../catalog/repos/arplaboratory__sthn.md) (deep homography thermal => satellite) or [UASTHN](../../catalog/repos/arplaboratory__uasthn.md) (adds uncertainty, useful as the measurement covariance) before handing a fix to a filter.
- TGM is a data tool: generate synthetic thermal from satellite tiles of your own area to fine-tune or test SGM where you have no thermal flights.
- Fix output is 2D position only; fuse it as an absolute position update in an EKF/ESKF (pattern shown in [tercom_nav](./mzahana__tercom_nav.md)), with altitude and heading from the autopilot.

## Gotchas
- Two incompatible code states: README says the Google Drive pretrained weights "may not be compatible with this repository" and points to STHN/global_pipeline; the HF demo needs the `demo` branch. Do not mix `main` code with HF weights.
- Dataset has no geographic coordinates: issue #29, maintainer: "we don't have latitude and longitude information for this dataset". Benchmarks are in map-pixel space; you supply georeferencing for your own area.
- Dataset is gated on Hugging Face (login + accept) and split into `thermal_dataset.tar.gz.part*` chunks; the README lists md5sums to check. `extended_queries.h5` must be generated yourself with a trained TGM.
- Training scripts are SLURM-only and there are 79 near-identical `.sbatch` files in `scripts/`; README marks the "Best choice" ones.
- TGM output range issues on other data (issue #22): output is typically in [-1, 1]; clamping/normalising is needed, or retrain with tanh.
- `faiss-gpu` + `cudatoolkit=11.3` pins are 2022-era; expect conda solve pain on new drivers. CPU path requires building your own env.
- Weight license unstated: fine for a hackathon demo, ask the authors before shipping.

## Alternatives
- [STHN](../../catalog/repos/arplaboratory__sthn.md) - same lab, newer; README itself recommends its `global_pipeline` for pretrained compatibility, and adds the fine homography stage.
- [SCC-Loc](../../catalog/repos/floralhercules__scc-loc.md) - zero-shot thermal geo-localization without thermal-specific training; try it when your thermal camera differs from the Boson used here.
- [AnyLoc](./anyloc__anyloc.md) - RGB-only, but training-free; use it for day flights and keep STGL for night.

Sources: arplaboratory/satellite-thermal-geo-localization README.md, LICENSE, LICENSE_FOR_REFERENCE, env.yml, repo tree (main and demo branches), demo-branch SGM_demo.py, TGM_demo.py, model/network.py; issues #22, #29, #30, #33; Hugging Face API/model cards for xjh19972/SGM, xjh19972/TGM, datasets/xjh19972/boson-nighttime (2026-11-06).
