# GPSJam - daily GPS interference map

`res:gpsjam-org` - dataset - <https://gpsjam.org/faq/>

**By:** John Wiseman - **Year:** 2022 - **Level:** intro - **Access:** open

Daily world map of likely GPS interference derived from ADS-B navigation-integrity reports (NIC/NACp) aggregated into hexagons from community flight-tracking data. The FAQ documents the method and its blind spots.

## Key takeaways

- Interference is inferred from aircraft self-reported integrity, not measured RF
- Empty cells mean no data, not no jamming
- Easy to reproduce with your own ADS-B receiver
- Derived from ADS-B NIC/NACp degradation
- Hex-binned daily snapshots
- Shows persistent interference zones (Baltic, Middle East, Black Sea)
- Method is indirect: inferred from aircraft-reported accuracy

## Deep dives

- [adsbexchange-samples](../../docs/dataset-cards/adsbexchange-samples.md) (dataset-cards)

**Concepts:** [Jamming and spoofing](../../catalog/concepts/gnss-interference.md), [Situational awareness and C2 interop](../../catalog/concepts/situational-awareness.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md), [Electronic warfare resilience](../../catalog/concepts/ew-resilience.md)

**Tags:** `ads-b`, `nic`, `map`, `osint`, `gpsjam`, `jamming`

## Related

- uses: [readsb](../../catalog/repos/wiedehopf__readsb.md)
- uses: [ADSBCOT](../../catalog/repos/snstac__adsbcot.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [1. PNT fundamentals](../../docs/primer/01-pnt-fundamentals.md) (mentions)
- [2. GNSS and its threats](../../docs/primer/02-gnss-and-threats.md) (mentions)
- [7. Maps, geodesy and planning](../../docs/primer/07-maps-geodesy-planning.md) (mentions)
- [9. Evaluation and datasets](../../docs/primer/09-evaluation-and-datasets.md) (mentions)
- [Bellingcat OSINT Toolkit - GPSJam](../../catalog/resources/bellingcat-toolkit-gpsjam.md) (explains)
- [ADS-B Data Analysis for GNSS Interference Mapping](../../catalog/resources/insidegnss-adsb-interference-mapping.md) (explains)
- [Неоднозначный сигнал](../../catalog/resources/novayagazeta-gnss-interference-europe-2025.md) (cites)
- [OSINT interference map from free data: ADS-B NACp hexes and Sentinel-1 C-band RFI over Kaliningrad / the SE Baltic](../../catalog/samples/osint-jamming-map.md) (explains)

_Indexed by lane(s): defense-context, docs-standards, gnss_
