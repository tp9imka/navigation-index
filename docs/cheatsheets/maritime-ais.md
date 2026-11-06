# Cheat sheet: maritime, USV and AIS spoofing

Briefs like "USV operating in a spoofed area", "port / coast / patrol vessel", "spot GNSS
manipulation zones from AIS". Decoder rows 7, 8. Underwater (row 17) is at the end: no sample.

## 1. What judges likely want (30 s)

Two products: own-ship ("the bridge sees the moment GNSS stops agreeing with physics, and which
position to trust") or shore-side ("public AIS shows where GNSS is manipulated, hours not
weeks later"). Judges want real AIS or chart data, alarm time, and what the system shows as
trusted.

## 2. The demo in 24-48 h

Own ship: compass + speed-log dead reckoning, radar returns matched to the real OSM chart,
monitor excludes the spoofed GNSS on a 19.6 km Oresund transit. Shore side: track-plausibility
detectors on real Danish AIS with injected episodes, output as GeoJSON + CoT.

| Sample | Status | Deps | Setup / download | First commands (from `samples/<name>/`) |
|---|---|---|---|---|
| [usv-gnss-denied-nav](../../samples/usv-gnss-denied-nav/) | ran | stdlib | committed OSM chart + DMA AIS fixtures; tests ~1 s, run ~2 min | `python3 -m unittest test_core && python3 run.py` |
| [maritime-ais-spoofing](../../samples/maritime-ais-spoofing/) | ran | stdlib for tests; venv for the real run | detectors 5 s on 1.7 M fixes; DMA day ~110 s, 0.5 GB CSV | `python3 -m unittest -v`, then the README "Run" block (`venv/bin/python dma.py ...`, `run.py ...`) |

## 3. First 2 hours (3-5 people)

| Who | 0:00-1:00 | 1:00-2:00 |
|---|---|---|
| Lead | Own ship or shore side? Radar / AIS / NMEA provided? | ADR-001: alarm time + max error, or recall + precision |
| Nav | `run.py` on usv, read the monitor | Tune DR model (current, leeway) to the brief's area |
| Platform | Fetch one DMA AIS day (or the provided feed) | NMEA / Signal K adapter if the brief names a bridge system |
| Viz (4-5) | GeoJSON on a map, CoT to a local sink | Trusted position vs GNSS on one chart view |
| Pitch (5) | Pitch geography: Baltic, Gulf | Read the samples' limits, write the honest slide |

## 4. Numbers you can cite

- Coastal GNSS drag: alarm and exclusion 125-131 s after onset, max error with the monitor
  10-25 m; without the monitor GNSS + DR reached 1391-2261 m across the drag scenarios; 0 false
  alarms. **Synthetic**
  sensors over real OSM chart and real DMA AIS traffic, 5 seeds x 5 scenarios.
- AIS detectors on injected episodes: recall 0.75 on the held-out day, median TTD 8 s,
  precision per run 0.64-0.70. **Real** DMA AIS with **synthetic** episodes, 3 seeds x 2 days.
- Unaltered real AIS, 8.8 h: no spoofing found; 132 / 159 alerts per day, mostly on land
  (Kiel Canal, fjords). **Real**.

## 5. Top traps

1. The simulated radar sees the same chart it matches against: radar fix errors (median
   1.1-3.7 m) are optimistic. Real radar: [Pohang](../dataset-cards/maritime-datasets.md)
   navigation.zip (about 20 MB).
2. No real AIS spoofing event was found in the data analysed; detection numbers come from
   injected geometric episodes. A spoofer that also fakes consistent SOG / COG defeats the
   speed checks; only gyro heading stays independent.
3. DR quality depends on the current / leeway model; at 1.5 km radar range alarm time grows to
   397-602 s and error to 175-1024 m.

## 6. Stretch goal

Replace the simulated radar with real Pohang radar and show the fix rate honestly, or put the
own-ship monitor into Signal K / OpenCPN so the bridge sees "trusted source" live.

Underwater (row 17): no sample and no recorded DVL / USBL data in the hub. Start from the
hold-and-correct pattern in [gnss-ins-ekf-outage](../../samples/gnss-ins-ekf-outage/)
(synthetic ground vehicle) and the [Stonefish card](../integration-cards/patrykcieslak__stonefish.md)
(read, not run). Data: [underwater sets](../dataset-cards/underwater-datasets.md).

## 7. Links

- Decoder: [rows 7, 8, 17](../problem-statement-decoder.md#the-table); evidence:
  [section 7](../evidence-matrix.md#7-maritime), AIS in
  [section 2](../evidence-matrix.md#2-receiver-and-signal-level-detection).
- Cards: [Signal K](../integration-cards/signalk__signalk-server.md),
  [OpenCPN](../integration-cards/opencpn__opencpn.md), [pyais](../integration-cards/m0r13n__pyais.md),
  [AIS-catcher](../integration-cards/jvde-github__ais-catcher.md),
  [Stone Soup](../integration-cards/dstl__stone-soup.md), [PyTAK](../integration-cards/snstac__pytak.md).
- Datasets: [DMA AIS](../dataset-cards/dma-ais.md), [maritime sets](../dataset-cards/maritime-datasets.md).
