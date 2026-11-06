# Danish Maritime Authority historical AIS

<!-- about: res:dma-historical-ais, sample:maritime-ais-spoofing, sample:usv-gnss-denied-nav, repo:m0r13n/pyais -->

Daily CSV dumps of all AIS messages received by the Danish Maritime Authority's shore network: Danish waters and approaches (Skagerrak, Kattegat, the belts, western Baltic, part of the North Sea). Free, no login, one zip per UTC day. This dataset has no index id of its own; the marker above names the samples and decoder that use it.

| Field | Value |
|---|---|
| Platform | Shore base stations receiving ship-borne AIS (Class A, Class B, AtoN, base stations, SART) |
| Environment | Danish waters; dense traffic incl. Kiel Canal approaches, Oresund, Fehmarn Belt |
| Sensors and rates | One row per received report: receive timestamp (1 s), MMSI, type of mobile, lat/lon, SOG, COG, heading, ship type, length, name and other static fields. Class A reports every few seconds underway |
| Ground truth | None. Positions are what each ship's own GNSS reported; timestamps are receive times at base stations |
| Size | `aisdk-2026-11-03.zip` = 624,618,400 B (HEAD Content-Length, 2026-11-06); the sample saw 0.5-0.9 GB zipped per day and about 3+ GB of CSV unzipped |
| License | Free reuse under the Danish PSI act, commercial or not, with the attribution "Contains data from the Danish Maritime Authority that is used in accordance with the conditions for the use of Danish public data"; as-is ([DMA conditions](https://dma.dk/safety-at-sea/navigational-information/download-data/conditions-for-the-use-of-data), as read by the sample) |
| Format | Zip with one CSV, comma-separated, timestamp `dd/mm/YYYY HH:MM:SS`, roughly time-ordered |
| Index | [maritime-ais-spoofing sample](../../samples/maritime-ais-spoofing/), [usv-gnss-denied-nav sample](../../samples/usv-gnss-denied-nav/), [pyais](../../catalog/repos/m0r13n__pyais.md) |

## Download

```bash
# whole day (about 0.6 GB)
curl -O http://aisdata.ais.dk/aisdk-2026-11-03.zip
# first 100 MiB only, inflated into the first ~4.4 h of the day (HTTP Range + raw deflate)
python3 samples/maritime-ais-spoofing/dma.py --date 2026-11-03 --mb 100 --out-dir data
```

The partial trick works because the zip holds a single deflate stream that starts right after the local file header: `dma.py` reads the header length, inflates whatever arrived and cuts at the last newline.

## Used in this repo

- [samples/maritime-ais-spoofing](../../samples/maritime-ais-spoofing/), run 2026-11-06. Two days, 100 MB range each: 2026-11-03 (100,000,000 of 624,618,400 B => 2,799,513 rows, 00:00-04:23 UTC, 2,540 MMSIs) and 2026-10-20 (104,857,600 of 595,847,268 B => 2,992,461 rows, 3,044 MMSIs). Range fetch about 110 s. Detectors over 1.7 M fixes in 5 s.
- [samples/usv-gnss-denied-nav](../../samples/usv-gnss-denied-nav/) `fetch_data.py ais`: cuts 75 min of 2026-10-20 (02:00-03:15 UTC) to its chart bbox as radar targets; reuses `dma.py` when no local CSV is given.
- Cleaning facts measured by the AIS sample: about 1.08 M of 2.8 M rows are exact duplicates (one report heard by several base stations); lat 91 / lon 181 / 0,0 mean "not available"; some old reports are re-delivered with a new receive time, which reads as a halt plus a catch-up teleport.

## Loading and tooling

- pandas: `dma.load_frame()` in the sample (column map, timestamp parse, de-duplication), then `frame_to_tracks()`.
- Raw NMEA instead of CSV: [pyais](../../catalog/repos/m0r13n__pyais.md) decode / encode; the sample round-trips injected tracks through AIVDM with tag-block timestamps.

## Hackathon fit

- Idea 3 (AIS track-plausibility spoofing detector) and idea 12 (maritime position integrity): real traffic picture with no login, plus injected spoofing episodes for ground truth.
- Radar-target stand-in for maritime GNSS-denied navigation demos (as the USV sample does).

## Pitfalls

- Natural Earth 10 m land draws the Kiel Canal, fjord heads and harbours as land: almost all "on land" alerts in the sample were coastline resolution. Use a large-scale water mask.
- No spoofing was found in 8.8 h of 2026 Danish data; real spoofing episodes have to be injected or taken from other regions.
- Receive-time stamps, not transmit time. Delayed reports create artefacts in any speed or jump test.
- Plain HTTP host. Tried and not used by the sample: NOAA MarineCadastre (`AIS_2024_01_01.zip` returned 404) and the Kystverket open NMEA stream (TCP timed out).

## Sources

- HEAD on `http://aisdata.ais.dk/aisdk-2026-11-03.zip`, 2026-11-06
- samples/maritime-ais-spoofing/README.md and `dma.py`; samples/usv-gnss-denied-nav/README.md and `fetch_data.py`
