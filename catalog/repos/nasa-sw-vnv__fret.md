# FRET

`repo:nasa-sw-vnv/fret` - <https://github.com/NASA-SW-VnV/fret>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 509 | JavaScript | NOASSERTION | 2026-04-14 | False | active-research | medium |

NASA's Formal Requirements Elicitation Tool: write requirements in a structured English (FRETish), get temporal-logic formalisations, consistency checks and test cases. Exports feed Ogma and other monitor generators.

**Why it matters:** Certification work starts from requirements. Writing the nav function's safety requirements in FRET gives a traceable artifact that maps to the DO-178C requirements-based mindset.

**Build notes:** Electron desktop app. License is a NASA agreement in LICENSE.pdf (GitHub reports NOASSERTION; not read here). A 30-minute exercise: 5 requirements for the nav output, exported to Ogma, shown as one slide of traceability.

**Concepts:** [Standards and interface specs](../../catalog/concepts/standards.md)

**Tags:** `requirements`, `formal-methods`, `electron`, `nasa`, `traceability`

**Domains:** air, space, multi

## Related

- integrates_with: [Ogma](../../catalog/repos/nasa__ogma.md)

## Referenced by

- [Path to product: from a nav algorithm to something that flies](../../docs/path-to-product.md) (mentions)
- [Ogma](../../catalog/repos/nasa__ogma.md) (integrates_with)
- [R2U2](../../catalog/repos/r2u2__r2u2.md) (integrates_with)

_Indexed by lane(s): flight-embedded_

_GitHub metadata fetched 2026-11-16._
