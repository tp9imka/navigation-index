# Galileo OSNMA Receiver Guidelines Issue 1.3

`res:galileo-osnma-receiver-guidelines` - standard - <https://www.gsc-europa.eu/sites/default/files/sites/all/files/Galileo_OSNMA_Receiver_Guidelines_v1.3.pdf>

**By:** EU / European GNSS Service Centre, European Union / EUSPA - **Year:** 2024 - **Level:** advanced - **Access:** open

Companion to the OSNMA ICD describing how a receiver should process OSNMA: time-sync requirements, key and Merkle-tree handling, verification procedures and how to report authentication status to the user.

## Key takeaways

- Spells out the receiver time-sync assumption that OSNMA security depends on
- Covers cold start, key renewal and chain transitions
- Practical checklist for implementing OSNMA in software
- Explains which attacks OSNMA does and does not stop (e.g. replay/meaconing limits)
- Covers key renewal and alert handling

## Deep dives

- [galileo-osnma](../../docs/paper-digests/galileo-osnma.md) (paper-digests)
- [trends-2025-2026](../../docs/landscape/trends-2025-2026.md) (landscape)

**Concepts:** [GNSS positioning](../../catalog/concepts/gnss.md), [Jamming and spoofing](../../catalog/concepts/gnss-interference.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [Standards and interface specs](../../catalog/concepts/standards.md)

**Tags:** `osnma`, `galileo`, `receiver`, `anti-spoofing`

## Related

- has_code: [galileo-osnma (Rust)](../../catalog/repos/daniestevez__galileo-osnma.md)
- has_code: [OSNMAlib](../../catalog/repos/algafix__osnma.md)
- has_code: [FGI-OSNMA](../../catalog/repos/nlsfi__fgi-osnma.md)
- has_code: [OSNMA_ublox](../../catalog/repos/axelbjork__osnma_ublox.md)
- part_of: [Galileo OSNMA Signal-In-Space Interface Control Document Issue 1.1](../../catalog/resources/galileo-osnma-sis-icd.md)
- explains: [OSNMAlib](../../catalog/repos/algafix__osnma.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Landscape: what judges already know](../../docs/landscape/README.md) (mentions)
- [Navigation trends 2025-2026](../../docs/landscape/trends-2025-2026.md) (mentions)
- [Learning paths](../../docs/learning-paths.md) (mentions)
- [1. PNT fundamentals](../../docs/primer/01-pnt-fundamentals.md) (mentions)
- [2. GNSS and its threats](../../docs/primer/02-gnss-and-threats.md) (mentions)
- [GNSS interference monitor from u-blox telemetry and ADS-B NACp](../../catalog/samples/gnss-interference-monitor.md) (explains)
- [Galileo OSNMA authentication as a spoofing defence: real recording, file-level attacks, scorer adapter](../../catalog/samples/osnma-authentication.md) (explains)

_Indexed by lane(s): docs-standards, gnss_
