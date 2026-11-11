# Skyfield

`repo:skyfielders/python-skyfield` - <https://github.com/skyfielders/python-skyfield>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 1,801 | Python | MIT | 2026-09-29 | False | production | high |

Python library for high-accuracy positions of stars, planets and Earth satellites, with proper time scales and reference frames.

**Why it matters:** Gives the ephemerides any celestial or satellite-based nav prototype needs.

**Build notes:** pip install skyfield; downloads ephemeris files on first use.

## Deep dives

- [_index-round5-nav](../../docs/integration-cards/_index-round5-nav.md) (integration-cards)
- [skyfielders__python-skyfield](../../docs/integration-cards/skyfielders__python-skyfield.md) (integration-cards)

**Concepts:** [Celestial and star-tracker navigation](../../catalog/concepts/celestial-nav.md), [Space and orbital navigation](../../catalog/concepts/space-nav.md), [Geodesy and coordinate frames](../../catalog/concepts/geodesy.md)

**Tags:** `ephemeris`, `astronomy`, `tle`, `python`

**Domains:** multi

## Related

- integrates_with: [celnav](../../catalog/repos/ms8r__celnav.md)

## Referenced by

- [Competition playbook: navigation and PNT under GNSS denial](../../docs/competition-playbook.md) (mentions)
- [Integration cards](../../docs/integration-cards/README.md) (mentions)
- [Brief decoder](../../docs/problem-statement-decoder.md) (mentions)
- [celnav](../../catalog/repos/ms8r__celnav.md) (depends_on)
- [JPL DE421 planetary ephemeris (NAIF SPK kernel)](../../catalog/resources/jpl-de421-ephemeris.md) (has_code)
- [Celestial fix: cedar-solve plate solving on real star images, then position from star elevations above an IMU vertical](../../catalog/samples/celestial-star-tracker.md) (uses)

_Indexed by lane(s): gap-fill_

_GitHub metadata fetched 2026-11-09._
