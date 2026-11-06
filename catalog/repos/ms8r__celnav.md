# celnav

`repo:ms8r/celnav` - <https://github.com/ms8r/celnav>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 25 | Python | ? | 2024-08-20 | False | archived | medium |

Small Tkinter desktop app for celestial navigation on a boat: computes the Nautical Almanac daily-page data with PyEphem, reduces sights and fixes position from two LOPs, correcting for vessel motion between sights.

**Why it matters:** Scriptable sight reduction for a GNSS-free position fix.

**Hackathon notes:** Python 2 code (imports ConfigParser, Tkinter) with no commits since 2018; port the celnav.py core to Python 3 or use it as an algorithm reference. Pair with a camera-based sun or star altitude to automate a fix.

**Concepts:** [Celestial and star-tracker navigation](../concepts/celestial-nav.md), [Maritime navigation](../concepts/maritime-nav.md)

**Tags:** `sight-reduction`, `almanac`, `sextant`, `python`

**Domains:** maritime

## Related

- alternative_to: [celestial-navigation toolkit](../repos/alinnman__celestial-navigation.md)
- depends_on: [Skyfield](../repos/skyfielders__python-skyfield.md)

## Referenced by

- [navalm](../repos/kq6up__navalm.md) (alternative_to)
- [OpenCPN celestial navigation plugin](../repos/seandepagnier__celestial_navigation_pi.md) (alternative_to)
- [Skyfield](../repos/skyfielders__python-skyfield.md) (integrates_with)

_Indexed by lane(s): gap-fill_

_GitHub metadata fetched 2026-11-06._
