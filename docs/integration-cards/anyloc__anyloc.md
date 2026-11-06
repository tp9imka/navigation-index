# AnyLoc - integration card
<!-- about: repo:anyloc/anyloc -->
One-line: training-free DINOv2 + VLAD global descriptors with a released "aerial" vocabulary - a coarse "which satellite tile am I over" retrieval stage you can stand up without training anything.

| | |
|---|---|
| Install | Full repo: `git clone https://github.com/AnyLoc/AnyLoc.git && cd AnyLoc && conda create -n anyloc python=3.9 && conda activate anyloc && bash ./setup_conda.sh` (README: "about 11 GB of disk space"). Lighter path via the companion torch.hub repo [AnyLoc/DINO](https://github.com/AnyLoc/DINO): `pip install torch torchvision einops fast_pytorch_kmeans`, then `torch.hub.load("AnyLoc/DINO", "get_vlad_model", ...)`. No releases/tags on the main repo; last push 2024-03. |
| Runs on | Linux + NVIDIA GPU is the tested path (paper runs: RTX 3090 24 GB; README: "Ideally, a 16 GB GPU should also work"). `demo/anyloc_vlad_generate.py` hardcodes `torch.device("cuda")`. `DinoV2ExtractFeatures(..., device="cpu")` and the hub `get_vlad_model(device="cpu")` accept CPU, so CPU works by editing the device (slow with ViT-G/14). No MPS/Apple Silicon handling in source. No ONNX/TensorRT export provided. |
| Inputs | RGB images (PIL), ImageNet-normalized, cropped to multiples of 14 px (ViT patch). Demo caps the longest edge at `max_img_size=1024` "(GPU OOM)". Demo script only globs `*.jpg`. Vocabulary: `c_centers.pt` per domain (`indoor`, `urban`, `aerial`, and on the hub also `structured`, `unstructured`, `global`). |
| Outputs | One global descriptor per image. Default config (ViT-G/14, layer 31, facet value, 32 clusters) => shape `[N, 49152]` (AnyLoc/DINO README). Demo writes one `<image>.npy` per image. No poses, no geo - you supply tile coordinates yourself. |
| Key API / entry points | `demo/utilities.py`: `DinoV2ExtractFeatures(dino_model, layer, facet="token", use_cls=False, norm_descs=True, device="cpu")`, `VLAD(num_clusters, desc_dim=None, cache_dir=...)` with `.fit(train_descs or None)`, `.generate(query_descs)`, `.generate_multi(...)`. CLI: `python demo/anyloc_vlad_generate.py --in-dir ... --out-dir ... --domain aerial` (tyro, `LocalArgs`). Hub: `get_vlad_model(domain, backbone="DINOv2", vit_model="ViT-G/14", vit_layer=31, vit_facet="Value", num_c=32, device="cpu")`; returned model has `.extract(imgs)`, `.fit(descs)`, `model(imgs)`. |
| Time to first result | Estimate: 30-60 min via the torch.hub path on a CUDA box with internet (DINOv2 ViT-G weights + cluster centers download on first call). 2-4 h via `setup_conda.sh` + manual cache.zip download, which has been broken repeatedly (see Gotchas). |
| License | Code: BSD-3-Clause (GitHub metadata, AnyLoc/AnyLoc and AnyLoc/DINO). Backbone: DINOv2 repo is Apache-2.0 (GitHub metadata of facebookresearch/dinov2). VLAD vocabularies (`c_centers.pt`, `cache.zip`): license not stated - open issue #50 asks exactly this, unanswered at time of reading. Datasets in the public release: "copyright of each dataset is held by the original sources" (README). |

## Minimal usage
Not run. Adapted from the AnyLoc/DINO README (that repo says it is "work-in-progress ... Use `force_reload = True` while the API is unstable").

```python
import torch, numpy as np
from PIL import Image
import torchvision.transforms as T

dev = "cuda" if torch.cuda.is_available() else "cpu"
model = torch.hub.load("AnyLoc/DINO", "get_vlad_model",
                       domain="aerial", backbone="DINOv2", device=dev)
tf = T.Compose([T.ToTensor(), T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])

def desc(path, side=518):                     # 518 = 37 * 14
    img = tf(Image.open(path).convert("RGB").resize((side, side)))[None].to(dev)
    with torch.no_grad():
        return model(img).cpu().numpy()       # [1, 49152]

db = np.concatenate([desc(p) for p in tile_paths])   # satellite tiles, offline
q = desc("drone_frame.jpg")
top5 = np.argsort(((db - q) ** 2).sum(1))[:5]        # candidate tiles for fine matching
```

## Wiring it into a nav stack
- Stage 1 of a two-stage visual-geolocalization pipeline: cut a georeferenced orthophoto into overlapping tiles (keep the tile => corner lat/lon table), precompute AnyLoc descriptors offline, query with each nadir drone frame, pass top-k tiles to a local matcher ([LightGlue](../../catalog/repos/cvg__lightglue.md), [RoMa](../../catalog/repos/parskatt__roma.md)) for a homography => lat/lon fix. [WildNav](./tiers__wildnav.md) is exactly the stage-2 half without retrieval.
- For many tiles use FAISS (as [VPR-methods-evaluation](./gmberton__vpr-methods-evaluation.md) does with `IndexFlatL2`). 49152 float32 dims = 192 KB per tile (computed), so PCA or a lighter model matters at city scale.
- Retrieval output is a candidate set, not a measurement. Gate it (match inlier count) before feeding a position into an EKF or a MAVLink position message.
- Same descriptor is reachable through VPR-methods-evaluation `--method anyloc-aerial` if you want to compare it against SALAD/MegaLoc on your own tiles first.

## Gotchas
- Asset hosting is fragile: cache.zip / OneDrive links broke (issues #33, #35, #39, #41, #43); maintainer moved everything to a single ~32 GB Dropbox tarball (issue #34 comment). The torch.hub path pulls cluster centers from GitHub release `AnyLoc/DINO` v1 instead - prefer it.
- Only ViT-G/14 layer-31 vocabularies are released (issue #45, and `AVAIL_VLADCC_FILES` in `AnyLoc/DINO/hubconf.py`). Smaller backbones need `domain=None` + your own `model.fit(...)` on map-specific descriptors.
- `demo/anyloc_vlad_generate.py` accepts `--imgs-ext` but globs `*.jpg` only (source, line with `glob.glob(f"{imgs_dir}/*.jpg")`) - PNG tiles are silently skipped.
- No rotation invariance: issue #29 asks about randomly rotated UAV images; maintainer points elsewhere (RoRD). Rotate nadir frames to north-up from heading before querying, or add rotated tile copies.
- Scaling: issue #48 reports strong degradation going from a 0.01 deg flight path to a 1x1 deg search area, with correct tiles only somewhere in top-1000. Use a prior (last fix + INS drift bound) to restrict the tile set.
- Licensing trap is the vocabulary, not the code: commercial use of `c_centers.pt` is unclarified (issue #50). Fitting your own vocabulary on your own map tiles sidesteps it.

## Alternatives
- [SALAD](../../catalog/repos/serizba__salad.md) - also DINOv2-based, smaller descriptors; code is GPL-3.0 (GitHub metadata), which matters if you ship.
- [EigenPlaces](../../catalog/repos/gmberton__eigenplaces.md) / [CosPlace](../../catalog/repos/gmberton__cosplace.md) - ResNet backbones, MIT, 512-2048 dims, run fine on CPU or small GPUs; trained on street-level imagery, so validate on aerial.
- [VPR-methods-evaluation](./gmberton__vpr-methods-evaluation.md) - not an alternative model but the fastest way to pick between all of the above on your own data.

Sources: AnyLoc/AnyLoc README.md, demo/README.md, demo/anyloc_vlad_generate.py, demo/utilities.py; AnyLoc/DINO README.md and hubconf.py; AnyLoc issues #29, #34, #39, #41, #45, #48, #50; GitHub repo metadata for AnyLoc/AnyLoc, AnyLoc/DINO, facebookresearch/dinov2 (via `gh api`, 2026-11-06).
