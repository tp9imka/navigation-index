# Anti-UAV (plus Drone-vs-Bird and MAV-VID)

<!-- about: repo:zhaoj9014/anti-uav, res:anti-uav-benchmark-paper, repo:kostadinovshalon/uavdetectiontrackingbenchmark, repo:ultralytics/ultralytics, repo:mikel-brostrom/boxmot -->

Video benchmarks for detecting and tracking small drones from the ground (defensive C-UAS
situational awareness). Anti-UAV is the main RGB + thermal IR set (arXiv 2101.08466;
CVPR/ICCV workshop challenges 2020-2025). Drone-vs-Bird and MAV-VID are the two
RGB sets that the indexed UAV Detection and Tracking Benchmark converts into one COCO format.

| Dataset | Sensors | Annotations | Size | Access / license |
|---|---|---|---|---|
| Anti-UAV300 | Paired RGB + thermal IR video, Full HD RGB (README), unaligned | Per-frame boxes + "target exists" flag, attributes | `Anti-UAV-RGBT.zip`, Google Drive reports 5.6 GB (2026-11-06) | Google Drive / Baidu; repo MIT, data terms not stated |
| Anti-UAV410 | Thermal IR only | Same scheme | Not verified (Baidu only) | Baidu (password wfds) |
| Anti-UAV600 (3rd challenge, CVPR 2023) | Thermal IR only | COCO-style boxes (ModelScope card) | Not verified; index CSVs on ModelScope reference images stored elsewhere | ModelScope, license "other" |
| Drone-vs-Bird (WOSDETC / AVSS) | RGB video, long range, birds as distractors | Per-frame boxes, custom txt | Not verified | Videos on request; annotations on GitHub |
| MAV-VID | RGB video from other drones, ground cameras, handhelds | YOLO txt | Not verified | Bitbucket (Kaggle page reported dead by the benchmark repo) |

Statistics from the UAV Detection and Tracking Benchmark README:

| Dataset | Train | Val | Mean object size |
|---|---|---|---|
| MAV-VID | 53 videos, 29,500 images | 11 videos, 10,732 images | 215x128 px (3.28% of image) |
| Drone-vs-Bird | 61 videos, 85,904 images | 16 videos, 18,856 images | 34x23 px (0.10%) |
| Anti-UAV (v1) | 60 videos, 149,478 images | 40 videos, 37,016 images | RGB 125x59 px, IR 52x29 px |

Anti-UAV paper abstract: more than 300 video pairs and over 580k annotated boxes. GT is
manual boxes. Recordings cover 6 UAV models under different lighting and backgrounds
(benchmark README); the camera platform is not described on the pages checked.

## Download

```bash
git clone https://github.com/ZhaoJ9014/Anti-UAV.git
VENV=.venv; uv venv "$VENV"; uv pip install --python "$VENV/bin/python" gdown
"$VENV/bin/gdown" 1NPYaop35ocVTYWHOYQQHn8YHsM9jmLGr -O Anti-UAV-RGBT.zip     # Anti-UAV300, 5.6 GB
# Anti-UAV410: https://pan.baidu.com/s/1PbINXhxc-722NWoO8P2AdQ (password wfds)
# Anti-UAV600 via ModelScope SDK (pip install modelscope in the venv):
#   MsDataset.load('3rd_Anti-UAV', namespace='ly261666', split='train')
git clone https://github.com/KostadinovShalon/UAVDetectionTrackingBenchmark.git  # COCO converters
git clone https://github.com/wosdetc/challenge.git           # Drone-vs-Bird annotations
git clone https://bitbucket.org/alejodosr/mav-vid-dataset.git # MAV-VID (not checked)
```

## Loading and tooling

- `convert_anti_uav_to_coco.py`, `convert_drone_vs_bird_to_coco.py`,
  `convert_mav_vid_to_coco.py`, `video_to_images.py` in the
  [benchmark repo](../../catalog/repos/kostadinovshalon__uavdetectiontrackingbenchmark.md)
  produce COCO JSON for MMDetection / MMTracking (pinned to 2021 versions).
- Faster route in 48 h: COCO => YOLO labels, fine-tune [Ultralytics YOLO](../../catalog/repos/ultralytics__ultralytics.md),
  track with [BoxMOT](../../catalog/repos/mikel-brostrom__boxmot.md); report the Anti-UAV
  accuracy metric (IoU with visibility flag, defined in the Anti-UAV README).

## Hackathon fit

- Idea 1 / 2 style situational-awareness picture: camera detections of drones fused onto a
  map or TAK overlay alongside RF / Remote ID detections.
- Thermal IR at night is the differentiator; Anti-UAV300 is the only set here with RGB and
  IR of the same scenes, at 5.6 GB.

## Pitfalls

- Targets are tiny (Drone-vs-Bird mean 0.10% of the image); default YOLO input sizes miss
  them. Tile or raise input resolution.
- RGB and IR in Anti-UAV300 are not pixel-aligned.
- Anti-UAV410/600 are IR only; mixing versions changes the test set, so state which.
- Drone-vs-Bird needs an emailed request; plan a week.
- Scope: use for detection and tracking (awareness), not for anything that steers an effector.

## Sources

- https://github.com/ZhaoJ9014/Anti-UAV README (versions, links, modalities, metric), 2026-11-06.
- https://github.com/KostadinovShalon/UAVDetectionTrackingBenchmark README (statistics, converters, links).
- ModelScope API for `ly261666/3rd_Anti-UAV` (file list, README, license "other").
- Google Drive download page for the Anti-UAV300 file id (name and size).
- arXiv 2101.08466 abstract.
