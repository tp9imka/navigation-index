# GPS-SDR-SIM

`repo:osqzss/gps-sdr-sim` - <https://github.com/osqzss/gps-sdr-sim>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 3,474 | C | MIT | 2025-01-26 | True | archived | high |

Generates GPS L1 C/A baseband IQ sample files for a user-defined static or moving trajectory from a broadcast ephemeris file, for playback through an SDR.

**Why it matters:** The standard open test-signal generator for evaluating receiver behavior under simulated or spoofed conditions. Cabled or shielded-enclosure use only: radiating GNSS signals over the air is illegal in most jurisdictions.

**Hackathon notes:** Generate IQ files and feed GNSS-SDR directly (no RF needed) to test detectors. Repository archived in 2025 but still works. Cabled or shielded-enclosure use only: radiating GNSS signals over the air is illegal in most jurisdictions.

## Deep dives

- [_index-gnss-fusion-gis](../../docs/integration-cards/_index-gnss-fusion-gis.md) (integration-cards)
- [osqzss__gps-sdr-sim](../../docs/integration-cards/osqzss__gps-sdr-sim.md) (integration-cards)

**Concepts:** [GNSS positioning](../../catalog/concepts/gnss.md), [Jamming and spoofing](../../catalog/concepts/gnss-interference.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md)

**Tags:** `simulator`, `iq`, `hackrf`, `gps-l1`

**Domains:** multi

## Related

- integrates_with: [GNSS-SDR](../../catalog/repos/gnss-sdr__gnss-sdr.md)
- alternative_to: [multi-sdr-gps-sim](../../catalog/repos/mictronics__multi-sdr-gps-sim.md)

## Referenced by

- [Export control and ethics](../../docs/export-control-and-ethics.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [2. GNSS and its threats](../../docs/primer/02-gnss-and-threats.md) (mentions)
- [9. Evaluation and datasets](../../docs/primer/09-evaluation-and-datasets.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [GNSS-SDR](../../catalog/repos/gnss-sdr__gnss-sdr.md) (integrates_with)
- [multi-sdr-gps-sim](../../catalog/repos/mictronics__multi-sdr-gps-sim.md) (fork_of)
- [bladeGPS](../../catalog/repos/osqzss__bladegps.md) (extends)
- [LimeGPS](../../catalog/repos/osqzss__limegps.md) (extends)
- [Low-cost GPS simulator: GPS spoofing by SDR (DEF CON 23)](../../catalog/resources/defcon23-low-cost-gps-spoofing-sdr.md) (uses)
- [IS-GPS-200N: NAVSTAR GPS Space Segment / Navigation User Segment Interfaces](../../catalog/resources/gps-is-gps-200n.md) (explains)
- [IS-GPS-200N: NAVSTAR GPS Space Segment / Navigation User Segment Interfaces](../../catalog/resources/gps-is-gps-200n.md) (has_code)
- [IGS daily merged broadcast navigation files (BKG mirror)](../../catalog/resources/igs-bkg-brdc-broadcast-ephemeris.md) (has_code)
- [Safran Skydel simulation engine / GSG-8 GNSS simulator (ex-Orolia)](../../catalog/resources/safran-skydel-gsg8.md) (alternative_to)
- [Spirent GSS7000 and PNT X GNSS/PNT simulators](../../catalog/resources/spirent-gss7000-pntx.md) (alternative_to)
- [File-based GNSS signal chain: gps-sdr-sim => GNSS-SDR => spoofing/jamming scorer](../../catalog/samples/gnss-signal-chain.md) (uses)

_Indexed by lane(s): gnss_

_GitHub metadata fetched 2026-11-06._
