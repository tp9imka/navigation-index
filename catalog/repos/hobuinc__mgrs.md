# mgrs (Python)

`repo:hobuinc/mgrs` - <https://github.com/hobuinc/mgrs>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 136 | C++ | MIT | 2026-11-03 | False | production | high |

Python library converting between latitude/longitude and MGRS grid references, built on NGA GEOTRANS 3.10 (now a Rust port exposed through a pybind11 extension).

**Why it matters:** MGRS is the grid language of military users; needed for any C2 UI or report generator.

**Hackathon notes:** pip install mgrs; mind the precision argument for 1 m vs 10 m references. Since 1.6.0 inverse conversion returns the grid-cell centre, not the south-west corner.

**Concepts:** [Geodesy and coordinate frames](../../catalog/concepts/geodesy.md), [Standards and interface specs](../../catalog/concepts/standards.md)

**Tags:** `mgrs`, `utm`, `grid-reference`

**Domains:** multi

## Related

- alternative_to: [GeographicLib](../../catalog/repos/geographiclib__geographiclib.md)

## Referenced by

- [7. Maps, geodesy and planning](../../docs/primer/07-maps-geodesy-planning.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [GeographicLib](../../catalog/repos/geographiclib__geographiclib.md) (alternative_to)

_Indexed by lane(s): planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
