# Galileo OSNMA Receiver Guidelines Issue 1.3

`res:galileo-osnma-receiver-guidelines` - standard - <https://www.gsc-europa.eu/sites/default/files/sites/all/files/Galileo_OSNMA_Receiver_Guidelines_v1.3.pdf>

**By:** EU / European GNSS Service Centre - **Year:** 2023 - **Level:** advanced - **Access:** open

Companion to the OSNMA ICD describing how a receiver should process OSNMA: time-sync requirements, key and Merkle-tree handling, verification procedures and how to report authentication status to the user.

## Key takeaways

- Spells out the receiver time-sync assumption that OSNMA security depends on
- Covers cold start, key renewal and chain transitions
- Practical checklist for implementing OSNMA in software

**Concepts:** [GNSS positioning](../concepts/gnss.md), [Jamming and spoofing](../concepts/gnss-interference.md), [Assured / resilient PNT](../concepts/assured-pnt.md), [Standards and interface specs](../concepts/standards.md)

**Tags:** `osnma`, `galileo`, `receiver`, `anti-spoofing`

## Related

- has_code: [galileo-osnma (Rust)](../repos/daniestevez__galileo-osnma.md)
- has_code: [OSNMAlib](../repos/algafix__osnma.md)
- has_code: [FGI-OSNMA](../repos/nlsfi__fgi-osnma.md)
- has_code: [OSNMA_ublox](../repos/axelbjork__osnma_ublox.md)
- part_of: [Galileo OSNMA Signal-In-Space Interface Control Document Issue 1.1](../resources/galileo-osnma-sis-icd.md)

_Indexed by lane(s): docs-standards_
