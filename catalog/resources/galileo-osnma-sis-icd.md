# Galileo OSNMA Signal-In-Space Interface Control Document Issue 1.1

`res:galileo-osnma-sis-icd` - standard - <https://www.gsc-europa.eu/sites/default/files/sites/all/files/Galileo_OSNMA_SIS_ICD_v1.1.pdf>

**By:** EU / European GNSS Service Centre, European Union / EUSPA - **Year:** 2023 - **Level:** advanced - **Access:** open

Defines Open Service Navigation Message Authentication: how TESLA-chain MACs and keys are embedded in spare I/NAV bits so a receiver can cryptographically verify that navigation data came from Galileo. It is the first civil GNSS data-authentication service in operation.

## Key takeaways

- Uses a TESLA key chain with delayed key disclosure
- Authenticates navigation data, not the ranging signal itself
- Requires loose time sync and a public key obtained out of band
- Civil signal authentication is available today on Galileo E1-B
- Receivers need loose time synchronization to verify TESLA keys
- Defines what an authenticated vs unauthenticated navigation message means

## Deep dives

- [galileo-osnma](../../docs/paper-digests/galileo-osnma.md) (paper-digests)

**Concepts:** [GNSS positioning](../../catalog/concepts/gnss.md), [Jamming and spoofing](../../catalog/concepts/gnss-interference.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [Standards and interface specs](../../catalog/concepts/standards.md)

**Tags:** `osnma`, `galileo`, `authentication`, `anti-spoofing`, `tesla`

## Related

- has_code: [galileo-osnma (Rust)](../../catalog/repos/daniestevez__galileo-osnma.md)
- has_code: [OSNMAlib](../../catalog/repos/algafix__osnma.md)
- has_code: [FGI-OSNMA](../../catalog/repos/nlsfi__fgi-osnma.md)
- has_code: [OSNMA_ublox](../../catalog/repos/axelbjork__osnma_ublox.md)
- has_code: [OSNMA-SDR-SIM](../../catalog/repos/haiyang-wong__osnma-sdr-sim.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [2. GNSS and its threats](../../docs/primer/02-gnss-and-threats.md) (mentions)
- [Galileo OSNMA Receiver Guidelines Issue 1.3](../../catalog/resources/galileo-osnma-receiver-guidelines.md) (part_of)
- [Galileo Open Service Navigation Message Authentication (OSNMA) - service page](../../catalog/resources/galileo-osnma-service-page.md) (part_of)
- [Navipedia: Galileo Open Service Navigation Message Authentication](../../catalog/resources/navipedia-osnma.md) (explains)
- [Septentrio AIM+ GNSS jamming and spoofing protection](../../catalog/resources/septentrio-aim-plus.md) (uses)
- [Galileo OSNMA authentication as a spoofing defence: real recording, file-level attacks, scorer adapter](../../catalog/samples/osnma-authentication.md) (explains)

_Indexed by lane(s): docs-standards, gnss_
