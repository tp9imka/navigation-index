# Maritime AIS tracks under GNSS spoofing: detectors, injected ground truth, GeoJSON + CoT

<!-- about: repo:m0r13n/pyais, res:c4ads-above-us-only-stars, res:windward-2025-maritime-stress-test, res:itu-r-m1371-ais -->

Goal: spot GNSS spoofing from the shore side, using only the AIS traffic picture. A ship's AIS
position comes from its own GNSS receiver, so when the receiver is spoofed the AIS track shows
it: ships "at" an inland airport, groups of ships circling one point, teleports, a track that
disagrees with the ship's own reported speed, course and gyro heading. This sample runs a set
of detectors over real Danish AIS, injects synthetic spoofing episodes into the same real
tracks for ground truth, scores recall and time-to-detect, and exports flagged vessels as
GeoJSON and Cursor-on-Target (CoT) for TAK.

Defensive scope: receive-only analysis of public AIS. Nothing here transmits or generates
GNSS or AIS signals (the pyais encoder is used only to write a local NMEA file for a
decoder round trip).

## Public incidents the detectors are modelled on

| Case | What the AIS picture showed | Source (read / snippet only) |
|---|---|---|
| Black Sea, June 2017 | About 20 ships near Novorossiysk had GPS positions at Gelendzhik airport, about 32 km inland (NRK counted 24) | New Scientist, D. Hambling, 10 Aug 2017, via [RNT Foundation repost](https://rntfnd.org/?p=7868) and [RNT press release](https://rntfnd.org/wp-content/uploads/GPS-Spoofing-Patterns-Press-Release.1-26-Sep-17-RNT-Foundation.pdf) (search snippets, not opened) |
| Russia, Crimea, Syria 2016-2018 | 9,883 suspected spoofing instances affecting 1,311 civilian vessel navigation systems at 10 locations, Feb 2016 - Nov 2018 | C4ADS, *Above Us Only Stars*, 26 Mar 2019 (`res:c4ads-above-us-only-stars`; numbers read from [the report page](https://c4ads.org/reports/above-us-only-stars/)) |
| Airports in Sochi, St Petersburg, Gelendzhik | Nearly 450 cases of ships at sea displayed at airports | Windward, quoted in [Maritime Executive](https://maritime-executive.com/article/gps-spoofing-patterns-discovered) (snippet) |
| Shanghai 2019, Point Reyes | Circling AIS tracks ("crop circles"); SkyTruth / Global Fishing Watch found nine circling locations | [UT Radionavigation Lab](https://radionavlab.ae.utexas.edu/?p=1583), [The Log](https://www.thelog.com/snw/ships-AIS-broadcasts-draw-GPS-crop-circles-thousands-of-miles-away-from-actual-locations/) (snippets) |
| Tanker Skipper, 5 Jul 2025 16:34-17:07 UTC | Positions jumped into a circling pattern at an oil terminal near Bidkhun, Iran; separate later episodes were operator AIS falsification, not GNSS | [SkyTruth](https://skytruth.org/blog/analysis-shows-intercepted-oil-tanker-demonstrated-spoofing-activity) (read) |
| Gulf / Hormuz 2025 | Large-scale jamming and spoofing after the June 2025 strikes | Windward 2025 review (`res:windward-2025-maritime-stress-test`) |
| Baltic 2025 | "Ship-on-land" clusters sharing one false position, sometimes circling; combined spoofing-jamming near Kaliningrad (GPSPATRON + Gdynia Maritime University, 23 Jun - 14 Oct 2025); Swedish Transport Agency 733 interference reports Jan-Aug 2025 vs 495 in all of 2024 | [Maritime Executive Dec 2025](https://maritime-executive.com/article/study-baltic-gps-disruption-comes-from-a-tactically-controlled-network), [GPSPATRON report](https://gpspatron.com/new-gnss-interference-report-released-shipborne-measurements-near-the-kaliningrad-border/GPSPATRON-Report-Shipborne-Observations-near-the-Kaliningrad-Border-v13) (snippets) |

Takeaways used below: spoofed positions jump, circle, or sit on land; several ships in one
area share one false point; reported speed and course often stay steady while positions
circle; gyro heading is not affected by GNSS at all.

## Data

- **AIS: Danish Maritime Authority historical AIS**, `http://aisdata.ais.dk/aisdk-YYYY-MM-DD.zip`,
  no login. One CSV per day, 0.5-0.9 GB zipped, covering Danish waters and approaches.
  Licence: free reuse under the Danish PSI act, commercial or not, with the attribution
  *"Contains data from the Danish Maritime Authority that is used in accordance with the
  conditions for the use of Danish public data"*, data provided as-is
  ([DMA conditions](https://dma.dk/safety-at-sea/navigational-information/download-data/conditions-for-the-use-of-data)).
  `dma.py` downloads only the first N MB with an HTTP Range request and inflates the start
  of the deflate stream, which gives the first ~4.4 h of the day without the 3+ GB CSV.
- **Coastline: Natural Earth 10m land** (public domain), `ne_10m_land.zip`, 3.3 MB.
- **Raw NMEA: `tests/nmea-sample` from pyais** (MIT), 85,194 lines of real AIVDM without timestamps.
- Tried and not used: NOAA MarineCadastre (the `AIS_2024_01_01.zip` URL tried returned 404; not investigated further) and the
  Norwegian Kystverket open NMEA stream `153.44.253.27:5631` (TCP connect timed out from
  this network).

Two days were used. 2026-11-03 was used while tuning thresholds; 2026-10-20 was run once
with the final thresholds as a held-out check.

| Day (UTC) | Bytes fetched | CSV rows | Window | Rows after cleaning | MMSIs | Fixes used |
|---|---|---|---|---|---|---|
| 2026-11-03 | 100,000,000 of 624,618,400 | 2,799,513 | 00:00:00-04:23:14 | 1,719,325 | 2,540 (1,731 Class A, 619 Class B, 145 AtoN, 44 base, 1 SART) | 1,713,811 |
| 2026-10-20 | 104,857,600 of 595,847,268 | 2,992,461 | 00:00:00-04:24:50 | 1,791,653 | 3,044 (1,999 Class A, 752 Class B, 224 AtoN, 69 base) | 1,785,244 |

Cleaning: drop lat 91 / lon 181 / 0,0, drop exact duplicates (the same report heard by
several base stations, about 1.08 M of the 2.8 M rows), keep the first of same-second
reports with different positions (5,514 and 6,409 rows).

## Detectors (`detectors.py`, stdlib)

| Flag | Rule (defaults in `Config`) | Strength |
|---|---|---|
| `jump` | step > 500 m and implied speed > 1.3 x type max (cargo/tanker 30 kn, HSC 60, default 50) | strong |
| `speed` | same speed limit over a 60-600 s lookback | weak |
| `sog_mismatch` | position-derived speed vs mean reported SOG differs by > max(3 kn, 50%) | weak |
| `cog_mismatch` | position-derived bearing vs reported COG (or heading) > 60 deg, SOG >= 3 kn, >= 200 m moved | weak |
| `turn` | circumradius of 150 m-spaced points < 1 ship length, ships >= 100 m, SOG >= 5 kn | weak |
| `loiter_underway` | per 10-min bin: reported SOG >= 5 kn but path implied by SOG > 1.5 x (2 x position spread) | weak |
| `cluster` | >= 3 MMSIs loitering-underway within 2 km in the same bin (crop circle) | strong |
| `on_land` | inside Natural Earth land eroded inward by 1 km, SOG >= 1 kn | strong |
| `mmsi_*` | placeholder (repeated digits, 123456789...), Class A/B MMSI not starting 2-7, MID outside 201-775, > 9 digits | reported separately |
| `mmsi_shared` | >= 6 jumps in one track: two transmitters on one MMSI, or repeated spoofing | strong |

`aggregate()` groups a vessel's flags with gaps <= 10 min into alerts; an alert needs one
strong flag or >= 3 weak ones. `drop_stale_repeats()` removes a single exact repeat of the
previous position while SOG >= 1 kn before the kinematic checks (DMA re-delivers some old
reports with a new receive time, which read as a halt plus a catch-up teleport); a run of
repeats, which is what a frozen spoofed position looks like, is kept.

## Injected episodes (`inject.py`)

Only positions change; reported SOG, COG and heading stay as the ship sent them. Vessels:
Class A, >= 100 fixes, >= 50 min of track, median SOG >= 5 kn, and no alert on the unaltered
data (so detections can be attributed). Each episode lasts 30 min.

- `offset`: constant shift, log-uniform 0.2-40 km, random bearing (Gelendzhik-airport style).
- `drift`: shift growing at 1-5 m/s (slow pull-off).
- `circle`: the vessel's positions go round a 200-600 m circle at its reported speed, around
  its own position at episode start.
- `circle_group`: a seed vessel and up to 4 real neighbours within 30 km all go round one
  shared 300-800 m circle centred 5-25 km away (crop circle).

Per seed: 100 offset, 50 drift, 50 circle, 12 groups. 3 seeds per day. Recall counts an
episode as detected when any alert flag on that vessel falls inside the episode; TTD is the
first such flag minus episode start. "Observable" episodes have >= 10 fixes and no receive
gap > 5 min right before the start; the rest start in a coverage hole.

## Run

```
uv venv venv && uv pip install --python venv/bin/python -r requirements.txt
venv/bin/python dma.py --date 2026-11-03 --mb 100 --out-dir data   # ~110 s, 0.5 GB CSV
venv/bin/python -c "import land; land.fetch_land('data')"
venv/bin/python run.py --csv data/aisdk-2026-11-03.head100mb.csv --land data/ne_10m_land.shp \
    --seeds 1 2 3 --out example_output --nmea-roundtrip
python3 summarize_results.py example_output/injection_results_2026-11-03.json
venv/bin/python nmea_io.py stats path/to/pyais/tests/nmea-sample
python3 -m unittest -v                                               # stdlib only
```

On this Mac (python 3.12.14): CSV load 6-8 s, detectors on 1.7 M fixes 5 s, each injected
run 5-6 s, NMEA round trip a few seconds. The 2026-11-03 file in these runs was fetched with
a 100,000,000-byte range; `dma.py --mb 100` fetches 100 MiB, so a fresh run sees about 4 more
minutes of data and the numbers will move slightly.

## Results on injected episodes (all ran 2026-11-06)

2026-11-03 (tuning day), 3 seeds pooled. Detector columns = share of episodes where that
flag fired inside the episode.

| episodes | n | recall | recall (observable) | TTD median s | TTD p90 s | jump | sog_mismatch | cog_mismatch | turn | loiter_underway | cluster | on_land |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| offset 0.2-0.5 km | 46 | 0.09 | 0.09 | 11 | 13 | 0.02 | 0.04 | 0.04 | 0.04 | 0.00 | 0.00 | 0.00 |
| offset 0.5-2 km | 87 | 0.82 | 0.93 | 5 | 14 | 0.78 | 0.02 | 0.03 | 0.01 | 0.00 | 0.00 | 0.01 |
| offset 2-10 km | 96 | 0.93 | 0.99 | 6 | 11 | 0.93 | 0.01 | 0.00 | 0.00 | 0.02 | 0.00 | 0.04 |
| offset 10-40 km | 71 | 0.96 | 1.00 | 6 | 49 | 0.96 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.07 |
| drift 1-2 m/s | 30 | 0.10 | 0.10 | 273 | 882 | 0.00 | 0.10 | 0.00 | 0.00 | 0.03 | 0.00 | 0.00 |
| drift 2-3 m/s | 45 | 0.36 | 0.38 | 78 | 636 | 0.00 | 0.36 | 0.00 | 0.00 | 0.02 | 0.00 | 0.02 |
| drift 3-4 m/s | 39 | 0.67 | 0.68 | 82 | 1319 | 0.00 | 0.56 | 0.03 | 0.00 | 0.23 | 0.00 | 0.03 |
| drift 4-5 m/s | 36 | 0.72 | 0.73 | 72 | 1465 | 0.00 | 0.64 | 0.19 | 0.06 | 0.25 | 0.00 | 0.03 |
| circle | 150 | 0.95 | 0.97 | 17 | 86 | 0.20 | 0.43 | 0.93 | 0.19 | 0.91 | 0.00 | 0.00 |
| circle_group | 138 | 0.99 | 1.00 | 5 | 14 | 0.99 | 0.08 | 0.93 | 0.00 | 0.81 | 0.68 | 0.07 |
| ALL | 738 | 0.79 | 0.82 | 7 | 80 | 0.53 | 0.20 | 0.38 | 0.05 | 0.37 | 0.13 | 0.03 |

2026-10-20 (held out, final thresholds, 3 seeds): ALL recall 0.75 (0.81 observable, n=741),
TTD median 8 s, p90 106 s; offset 0.2-0.5 km 0.10; offset >= 2 km 0.90 (0.99 observable); circle 0.89 (0.97);
circle_group 0.99 (1.00); drift 0.39 (0.40). Full tables: `example_output/run_2026-10-20.log`
and `python3 summarize_results.py example_output/injection_results_2026-10-20.json`.

Precision. Alerts that overlap an injected episode (+5 min for the jump back when spoofing
stops) count as true. On injected vessels only 0-2 alerts per run fell outside episodes, but
that is optimistic by construction (vessels with alerts on clean data were excluded). Over
the whole picture, precision per run was 0.69-0.70 on 2026-11-03 and 0.64-0.65 on
2026-10-20, where every alert on the unaltered data counts as false. Those real-data alerts
are the honest false-alarm number; they are broken down below.

NMEA round trip: the last seed's injected vessels were encoded to AIVDM (msg 1 / 18 with
`\c:` tag-block timestamps) with pyais, decoded back with pyais and re-run: identical recall
and TTD table on both days (373,640 and 348,168 fixes).

What this says:
- Teleports above ~0.5 km are caught within one or two reports (median 5-6 s at the ~10 s
  Class A rate). 0.2-0.5 km offsets are below the noise-tolerant jump threshold and are
  essentially missed.
- Circles are caught mostly by the vessel's own reports: position-derived bearing stops
  matching the reported COG / gyro heading (0.93 of circle episodes) and the spread is far
  too small for the reported speed (0.91).
- The `cluster` signature fired in 0.68 of group episodes; the group episodes were all
  detected anyway because the move onto the shared circle was a jump. Clusters of 3 need
  3 members whose 10-min bins all pass the loiter test.
- Slow drift is the weak spot: 1-2 m/s drift is 0.10-0.11 recall. A drift that slowly adds a
  few knots looks like current or leeway to every rule here. Catching it needs an
  independent reference (radar, a second constellation, a shore-based range such as R-Mode,
  or a dead-reckoning prior from the ship's own log speed and gyro).

## What the detectors flag on unaltered real data

| | 2026-11-03 (4.4 h) | 2026-10-20 (4.4 h) |
|---|---|---|
| Class A + B tracks | 2,350 | 2,751 |
| Alerts / vessels | 132 / 61 | 159 / 70 |
| on_land alerts | 98 | 112 |
| jump alerts | 7 | 19 |
| mmsi_shared alerts | 0 (1 flag, on Class B MUNIN, counted under on_land) | 3 |
| weak-only alerts | 27 | 25 |
| Static MMSI anomalies (MMSIs) | 15 not-a-ship-MMSI, 1 placeholder | 12 not-a-ship-MMSI, 1 placeholder |

Looked at by hand:

- **on_land is almost all coastline resolution.** 2026-11-03: 56 alerts / 19 vessels in the
  Kiel Canal, 5 at the head of Flensburg fjord, 4 on the Gota alv at Gothenburg, 2 in the
  Trollhatte canal, plus harbours (Varberg, Fredericia, Nykobing) and lake Vanern on
  2026-10-20. Natural Earth 10m draws all of these as land. Requiring SOG >= 1 kn removed the
  moored vessels (204 => 42 on_land alerts on the first 2 h of 2026-11-03). Fix: a
  large-scale water mask (OSM water polygons or GSHHG full resolution) and a port polygon list.
- **One real inland anomaly: MMSI 219003959 "S 501 SOFIE"** (Class B). Moored at Hirtshals
  (57.5928 N 9.9620 E), then one report at 01:21:40 on 2026-11-03 at 57.4178 N 9.8688 E,
  20 km inland, SOG 14.5 kn, then back at the berth. Same pattern on 2026-10-20 (one report
  at 57.1959 N 9.7327 E, 13.5 kn). Fits a second transmitter on the same MMSI moving by
  road, or a corrupted report; the cause is not verified. In `fixtures/`.
- **MMSI conflict: 246843000 "MARFAAM".** On 2026-10-20 the same MMSI reports moored in
  Copenhagen (55.6866 N 12.6326 E, SOG 0) and underway at ~14 kn in the North Sea and off northern
  Scotland, alternating within minutes. Caught as `mmsi_shared`. In `fixtures/`.
- Other jumps: single far teleports (TAVASTLAND 739 km in 6 s, ROBIN HOOD 393 km in 4 s,
  LOLLAND 10 km in 13 s), consistent with corrupted single reports. None formed a cluster.
- Stale repeats: before `drop_stale_repeats()` there were 20 / 40 jump alerts; most were
  "same position twice, then a 0.5-1 km catch-up". 13 / 21 of them went away.
- Weak-only alerts: a guard vessel really circling at ~6 kn near Fehmarn Belt (GUARDIAN; its
  heading follows its COG, so `cog_mismatch` fired once, unlike injected circles), pilot
  boats, HSC and port tenders manoeuvring, moored Class B units with noisy SOG, and fishing
  net markers.
- Static MMSI anomalies: fishing-net / gear markers (`97000106` "KEEP CLEAR 0.25NM",
  `970010055`, `992190005` "FISHFARM 95%", `108100119` "NET-2-91%"), a coast-station style
  MMSI on a Class A unit (`2190045` "ESBJERG HARBOUR"), and `555555555` "AGGERSUNDBROEN"
  (a bridge).
- No crop-circle `cluster` fired on either day. No spoofing was found in these 8.8 h of
  Danish data; none was expected to be verified here.

pyais sample (`nmea_io.py stats`): 82,748 decoded messages, 2 `UnknownMessageException`,
73,602 position reports of which 1,055 had position-not-available, 11,075 MMSIs; identity flags
(per MMSI and station class): 161 not-a-ship, 17 placeholder, 2 bad-MID, 2 over-length. It has no timestamps, so it
is only used for decoding and identity checks.

## Output

- `example_output/real_alerts.geojson` - per alert: `suspect_track` LineString, last flagged
  position, last pre-alert position (properties: MMSI, name, ship type, detector counts).
- `example_output/real_alerts.cot.xml` - one CoT event per alert, built with
  `../mavlink-to-tak-cot/cot.py` (imported unchanged): type `a-u-S` (unknown surface), uid
  `ais-<MMSI>`, point at the last fix before the alert, flagged position and detectors in
  `<remarks>`, stale 10 min. A list of events in an `<events>` wrapper; send them one by one
  with `pytak` or the UDP sender in `../interference-geolocation-to-tak/tak_out.py`.
- `example_output/injected_alerts_first20.cot.xml`, `injection_results_*.json`, `run_*.log`.

Not done: loading the CoT in ATAK/WinTAK (XML parses with ElementTree only), and live
ingestion (`pyais.stream.TCPConnection` on an AIS-catcher or Kystverket feed would feed
`nmea_io.rows_to_tracks` with receive timestamps; not run).

## Files

- `detectors.py` - all detectors, alert aggregation (stdlib).
- `geo.py` - haversine, bearing, destination, circumradius (stdlib).
- `inject.py`, `evaluate.py`, `summarize_results.py` - ground truth and scoring (stdlib).
- `export.py` - GeoJSON and CoT (stdlib + sibling `cot.py`).
- `dma.py` - partial download (stdlib) and pandas loader.
- `land.py` - Natural Earth on-land mask (pyshp + shapely).
- `nmea_io.py` - pyais decode / encode with tag-block timestamps.
- `run.py` - CLI tying it together.
- `test_detectors.py` - 19 stdlib unit tests on synthetic fixtures and two real DMA excerpts
  (`fixtures/dma_excerpts.csv`, 49 rows, DMA data).

## Limitations

- Thresholds were tuned on 2026-11-03 (loiter ratio 4 => 2 => 1.5, on-land SOG gate, stale
  repeat filter) and checked once on 2026-10-20; no larger held-out set.
- Injected spoofing is geometric. Real spoofed receivers also show clock jumps, C/N0 changes
  and SOG / COG computed from the spoofed signal; when a spoofer also fakes consistent
  velocity, the SOG / COG checks lose their power and only heading (gyro) stays independent.
- 10-min aligned bins: a loiter episode shorter than ~15 min may not fill a bin.
- DMA timestamps are receive times at base stations; delayed reports cause the stale-repeat
  artifacts above.
- Vessel-type speed limits are rough; SAR, HSC and military craft get loose limits.
