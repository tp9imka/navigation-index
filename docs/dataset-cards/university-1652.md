# University-1652

<!-- about: repo:layumi/university1652-baseline, res:university-1652-benchmark-2020, repo:skyy93/sample4geo, repo:wtyhub/lpn -->

Drone / satellite / ground cross-view geo-localization benchmark over 1,652 university
buildings worldwide. Zheng et al., ACM MM 2020 (arXiv 2002.12186). The reference benchmark
most drone-to-satellite retrieval papers report on.

| Field | Value |
|---|---|
| Platform | Synthetic drone views (paper abstract: "synthetic drones", rendered from 3D Earth models while orbiting each building), satellite tiles, ground photos |
| Environment | 72 universities (33 train, 39 test, no overlap), building-centric scenes |
| Sensors and rates | RGB images only; drone views are orbit renders, not flight video. No IMU, no poses |
| Ground truth | Building ID (class label) per image, so the task is retrieval, not metric localization. Building lat/lon available as a separate KML (README "Latitude and Longitude" link) |
| Size | Not verified (link is emailed on request) |
| License | Code MIT. Data: request email states research-only use, no third-party sharing, no profit (Request.md) |
| Format | ImageFolder trees: `train/{drone,street,satellite,google}/<id>/`, `test/{query,gallery}_{drone,satellite,street}/` |
| Index | [Baseline repo](../../catalog/repos/layumi__university1652-baseline.md), [paper](../../catalog/resources/university-1652-benchmark-2020.md), [Sample4Geo](../../catalog/repos/skyy93__sample4geo.md), [LPN](../../catalog/repos/wtyhub__lpn.md) |

## What's in it

| Split | Images | Buildings |
|---|---|---|
| Train | 50,218 | 701 |
| Query drone / satellite / ground | 37,855 / 701 / 2,579 | 701 |
| Gallery drone / satellite / ground | 51,355 / 951 / 2,921 | 951 / 951 / 793 |

Two tasks: drone => satellite (target localization) and satellite => drone ("drone navigation").

## Download

```bash
# 1. Email zdzheng12@gmail.com from an academic address with the template in
#    https://github.com/layumi/University1652-Baseline/blob/master/Request.md
#    (README claims a reply within minutes; not tested)
# 2. Baseline code and pretrained model
git clone https://github.com/layumi/University1652-Baseline.git
```

## Loading and tooling

Torchvision `ImageFolder` works directly on the split folders. The baseline
`train.py`/`test.py` report Recall@K and AP. Stronger retrieval baselines with checkpoints:
[Sample4Geo](../../catalog/repos/skyy93__sample4geo.md), [LPN](../../catalog/repos/wtyhub__lpn.md).

```python
from torchvision.datasets import ImageFolder
q = ImageFolder("University-1652/test/query_drone")
g = ImageFolder("University-1652/test/gallery_satellite")
```

## Hackathon fit

- Pretraining or sanity-checking the retrieval stage of idea 18 / 20 (which satellite tile
  am I over?). Use a pretrained Sample4Geo checkpoint rather than training in 48 h.
- Not suitable as the headline demo: no metric GT, synthetic drone views, no trajectories.

## Pitfalls

- Results reported as Recall@1 on building IDs do not translate into meters of error;
  judges asking "how many meters" need a different dataset (UAV-VisLoc, AnyVisLoc, VPAIR).
- Access depends on a human answering email; request a week ahead.
- Domain gap: synthetic renders vs real drone frames.

## Sources

- https://github.com/layumi/University1652-Baseline README and Request.md, read 2026-11-06.
- arXiv 2002.12186 abstract (synthetic drones, 1,652 buildings).
