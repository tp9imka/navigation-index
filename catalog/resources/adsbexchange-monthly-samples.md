# ADS-B Exchange free monthly sample data (readsb-hist)

`res:adsbexchange-monthly-samples` - dataset - <https://www.adsbexchange.com/data-products/sample-data/>

**By:** ADS-B Exchange - **Year:** ? - **Level:** intermediate - **Access:** open

ADS-B Exchange publishes its complete global feed for the 1st day of each month free of charge, as gzipped readsb aircraft.json snapshots every 5 s. Each aircraft entry carries quality fields such as NACp and NIC plus MLAT flags, which is enough to rebuild a GPSJam-style GNSS interference map for any past 1st-of-month. No open licence is named; the site's terms of use apply.

## Key takeaways

- Only the 1st of each month is published, appearing about 1.5 days later
- Each global snapshot is about 5 MB gzipped; filter to a bbox while downloading
- Low NACp says 'degraded', not why; under spoofing the reported position is itself false
- Check the terms before redistributing raw snapshots; commit derived aggregates instead

## Deep dives

- [adsbexchange-samples](../../docs/dataset-cards/adsbexchange-samples.md) (dataset-cards)

**Concepts:** [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md), [Jamming and spoofing](../../catalog/concepts/gnss-interference.md), [Situational awareness and C2 interop](../../catalog/concepts/situational-awareness.md)

**Tags:** `ads-b`, `readsb`, `nacp`, `gnss-jamming-map`, `osint`, `aviation`

## Related

- dataset_for: [OSINT interference map from free data: ADS-B NACp hexes and Sentinel-1 C-band RFI over Kaliningrad / the SE Baltic](../../catalog/samples/osint-jamming-map.md)
- has_code: [readsb](../../catalog/repos/wiedehopf__readsb.md)
- has_code: [ADSBCOT](../../catalog/repos/snstac__adsbcot.md)

_Indexed by lane(s): datasets-used_
