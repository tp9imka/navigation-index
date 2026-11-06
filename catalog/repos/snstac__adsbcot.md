# ADSBCOT

`repo:snstac/adsbcot` - <https://github.com/snstac/adsbcot>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1 | Python | Apache-2.0 | 2026-10-23 | False | production | high |

Gateway that converts ADS-B traffic from dump1090/readsb or aggregator APIs into Cursor-on-Target so aircraft show in TAK.

**Why it matters:** ADS-B also carries NIC/NACp integrity fields - the same signal GPSJam uses - so this is a ready bridge for a live GNSS-interference overlay.

**Hackathon notes:** Run alongside readsb on an RTL-SDR; add a filter that flags low NIC aircraft as an interference indicator.

## Deep dives

- [snstac__adsbcot](../../docs/integration-cards/snstac__adsbcot.md) (integration-cards)

**Concepts:** [Situational awareness and C2 interop](../concepts/situational-awareness.md), [Jamming and spoofing](../concepts/gnss-interference.md), [Counter-UAS and drone detection](../concepts/counter-uas.md)

**Tags:** `ads-b`, `tak`, `cot`, `sdr`

**Domains:** air

## Related

- depends_on: [PyTAK](../repos/snstac__pytak.md)
- integrates_with: [readsb](../repos/wiedehopf__readsb.md)
- integrates_with: [dump1090-fa](../repos/flightaware__dump1090.md)

## Referenced by

- [Stone Soup](../repos/dstl__stone-soup.md) (integrates_with)
- [PyTAK](../repos/snstac__pytak.md) (same_org)
- [readsb](../repos/wiedehopf__readsb.md) (integrates_with)
- [GPSJam - daily GPS interference map](../resources/gpsjam-org.md) (uses)

_Indexed by lane(s): defense-context, planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
