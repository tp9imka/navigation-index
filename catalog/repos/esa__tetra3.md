# tetra3

`repo:esa/tetra3` - <https://github.com/esa/tetra3>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 175 | Python | Apache-2.0 | 2024-08-14 | False | production | high |

Fast lost-in-space plate solver for star trackers from ESA: identifies stars in an image and returns attitude using a precomputed pattern database.

**Why it matters:** Star-based attitude (and with time + gravity vector, position) is jam-proof; tetra3 is the easiest open solver.

**Hackathon notes:** Not on PyPI: pip install git+https://github.com/esa/tetra3.git; solve sample images in minutes. Combine attitude with a level sensor and clock for a celestial fix demo.

## Deep dives

- [_index-perception-altnav](../../docs/integration-cards/_index-perception-altnav.md) (integration-cards)
- [esa__tetra3](../../docs/integration-cards/esa__tetra3.md) (integration-cards)

**Concepts:** [Celestial and star-tracker navigation](../../catalog/concepts/celestial-nav.md), [Space and orbital navigation](../../catalog/concepts/space-nav.md)

**Tags:** `star-tracker`, `plate-solver`, `esa`

**Domains:** space, air, maritime

## Related

- fork_of: [cedar-solve](../../catalog/repos/smroid__cedar-solve.md)
- alternative_to: [OpenStarTracker](../../catalog/repos/ubnanosatlab__openstartracker.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [5. Absolute alternative PNT](../../docs/primer/05-absolute-alt-pnt.md) (mentions)
- [8. Maritime, underwater, ground and dismounted](../../docs/primer/08-maritime-underwater-ground.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [celestial-navigation toolkit](../../catalog/repos/alinnman__celestial-navigation.md) (integrates_with)
- [Astrometry.net](../../catalog/repos/dstndstn__astrometry.net.md) (alternative_to)
- [NASA COTS Star Tracker](../../catalog/repos/nasa__cots-star-tracker.md) (alternative_to)
- [cedar-solve](../../catalog/repos/smroid__cedar-solve.md) (fork_of)
- [SPEL Open Star Tracker](../../catalog/repos/spel-uchile__star_tracker.md) (alternative_to)
- [OpenStarTracker](../../catalog/repos/ubnanosatlab__openstartracker.md) (alternative_to)
- [LOST](../../catalog/repos/uwcubesat__lost.md) (alternative_to)
- [tetra3 documentation](../../catalog/resources/tetra3-docs.md) (explains)
- [Celestial fix: cedar-solve plate solving on real star images, then position from star elevations above an IMU vertical](../../catalog/samples/celestial-star-tracker.md) (explains)

_Indexed by lane(s): alt-nav_

_GitHub metadata fetched 2026-11-06._
