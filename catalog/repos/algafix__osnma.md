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
- [osnmalib-recording](../../docs/dataset-cards/osnmalib-recording.md) (dataset-cards)
- [galileo-osnma](../../docs/paper-digests/galileo-osnma.md) (paper-digests)

**Concepts:** [GNSS positioning](../../catalog/concepts/gnss.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [Jamming and spoofing](../../catalog/concepts/gnss-interference.md)

**Tags:** `osnma`, `galileo`, `authentication`, `python`

**Domains:** multi

## Related

- alternative_to: [galileo-osnma (Rust)](../../catalog/repos/daniestevez__galileo-osnma.md)
- integrates_with: [GNSS-SDR](../../catalog/repos/gnss-sdr__gnss-sdr.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Learning paths](../../docs/learning-paths.md) (mentions)
- [2. GNSS and its threats](../../docs/primer/02-gnss-and-threats.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [Upstream findings](../../docs/upstream-findings.md) (mentions)
- [OSNMA_ublox](../../catalog/repos/axelbjork__osnma_ublox.md) (alternative_to)
- [galileo-osnma (Rust)](../../catalog/repos/daniestevez__galileo-osnma.md) (alternative_to)
- [GNSS-SDR](../../catalog/repos/gnss-sdr__gnss-sdr.md) (integrates_with)
- [OSNMA-SDR-SIM](../../catalog/repos/haiyang-wong__osnma-sdr-sim.md) (integrates_with)
- [FGI-OSNMA](../../catalog/repos/nlsfi__fgi-osnma.md) (alternative_to)
- [Galileo OSNMA Receiver Guidelines Issue 1.3](../../catalog/resources/galileo-osnma-receiver-guidelines.md) (explains)
- [Galileo OSNMA Receiver Guidelines Issue 1.3](../../catalog/resources/galileo-osnma-receiver-guidelines.md) (has_code)
- [Galileo Open Service Navigation Message Authentication (OSNMA) - service page](../../catalog/resources/galileo-osnma-service-page.md) (has_code)
- [Galileo OSNMA Signal-In-Space Interface Control Document Issue 1.1](../../catalog/resources/galileo-osnma-sis-icd.md) (has_code)
- [Navipedia: Galileo Open Service Navigation Message Authentication](../../catalog/resources/navipedia-osnma.md) (has_code)
- [OSNMAlib bundled Galileo I/NAV recording (custom_run)](../../catalog/resources/osnmalib-galileo-inav-recording.md) (part_of)
- [GNSS interference monitor from u-blox telemetry and ADS-B NACp](../../catalog/samples/gnss-interference-monitor.md) (explains)
- [Galileo OSNMA authentication as a spoofing defence: real recording, file-level attacks, scorer adapter](../../catalog/samples/osnma-authentication.md) (uses)

_Indexed by lane(s): gnss_

_GitHub metadata fetched 2026-11-06._
