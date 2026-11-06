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

**Concepts:** [Jamming and spoofing](../concepts/gnss-interference.md), [Situational awareness and C2 interop](../concepts/situational-awareness.md), [Datasets and benchmarks](../concepts/datasets-benchmarks.md), [Electronic warfare resilience](../concepts/ew-resilience.md)

**Tags:** `ads-b`, `nic`, `map`, `osint`, `gpsjam`, `jamming`

## Related

- uses: [readsb](../repos/wiedehopf__readsb.md)
- uses: [ADSBCOT](../repos/snstac__adsbcot.md)

## Referenced by

- [Bellingcat OSINT Toolkit - GPSJam](../resources/bellingcat-toolkit-gpsjam.md) (explains)
- [ADS-B Data Analysis for GNSS Interference Mapping](../resources/insidegnss-adsb-interference-mapping.md) (explains)
- [Неоднозначный сигнал](../resources/novayagazeta-gnss-interference-europe-2025.md) (cites)
- [OSINT interference map from free data: ADS-B NACp hexes and Sentinel-1 C-band RFI over Kaliningrad / the SE Baltic](../samples/osint-jamming-map.md) (explains)

_Indexed by lane(s): defense-context, docs-standards, gnss_
