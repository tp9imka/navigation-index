# DragonSync

`repo:alphafox02/dragonsync` - <https://github.com/alphafox02/DragonSync>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 99 | Python | Apache-2.0 | 2026-10-28 | False | active-research | high |

Gateway that takes drone Remote ID / DroneID detections from WarDragon-style sensors and publishes them as CoT to TAK and other outputs.

**Why it matters:** Working example of a passive drone-detection to common-operating-picture pipeline.

**Hackathon notes:** Read it as a reference architecture even without the WarDragon kit; reuse its CoT mapping for your own detector.

## Deep dives

- [_index-round3](../../docs/integration-cards/_index-round3.md) (integration-cards)
- [alphafox02__dragonsync](../../docs/integration-cards/alphafox02__dragonsync.md) (integration-cards)

**Concepts:** [Counter-UAS and drone detection](../concepts/counter-uas.md), [Situational awareness and C2 interop](../concepts/situational-awareness.md)

**Tags:** `remote-id`, `tak`, `cot`, `sensor-gateway`, `droneid`, `adsb`

**Domains:** air, dismounted

## Related

- integrates_with: [Open Drone ID Core C](../repos/opendroneid__opendroneid-core-c.md)
- integrates_with: [PyTAK](../repos/snstac__pytak.md)
- integrates_with: [FreeTAKServer](../repos/freetakteam__freetakserver.md)
- same_org: [WarDragon docs](../repos/alphafox02__wardragon.md)
- integrates_with: [samples2djidroneid](../repos/anarkiwi__samples2djidroneid.md)

## Referenced by

- [WarDragon docs](../repos/alphafox02__wardragon.md) (same_org)
- [FreeTAKServer](../repos/freetakteam__freetakserver.md) (integrates_with)
- [Open Drone ID Core C](../repos/opendroneid__opendroneid-core-c.md) (alternative_to)

_Indexed by lane(s): defense-context, domains-swarm_

_GitHub metadata fetched 2026-11-06._
