<!-- about: repo:cvg/lightglue, repo:magicleap/superpointpretrainednetwork, repo:magicleap/supergluepretrainednetwork, repo:verlab/accelerated_features, repo:zju3dv/loftr, repo:parskatt/roma, repo:naver/mast3r, repo:rmurai0610/mast3r-slam, repo:anyloc/anyloc, repo:amaralibey/mixvpr, repo:serizba/salad, repo:gmberton/eigenplaces, repo:gmberton/cosplace, repo:amaralibey/bag-of-queries, repo:ultralytics/ultralytics, repo:nvidia-isaac/cuvslam, repo:princeton-vl/droid-slam, repo:princeton-vl/dpvo, repo:cvg/hierarchical-localization, repo:cvg/glue-factory, repo:fabio-sim/lightglue-onnx, repo:gmberton/vismatch, repo:gmberton/vpr-methods-evaluation -->

# Model weights licenses: code vs weights vs training data

Learned models in navigation pipelines carry three separate sets of terms:

1. **Code license** - the repo LICENSE file.
2. **Weights license** - often the same, sometimes not (Depth-Anything-V2, DINOv2 sub-models,
   SuperPoint inside LightGlue).
3. **Training-data terms** - datasets such as ScanNet are "non-commercial research" only. Whether
   those terms bind *weights trained on them* is legally unsettled. Some authors pass them on
   explicitly (MASt3R's `CHECKPOINTS_NOTICE`), most say nothing.

This page records what each source actually says. It is engineering triage, not legal advice.
"Read" means the license text or README section was fetched on 2026-11-06 via `gh api` or
WebFetch. "Paper" means the claim comes from the paper as I remember it, not from a document
fetched for this page. Treat those as unverified.

## Verdict key

- **yes** - the stated terms allow it with normal attribution and notice.
- **copyleft** - allowed, but your combined work must ship under the same license (GPL or AGPL)
  with source, including network use for AGPL.
- **check** - the code and weights are permissive, but training-data terms are non-commercial or
  unknown. Fine for research and most hackathons. Get a lawyer's read before a product.
- **no** - the stated terms forbid it.

"Defense" means use by or for a defense customer, which is commercial in most readings. It also
carries export-control duties whatever the license says: see
[export-control-and-ethics.md](export-control-and-ethics.md). The NVIDIA Community License,
for one, has an explicit trade-compliance clause.

## Matrix: local features and matchers

| Model | Code license | Weights license | Training data (terms) | Source read | Research | Hackathon | Commercial | Defense |
|---|---|---|---|---|---|---|---|---|
| SuperPoint (Magic Leap original, also `lightglue/superpoint.py` and its weights) | Magic Leap "Academic or non-profit organization noncommercial research use only" | same | synthetic shapes + MS-COCO (paper) | [SuperPoint LICENSE](https://github.com/magicleap/SuperPointPretrainedNetwork/blob/master/LICENSE), [LightGlue README "License"](https://github.com/cvg/LightGlue#license) | yes (internal, noncommercial) | **no / risky**: see note 1 | no | no |
| SuperGlue | Magic Leap, same terms as SuperPoint | same | ScanNet (indoor), MegaDepth (outdoor) (paper) | [SuperGlue LICENSE](https://github.com/magicleap/SuperGluePretrainedNetwork/blob/master/LICENSE) | yes (internal) | no / risky | no | no |
| SuperPoint "open" (rpautrat, used by glue-factory) | MIT | MIT (glue-factory README: its trained models are Apache-2.0) | own training (not checked) | [rpautrat/SuperPoint](https://github.com/rpautrat/SuperPoint) (GitHub API: MIT), [glue-factory README "License"](https://github.com/cvg/glue-factory#license) | yes | yes | check | check |
| LightGlue + SuperPoint weights (`superpoint_lightglue`) | Apache-2.0 | Apache-2.0 for the LightGlue part | Oxford-Paris 1M distractors + MegaDepth (paper) | [LightGlue README "License"](https://github.com/cvg/LightGlue#license) | yes | no / risky: needs the SuperPoint extractor | no (extractor) | no (extractor) |
| LightGlue + DISK weights | Apache-2.0 | Apache-2.0 ("DISK follows this license as well") | as above; DISK on MegaDepth (CC BY 4.0, images keep Flickr licenses) | [LightGlue README](https://github.com/cvg/LightGlue#license), [MegaDepth page](https://www.cs.cornell.edu/projects/megadepth/) | yes | yes | check (Flickr image licenses in MegaDepth) | check |
| LightGlue + ALIKED weights | Apache-2.0 | Apache-2.0 (matcher), BSD-3-Clause (ALIKED) | MegaDepth (paper; ALIKED training code is not published) | [LightGlue README](https://github.com/cvg/LightGlue#license), [ALIKED repo](https://github.com/Shiaoming/ALIKED) (GitHub API: BSD-3-Clause) | yes | yes | check | check |
| LightGlue + SIFT weights (`sift_lightglue`) | Apache-2.0 | Apache-2.0 | as above | [LightGlue README](https://github.com/cvg/LightGlue#license) | yes | yes | check (matcher training data only) | check |
| DISK (extractor) | Apache-2.0 | Apache-2.0 | MegaDepth-derived set (~164 GB, README) | [cvlab-epfl/disk](https://github.com/cvlab-epfl/disk) (GitHub API: Apache-2.0) | yes | yes | check | check |
| ALIKED (extractor) | BSD-3-Clause | BSD-3-Clause (weights in `models/` of the repo) | MegaDepth (paper) | [Shiaoming/ALIKED](https://github.com/Shiaoming/ALIKED) | yes | yes | check | check |
| SIFT (OpenCV) | Apache-2.0 (OpenCV 4.5+) | n/a, not learned | none | [opencv/opencv](https://github.com/opencv/opencv) (GitHub API: Apache-2.0). US patent 6,711,293 expired in March 2020 (from memory, not re-checked) | yes | yes | yes | yes |
| XFeat | Apache-2.0 | Apache-2.0 (weights in repo, torch.hub) | MegaDepth + COCO_20k subset ("check COCO terms of use", README) | [XFeat README "License", "Training"](https://github.com/verlab/accelerated_features#license) | yes | yes | check (COCO image licenses) | check |
| LoFTR | Apache-2.0 | Apache-2.0 (no separate statement) | indoor: ScanNet ("only for non-commercial research and educational purposes"); outdoor: MegaDepth | [LoFTR README](https://github.com/zju3dv/LoFTR), [ScanNet ToS PDF](https://kaldir.vc.in.tum.de/scannet/ScanNet_TOS.pdf) | yes | yes (outdoor-ds model) | check; avoid indoor and `-ot` models | check |
| RoMa (and RoMaV2) | MIT (DINOv2 part Apache-2.0) | MIT | MegaDepth outdoor, ScanNet indoor (paper) | [RoMa README "License"](https://github.com/Parskatt/RoMa#license) | yes | yes | check | check |
| DUSt3R | CC BY-NC-SA 4.0 | CC BY-NC-SA 4.0 + every training dataset's terms | CO3Dv2 (CC BY-NC), ARKitScenes (CC BY-NC-SA), ScanNet++ (non-commercial), Waymo (non-commercial), others | [DUSt3R README "License" and training list](https://github.com/naver/dust3r#license) | yes | **risky**: NC, ShareAlike; prize money arguably "monetary compensation" | no | no |
| MASt3R (and MASt3R-SLAM, which uses its weights) | CC BY-NC-SA 4.0 | CC BY-NC-SA 4.0 + `CHECKPOINTS_NOTICE`: 3D Street View (non-commercial), IndoorVL (CC BY-NC-ND modified), Map-free ("very restrictive") | many | [MASt3R README](https://github.com/naver/mast3r#license), [CHECKPOINTS_NOTICE](https://github.com/naver/mast3r/blob/main/CHECKPOINTS_NOTICE) | yes | risky | no | no |

## Matrix: global descriptors / visual place recognition

| Model | Code license | Weights license | Training data (terms) | Source read | Research | Hackathon | Commercial | Defense |
|---|---|---|---|---|---|---|---|---|
| DINOv2 (ViT-S/B/L/g backbones) | Apache-2.0 | Apache-2.0 since 2023-08-31 (commit "Update code and models license from CC-BY-NC to Apache 2.0") | LVD-142M, not released | [dinov2 README "License"](https://github.com/facebookresearch/dinov2#license), LICENSE commit history; HF `facebook/dinov2-base` card: apache-2.0 | yes | yes | yes (backbones only) | yes, with export check |
| DINOv2 sub-models in the same repo (XRay-DINO, Cell-DINO) | Cell-DINO code CC BY-NC | FAIR Noncommercial Research License | medical / cell data | same README, sections near the end | yes | no | no | no |
| AnyLoc | BSD-3-Clause | DINOv2 (Apache-2.0) + released VLAD vocabularies | vocabularies built from VPR benchmark images (terms vary, not checked) | [AnyLoc README badge](https://github.com/AnyLoc/AnyLoc) (GitHub API: BSD-3-Clause) | yes | yes | check (vocab source images) | check |
| NetVLAD (Relja, MATLAB) and hloc's converted VGG16-NetVLAD | MIT | MIT (no separate statement); hloc downloads `Pitts30K_struct.mat` / `TokyoTM_struct.mat` from cvg-data.inf.ethz.ch | Pittsburgh 30k and Tokyo Time Machine, both Google Street View imagery (terms not checked) | [netvlad README](https://github.com/Relja/netvlad) ("distributed under the MIT License"), [hloc netvlad.py](https://github.com/cvg/Hierarchical-Localization/blob/master/hloc/extractors/netvlad.py) | yes | yes | check | check |
| MixVPR | **no LICENSE file** (GitHub API: none): all rights reserved by default | not stated | GSV-Cities (Kaggle; license not readable without login), Google Street View origin | [MixVPR README](https://github.com/amaralibey/MixVPR) | yes (reading, eval) | risky: no grant to copy or redistribute | no | no |
| SALAD | **GPL-3.0** | not stated separately (assume GPL-3.0) | GSV-Cities + DINOv2 backbone | [salad repo](https://github.com/serizba/salad) (GitHub API: GPL-3.0) | yes | copyleft | copyleft (ship source) + check data | copyleft + check |
| BoQ (Bag-of-Queries) | MIT | MIT (torch.hub weights) | GSV-Cities; ResNet50 (ImageNet init) or DINOv2 backbone | [BoQ README](https://github.com/amaralibey/Bag-of-Queries) (GitHub API: MIT) | yes | yes | check (GSV-Cities, ImageNet) | check |
| EigenPlaces | MIT | MIT (torch.hub) | SF-XL panoramas; download behind a Google form, terms not read | [EigenPlaces README](https://github.com/gmberton/EigenPlaces) (GitHub API: MIT) | yes | yes | check | check |
| CosPlace | MIT | MIT (torch.hub, Google Drive) | SF-XL (same) | [CosPlace README](https://github.com/gmberton/CosPlace) (GitHub API: MIT) | yes | yes | check | check |

## Matrix: detection and depth

| Model | Code license | Weights license | Training data (terms) | Source read | Research | Hackathon | Commercial | Defense |
|---|---|---|---|---|---|---|---|---|
| YOLO (Ultralytics: YOLOv8 / 11 / 26, and their RT-DETR port) | **AGPL-3.0** or paid Enterprise License | same dual license (README: Enterprise covers "Ultralytics software and AI models") | COCO and others | [ultralytics README "License"](https://github.com/ultralytics/ultralytics#-license), LICENSE file (AGPL v3) | yes | copyleft: fine if the whole project is open under AGPL; a closed demo served over a network still triggers AGPL | Enterprise license | Enterprise license |
| RT-DETR / RT-DETRv2 (lyuwenyu, original authors) | Apache-2.0 | Apache-2.0 (GitHub release assets, no separate statement) | COCO; some checkpoints COCO+Objects365 (Objects365 terms not checked) | [RT-DETR README](https://github.com/lyuwenyu/RT-DETR), [rtdetrv2_pytorch README](https://github.com/lyuwenyu/RT-DETR/tree/main/rtdetrv2_pytorch) | yes | yes | check (COCO images; avoid the Objects365 checkpoints until checked) | check |
| Depth-Anything (V1, all sizes) | Apache-2.0 | apache-2.0 (HF cards `LiheYoung/depth-anything-small-hf` and `-large-hf`, via HF API) | 1.5M labeled + 62M unlabeled images (paper) | [Depth-Anything repo](https://github.com/LiheYoung/Depth-Anything) (GitHub API: Apache-2.0) | yes | yes | check | check |
| Depth-Anything-V2 Small | Apache-2.0 | Apache-2.0 | synthetic + pseudo-labeled real (paper) | [V2 README "LICENSE"](https://github.com/DepthAnything/Depth-Anything-V2#license) | yes | yes | check | check |
| Depth-Anything-V2 Base / Large / Giant | Apache-2.0 | **CC-BY-NC-4.0** | same | same; HF card `Depth-Anything-V2-Large-hf`: cc-by-nc-4.0 | yes | risky (NC) | no | no |

## Matrix: VO / SLAM

| Model | Code license | Weights license | Training data (terms) | Source read | Research | Hackathon | Commercial | Defense |
|---|---|---|---|---|---|---|---|---|
| cuVSLAM (NVIDIA, now on GitHub) | **NVIDIA Community License** (v. 2026-02-25) | same | n/a for the core tracker; repo also has a `models/` dir (not inspected) | [cuVSLAM LICENSE](https://github.com/nvidia-isaac/cuVSLAM/blob/main/LICENSE), [README "License"](https://github.com/nvidia-isaac/cuVSLAM#license) | yes | yes, on NVIDIA hardware only | yes, "commercially usable", **only on NVIDIA GPUs/CPUs** | yes, on NVIDIA hardware; clause 10 restates US export and sanctions duties |
| DROID-SLAM | BSD-3-Clause | not stated separately; `droid.pth` from Google Drive | TartanAir (CC BY 4.0) | [DROID-SLAM repo](https://github.com/princeton-vl/DROID-SLAM) (GitHub API: BSD-3-Clause), [TartanAir terms](https://theairlab.org/tartanair-dataset/) | yes | yes | yes, with attribution (third-party deps not audited) | yes, same caveat |
| DPVO (and DPV-SLAM) | MIT | not stated separately; `models.zip` from Google Drive | TartanAir (CC BY 4.0) | [DPVO repo](https://github.com/princeton-vl/DPVO) (GitHub API: MIT) | yes | yes | yes, with attribution (deps not audited) | yes, same caveat |
| TartanVO | BSD-3-Clause ("This software is BSD licensed", CMU) | not stated separately | TartanAir (CC BY 4.0) | [tartanvo README "License"](https://github.com/castacks/tartanvo#license) | yes | yes | yes, with attribution | yes |

## Tooling around the models

| Tool | License | Note |
|---|---|---|
| glue-factory | Apache-2.0, code and trained models | Retrain LightGlue on your own imagery: the cleanest path to weights with known provenance. Non-free models are kept apart in `gluefactory_nonfree`. Ships `superpoint-open+lightglue_*.yaml` configs. Whether pretrained weights for that pair are published: not checked. |
| LightGlue-ONNX (fabio-sim) | Apache-2.0 | Export does not change the weights license. An ONNX SuperPoint is still Magic Leap-licensed. |
| hloc | Apache-2.0 (GitHub API) | Configs default to SuperPoint + SuperGlue/LightGlue. Switch to `aliked-n16` / `disk` + LightGlue and NetVLAD / other retrieval to stay clean. |
| kornia | Apache-2.0 | Its DISK `from_pretrained("depth")`, which LightGlue calls, downloaded `depth-save.pth` from `huggingface.co/kornia/disk` in our run, not from the cvlab-epfl GitHub repo. That HF card says MIT, while the original repo is Apache-2.0. Both are permissive. Record which copy you used. |

## Notes

1. **SuperPoint and SuperGlue are the most common trap.** They are the default in LightGlue's
   README example, in hloc configs and in most UAV-to-satellite papers. The Magic Leap terms
   limit use to "your own noncommercial internal research purposes". They forbid giving third
   parties access. They also say that "all and any such derivatives and modifications will be
   owned by Licensor". A hackathon entry is shown to judges and often handed to a sponsor, which
   is hard to call internal research. Swap to ALIKED or DISK + LightGlue: it is a one-line
   change (`LightGlue(features="aliked")`). The sample in
   [samples/geoloc-license-clean](../samples/geoloc-license-clean/) shows those swaps working.
2. **"Non-commercial" plus prize money or a sponsor is ambiguous.** CC BY-NC defines
   NonCommercial as "not primarily intended for or directed towards commercial advantage or
   monetary compensation". A defense-sponsored hackathon with prizes, or one whose terms give the
   organizer a license to your submission, can fall on the wrong side. If the hackathon terms
   assign IP or grant the sponsor a license, you cannot pass on rights you do not have: NC, AGPL,
   no-license and Magic Leap components break that. Read the event's IP clause first. Decide your
   stack before writing code, not at submission.
3. **Copyleft is not the same as forbidden.** SALAD (GPL-3.0) and Ultralytics (AGPL-3.0) are fine
   in a public hackathon repo under the same license. They are a problem when the sponsor wants a
   closed deliverable. AGPL also triggers on network use: a hosted demo counts.
4. **No LICENSE file means no grant** (MixVPR). You may read the code and cite the paper. Copying
   or redistributing it needs permission. Reimplementing from the paper is the usual path.
5. **Training-data inheritance is unresolved.** ScanNet's ToS binds the researcher's use of the
   database. Whether it reaches LoFTR-indoor or RoMa-indoor weights is not settled law. Naver
   chose to pass dataset terms through explicitly. Most authors are silent. For anything beyond
   research, prefer weights trained on CC BY data (TartanAir, MegaDepth) or retrain with
   glue-factory on your own data.
6. **Imagery is a separate license.** NAIP is listed "Public Domain with Attribution" on the
   [AWS Open Data registry](https://registry.opendata.aws/naip/). OpenDroneMap's
   `odm_data_aukerman` frames are CC0-1.0. Google / Bing tiles are not redistributable.
   UAV-VisLoc's README states no license.
7. **Weights download from third-party hosts at runtime** (GitHub releases, Google Drive,
   cvg-data.inf.ethz.ch, torch.hub). For an air-gapped demo, pre-cache them in
   `~/.cache/torch/hub/checkpoints/` and record the URL and SHA256 of each file. That record is
   your provenance trail.

## Recommended clean stacks

- **Frame-to-map matching:** ALIKED or DISK + LightGlue (Apache-2.0 / BSD-3). SIFT + LightGlue as
  the fallback with no learned extractor. Measured in the sample: see its README.
- **Retrieval over large maps:** DINOv2 backbone (Apache-2.0) with your own VLAD/GeM head (AnyLoc
  style, BSD-3). Or EigenPlaces / CosPlace / BoQ (MIT, with the dataset caveat). Avoid SALAD
  unless the project is GPL anyway. Avoid MixVPR (no license).
- **Dense matching / 3D:** RoMa (MIT) or LoFTR outdoor (Apache-2.0) instead of MASt3R/DUSt3R
  (NC-SA).
- **Detection (C-UAS, situational awareness):** RT-DETR from lyuwenyu (Apache-2.0) instead of
  Ultralytics, unless AGPL is acceptable.
- **Depth:** Depth-Anything V1 or V2-Small (Apache-2.0). Not V2 Base/Large/Giant.
- **VO:** DPVO (MIT) or DROID-SLAM (BSD-3) on TartanAir weights. cuVSLAM if the target is a
  Jetson.
