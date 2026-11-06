# ADSBCOT

`repo:snstac/adsbcot` - <https://github.com/snstac/adsbcot>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1 | Python | Apache-2.0 | 2026-10-23 | False | production | high |

Gateway that converts ADS-B traffic from dump1090/readsb or aggregator APIs into Cursor-on-Target so aircraft show in TAK.

**Why it matters:** ADS-B also carries NIC/NACp integrity fields - the same signal GPSJam uses - so this is a ready bridge for a live GNSS-interference overlay.

**Hackathon notes:** Run alongside readsb on an RTL-SDR; add a filter that flags low NIC aircraft as an interference indicator.

## Deep dives

- [_index-round3](../../docs/integration-cards/_index-round3.md) (integration-cards)
- [snstac__adsbcot](../../docs/integration-cards/snstac__adsbcot.md) (integration-cards)

**Concepts:** [Situational awareness and C2 interop](../../catalog/concepts/situational-awareness.md), [Jamming and spoofing](../../catalog/concepts/gnss-interference.md), [Counter-UAS and drone detection](../../catalog/concepts/counter-uas.md)

**Tags:** `ads-b`, `tak`, `cot`, `sdr`

**Domains:** air

## Related

- depends_on: [PyTAK](../../catalog/repos/snstac__pytak.md)
- integrates_with: [readsb](../../catalog/repos/wiedehopf__readsb.md)
- integrates_with: [dump1090-fa](../../catalog/repos/flightaware__dump1090.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [Stone Soup](../../catalog/repos/dstl__stone-soup.md) (integrates_with)
- [PyTAK](../../catalog/repos/snstac__pytak.md) (same_org)
- [readsb](../../catalog/repos/wiedehopf__readsb.md) (integrates_with)
- [ADS-B Exchange free monthly sample data (readsb-hist)](../../catalog/resources/adsbexchange-monthly-samples.md) (has_code)
- [GPSJam - daily GPS interference map](../../catalog/resources/gpsjam-org.md) (uses)

_Indexed by lane(s): defense-context, planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
