# tetra3

`repo:esa/tetra3` - <https://github.com/esa/tetra3>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 175 | Python | Apache-2.0 | 2024-08-14 | False | production | high |

Fast lost-in-space plate solver for star trackers from ESA: identifies stars in an image and returns attitude using a precomputed pattern database.

**Why it matters:** Star-based attitude (and with time + gravity vector, position) is jam-proof; tetra3 is the easiest open solver.

**Hackathon notes:** pip install; solve sample images in minutes. Combine attitude with a level sensor and clock for a celestial fix demo.

**Concepts:** [Celestial and star-tracker navigation](../concepts/celestial-nav.md), [Space and orbital navigation](../concepts/space-nav.md)

**Tags:** `star-tracker`, `plate-solver`, `esa`

**Domains:** space, air, maritime

## Related

- fork_of: [cedar-solve](../repos/smroid__cedar-solve.md)
- alternative_to: [OpenStarTracker](../repos/ubnanosatlab__openstartracker.md)

## Referenced by

- [celestial-navigation toolkit](../repos/alinnman__celestial-navigation.md) (integrates_with)
- [NASA COTS Star Tracker](../repos/nasa__cots-star-tracker.md) (alternative_to)
- [cedar-solve](../repos/smroid__cedar-solve.md) (fork_of)
- [OpenStarTracker](../repos/ubnanosatlab__openstartracker.md) (alternative_to)
- [LOST](../repos/uwcubesat__lost.md) (alternative_to)
- [tetra3 documentation](../resources/tetra3-docs.md) (explains)

_Indexed by lane(s): alt-nav_

_GitHub metadata fetched 2026-11-06._
