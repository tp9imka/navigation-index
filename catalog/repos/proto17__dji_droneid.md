# dji_droneid

`repo:proto17/dji_droneid` - <https://github.com/proto17/dji_droneid>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 552 | MATLAB | MIT | 2024-05-27 | False | research-prototype | low |

Original reverse engineering of DJI DroneID with MATLAB/Octave scripts that demodulate frames, C++ turbo-code helpers and a GNU Radio correlation test flowgraph.

**Why it matters:** Foundational work behind open DJI DroneID decoders.

**Build notes:** Use for understanding the PHY; prefer samples2djidroneid for decoding.

## Deep dives

- [remote-id-droneid-captures](../../docs/dataset-cards/remote-id-droneid-captures.md) (dataset-cards)

**Concepts:** [Counter-UAS and drone detection](../../catalog/concepts/counter-uas.md)

**Tags:** `dji`, `droneid`, `gnuradio`, `matlab`

**Domains:** air

## Related

- alternative_to: [samples2djidroneid](../../catalog/repos/anarkiwi__samples2djidroneid.md)

## Referenced by

- [Competition playbook: navigation and PNT under GNSS denial](../../docs/competition-playbook.md) (mentions)
- [Dataset cards](../../docs/dataset-cards/README.md) (mentions)
- [The first three hours](../../docs/first-three-hours.md) (mentions)
- [Brief decoder](../../docs/problem-statement-decoder.md) (mentions)
- [samples2djidroneid](../../catalog/repos/anarkiwi__samples2djidroneid.md) (extends)

_Indexed by lane(s): domains-swarm_

_GitHub metadata fetched 2026-11-16._
