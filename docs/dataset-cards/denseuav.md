# DenseUAV

<!-- about: repo:dmmm1997/denseuav -->

Low-altitude urban UAV self-positioning dataset with densely sampled drone and satellite
views and per-image GPS. Dai et al., "Vision-Based UAV Self-Positioning in Low-Altitude
Urban Environments", IEEE TIP 2023 (arXiv 2201.09201).

| Field | Value |
|---|---|
| Platform | Real UAV (model not stated in README) |
| Environment | Low-altitude urban scenes across 14 universities (10 train, 4 test) |
| Sensors and rates | RGB stills at three heights per sample point (file names H80 / H90 / H100, i.e. 80, 90, 100 m) plus satellite crops, including an older satellite epoch (`*_old.tif`) |
| Ground truth | Per-image latitude, longitude, height in `Dense_GPS_ALL.txt` (source and accuracy not stated) |
| Size | 16.7 GB: `DenseUAV.zip` 16,738,945,339 bytes (Hugging Face API, 2026-11-06) |
| License | Repo: Apache-2.0. Hugging Face card: MIT. Neither text explicitly scopes the imagery; satellite tiles carry their provider's terms |
| Format | `train/{drone,satellite}/<id>/H{80,90,100}.JPG|tif`, `test/query_{drone,satellite}/`, GPS text files |
| Index | [DenseUAV](../../catalog/repos/dmmm1997__denseuav.md) |

## What's in it

| Subset | UAV-view | Satellite-view | Classes |
|---|---|---|---|
| Train | 6,768 | 13,536 | 2,256 |
| Query | 2,331 | 4,662 | 777 |
| Gallery | 9,099 | 18,198 | 3,033 |

Dense sampling means neighbouring classes look alike, so the benchmark measures fine
position discrimination and reports a distance-based metric (SDM) besides Recall@K.

## Download

```bash
# not gated (HF API gated=False on 2026-11-06)
hf download Dmmm997/DenseUAV --repo-type dataset --local-dir DenseUAV
# or
curl -L -o DenseUAV.zip https://huggingface.co/datasets/Dmmm997/DenseUAV/resolve/main/DenseUAV.zip
git clone https://github.com/Dmmm1997/DenseUAV.git
```

## Loading and tooling

```python
rows = [l.split() for l in open("DenseUAV/Dense_GPS_ALL.txt")]
# path latitude longitude height
```

Baseline training/eval in the repo (PyTorch 1.10 + CUDA 11.3 pinned in README; expect to
bump versions). Follow-ups from the same author: DRL, SWA-PF (linked from README, not indexed).

## Hackathon fit

- Idea 18 / 20 when the demo is a low urban flight: retrieval output can be turned into
  meters via the GPS file, unlike University-1652.
- Old vs new satellite epoch lets you show map-age robustness, a point judges like.

## Pitfalls

- One 16.7 GB zip, no per-split download.
- Stills, not sequences; no IMU.
- Pinned old PyTorch stack in README.

## Sources

- https://github.com/Dmmm1997/DenseUAV README (splits, layout, license), read 2026-11-06.
- https://huggingface.co/api/datasets/Dmmm997/DenseUAV (file size, license tag, gated flag).
