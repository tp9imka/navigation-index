# OSNMA-SDR-SIM

`repo:haiyang-wong/osnma-sdr-sim` - <https://github.com/Haiyang-Wong/OSNMA-SDR-SIM>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 4 | C++ | ? | 2026-07-06 | False | active-research | high |

Galileo E1-B/E5b signal simulator with OSNMA authentication data embedded, configurable OSNMA parameters and USRP or file output, tested against GNSS-SDR and OSNMAlib.

**Why it matters:** Rare open tool to generate authenticated (and deliberately broken) Galileo signals for testing OSNMA-aware receivers.

**Hackathon notes:** Use file sink output into GNSS-SDR plus OSNMAlib for a full authenticate-or-alarm pipeline without RF. Cabled or shielded-enclosure use only: radiating GNSS signals over the air is illegal in most jurisdictions.

## Deep dives

- [_index-round3](../../docs/integration-cards/_index-round3.md) (integration-cards)
- [haiyang-wong__osnma-sdr-sim](../../docs/integration-cards/haiyang-wong__osnma-sdr-sim.md) (integration-cards)

**Concepts:** [GNSS positioning](../../catalog/concepts/gnss.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md), [Jamming and spoofing](../../catalog/concepts/gnss-interference.md)

**Tags:** `osnma`, `galileo`, `usrp`, `simulator`

**Domains:** multi

## Related

- integrates_with: [OSNMAlib](../../catalog/repos/algafix__osnma.md)
- integrates_with: [GNSS-SDR](../../catalog/repos/gnss-sdr__gnss-sdr.md)
- same_org: [Beidou-SDR-SIM](../../catalog/repos/haiyang-wong__beidou-sdr-sim.md)

## Referenced by

- [Export control and ethics](../../docs/export-control-and-ethics.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [2. GNSS and its threats](../../docs/primer/02-gnss-and-threats.md) (mentions)
- [9. Evaluation and datasets](../../docs/primer/09-evaluation-and-datasets.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [GNSS-SDR](../../catalog/repos/gnss-sdr__gnss-sdr.md) (integrates_with)
- [Beidou-SDR-SIM](../../catalog/repos/haiyang-wong__beidou-sdr-sim.md) (same_org)
- [Galileo OSNMA Signal-In-Space Interface Control Document Issue 1.1](../../catalog/resources/galileo-osnma-sis-icd.md) (has_code)
- [Safran Skydel simulation engine / GSG-8 GNSS simulator (ex-Orolia)](../../catalog/resources/safran-skydel-gsg8.md) (alternative_to)
- [Spirent GSS7000 and PNT X GNSS/PNT simulators](../../catalog/resources/spirent-gss7000-pntx.md) (alternative_to)
- [Galileo OSNMA authentication as a spoofing defence: real recording, file-level attacks, scorer adapter](../../catalog/samples/osnma-authentication.md) (uses)

_Indexed by lane(s): gnss_

_GitHub metadata fetched 2026-11-06._
