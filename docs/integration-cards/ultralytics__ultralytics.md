# Ultralytics YOLO - integration card
<!-- about: repo:ultralytics/ultralytics -->
One-line: the fastest way to get a trained detector, segmenter or tracker running on a camera feed (`yolo predict`, `model.track`, export to ONNX/TensorRT). Read the licence section before you build a team deliverable on it.

| | |
|---|---|
| Install | `pip install ultralytics` (PyPI `ultralytics` 8.4.203, `requires_python >=3.8`, checked 2026-11-06). Pulls `torch`, `torchvision`, `opencv-python`, `polars` and more (pyproject `dependencies`). Docker images built from `docker/Dockerfile*`, including `Dockerfile-jetson-jetpack4/5/6`, `Dockerfile-arm64`, `Dockerfile-cpu`. Hub name `ultralytics/ultralytics` (README). Tags such as `latest-jetson-jetpack6` show up in issue #23845; the full tag list was not checked. |
| Runs on | Linux / macOS / Windows, CPU or CUDA GPU, Apple MPS. Jetson through the JetPack Dockerfiles or [jetson-containers](./dusty-nv__jetson-containers.md). Export targets include ONNX, TensorRT, OpenVINO, TFLite, CoreML (`model.export(format=...)`). |
| Inputs | Images, video files, directories, globs, URLs, RTSP/HTTP streams, webcam index (`source=0`), numpy/PIL frames. Training data: YOLO-format txt labels with a dataset YAML (`data="coco8.yaml"`). |
| Outputs | `list[Results]`. Each `Results` has `.boxes` (`Boxes`: `xyxy`, `xywh`, `conf`, `cls`, and `id` when tracking), `.masks`, `.keypoints`, `.obb`, `.probs`. Helpers: `plot()`, `save_txt()`, `summary()`, and DataFrame/CSV/JSON export through `DataExportMixin`. All coordinates are image pixels, so there is no geo output. |
| Key API / entry points | CLI `yolo` and `ultralytics`, both `ultralytics.cfg:entrypoint` (pyproject `[project.scripts]`): `yolo predict model=yolo26n.pt source=...`, `yolo track ...`, `yolo train data=... model=...`, `yolo export model=... format=engine`. Python: `from ultralytics import YOLO`; `YOLO(path)`; `Model.predict(...)`, `Model.track(...)`, `Model.train(...)`, `Model.val(...)`, `Model.export(...)` (`ultralytics/engine/model.py`). Results classes are in `ultralytics/engine/results.py`. |
| Time to first result | Estimate: 10 min to boxes on a test image on a laptop with pip. Fine-tuning on a small drone dataset takes a few hours on one GPU. A TensorRT engine on a Jetson takes 1-2 h with a matching JetPack container. |
| License | **AGPL-3.0** (LICENSE file is GNU AGPL v3). Dual licensed: the README offers an "Ultralytics Enterprise License" for anything that should not follow AGPL. **The pretrained weights** (`yolo26n.pt` etc., auto-downloaded from `ultralytics/assets` releases) are under the same dual licence. The Enterprise licence covers "Ultralytics software and AI models" (README; see [model-weights-licenses](../model-weights-licenses.md)). |

## Licence trap for a defence hackathon

This needs deciding before any code is written, because it decides what the team can hand over.

- AGPL-3.0 is copyleft and applies on network use. If the team ships, deploys or **serves over a network** (a web dashboard counts) software that includes Ultralytics, the **complete source** of that work must be available under AGPL-3.0.
- Ultralytics reads this broadly. In issue #26703 (2026) a user asked whether a YOLO process could be kept separate from a proprietary process that talks to it over sockets. The Ultralytics answer: their guidance "requires open-sourcing the entire project incorporating YOLO, not just Process B; separating A and B through sockets does not by itself exempt A". The same reply says that trained weights, training scripts and configs must also be published. It also says a dataset the provider forbids redistributing does not by itself have to be disclosed. That is the vendor's position, not legal advice, and a court might draw the line elsewhere. Plan for the vendor's position.
- Fine-tuned weights started from `yolo26n.pt` are derived from AGPL weights. Training from scratch with the Ultralytics code is still Ultralytics code.
- Hackathon terms often assign IP to the sponsor or ask for a closed deliverable. A defence sponsor will usually not accept AGPL obligations, and you cannot grant rights you do not hold. Your options are:
  1. Build openly under AGPL-3.0 and say so up front (fine for a public demo).
  2. Get an Enterprise licence. That is a commercial negotiation with Ultralytics, and the price is not stated in the repo.
  3. Use a permissive detector from the start: RF-DETR (`pip install rfdetr`, Apache-2.0 for the code and the Nano/Small/Medium/Large detection weights, while the `rfdetr[plus]` models use PML 1.0, per the rf-detr README), RT-DETR from `lyuwenyu/RT-DETR` (Apache-2.0, GitHub metadata), YOLOX (Apache-2.0, GitHub metadata), or [jetson-inference](./dusty-nv__jetson-inference.md) SSD-Mobilenet (MIT code, check the weights). None of these are in the index except jetson-inference, and their weights licences were not checked beyond the READMEs.
- Note that the RT-DETR port *inside* Ultralytics is AGPL. The licence follows the code you import, not the paper.
- [BoxMOT](./mikel-brostrom__boxmot.md) is AGPL-3.0 too, so swapping only the tracker does not remove the obligation.

## Minimal usage

Not run. Taken from the README, adapted to track small objects in a video and dump the tracks as CSV rows for a downstream filter.

```bash
pip install ultralytics
yolo predict model=yolo26n.pt source='https://ultralytics.com/images/bus.jpg'
```

```python
from ultralytics import YOLO

model = YOLO("yolo26n.pt")            # COCO classes; fine-tune for drones, COCO has no "drone" class
for r in model.track(source="clip.mp4", stream=True, persist=True, conf=0.25):
    if r.boxes.id is None:
        continue
    for (x1, y1, x2, y2), tid, c in zip(r.boxes.xyxy.tolist(), r.boxes.id.int().tolist(), r.boxes.conf.tolist()):
        print(f"{tid},{x1:.0f},{y1:.0f},{x2:.0f},{y2:.0f},{c:.2f}")
```

Export for the edge: `yolo export model=best.pt format=engine half=True` (build the engine on the target device).

## Wiring it into a nav stack

- C-UAS situational awareness: run detection on EO/IR video => pixel tracks => bearing from the camera intrinsics and the gimbal/vehicle attitude => fuse with RF or radar cues in [Stone Soup](./dstl__stone-soup.md) => push to TAK as CoT (see [samples/cuas-classifiers](../../samples/cuas-classifiers/) and [samples/mavlink-to-tak-cot](../../samples/mavlink-to-tak-cot/)). Ultralytics only gives you the pixel part.
- Training data: [Anti-UAV dataset card](../dataset-cards/anti-uav.md) (RGB + IR drone video, with a converter to COCO/YOLO in the UAV detection benchmark repo) and Drone-vs-Bird ([catalog](../../catalog/repos/wosdetc__challenge.md)).
- Tracker choice: built-in `model.track` takes a tracker YAML from `ultralytics/cfg/trackers/` (`botsort`, `bytetrack`, `ocsort`, `deepocsort`, `fasttrack`, `tracktrack`). For more trackers or ReID see [BoxMOT](./mikel-brostrom__boxmot.md). For multi-sensor tracking, hand detections to Stone Soup instead.
- Edge: export to TensorRT and run it in a [jetson-containers](./dusty-nv__jetson-containers.md) image. Publish to ROS as `vision_msgs/Detection2DArray` from your own node, because Ultralytics has no ROS node.
- Visual-nav use: segmentation masks can drop dynamic objects before feature matching ([LightGlue card](./cvg__lightglue.md)).

Catalog page: [catalog/repos/ultralytics__ultralytics.md](../../catalog/repos/ultralytics__ultralytics.md). Concepts: [counter-uas](../../catalog/concepts/counter-uas.md), [edge-ai](../../catalog/concepts/edge-ai.md), [target-tracking](../../catalog/concepts/target-tracking.md).

## Gotchas

- Licence: see above. Two open issues in 2026 (#26703, #26807) are users asking what AGPL requires, so the question comes up often.
- COCO weights have no drone class, and tiny targets (the Drone-vs-Bird mean object is about 34x23 px, per the [dataset card](../dataset-cards/anti-uav.md)) need fine-tuning plus a larger `imgsz` or tiling.
- Jetson TensorRT export: #26655 (JetPack 6 / TRT 10.3, INT8 export with `nms=True` fails, closed), #24607 (TRT 8.2 cannot parse the YOLO26 ONNX at opset 11, closed), #23845 (TRT export errors inside the `latest-jetson-jetpack6` container, closed), #25030 (YOLO26n latency on AGX Orin well above the published benchmark, closed). Build the engine on the device that will run it and pin the JetPack.
- Weights download on first use from GitHub releases. Pre-stage `.pt` files for an offline or air-gapped venue. #22273 reported that training "from scratch" still downloaded `yolo11n.pt` (closed).
- The package is heavy (torch + opencv) and pins some numpy versions on macOS (pyproject).
- Fast release cadence (8.4.x). Pin the version for reproducibility.

## Alternatives

- [jetson-inference](./dusty-nv__jetson-inference.md) - MIT code, native TensorRT on Jetson, ROS nodes. Prefer it when the licence must be permissive and SSD-class accuracy is enough.
- RF-DETR / RT-DETR / YOLOX (not indexed) - Apache-2.0 detectors. Prefer them for a closed deliverable.
- [ByteTrack](../../catalog/repos/foundationvision__bytetrack.md) - MIT tracker to pair with a permissive detector.

Sources: `gh api repos/ultralytics/ultralytics` (license AGPL-3.0, default branch main), LICENSE, README.md (install, usage, models, License section), pyproject.toml (`dependencies`, `[project.scripts]`), `docker/` listing, `ultralytics/engine/model.py` and `ultralytics/engine/results.py` (method and class names), PyPI JSON for `ultralytics`, issues #26703 (with maintainer comment), #26807, #26655, #24607, #23845, #25030, #22273. rf-detr README (licence lines), GitHub metadata for lyuwenyu/RT-DETR, Megvii-BaseDetection/YOLOX, FoundationVision/ByteTrack.
