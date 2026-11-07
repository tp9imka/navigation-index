# Sample: GNSS spoofing signatures in real AIS tracks: detectors, injected ground truth, GeoJSON and CoT

`sample:maritime-ais-spoofing` - code and walkthrough in [samples/maritime-ais-spoofing](../../samples/maritime-ais-spoofing/)

Shore-side detection of GNSS spoofing from the AIS picture, on real Danish Maritime Authority AIS (partial HTTP-range download of a daily file, ~4.4 h, 1.7 M fixes, 2.5-3 k vessels). Stdlib detectors for teleports, vessel-type speed limits, position-derived vs reported SOG/COG/heading, turn radius vs ship length, loitering-while-underway, crop-circle clusters of vessels on one point, on-land positions (Natural Earth 10m, eroded) and MMSI anomalies including one MMSI on two transmitters. Offset, drift, single-circle and group crop-circle episodes are injected into real tracks to measure recall and time-to-detect (offsets >= 2 km and circles ~0.9-1.0 recall, median TTD 5-17 s; slow 1-2 m/s drift ~0.1). Alerts on unaltered data are broken down by hand (coastline artifacts, a real MMSI conflict, an inland Class B report). pyais handles raw NMEA decode and an encode/decode round trip; flagged vessels export as GeoJSON and Cursor-on-Target via the mavlink-to-tak-cot builder. Public incidents (Black Sea 2017, C4ADS 2019, SkyTruth 2025, Baltic 2025) are cited.

**Verification:** Ran 2026-11-06: run.py with python 3.12.14 (pyais 3.3.1, pandas 3.1.1, shapely 2.2.0, pyshp 3.1.6) on DMA AIS 2026-11-03 and 2026-10-20 (first ~100 MB of each zip), 3 injection seeds per day, plus a pyais NMEA encode/decode round trip with identical scores; nmea_io.py stats on the pyais tests/nmea-sample file; 19 stdlib unit tests pass on python 3.14.7, and disabling the jump, cluster, turn, on-land or SOG checks makes tests fail. Not done: CoT shown in an ATAK/WinTAK client, live NMEA stream ingestion (Kystverket stream unreachable from this network), NOAA MarineCadastre data. No real spoofing event was found in the 8.8 h analysed; detection numbers come from injected episodes.

## Practical readiness

| Compute | Hardware | Offline | Setup | Dataset download | Tested platforms | Validation |
|---|---|---|---|---|---|---|
| unknown | unknown | unknown | unknown | unknown | unknown | unverified |

**Main limitation:** Read the sample verification; readiness has not been curated.

## Deep dives

- [dma-ais](../../docs/dataset-cards/dma-ais.md) (dataset-cards)

**Concepts:** [Maritime navigation](../../catalog/concepts/maritime-nav.md), [Jamming and spoofing](../../catalog/concepts/gnss-interference.md), [Situational awareness and C2 interop](../../catalog/concepts/situational-awareness.md), [Electronic warfare resilience](../../catalog/concepts/ew-resilience.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md)

**Tags:** `ais`, `spoofing`, `crop-circles`, `ship-on-land`, `nmea`, `aivdm`, `pyais`, `danish-maritime-authority`, `natural-earth`, `mmsi`, `anomaly-detection`, `cot`, `tak`, `geojson`, `stdlib`

## Related

- uses: [pyais](../../catalog/repos/m0r13n__pyais.md)
- explains: [AIS-catcher](../../catalog/repos/jvde-github__ais-catcher.md)
- explains: [noaadata](../../catalog/repos/schwehr__noaadata.md)
- explains: [OpenCPN](../../catalog/repos/opencpn__opencpn.md)
- explains: [PyTAK](../../catalog/repos/snstac__pytak.md)
- explains: [Above Us Only Stars: Exposing GPS Spoofing in Russia and Syria](../../catalog/resources/c4ads-above-us-only-stars.md)
- explains: [2025 Was a Stress Test & Maritime AI™ Is the Only Way to Pass](../../catalog/resources/windward-2025-maritime-stress-test.md)
- explains: [ITU-R M.1371-6 - Technical characteristics for VHF automatic identification system using time division multiple access in the maritime mobile service](../../catalog/resources/itu-r-m1371-ais.md)
- explains: [R-Mode Baltic and R-Mode Baltic 2](../../catalog/resources/dlr-r-mode-baltic.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [Danish Maritime Authority historical AIS data](../../catalog/resources/dma-historical-ais.md) (dataset_for)
- [Natural Earth vector data](../../catalog/resources/natural-earth-vectors.md) (dataset_for)

_Indexed by lane(s): samples_
