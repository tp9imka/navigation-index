# SUES-200

<!-- about: repo:reza-zhu/sues-200-benchmark, res:sues-200-benchmark-2022 -->

Drone-to-satellite cross-view matching benchmark with real drone imagery at four flight
heights over 200 scenes. Zhu et al., arXiv 2204.10704 (2022).

| Field | Value |
|---|---|
| Platform | Real drone (model not stated in README) |
| Environment | 200 scenes of mixed types (paper: "multi-scene"); location and scene list not checked here |
| Sensors and rates | RGB stills at 150, 200, 250, 300 m; 24,120 drone images total (paper abstract) plus one satellite image per scene |
| Ground truth | Scene ID pairing drone and satellite views (retrieval labels). No per-image pose or GPS published |
| Size | Google Drive reports `SUES-200-512x512-V2.zip (5.3G)` (checked 2026-11-06) |
| License | Repo code MIT; README says the dataset is for academic research only |
| Format | `drone_view_512/<scene>/<height>/*.jpg`, `satellite-view/<scene>/0.png`, 512x512 |
| Index | [SUES-200 repo](../../catalog/repos/reza-zhu__sues-200-benchmark.md), [paper](../../catalog/resources/sues-200-benchmark-2022.md) |

## What's in it

- 50 drone images per scene per height (24,120 / 200 / 4, consistent with paper count).
- Train/test split by scene; evaluation per height so you can show how altitude changes recall.

## Download

```bash
VENV=.venv; uv venv "$VENV"; uv pip install --python "$VENV/bin/python" gdown
"$VENV/bin/gdown" 1UyVyFJ_pRaJHIr_eBY2HL7gkS5y9UxqI -O SUES-200-512x512-V2.zip
# mirrors: Baidu https://pan.baidu.com/s/1mrd-7ADm57_OchAvO1XmNw (code p836)
#          Tianyi https://cloud.189.cn/t/yMnaEnR322Yj (code veh7)
git clone https://github.com/Reza-Zhu/SUES-200-Benchmark.git
python SUES-200-Benchmark/script/split_datasets.py --path /path/to/SUES-200-512x512
```

## Loading and tooling

`split_datasets.py` symlinks the raw archive into `Training/<height>/{drone,satellite}/<scene>/`
and `Testing/<height>/...` ImageFolder trees. Same retrieval baselines as University-1652
apply ([Sample4Geo](../../catalog/repos/skyy93__sample4geo.md)).

## Hackathon fit

- Idea 18 / 20 retrieval stage when the demo needs to show altitude robustness: train or
  test at 150 m, evaluate at 300 m.
- Small enough (5.3 GB) to carry on a laptop.

## Pitfalls

- Retrieval labels only; no meters-of-error metric possible.
- Fixed 512x512 crops; satellite is one image per scene, so the gallery is small (easy).
- V2 archive name differs from older papers' "SUES-200" splits; report which you used.

## Sources

- https://github.com/Reza-Zhu/SUES-200-Benchmark README, read 2026-11-06.
- arXiv 2204.10704 abstract (24,120 images, four heights).
- Google Drive download page for the file id (name and size), 2026-11-06.
