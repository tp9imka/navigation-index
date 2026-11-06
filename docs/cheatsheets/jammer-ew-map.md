# Cheat sheet: jammer detection, localization, EW map

Briefs like "detect and map GNSS jamming over an area", "low-cost sensor network", "find the
jammer", "common operating picture under EW". Decoder rows 3, 5, 12. Awareness product, not a
vehicle.

## 1. What judges likely want (30 s)

A map an operator can act on, built from receivers a unit already owns, on real recorded
attacks. They will check that "no data" looks different from "no interference", that alerts
come with a false-alarm rate, and that nothing transmits.

## 2. The demo in 24-48 h

Replay real Jammertest 2024 u-blox logs through the per-node scorer, aggregate many nodes into
hex cells with confidence, localize the emitter, push cells and the emitter ellipse to TAK as CoT.

| Sample | Status | Deps | Setup / download | First commands (from `samples/<name>/`) |
|---|---|---|---|---|
| [real-attack-replay](../../samples/real-attack-replay/) | ran | stdlib | 64 MB download (~25 s), replay of 7 logs ~14 s | `python3 -m unittest -v test_real_attack_replay.py && ./fetch_data.sh && python3 replay.py --data data/vaara --no-pos-drift --baseline-max-score 0.3` |
| [jammer-sensor-network](../../samples/jammer-sensor-network/) | ran | stdlib | none; demo ~40 s, evaluate ~2 min | `python3 demo.py` |
| [interference-geolocation-to-tak](../../samples/interference-geolocation-to-tak/) | ran | stdlib (`--method all` needs Stone Soup venv) | ls under 1 s, all methods ~40 s | `python3 locate.py` |
| [osint-jamming-map](../../samples/osint-jamming-map/) | ran | venv | ADS-B download 600-750 MB, Sentinel-1 ~8 min | `.venv/bin/python adsb_hexmap.py && .venv/bin/python s1_rfi.py && .venv/bin/python make_map.py` |

CoT sink for testing without a TAK server: `python3 ../mavlink-to-tak-cot/cot_sink.py`
(see [mavlink-to-tak-cot](../../samples/mavlink-to-tak-cot/)).

## 3. First 2 hours (3-5 people)

| Who | 0:00-1:00 | 1:00-2:00 |
|---|---|---|
| Lead | Hardware on site? Receive-only rule? Provided logs? ADR-001 | Pick the metric: detection per slot + false alarms per hour |
| Nav | `real-attack-replay` end to end | Feed per-node scores into the jammer-sensor-network aggregator |
| Platform | Fetch VAARA logs; if receivers are provided, capture UBX now | Adapter for the provided format (`PoseSource` or scorer input) |
| Viz (4-5) | GoATAK or OpenTAKServer local, CoT sink | Cells coloured by state, grey for no data |
| Pitch (5) | Ethics line: receive-only, no transmission | Licence check: VAARA states none, do not redistribute |

## 4. Numbers you can cite

- 20 of 20 attack slots alert, 0 alerts in the one logged quiet window, 1-6 alarm raises per
  hour in unlogged time. **Real** (VAARA u-blox logs, Jammertest 2024), 21 slots, 1 receiver.
- 16 nodes on 4 x 4 km, 6 dB shadowing: grid median 313 m, grid + 3 DF stations 40 m.
  **Synthetic** (assumed path loss), 40 trials.
- ADS-B NACp: 110 of 129 aircraft NACp < 8 over the SE Baltic vs 19 of 879 in a NL/DE control.
  **Real** ADS-B Exchange samples; the control was sampled 10x more sparsely, compare ratios.

## 5. Top traps

1. Every localization number is synthetic: no open DF recording with ground truth exists in
   the hub, and the DF model has no bearing bias, so ellipses are best case. Say so.
2. The scorer's 4 parameters were tuned on 3 of the 7 VAARA logs; detection counts alerts up to
   300 s before a slot; 2.4.2 / 2.4.3 windows are plan-shifted guesses. VAARA logs have no
   MON-RF / AGC and break pyubx2 1.4.1 (use the sample's framer).
3. Empty cells mean no data, not no jamming. The Sentinel-1 RFI layer did not agree with the
   ADS-B layer; no link between C-band RFI and GNSS jammers was shown.

## 6. Stretch goal

Calibrate the C/N0 path-loss model on real Jammertest drive-by data instead of the assumed
exponent, then track a moving jammer with Stone Soup. Or publish onset / end labels for the
logs you used: no open labelled multi-constellation spoofing set with raw observables exists.

## 7. Links

- Decoder: [rows 3, 5, 12](../problem-statement-decoder.md#the-table); evidence:
  [section 2](../evidence-matrix.md#2-receiver-and-signal-level-detection),
  [section 6](../evidence-matrix.md#6-jammer-localization-and-interference-mapping).
- Cards: [pyubx2](../integration-cards/semuconsulting__pyubx2.md),
  [readsb](../integration-cards/wiedehopf__readsb.md), [PyTAK](../integration-cards/snstac__pytak.md),
  [OpenTAKServer](../integration-cards/brian7704__opentakserver.md),
  [GoATAK](../integration-cards/kdudkov__goatak.md),
  [KrakenSDR DoA](../integration-cards/krakenrf__krakensdr_doa.md),
  [Stone Soup](../integration-cards/dstl__stone-soup.md),
  [milsymbol](../integration-cards/spatialillusions__milsymbol.md).
- Datasets: [Jammertest](../dataset-cards/jammertest-data.md),
  [ADS-B Exchange samples](../dataset-cards/adsbexchange-samples.md),
  [Sentinel-1 GRD](../dataset-cards/sentinel-1-grd.md).
- Guide: [integrity-monitoring](../integrity-monitoring.md); scope:
  [export-control-and-ethics](../export-control-and-ethics.md).
