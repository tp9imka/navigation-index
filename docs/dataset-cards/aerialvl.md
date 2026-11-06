# AerialVL

<!-- about: repo:hmf21/aerialvl, repo:hmf21/uavlocalization -->

Aerial visual localization dataset with long UAV flight sequences, geo-referenced satellite
maps and VPR tiles. He et al., IEEE RA-L 9(10), 2024. A follow-up (GeoVINS, T-RO 2025)
adds rosbags with IMU and a DEM.

| Field | Value |
|---|---|
| Platform | UAV with gimballed FLIR BFS-U3-31S4C-C RGB camera (README) |
| Environment | About 70 km of trajectories, varied terrain, multiple heights and lighting; maps around 120.4E 36.6N (Qingdao area, from map file names) |
| Sensors and rates | RGB frames; NovAtel OEM718D GNSS. Frame rate not stated in README. GeoVINS rosbags add IMU (Baidu only) |
| Ground truth | GNSS position per frame (in file names); README states 1.5 m RMS single-point accuracy, so GT is meter-level, not RTK |
| Size | 145.7 GB total on Hugging Face (API sum, 2026-11-06): VAL part 57.8 GB (27 split zip parts), VPR part 76.5 GB (36 parts), VPR training satellite imagery 11.4 GB (6 parts) |
| License | Hugging Face card: CC-BY-4.0. Repo code: MIT. Satellite tiles come from Google Earth / USGS under their terms |
| Format | PNG frames named `@UTCTimeStamp@Lon@Lat@.png`, GeoTIFF maps named with corner coordinates, VPR tiles named with bounds |
| Index | [AerialVL](../../catalog/repos/hmf21__aerialvl.md), [UAVLocalization](../../catalog/repos/hmf21__uavlocalization.md) (same author's retrieval + alignment pipeline) |

## What's in it

- VAL (sequence localization): 11 sequences, 3.7 km to 11 km, plus a large and a small
  geo-referenced map.
- VPR: 18,361 aerial images and 14,096 map patches at three tile levels; four query sets.
- Training: multi-year USGS satellite imagery for training aerial VPR models.

## Download

```bash
# whole dataset (~146 GB)
hf download hmf21/AerialVL --repo-type dataset --local-dir AerialVL
# only the sequence-localization part (~58 GB)
hf download hmf21/AerialVL --repo-type dataset --include "images/VAL/*" --local-dir AerialVL
cat AerialVL/images/VAL/VAL.zip.0* > VAL.zip && unzip VAL.zip   # parts are byte splits
# mirrors: Tsinghua Cloud https://cloud.tsinghua.edu.cn/d/68c3a4ed24cc40f1a7da/ , Baidu (see README)
```

The split format was inferred from `VAL.zip.001...027` naming with 2 GiB parts; if `unzip`
complains, try `7z x VAL.zip.001`.

## Loading and tooling

```python
import re, glob
for p in sorted(glob.glob("VAL/long_trajtr/2023-03-18-12-18-25/*.png")):
    ts, lon, lat = re.findall(r"@([^@]+)", p.split("/")[-1])[:3]
```

- [UAVLocalization](../../catalog/repos/hmf21__uavlocalization.md): map retrieval + alignment
  pipeline from the same author.
- [VPR methods evaluation](../../catalog/repos/gmberton__vpr-methods-evaluation.md) for the VPR part.

## Hackathon fit

- Idea 18 (geolocalization fused with VO): the only indexed aerial set with long continuous
  sequences (3.7-11 km) against one map, so you can show drift-bounded tracking along a path.
- Idea 20 (Jetson): replay one short sequence through a real-time pipeline.

## Pitfalls

- Big: no single small sequence download; the VAL part is all-or-nothing (58 GB).
- GT is single-point GNSS (1.5 m RMS), so do not claim sub-meter accuracy.
- Frames are rotated to heading east and maps to north (README); tiles in the VPR part use a
  different convention from the VAL part.
- GeoVINS rosbags and the DEM are Baidu-only.

## Sources

- https://github.com/hmf21/AerialVL README (sensors, counts, layout, links), read 2026-11-06.
- https://huggingface.co/api/datasets/hmf21/AerialVL/tree/main?recursive=true (sizes) and card (license).
