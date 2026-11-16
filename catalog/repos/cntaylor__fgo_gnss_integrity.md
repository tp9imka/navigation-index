# FGO_gnss_integrity

`repo:cntaylor/fgo_gnss_integrity` - <https://github.com/cntaylor/FGO_gnss_integrity>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 9 | Python | ? | 2026-03-24 | False | research-prototype | low |

Code behind an ION ITM 2026 paper comparing a robust factor-graph approach with solution-separation ARAIM on real GNSS epochs (from libRSF datasets) plus Monte Carlo outliers.

**Why it matters:** Recent bridge between robust factor graphs and classic integrity monitoring, the comparison reviewers ask about when a team says 'robust kernel'.

**Build notes:** No license file. Data DB stored via git LFS. Reference for evaluation design.

**Concepts:** [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [GNSS positioning](../../catalog/concepts/gnss.md)

**Tags:** `integrity`, `araim`, `factor-graph`, `robust`

**Domains:** ground

## Related

- evaluated_on: [libRSF](../../catalog/repos/tuc-proaut__librsf.md)

## Referenced by

- [factorGraph2DsatelliteExample](../../catalog/repos/cntaylor__factorgraph2dsatelliteexample.md) (same_org)

_Indexed by lane(s): nav-differentiators_

_GitHub metadata fetched 2026-11-16._
