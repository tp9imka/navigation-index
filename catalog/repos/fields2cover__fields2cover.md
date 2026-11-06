# Fields2Cover

`repo:fields2cover/fields2cover` - <https://github.com/fields2cover/fields2cover>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 922 | C++ | BSD-3-Clause | 2026-10-27 | False | production | high |

Modular coverage path planning library: headland generation, swath generation, route ordering (boustrophedon, snake, spiral) and Dubins/Reeds-Shepp path smoothing, with Python bindings.

**Why it matters:** Ready coverage planner for area search or survey patterns by ground or air vehicles.

**Hackathon notes:** Build from source with GDAL dependency; Python bindings let you produce a sweep over a GeoJSON polygon quickly.

**Concepts:** [Path and motion planning](../concepts/path-planning.md), [Mission planning and routing](../concepts/mission-planning.md)

**Tags:** `coverage`, `boustrophedon`, `dubins`, `python-bindings`

**Domains:** ground, air

## Related

- integrates_with: [opennav_coverage](../repos/open-navigation__opennav_coverage.md)
- alternative_to: [polygon_coverage_planning](../repos/ethz-asl__polygon_coverage_planning.md)

## Referenced by

- [polygon_coverage_planning](../repos/ethz-asl__polygon_coverage_planning.md) (alternative_to)
- [opennav_coverage](../repos/open-navigation__opennav_coverage.md) (depends_on)
- [Fields2Cover: An open-source coverage path planning library for unmanned agricultural vehicles](../resources/fields2cover-paper.md) (has_code)

_Indexed by lane(s): planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
