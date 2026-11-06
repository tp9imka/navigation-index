# Sample: OSINT interference map from free data: ADS-B NACp hexes and Sentinel-1 C-band RFI over Kaliningrad / the SE Baltic

`sample:osint-jamming-map` - code and walkthrough in [samples/osint-jamming-map](../../samples/osint-jamming-map/)

Two no-login OSINT layers for the same area and morning (2026-10-01, SE Baltic around Kaliningrad). ADS-B: the ADS-B Exchange free readsb-hist sample (1st of each month) is cut to a bbox and binned into H3 hexes with the GPSJam percentage formula on aircraft-reported NACp. Sentinel-1: an 18-scene GRD stack of one relative orbit from Microsoft Planetary Computer, scored two ways - ESA's own per-swath RFI annotation (rfiDetected, KL divergence, in-band/out-band power) and a port of zephr-xyz/sentinel1-rfi-detection's temporal z-score on VH backscatter. Outputs a GeoJSON loadable by templates/demo-dashboard, navdash/1 point tracks of the aircraft reports, and a PNG map.

**Verification:** ran on 2026-11-06 with Python 3.13.15 (macOS arm64) against live public data, no credentials: adsb_hexmap.py pulled 121 ADS-B Exchange snapshots (2026-10-01 03:51-05:51 UTC, 60 s step) => 110 of 129 classified aircraft NACp<8, 64 red hexes, 0 green; control run over NL/DE (13 snapshots, 600 s step) => 19 of 879 bad, 108 green hexes. s1_rfi.py processed 18 S1C/S1D GRD scenes of relative orbit 51 (2026-07-15..2026-10-31, VH at 1/8 resolution, Copernicus DEM slope mask): target scene 2026-10-01 04:51 UTC had 0.128% of pixels at z>3 and 0 candidate hexes; ESA rfiDetected on 9 of 18 dates, one IW3 strip NW of the Sambia peninsula on 6 dates. make_map.py wrote zones.geojson + map.png; the dashboard loaded the manifest in headless Chrome (screenshot out/dashboard.png). 8 offline unit tests pass. Not verified: any link between the C-band RFI and GNSS jammers, land/sea separation, other regions or dates beyond 2026-08-14 (rerun: 38 candidate hexes, 25 of them centred over water per Natural Earth 50m, incl. 8 of the 10 strongest).

## Deep dives

- [adsbexchange-samples](../../docs/dataset-cards/adsbexchange-samples.md) (dataset-cards)
- [copernicus-glo30](../../docs/dataset-cards/copernicus-glo30.md) (dataset-cards)
- [sentinel-1-grd](../../docs/dataset-cards/sentinel-1-grd.md) (dataset-cards)

**Concepts:** [Jamming and spoofing](../../catalog/concepts/gnss-interference.md), [Situational awareness and C2 interop](../../catalog/concepts/situational-awareness.md), [Electronic warfare resilience](../../catalog/concepts/ew-resilience.md), [GIS, maps and geospatial data](../../catalog/concepts/gis-mapping.md)

**Tags:** `osint`, `ads-b`, `nacp`, `nic`, `gpsjam`, `h3`, `adsbexchange`, `readsb-hist`, `sentinel-1`, `sar`, `rfi`, `c-band`, `planetary-computer`, `stac`, `kaliningrad`, `baltic`, `geojson`

## Related

- uses: [Sentinel-1 RFI detection](../../catalog/repos/zephr-xyz__sentinel1-rfi-detection.md)
- uses: [pystac-client](../../catalog/repos/stac-utils__pystac-client.md)
- uses: [readsb](../../catalog/repos/wiedehopf__readsb.md)
- explains: [GPSJam - daily GPS interference map](../../catalog/resources/gpsjam-org.md)
- uses: [Copernicus DEM on AWS Open Data](../../catalog/resources/copernicus-dem-aws.md)
- explains: [GNSS interference report: Russia 2024/2025 - Part 1: Kaliningrad and the Baltic Sea](../../catalog/resources/spire-gnss-interference-russia-kaliningrad.md)
- explains: [GNSS interference monitor from u-blox telemetry and ADS-B NACp](../../catalog/samples/gnss-interference-monitor.md)

## Referenced by

- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [ADS-B Exchange free monthly sample data (readsb-hist)](../../catalog/resources/adsbexchange-monthly-samples.md) (dataset_for)
- [Natural Earth vector data](../../catalog/resources/natural-earth-vectors.md) (dataset_for)
- [Sentinel-1 Level-1 GRD on Microsoft Planetary Computer](../../catalog/resources/sentinel-1-grd-planetary-computer.md) (dataset_for)

_Indexed by lane(s): samples_
