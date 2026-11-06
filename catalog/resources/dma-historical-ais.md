# Danish Maritime Authority historical AIS data

`res:dma-historical-ais` - dataset - <https://dma.dk/safety-at-sea/navigational-information/ais-data>

**By:** Danish Maritime Authority - **Year:** ? - **Level:** intermediate - **Access:** open

Daily zip files, one CSV per UTC day, holding every AIS report received by the Danish shore network across Danish waters and approaches (Skagerrak, Kattegat, the belts, western Baltic). Free download over plain HTTP from aisdata.ais.dk with no account; a day is roughly 0.5-0.9 GB zipped. Positions are whatever each ship's own GNSS reported, stamped with base-station receive time.

## Key takeaways

- No login, one zip per day; a single deflate stream lets you HTTP-Range the first N MB and inflate a partial day
- Heavy duplication (one report heard by several stations) and 91/181/0,0 'not available' positions need cleaning first
- No ground truth for spoofing: inject episodes yourself; receive-time stamps create speed and jump artefacts
- Reuse under Danish public-data conditions with the DMA attribution sentence

## Deep dives

- [dma-ais](../../docs/dataset-cards/dma-ais.md) (dataset-cards)

**Concepts:** [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md), [Maritime navigation](../../catalog/concepts/maritime-nav.md), [Jamming and spoofing](../../catalog/concepts/gnss-interference.md), [Situational awareness and C2 interop](../../catalog/concepts/situational-awareness.md)

**Tags:** `ais`, `maritime`, `baltic`, `csv`, `spoofing-detection`, `no-login`

## Related

- dataset_for: [GNSS spoofing signatures in real AIS tracks: detectors, injected ground truth, GeoJSON and CoT](../../catalog/samples/maritime-ais-spoofing.md)
- dataset_for: [USV own-ship navigation under GNSS spoofing: radar-to-chart fixes and an integrity monitor in the Oresund](../../catalog/samples/usv-gnss-denied-nav.md)
- has_code: [pyais](../../catalog/repos/m0r13n__pyais.md)
- uses: [ITU-R M.1371-6 - Technical characteristics for VHF automatic identification system using time division multiple access in the maritime mobile service](../../catalog/resources/itu-r-m1371-ais.md)

_Indexed by lane(s): datasets-used_
