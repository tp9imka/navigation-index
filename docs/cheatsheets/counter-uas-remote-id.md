# Cheat sheet: counter-UAS detection and Remote ID to TAK

Briefs like "detect and track drones for airspace awareness", "small drones near a FOB",
"hostile drones", "common operating picture". Decoder rows 13, 12. Detection and awareness only.

## 1. What judges likely want (30 s)

Every drone in the area becomes a track on the shared map, cooperative or not. Judges want
fused sources (Remote ID, RF, radar or camera) => tracks => TAK, with a classifier number that
survives a cross-site or held-out test, and a clear line that the project stops at awareness.

## 2. The demo in 24-48 h

Remote ID decoder (validated against the reference C library) => track table with plausibility
flags => CoT. Next to it, a UAV-vs-bird classifier on real radar tracks and Stone Soup tracking.

| Sample | Status | Deps | Setup / download | First commands (from `samples/<name>/`) |
|---|---|---|---|---|
| [remote-id-to-tak](../../samples/remote-id-to-tak/) | ran | stdlib (PyTAK venv only for `--cot-url`) | optional public pcaps via `./fetch_captures.sh`; tests 0.086 s | `python3 rid_to_cot.py --sim --offline --quiet` |
| [cuas-classifiers](../../samples/cuas-classifiers/) | ran | venv, Python 3.12 | NRC radar tracks ~59 MB, train 104-329 s; DroneRF subset 692 MB RAR (6.6 GB extracted), ~10 min | `python3 download_data.py radar && .venv/bin/python train_radar.py --save-model out/radar_model.pkl` |
| [stone-soup-tracking](../../samples/stone-soup-tracking/) | ran | venv (Stone Soup needs Python 3.11+) | runtime not measured | `.venv/bin/python radar_jpda_ospa.py` |

## 3. First 2 hours (3-5 people)

| Who | 0:00-1:00 | 1:00-2:00 |
|---|---|---|
| Lead | Sensors on site (Wi-Fi / BT receiver, SDR, radar, camera)? Scope line written | ADR-001: metric = detection / classification on held-out data + track continuity |
| Nav | Radar classifier trained and saved | Stone Soup tracker fed by RID + radar detections |
| Platform | RID decoder on public pcaps, receiver hardware if present | Live capture path; never set `LOCK_LEVEL=2` on an ArduRemoteID board |
| Viz (4-5) | GoATAK / OpenTAKServer local, CoT from `rid_to_cot.py` | Cooperative vs non-cooperative symbols (milsymbol) |
| Pitch (5) | Ethics: detection only, privacy of operator positions | Honest slide: what the classifiers were not tested on |

## 4. Numbers you can cite

- Radar UAV vs bird: balanced accuracy 0.928 (5-fold GroupKFold by session); trained on one
  site, tested on another 0.902-0.918. **Real** NRC Echodyne radar tracks (510 tracks).
- RF detection on DroneRF: balanced accuracy 0.977-0.994 (temporal holdout). **Real** subset, one
  recording session per class: the sample says do not quote it as field performance.
- Remote ID decoder field-for-field equal to opendroneid-core-c on 500 encoded vectors, 500
  random raw messages and 81 payloads from public captures. **Real** captures + generated
  vectors; validates a decoder, not detection rates.

## 5. Top traps

1. Scope creep toward interception. Stay on detect, track, display.
2. Remote ID values are claims: location, operator position and ID can be fabricated. The
   reference C library has its own defects (4 NM decodes to 7808 m, a pack decode that trusts
   `MsgPackSize`; [upstream findings 3-5](../upstream-findings.md#summary)). Decoded operator
   positions are personal data.
3. Small test sets: the cross-site radar test has only 22 bird tracks; DroneRF class and session
   coincide. Plausibility flags were shown to fire on scripted tracks, not that thresholds are right.

## 6. Stretch goal

Fuse Remote ID with radar tracks in Stone Soup and flag a radar track that has no matching RID
broadcast (non-cooperative), or an RID claim the radar contradicts (spoofed RID). Both pieces
exist; the association and the flag are the new part.

## 7. Links

- Decoder: [rows 12, 13](../problem-statement-decoder.md#the-table); evidence:
  [section 11](../evidence-matrix.md#11-counter-uas-detection),
  [section 13](../evidence-matrix.md#13-functional-checks-no-accuracy-metric).
- Cards: [OpenDroneID receiver](../integration-cards/opendroneid__receiver-android.md),
  [opendroneid-core-c](../integration-cards/opendroneid__opendroneid-core-c.md),
  [ArduRemoteID](../integration-cards/ardupilot__arduremoteid.md),
  [Stone Soup](../integration-cards/dstl__stone-soup.md), [PyTAK](../integration-cards/snstac__pytak.md),
  [OpenTAKServer](../integration-cards/brian7704__opentakserver.md),
  [milsymbol](../integration-cards/spatialillusions__milsymbol.md),
  [anti-uav](../integration-cards/zhaoj9014__anti-uav.md),
  [DragonSync](../integration-cards/alphafox02__dragonsync.md).
- Datasets: [Remote ID captures](../dataset-cards/remote-id-droneid-captures.md),
  [drone RF sets](../dataset-cards/drone-rf-datasets.md), [NRC C-UAS](../dataset-cards/nrc-cuas-sensing.md),
  [Anti-UAV](../dataset-cards/anti-uav.md).
