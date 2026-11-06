# Galileo OSNMA Signal-In-Space Interface Control Document Issue 1.1

`res:galileo-osnma-sis-icd` - standard - <https://www.gsc-europa.eu/sites/default/files/sites/all/files/Galileo_OSNMA_SIS_ICD_v1.1.pdf>

**By:** EU / European GNSS Service Centre - **Year:** 2023 - **Level:** advanced - **Access:** open

Defines Open Service Navigation Message Authentication: how TESLA-chain MACs and keys are embedded in spare I/NAV bits so a receiver can cryptographically verify that navigation data came from Galileo. It is the first civil GNSS data-authentication service in operation.

## Key takeaways

- Uses a TESLA key chain with delayed key disclosure
- Authenticates navigation data, not the ranging signal itself
- Requires loose time sync and a public key obtained out of band

**Concepts:** [GNSS positioning](../concepts/gnss.md), [Jamming and spoofing](../concepts/gnss-interference.md), [Assured / resilient PNT](../concepts/assured-pnt.md), [Standards and interface specs](../concepts/standards.md)

**Tags:** `osnma`, `galileo`, `authentication`, `anti-spoofing`, `tesla`

## Related

- has_code: [galileo-osnma (Rust)](../repos/daniestevez__galileo-osnma.md)
- has_code: [OSNMAlib](../repos/algafix__osnma.md)
- has_code: [FGI-OSNMA](../repos/nlsfi__fgi-osnma.md)
- has_code: [OSNMA_ublox](../repos/axelbjork__osnma_ublox.md)

## Referenced by

- [Galileo OSNMA Receiver Guidelines Issue 1.3](../resources/galileo-osnma-receiver-guidelines.md) (part_of)
- [Navipedia: Galileo Open Service Navigation Message Authentication](../resources/navipedia-osnma.md) (explains)
- [Septentrio AIM+ GNSS jamming and spoofing protection](../resources/septentrio-aim-plus.md) (uses)

_Indexed by lane(s): docs-standards_
