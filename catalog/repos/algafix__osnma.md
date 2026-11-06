# OSNMAlib

`repo:algafix/osnma` - <https://github.com/Algafix/OSNMA>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 52 | Python | EUPL-1.2 | 2026-10-14 | False | active-research | high |

Python implementation of the Galileo OSNMA receiver protocol: verifies TESLA key chains and MACs on navigation data from several input formats (u-blox, Septentrio, GNSS-SDR, files).

**Why it matters:** Most practical open tool to add navigation message authentication to a Galileo-capable receiver pipeline.

**Hackathon notes:** Works live with a u-blox receiver outputting SFRBX; needs the public key and Merkle root from the GSC. Good basis for an 'authenticated position' demo.

## Deep dives

- [_index-gnss-fusion-gis](../../docs/integration-cards/_index-gnss-fusion-gis.md) (integration-cards)
- [algafix__osnma](../../docs/integration-cards/algafix__osnma.md) (integration-cards)

**Concepts:** [GNSS positioning](../concepts/gnss.md), [Assured / resilient PNT](../concepts/assured-pnt.md), [Jamming and spoofing](../concepts/gnss-interference.md)

**Tags:** `osnma`, `galileo`, `authentication`, `python`

**Domains:** multi

## Related

- alternative_to: [galileo-osnma (Rust)](../repos/daniestevez__galileo-osnma.md)
- integrates_with: [GNSS-SDR](../repos/gnss-sdr__gnss-sdr.md)

## Referenced by

- [OSNMA_ublox](../repos/axelbjork__osnma_ublox.md) (alternative_to)
- [galileo-osnma (Rust)](../repos/daniestevez__galileo-osnma.md) (alternative_to)
- [GNSS-SDR](../repos/gnss-sdr__gnss-sdr.md) (integrates_with)
- [OSNMA-SDR-SIM](../repos/haiyang-wong__osnma-sdr-sim.md) (integrates_with)
- [FGI-OSNMA](../repos/nlsfi__fgi-osnma.md) (alternative_to)
- [Galileo OSNMA Receiver Guidelines Issue 1.3](../resources/galileo-osnma-receiver-guidelines.md) (explains)
- [Galileo OSNMA Receiver Guidelines Issue 1.3](../resources/galileo-osnma-receiver-guidelines.md) (has_code)
- [Galileo Open Service Navigation Message Authentication (OSNMA) - service page](../resources/galileo-osnma-service-page.md) (has_code)
- [Galileo OSNMA Signal-In-Space Interface Control Document Issue 1.1](../resources/galileo-osnma-sis-icd.md) (has_code)
- [Navipedia: Galileo Open Service Navigation Message Authentication](../resources/navipedia-osnma.md) (has_code)

_Indexed by lane(s): gnss_

_GitHub metadata fetched 2026-11-06._
