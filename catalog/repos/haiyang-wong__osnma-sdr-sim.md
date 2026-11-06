# OSNMA-SDR-SIM

`repo:haiyang-wong/osnma-sdr-sim` - <https://github.com/Haiyang-Wong/OSNMA-SDR-SIM>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 4 | C++ | ? | 2026-07-06 | False | active-research | high |

Galileo E1-B/E5b signal simulator with OSNMA authentication data embedded, configurable OSNMA parameters and USRP or file output, tested against GNSS-SDR and OSNMAlib.

**Why it matters:** Rare open tool to generate authenticated (and deliberately broken) Galileo signals for testing OSNMA-aware receivers.

**Hackathon notes:** Use file sink output into GNSS-SDR plus OSNMAlib for a full authenticate-or-alarm pipeline without RF. Cabled or shielded-enclosure use only: radiating GNSS signals over the air is illegal in most jurisdictions.

**Concepts:** [GNSS positioning](../concepts/gnss.md), [Assured / resilient PNT](../concepts/assured-pnt.md), [Simulation and HIL/SITL](../concepts/simulation.md), [Jamming and spoofing](../concepts/gnss-interference.md)

**Tags:** `osnma`, `galileo`, `usrp`, `simulator`

**Domains:** multi

## Related

- integrates_with: [OSNMAlib](../repos/algafix__osnma.md)
- integrates_with: [GNSS-SDR](../repos/gnss-sdr__gnss-sdr.md)
- same_org: [Beidou-SDR-SIM](../repos/haiyang-wong__beidou-sdr-sim.md)

## Referenced by

- [GNSS-SDR](../repos/gnss-sdr__gnss-sdr.md) (integrates_with)
- [Beidou-SDR-SIM](../repos/haiyang-wong__beidou-sdr-sim.md) (same_org)
- [Galileo OSNMA Signal-In-Space ICD v1.1](../resources/galileo-osnma-sis-icd-1-1.md) (has_code)

_Indexed by lane(s): gnss_

_GitHub metadata fetched 2026-11-06._
