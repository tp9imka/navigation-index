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

**Concepts:** [Situational awareness and C2 interop](../concepts/situational-awareness.md), [Jamming and spoofing](../concepts/gnss-interference.md), [Counter-UAS and drone detection](../concepts/counter-uas.md), [Software-defined GNSS receivers](../concepts/gnss-sdr.md)

**Tags:** `ads-b`, `mode-s`, `rtl-sdr`, `decoder`

**Domains:** air

## Related

- alternative_to: [dump1090-fa](../repos/flightaware__dump1090.md)
- integrates_with: [tar1090](../repos/wiedehopf__tar1090.md)
- integrates_with: [ADSBCOT](../repos/snstac__adsbcot.md)

## Referenced by

- [dump1090-fa](../repos/flightaware__dump1090.md) (alternative_to)
- [pyModeS](../repos/junzis__pymodes.md) (integrates_with)
- [ADSBCOT](../repos/snstac__adsbcot.md) (integrates_with)
- [tar1090](../repos/wiedehopf__tar1090.md) (depends_on)
- [GPSJam - daily GPS interference map](../resources/gpsjam-org.md) (uses)
- [GNSS interference monitor from u-blox telemetry and ADS-B NACp](../samples/gnss-interference-monitor.md) (uses)

_Indexed by lane(s): defense-context, planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
