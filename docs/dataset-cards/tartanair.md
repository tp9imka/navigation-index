# TartanAir (v1 and v2)

<!-- about: res:cmu-tartanair-dataset, repo:castacks/tartanairpy -->

Synthetic SLAM dataset rendered in Unreal Engine / AirSim by CMU AirLab. v1 (Wang et al., IROS 2020) is stereo + depth + flow + pose over 30 environments; v2 adds a six-camera rig, lidar, IMU with a noise model, event cameras and customizable lenses, managed by the `tartanair` Python package. Perfect ground truth, hard motion and lighting.

| Field | Value |
|---|---|
| Platform | Simulated free-flying camera rig |
| Environment | v1: 30 photo-realistic UE scenes (indoor, outdoor, urban, nature, underwater-style); v2: more worlds incl. caves, mountains, the Moon (site text, no count stated) |
| Sensors and rates | v1: stereo RGB, depth, segmentation, optical flow, poses, simulated IMU and lidar as derived labels. v2: cameras lcam/rcam front/back/left/right/top/bottom, lidar, IMU with noise model, event camera, depth, seg, flow, occupancy. Frame rate not stated on the pages read |
| Ground truth | Exact simulator poses |
| Size | v1: 1106.75 GB total over 288 zip files; left RGB only 140.9 GB; smallest left-RGB zip japanesealley/Hard/image_left.zip 1.06 GB (sizes from `download_training_zipfiles.txt` in tartanair_tools). HF mirror theairlabcmu/tartanair usedStorage 1,106,753,562,291 bytes. v2: HF theairlabcmu/tartanair2 usedStorage 54.3 TB (HF API, 2026-11-06) |
| License | Site: CC BY 4.0 (v1 and v2 data), toolkit MIT. Hugging Face cards say bsd-3-clause; conflict unresolved, cite the site |
| Format | v1: zip per env/difficulty/modality; PNG images, NPY depth/flow/seg, pose_left.txt. v2: per-env zips via tartanairpy |
| Index | [TartanAir](../../catalog/resources/cmu-tartanair-dataset.md), [tartanairpy](../../catalog/repos/castacks__tartanairpy.md) |

## What's in it

- v1: each environment has Easy and Hard motion levels, trajectories P000..P0xx, left/right cameras. CVPR 2020 SLAM challenge test sets (mono 7.65 GB, stereo 17.51 GB on Google Drive, per tartanair_tools README).
- v2: same idea with many more modalities and a programmable "customization" step (re-render new lens models from cube maps locally).

## Download

```bash
# v1, one environment left RGB (smallest zip ~1.06 GB); tartanair_tools script, AirLab server by default
git clone https://github.com/castacks/tartanair_tools && cd tartanair_tools
pip install boto3 colorama          # inside a venv
python download_training.py --output-dir ./ta1 --rgb --only-left --only-hard --unzip
#   add --huggingface to use the HF mirror instead
# v2 via the package (venv)
pip install tartanair
python - <<'EOF'
import tartanair as ta
ta.init('./ta2')
ta.download(env=['Prison'], difficulty=['easy'], modality=['image','imu'],
            camera_name=['lcam_front'], unzip=True)
EOF
```

v1 script options select modality, difficulty and camera; it downloads every environment that matches, so filter the URL list (`download_training_zipfiles.txt`) by hand for a single env. `Prison` is from the repo's download example; list all names with `ta.list_envs()` (see `examples/list_example.py`).

## Loading and tooling

- [tartanairpy](../../catalog/repos/castacks__tartanairpy.md): download, iterate, dataloader, evaluator, customization examples in `examples/`.
- [DPVO](../../catalog/repos/princeton-vl__dpvo.md) ships `evaluate_tartan.py` and a TartanAir data reader; [DROID-SLAM](../../catalog/repos/princeton-vl__droid-slam.md) was trained on TartanAir (per its paper; eval script not checked).
- [evo](../../catalog/repos/michaelgrupp__evo.md) after converting pose_left.txt (NED camera frame per tartanair_tools data_type.md) to TUM with timestamps.

## Hackathon fit

- Idea 10 / 18: train or fine-tune learned VO, or test a pipeline under fog, night and motion blur where real data has no truth.
- Idea 20 (real-time visual geolocalization on Jetson): synthetic pre-training data only; no georeference.
- Fast sanity check of a depth or flow network before field data.

## Pitfalls

- Sizes: take one environment, one camera, one modality first. v2 total is tens of TB.
- Pose frame is NED camera convention in v1; convert before comparing with ENU or ROS conventions.
- Synthetic: sim-to-real gap for any learned component.
- License mismatch between site (CC BY 4.0) and HF card (BSD-3-Clause).

## Sources

- https://theairlab.org/tartanair-dataset/ (v1 modalities, 30 envs, CC BY 4.0)
- https://tartanair.org/ (v2 modalities, CC BY 4.0, toolkit MIT, `pip install tartanair`)
- `gh api repos/castacks/tartanair_tools/readme` and `download_training_zipfiles.txt` (v1 sizes, script flags, 3 TB note)
- `gh api repos/castacks/tartanairpy/contents/examples/download_example.py` (v2 download API, camera names)
- HF API datasets/theairlabcmu/tartanair and tartanair2 (usedStorage, card license)
