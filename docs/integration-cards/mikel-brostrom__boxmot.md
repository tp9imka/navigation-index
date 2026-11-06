# BoxMOT - integration card
<!-- about: repo:mikel-brostrom/boxmot -->
One-line: drop-in multi-object trackers (ByteTrack, BoT-SORT, OC-SORT, StrongSORT, DeepOCSORT, OccluBoost and others) that take any detector's `[x1,y1,x2,y2,conf,cls]` array and return track IDs. Includes OBB and 2D/3D tracking. AGPL-3.0.

| | |
|---|---|
| Install | `pip install boxmot` (PyPI `boxmot` 26.0.0, `requires_python >=3.10,<3.14`, checked 2026-11-06). Extras named in the README: `yolo`, `service`, `evolve`, `research`, `onnx`, `openvino`, `tflite` (details in docs/getting-started/installation.md, not read). Hard dependencies include `torch`, `torchvision`, `timm`, `opencv-python==4.11.0.86` (exact pin), `filterpy<2`, `gdown`, `huggingface-hub`, `pyarrow` (pyproject). |
| Runs on | Python 3.10-3.13, CPU or CUDA. An optional native C++ tracker backend (`--tracker-backend cpp`, also embeddable through CMake per the README) was not checked. |
| Inputs | `tracker.update(dets, frame)`: `dets` is an `N x 6` numpy array `[x1, y1, x2, y2, conf, cls]` in pixels, `frame` is a BGR `uint8` image (used by appearance and camera-motion trackers). OBB mode takes `[cx, cy, w, h, angle_rad, conf, cls]`. `EagerMot` also takes 3D boxes, a camera projection matrix and `camera_to_world` (README). |
| Outputs | Numpy array of active tracks. The README reads track IDs from column 4 (AABB) or column 5 (OBB). Other columns were not checked against source. CLI writes videos and MOT-format results. |
| Key API / entry points | CLI `boxmot` (`boxmot.engine.cli:main`) with subcommands `track`, `eval`, `tune`, `export`, `train-reid` and more (README), and CLI `boxmot-service` (`boxmot.engine.service.__main__:main`). Python: `from boxmot import ByteTrack, BotSort, OcSort, DeepOcSort, StrongSort, HybridSort, BoostTrack, OccluBoost, EagerMot` (lazy exports in `boxmot/__init__.py`), `create_tracker(spec, *, config=None, kalman=None, reid=None, ...)` (`boxmot/trackers/common/factory.py`), `ReIDConfig`, `KalmanConfig`. |
| Time to first result | Estimate: 15 min to IDs on a webcam with `boxmot track --detector yolo26n ...` after pip install, assuming the detector and ReID weights download. 30 min to wrap your own detector's output in `tracker.update`. |
| License | **AGPL-3.0** (LICENSE file is GNU AGPL v3; pyproject `license = "AGPL-3.0"`). Same network-use copyleft as [Ultralytics](./ultralytics__ultralytics.md). The default detector in the README example (`yolo26n`) is Ultralytics, which is AGPL as well. ReID weights carry dataset terms: see Gotchas. |

## Minimal usage

Not run. From the README "Minimal Usage", wired to an arbitrary detector.

```bash
pip install boxmot
boxmot track --detector yolo26n --reid lmbn_n_duke --tracker occluboost --source 0 --save --show
```

```python
import numpy as np
from boxmot import ByteTrack     # motion-only, no ReID weights needed

tracker = ByteTrack()
for frame, dets in my_detector_stream():          # dets: N x [x1,y1,x2,y2,conf,cls]
    tracks = tracker.update(np.asarray(dets, dtype=float), frame)
    for t in tracks:
        print(int(t[4]), t[:4])                    # README: column 4 is the track id
```

## Wiring it into a nav stack

- Sits between any detector ([Ultralytics](./ultralytics__ultralytics.md), [jetson-inference](./dusty-nv__jetson-inference.md), RF-DETR) and the situational-awareness layer. Pixel tracks plus camera pose give bearings, which go to [Stone Soup](./dstl__stone-soup.md) for multi-sensor fusion or straight to TAK as CoT ([samples/cuas-classifiers](../../samples/cuas-classifiers/)).
- Stable IDs are what make a C-UAS demo readable: one ID per drone across frames, so the operator view can show a track history rather than flickering boxes.
- `EagerMot` with `camera_to_world` per frame (README) is the hook for using the vehicle's own nav solution to keep 3D tracks in a world frame. That works only if your pose is good.
- Evaluation: `boxmot eval` runs MOT-style metrics (HOTA, MOTA, IDF1 per the README tables) on MOT17 and others. Data for drones: [Anti-UAV dataset card](../dataset-cards/anti-uav.md).

Catalog page: [catalog/repos/mikel-brostrom__boxmot.md](../../catalog/repos/mikel-brostrom__boxmot.md). Concepts: [target-tracking](../../catalog/concepts/target-tracking.md), [counter-uas](../../catalog/concepts/counter-uas.md).

## Gotchas

- AGPL-3.0. Replacing an AGPL detector with a permissive one does not help if BoxMOT stays in the stack. For a closed deliverable use [ByteTrack](../../catalog/repos/foundationvision__bytetrack.md) (MIT) directly.
- ReID weights: `boxmot/reid/core/catalog.py` downloads checkpoints from Google Drive via `gdown`, trained on **person** re-identification sets (Market1501, DukeMTMC-reID, MSMT17, named in the file). They do nothing useful for drones, and those datasets carry their own research-only terms. DukeMTMC was withdrawn by its authors. For small aerial targets use motion-only trackers (ByteTrack, OC-SORT) and skip ReID. Google Drive downloads also fail behind restrictive proxies and in offline venues.
- `opencv-python==4.11.0.86` is an exact pin (pyproject says it keeps benchmark preprocessing stable). It can clash with a Jetson OpenCV build with CUDA or with Ultralytics' own OpenCV requirement. Use a separate venv.
- The API changed a lot over versions: v26 adds new tracker classes and `create_tracker(spec, ...)`. Old blog snippets that pass `model_weights=`/`device=` positional arguments may not match. Pin `boxmot==26.0.0`.
- Jetson/TensorRT: #1597 (TensorRT install confusion, closed), #1748 (TensorRT 10 support request, closed), #2290 (DeepStream request, closed). Expect to export ReID models yourself.
- #2332: `ModuleNotFoundError` on ReID model instantiation (closed). #1667: install failing on Python >= 3.10 because of filterpy (closed, now pinned `filterpy<2`).

## Alternatives

- [ByteTrack](../../catalog/repos/foundationvision__bytetrack.md) - MIT, one tracker, fewer dependencies. Prefer it for a permissive stack.
- [Stone Soup](./dstl__stone-soup.md) - MIT, model-based multi-target tracking (JPDA, GM-PHD) in world coordinates with radar/RF fusion. Prefer it when tracks come from several sensors.
- Ultralytics built-in `model.track` - fewer moving parts if you already accept Ultralytics AGPL.

Sources: `gh api repos/mikel-brostrom/boxmot` (AGPL-3.0, default branch master), LICENSE, README.md (install, minimal usage, tracker table), pyproject.toml (`[project]`, dependencies, `[project.scripts]`), `boxmot/__init__.py`, `boxmot/trackers/common/factory.py`, `boxmot/reid/core/catalog.py`, PyPI JSON for `boxmot`, issues #2290, #1748, #1597, #2332, #1667.
