# pyModeS

`repo:junzis/pymodes` - <https://github.com/junzis/pymodes>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 673 | Python | GPL-3.0 | 2026-10-30 | False | production | high |

Python decoder for Mode S and ADS-B messages including Comm-B / EHS fields, with live streaming tools.

**Why it matters:** Decode raw Mode S yourself, including derived wind and airspeed data; underlies The 1090MHz Riddle book.

**Hackathon notes:** pip install pyModeS now installs the v3 rewrite (Python 3.11+): a single decode() call plus a stateful PipeDecoder for streams, and a modes CLI. Older tutorials and The 1090MHz Riddle use the v2 pms.adsb.* API; pin pyModeS<3 to follow them. Pairs with a Beast/raw feed from readsb.

## Deep dives

- [_index-round5-c2-gis](../../docs/integration-cards/_index-round5-c2-gis.md) (integration-cards)
- [junzis__pymodes](../../docs/integration-cards/junzis__pymodes.md) (integration-cards)

**Concepts:** [Situational awareness and C2 interop](../../catalog/concepts/situational-awareness.md), [Standards and interface specs](../../catalog/concepts/standards.md)

**Tags:** `mode-s`, `ads-b`, `python`

**Domains:** air

## Related

- integrates_with: [traffic](../../catalog/repos/xoolive__traffic.md)
- integrates_with: [readsb](../../catalog/repos/wiedehopf__readsb.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [traffic](../../catalog/repos/xoolive__traffic.md) (depends_on)
- [The 1090 Megahertz Riddle: A Guide to Decoding Mode S and ADS-B Signals](../../catalog/resources/junzis-1090mhz-riddle.md) (has_code)

_Indexed by lane(s): planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
