# Drone RF detection and identification datasets (DroneRF, RFUAV, DroneDetect, CardRF)

<!-- about: repo:al-sad/dronerf, repo:kitoweeknd/rfuav, res:dronedetect-rf-dataset-essex, res:cardrf-drone-rf-dataset, sample:cuas-classifiers -->

Open RF recordings for passive (receive-only) drone detection and classification in the 2.4 GHz band, for counter-UAS situational awareness. All four are indexed. DroneRF is the one a sample in this repo actually downloads and trains on ([cuas-classifiers](../../samples/cuas-classifiers/)); DroneDetect and CardRF sit behind an IEEE DataPort login and were not downloaded, so their rows come from the DataPort listings as found by search and the index records.

| Dataset | Content | Size | License / access |
|---|---|---|---|
| DroneRF (Qatar University, 2019) | 227 segments from 3 drones (modes: off, on and connected, hovering, flying, video recording) + background RF with no drone (Mendeley description). Receivers on two laptops (Mendeley); files split `_L`/`_H`, read as low/high band halves (naming only, not verified) | 4,027,462,446 B, 23 RAR files (Mendeley public API, 2026-11-06) | CC BY 4.0 (Mendeley API `data_licence`) |
| RFUAV (2025, arXiv 2503.09033) | Raw IQ from 35 emitter types at high SNR: DJI drones (FPV Combo, Avata 2, Mini 3, Mini 4 Pro, Mavic 3 Pro), Autel Evo Nano, and many RC transmitters (FrSky, Futaba, FlySky, RadioMaster, SIYI, Herelink, ...); spectrogram image sets; validation set; trained weights | 299 GB on Hugging Face (sum of file sizes via HF API, 2026-11-06): validation set 162 GB, Matlab-pipeline image set 18.4 GB, per-device raw RARs 1.2-15 GB, weights 9.3 GB | Apache-2.0 (HF card), not gated |
| DroneDetect (U. Essex, Swinney and Woods) | 7 commercial drones (DJI Mavic variants, Inspire 2, Phantom 4, Parrot Disco), modes on / hovering / flying, with no interference, Bluetooth, Wi-Fi, both. BladeRF at 60 MS/s, 28 MHz bandwidth, 2.4375 GHz center, about 2 s per file, `.dat` interleaved float | Not verified | IEEE DataPort, DOI 10.21227/5jjj-1m32, free IEEE account; index record says CC BY (not checked on the page) |
| CardRF (Medaiyese, U. Louisville) | UAV, controller, Bluetooth and Wi-Fi signals, outdoor LOS and BLOS, BladeRF + GNU Radio; 17 RCs from 8 makers; `.mat` | Listing says over 65 GB (not verified) | IEEE DataPort ([node/9593](https://ieee-dataport.org/node/9593)), DOI 10.21227/1xp7-ge95, free IEEE account; licence not checked |

| Field | Value |
|---|---|
| Platform | Ground SDR receivers listening to drones and their controllers |
| Ground truth | Class labels (drone model, flight mode, interference condition). No geolocation truth |
| Format | DroneRF: RAR archives of CSV text; each segment file is one line of 10,000,000 real-valued integer samples (counted by the sample); sample rate not stated in the Mendeley description or repo README. RFUAV: raw float32 IQ packs (MATLAB reader uses `float32`), 100 MS/s in README examples |
| Index | [DroneRF](../../catalog/repos/al-sad__dronerf.md), [RFUAV](../../catalog/repos/kitoweeknd__rfuav.md), [DroneDetect](../../catalog/resources/dronedetect-rf-dataset-essex.md), [CardRF](../../catalog/resources/cardrf-drone-rf-dataset.md), [cuas-classifiers sample](../../samples/cuas-classifiers/) |

## Download

```bash
# DroneRF (4.0 GB): list files and URLs from Mendeley
curl -s https://data.mendeley.com/public-api/datasets/f4c2b4n755 | python3 -c \
 "import json,sys;[print(f['filename'],f['size'],f['content_details']['download_url']) for f in json.load(sys.stdin)['files']]"

# RFUAV: pick one device, not the whole 299 GB (huggingface_hub in the project venv)
uv pip install --python "$VENV/bin/python" huggingface_hub
"$VENV/bin/huggingface-cli" download kitofrank/RFUAV "DJI MINI3.rar" --repo-type dataset --local-dir rfuav
"$VENV/bin/huggingface-cli" download kitofrank/RFUAV --repo-type dataset --include "weight/*" --local-dir rfuav

# DroneDetect / CardRF: log in at ieee-dataport.org and download from
#   https://ieee-dataport.org/node/4361   (DroneDetect)
#   https://ieee-dataport.org/documents/cardinal-rf-cardrf-outdoor-uavuasdrone-rf-signals-bluetooth-and-wifi-signals-dataset
```

## Used in this repo

[samples/cuas-classifiers](../../samples/cuas-classifiers/) `download_data.py rf`, run 2026-11-06:

- Pulls the file list and download URLs from the Mendeley public API, then 4 of the 23 RARs: `RF Data_00000_L1` (background), `10000_L` (Bebop), `10100_L` (AR Drone), `11000_L1` (Phantom). 692 MB of RAR, **6.6 GB** once extracted (CSV text). About 10 min here.
- Mendeley returns HTTP 403 to Python's default urllib User-Agent; send any custom User-Agent.
- Extraction uses `bsdtar` (libarchive; on macOS by default, `libarchive-tools` on Debian). No `unrar` needed.
- 73 segments, 730 windows. RandomForest on 69 PSD / burstiness features: detection balanced accuracy 0.98 (GroupKFold by segment) and 0.977 (temporal holdout); 4-class identification 0.94 => 0.85 when moving from GroupKFold to temporal holdout.
- Each class in that subset comes from one archive, so class and recording session coincide. Treat the numbers as a pipeline check, not field performance.
- DroneDetect and CardRF were skipped there because both need an IEEE DataPort login.

## Loading and tooling

- RFUAV repo: `graphic/RawDataProcessor.py` (`ShowSpectrogram`, `TransRawDataintoSpectrogram`, waterfall video), MATLAB `check.m`, SNR estimation/AWGN scaling, PyTorch training for ResNet/ViT/MobileNet/Swin etc. Data is USRP-recorded and replayable with GNU Radio (do not transmit without a licence and shielded setup).
- DroneRF repo: LabVIEW capture programs plus MATLAB/Python DNN detection/identification scripts.
- Quick start in numpy: `np.fromfile(path, np.complex64)` for float32 IQ packs, then `scipy.signal.stft`.
- DroneRF features and filename parsing (BUI codes, `_L` / `_H`): `samples/cuas-classifiers/rf_features.py`. One segment parses in about 1 s from CSV text.

## Hackathon fit

- C-UAS awareness feed: spectrogram classifier (drone vs controller vs Wi-Fi/BT) whose detections go to a TAK/C2 picture (reference architecture 4.2 pattern, playbook section 4.2).
- Idea 1 style monitor extended from GNSS bands to 2.4 GHz control links.

## Pitfalls

- Many RFUAV classes are RC transmitters, not airframes; a "drone detector" trained on it partly detects controllers.
- High-SNR lab-style recordings; real detection range needs the RFUAV SNR-adjust tools or field data.
- DroneRF's drones (2019) are old models; class overlap with today's fleet is small.
- IEEE DataPort downloads were reported to cut off; DataPort recommends its AWS option for large files.
- Receive-only use. Replay/transmit features exist in these tools but are out of scope and regulated.

## Sources

- Al-Sad/DroneRF README; Mendeley public API for f4c2b4n755 (description, license, 23 files, size)
- kitoweeknd/RFUAV README; Hugging Face API `api/datasets/kitofrank/RFUAV?blobs=true` (license, file sizes)
- DroneDetect and CardRF: web search summaries of ieee-dataport.org pages and the index records, 2026-11-06 (pages not opened directly)
- samples/cuas-classifiers/README.md and `download_data.py` (measured download size, extracted size, User-Agent gotcha)
