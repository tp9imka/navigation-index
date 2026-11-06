# Maritime datasets (Pohang Canal, MassMIND, Singapore Maritime, LaRS)

<!-- about: repo:osrf/vrx, repo:signalk/signalk-server, repo:dstl/stone-soup -->

None of these datasets are indexed; the about marker lists the indexed tools they pair with.
Pohang Canal is the navigation dataset (RTK, radar, lidar). The other three are perception
sets (obstacle segmentation and detection) for maritime situational awareness.

| Dataset | Platform | Sensors | GT | Size | License |
|---|---|---|---|---|---|
| Pohang Canal (Chung et al., 2023) | Surface vessel, 7.5 km route: canal, inner/outer port, near coast | 3 lidars (64 + 2x32 ch), marine radar, stereo RGB, IR camera, 6-way omni camera, AHRS, RTK GPS | RTK GPS + SLAM-based baseline trajectory | 1,296 GB total, 6 sequences (S3 listing). `navigation.zip` about 20 MB, `radar.zip` about 0.2 GB, `infrared.zip` 4.5-6.3 GB per sequence | CC BY-NC 4.0 |
| MassMIND (UMass Lowell) | Boat, Boston Harbor, 2 years | LWIR 640x512 | Pixel instance + semantic masks, 7 classes | 2,916 images; Drive: images 414 MB, masks about 7 MB each (2026-11-06) | CC BY-NC-SA 4.0 |
| Singapore Maritime Dataset (SMD) | Fixed shore camera and a moving vessel | Canon 70D 1080p video, visible + NIR | Horizon, bounding boxes, tracks | 81 videos: on-shore 2.9 GB, NIR 1.4 GB (Drive), on-board 768 MB (page) | Not stated; cite request only |
| LaRS (Ljubljana, ICCV 2023) | Mixed sources: lakes, rivers, seas | RGB frames | Panoptic masks, 3 stuff + 8 thing classes, scene attributes | Images 1.01 GB, annotations 23 MB, sequence frames 13.6 GB (HEAD on first two) | CC BY-NC 4.0, research on maritime obstacle detection only |

## Download

```bash
# Pohang Canal: public S3, no account needed
aws s3 cp s3://pohang-canal-dataset/pohang00/navigation.zip . --no-sign-request
aws s3 cp s3://pohang-canal-dataset/pohang00/radar.zip . --no-sign-request
aws s3 cp s3://pohang-canal-dataset/pohang00/infrared.zip . --no-sign-request
# without the AWS CLI: https://pohang-canal-dataset.s3.amazonaws.com/pohang00/navigation.zip
# pohang01 and pohang05 are night runs (no omni images)

# MassMIND (venv gdown)
gdown 1T572f0oqy5JmuTvVEwkSUeXLWOSHl4hL -O MassMIND_Images.zip
gdown 1pHp480_Q-s72RoDf1nD7ERzsv9yZTDE1 -O Segmentation_Masks.zip
gdown 16rPWhV8OEocyLLpT1-LSCALt757P_h0N -O InstanceSegmentation_Masks.zip

# SMD
gdown 1HnHyQzhzzDlYh15y9_K1mNZX3grlSDMM -O VIS_Onshore.rar
gdown 13wKWzHqkDQHMHjfuUWjgzwhTrnMoEE8P -O NIR.rar
# on-board: https://drive.google.com/file/d/0B43_rYxEgelVb2VFaXB4cE56RW8/view (resource-key link, browser)

# LaRS (agree to terms at https://lojzezust.github.io/lars-dataset/terms.html first)
curl -LO https://box.vicos.si/lars/lars_v1.0.0_images.zip
curl -LO https://box.vicos.si/lars/lars_v1.0.0_annotations.zip
```

## Loading and tooling

- Pohang: per-modality zips; README points to sensor calibration and a SLAM baseline
  trajectory. Feed `navigation.zip` GPS/AHRS into [Signal K](../../catalog/repos/signalk__signalk-server.md)
  to replay as a live vessel; compare against radar or lidar odometry.
- SMD: MATLAB `.mat` ground truth per video; community converters
  `tilemmpon/Singapore-Maritime-Dataset-Frames-Ground-Truth-Generation-and-Statistics` (not indexed).
- LaRS: COCO panoptic JSON; evaluator https://github.com/lojzezust/lars_evaluator .
- Tracking demos over detections: [Stone Soup](../../catalog/repos/dstl__stone-soup.md).
- Sim alternative: [VRX](../../catalog/repos/osrf__vrx.md).

## Hackathon fit

- Idea 12 (maritime multi-source position integrity in Signal K): Pohang `navigation.zip`
  is a 20 MB real RTK + AHRS track; add radar from the 0.2 GB radar zip for a
  radar-vs-GNSS consistency check, or inject a synthetic GNSS offset and show detection.
- Idea 3 (AIS plausibility) or a maritime SA overlay: MassMIND / SMD / LaRS give camera or
  LWIR detections to cross-check AIS contacts.
- Night operations: MassMIND LWIR and Pohang night runs.

## Pitfalls

- Pohang full sequences are 125-255 GB each because of stereo and omni images; never sync a
  whole folder at the venue.
- All four are non-commercial or unlicensed for redistribution.
- SMD ground truth is MATLAB-specific; budget time for conversion.
- MassMIND is a single-frame segmentation set, not sequences.

## Sources

- https://github.com/dhchung/pohang_canal_dataset README; S3 listing https://pohang-canal-dataset.s3.amazonaws.com/?list-type=2 (2026-11-06).
- https://github.com/uml-marine-robotics/MassMIND README; Google Drive download pages for sizes.
- https://sites.google.com/site/dilipprasad/home/singapore-maritime-dataset (counts, cameras, on-board size).
- https://lojzezust.github.io/lars-dataset/ and terms.html; HEAD on box.vicos.si files.
