# Anti-UAV - integration card
<!-- about: repo:zhaoj9014/anti-uav -->
One-line: benchmark repo for defensive drone detection and tracking in RGB and thermal IR video. Use it for the dataset links, the per-frame `exist` + `gt_rect` label format, the state-accuracy evaluator and a SiamFC baseline. Treat the code as research baselines, not a library.

| | |
|---|---|
| Install | No package. `git clone https://github.com/ZhaoJ9014/Anti-UAV`. The README points environment setup at the ModelScope model `iic/3rd_Anti-UAV_CVPR23` and recommends `python == 3.8`, CUDA 11.8 for RTX 30/40, `pip install -r requirements/cv.txt` (some packages fail and "can be ignored"), plus `jpeg4py` (written "jibjpeg4py" in the README) and `jittor == 1.3.8.5`. `Codes/readme.txt` lists PyTorch 1.7.1 / torchvision 0.8.2 for the older detect+track demo. |
| Runs on | Linux + NVIDIA GPU (implied by the CUDA notes). Jittor (Tsinghua framework) for the `anti_uav_jittor/` code, PyTorch for `Codes/` and `Eval/`. Not tested on Jetson or macOS by the README. |
| Inputs | Video sequences, each a folder with `IR.mp4` and/or `RGB.mp4` plus `IR_label.json` / `RGB_label.json` (`Eval/test.py`). Labels: `gt_rect` (per-frame box `[x, y, w, h]`) and `exist` (per-frame 0/1 visibility). Datasets: Anti-UAV300 (RGB + IR), Anti-UAV410 and Anti-UAV600 (IR only). |
| Outputs | Per-video tracker result txt files under `results/<tracker>/` and the challenge "state accuracy". That is mean per-frame IoU, where a frame with no target scores 1 if the tracker correctly predicts an empty box (`Eval/test.py` `eval()` / `not_exist()`). |
| Key API / entry points | `Eval/test.py` (`main(mode='IR')`, SiamFC baseline `TrackerSiamFC(net_path='model.pth')` with weights in the repo, `eval(out_res, label_res)`, `iou()`), `Codes/detect_tracking.py` and `Codes/demo_detect_track.py` (detector + tracker demo), `anti_uav_jittor/ltr/run_training.py`, `anti_uav_jittor/pysot_toolkit/test.py` (inference per the README), `anti_uav_jittor/demo.ipynb`. |
| Time to first result | Estimate: 1-2 h to run `Eval/test.py` on a few Anti-UAV300 test sequences, assuming the Google Drive download works and an old PyTorch is available. Half a day or more for the Jittor pipeline, going by the README's own install caveats. |
| License | Code: **MIT** (LICENSE, "Copyright (c) 2020 Zhao Jian"). **Data: no licence stated** in the README for Anti-UAV300/410. Anti-UAV600 on ModelScope is labelled "other" (see the [dataset card](../dataset-cards/anti-uav.md)). Treat the data as research-use with citation until terms are confirmed. In-repo baseline weights (`Eval/model.pth`) have no separate licence. |

## Minimal usage

Not run. Score a tracker against Anti-UAV labels with the repo's evaluator logic. The format comes from `Eval/test.py`.

```python
import json
# per-sequence label file from Anti-UAV300 test-dev
lab = json.load(open("dataset/test-dev/<seq>/IR_label.json"))
gt, exist = lab["gt_rect"], lab["exist"]          # [x,y,w,h] per frame, 0/1 per frame

def iou(a, b):
    ax2, ay2, bx2, by2 = a[0]+a[2], a[1]+a[3], b[0]+b[2], b[1]+b[3]
    iw, ih = max(0, min(ax2, bx2)-max(a[0], b[0])), max(0, min(ay2, by2)-max(a[1], b[1]))
    inter = iw*ih; union = a[2]*a[3] + b[2]*b[3] - inter
    return inter/union if union > 0 else 0.0

pred = my_tracker(f"dataset/test-dev/<seq>/IR.mp4")  # list of [x,y,w,h] or [] when no target
acc = sum((1.0 if not p else 0.0) if not e else (iou(p, g) if p else 0.0)
          for p, g, e in zip(pred, gt, exist)) / len(gt)
print("state accuracy", acc)
```

Repo baseline: `cd Eval && python test.py` (expects `dataset/test-dev/*` next to it).

## Wiring it into a nav stack

- Training and evaluation data for the camera leg of a defensive C-UAS demo. Fine-tune a detector ([Ultralytics](./ultralytics__ultralytics.md) for an AGPL-OK stack, or a permissive one), track with [BoxMOT](./mikel-brostrom__boxmot.md) or [ByteTrack](../../catalog/repos/foundationvision__bytetrack.md), then score with the `exist`-aware metric above. It rewards saying "no drone" correctly, which plain mAP does not.
- Convert to COCO/YOLO with the UAV detection and tracking benchmark repo described in the [dataset card](../dataset-cards/anti-uav.md).
- Thermal IR sequences are the useful part for night or low-contrast detection. Pair them with RF detection ([samples/cuas-classifiers](../../samples/cuas-classifiers/)) and fuse tracks in [Stone Soup](./dstl__stone-soup.md).
- This is detection and tracking for awareness only. Pixel tracks leave the camera as bearings or CoT, not as guidance.

Catalog page: [catalog/repos/zhaoj9014__anti-uav.md](../../catalog/repos/zhaoj9014__anti-uav.md). Dataset card: [anti-uav](../dataset-cards/anti-uav.md). Concepts: [counter-uas](../../catalog/concepts/counter-uas.md), [datasets-benchmarks](../../catalog/concepts/datasets-benchmarks.md).

## Gotchas

- Downloads: Anti-UAV300 is on Google Drive and Baidu, 410 on Baidu only (password in the README), 600 on ModelScope. Issue #8 (open) asks for a working Google Drive link for an older version. Baidu often needs an account and a client. Fetch before the event.
- Environment rot: Python 3.8, PyTorch 1.7.1, and a pinned Jittor. The README admits training in Jittor has problems, and its FAQ patches a numpy "inhomogeneous shape" error by hand. Use a container rather than fixing this on the host.
- Evaluator quirk: `Eval/test.py` `not_exist(pred)` returns `len(pred) == 1 and pred == 0`. For a Python list (`[0]`) the comparison with `0` is always False, so the repo evaluator scores correct "no target" predictions as 0 unless `pred` is a numpy array. Also, `iou()` crashes on an empty prediction when the target exists. This was found by reading the code, not by running it. Use your own scorer (like the one above) and state which one produced your numbers.
- RGB and IR in Anti-UAV300 are not pixel-aligned (dataset card). Do not reuse boxes across modalities.
- Data licence not stated (above). Do not redistribute the data inside your deliverable.
- The repo is a benchmark hub. Last push 2025-05-07 (GitHub metadata), with 34 issues in total.

## Alternatives

- Drone-vs-Bird ([catalog](../../catalog/repos/wosdetc__challenge.md)) - RGB, long range, birds as distractors. Prefer it for EO-only, false-alarm-heavy scenarios.
- [UAV detection and tracking benchmark](../../catalog/repos/kostadinovshalon__uavdetectiontrackingbenchmark.md) - unified COCO conversion of MAV-VID, Drone-vs-Bird and Anti-UAV with detector baselines.
- [NRC C-UAS sensing dataset](../../catalog/repos/nrc-cnrc__cuas-sensing-dataset.md) - radar tracks instead of video.

Sources: `gh api repos/zhaoj9014/anti-uav` (MIT, pushed 2025-05-07, default branch master), LICENSE, README.md (environment, data, metrics, training/inference, FAQ), `Codes/readme.txt`, `Eval/test.py`, repo and `anti_uav_jittor/` listings, issue #8, docs/dataset-cards/anti-uav.md.
