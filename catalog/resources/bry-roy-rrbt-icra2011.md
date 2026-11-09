# Rapidly-exploring Random Belief Trees for Motion Planning Under Uncertainty

`res:bry-roy-rrbt-icra2011` - paper - <https://groups.csail.mit.edu/rrg/papers/abry_icra11.pdf>

**By:** Adam Bry, Nicholas Roy - **Year:** 2011 - **Level:** advanced - **Access:** open

Belief-space planning: grows a tree over state and estimator covariance, propagating a Kalman filter along each edge, so the chosen path respects chance constraints given spatially varying sensing.

## Key takeaways

- Plan over covariance, not only position
- Spatially varying measurement quality is the motivating case, as with TRN or visual fixes
- Covariance propagation along candidate edges is cheap enough to do in Python for a 2D demo

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `belief-space`, `rrt`, `uncertainty`, `kalman-filter`

## Related

- explains: [edpl-ompl](../../catalog/repos/sauravag__edpl-ompl.md)

## Referenced by

- [04. Close-area navigation: prior art for three innovation angles, plus a wider scan](../../docs/research/close-area-nav/04-innovation-prior-art.md) (mentions)
- [01. Flyable maneuvers that separate competing location hypotheses](../../docs/research/innovation-prior-art/01-disambiguating-maneuvers.md) (mentions)
- [Non-Gaussian Belief Space Planning: Correctness and Complexity](../../catalog/resources/platt-2012-non-gaussian-belief-space-planning.md) (cites)
- [The Belief Roadmap: Efficient Planning in Belief Space by Factoring the Covariance](../../catalog/resources/prentice-roy-belief-roadmap-2009.md) (same_author)

_Indexed by lane(s): guidance-planning_
