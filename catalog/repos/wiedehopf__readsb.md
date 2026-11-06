# readsb

`repo:wiedehopf/readsb` - <https://github.com/wiedehopf/readsb>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 706 | C | NOASSERTION | 2026-11-04 | False | production | high |

ADS-B/Mode S decoder for RTL-SDR and other receivers with networking, JSON output, MLAT support and aggregation features.

**Why it matters:** Gives a team its own receiver for aircraft positions and navigation-integrity reports, the raw material for crowd-sourced jamming maps.

**Hackathon notes:** Install on a Pi with a cheap RTL-SDR and 1090 MHz antenna; JSON output is easy to parse for NIC/NACp statistics.

## Deep dives

- [_index-flight-c2](../../docs/integration-cards/_index-flight-c2.md) (integration-cards)
- [wiedehopf__readsb](../../docs/integration-cards/wiedehopf__readsb.md) (integration-cards)
- [adsbexchange-samples](../../docs/dataset-cards/adsbexchange-samples.md) (dataset-cards)

**Concepts:** [Situational awareness and C2 interop](../../catalog/concepts/situational-awareness.md), [Jamming and spoofing](../../catalog/concepts/gnss-interference.md), [Counter-UAS and drone detection](../../catalog/concepts/counter-uas.md), [Software-defined GNSS receivers](../../catalog/concepts/gnss-sdr.md)

**Tags:** `ads-b`, `mode-s`, `rtl-sdr`, `decoder`

**Domains:** air

## Related

- alternative_to: [dump1090-fa](../../catalog/repos/flightaware__dump1090.md)
- integrates_with: [tar1090](../../catalog/repos/wiedehopf__tar1090.md)
- integrates_with: [ADSBCOT](../../catalog/repos/snstac__adsbcot.md)

## Referenced by

- [Export control and ethics](../../docs/export-control-and-ethics.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Learning paths](../../docs/learning-paths.md) (mentions)
- [2. GNSS and its threats](../../docs/primer/02-gnss-and-threats.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [dump1090-fa](../../catalog/repos/flightaware__dump1090.md) (alternative_to)
- [pyModeS](../../catalog/repos/junzis__pymodes.md) (integrates_with)
- [ADSBCOT](../../catalog/repos/snstac__adsbcot.md) (integrates_with)
- [tar1090](../../catalog/repos/wiedehopf__tar1090.md) (depends_on)
- [ADS-B Exchange free monthly sample data (readsb-hist)](../../catalog/resources/adsbexchange-monthly-samples.md) (has_code)
- [GPSJam - daily GPS interference map](../../catalog/resources/gpsjam-org.md) (uses)
- [GNSS interference monitor from u-blox telemetry and ADS-B NACp](../../catalog/samples/gnss-interference-monitor.md) (uses)
- [OSINT interference map from free data: ADS-B NACp hexes and Sentinel-1 C-band RFI over Kaliningrad / the SE Baltic](../../catalog/samples/osint-jamming-map.md) (uses)

_Indexed by lane(s): defense-context, planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
