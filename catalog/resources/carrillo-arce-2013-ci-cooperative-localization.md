# Decentralized multi-robot cooperative localization using covariance intersection

`res:carrillo-arce-2013-ci-cooperative-localization` - paper - <https://doi.org/10.1109/IROS.2013.6696534>

**By:** Luis C. Carrillo-Arce, Esha D. Nerurkar, Jose L. Gordillo, Stergios I. Roumeliotis - **Year:** 2013 - **Level:** advanced - **Access:** paywalled

IROS 2013 paper applying covariance intersection to multi-robot cooperative localization so that each robot only keeps its own state and covariance. Processing and communication scale linearly with team size, and the authors compare against the earlier split-CI method in simulation and experiments.

## Key takeaways

- Each robot estimates only its own pose; CI absorbs unknown inter-robot correlations
- Linear cost in the number of robots
- Standard reference baseline for CI-based cooperative localization

**Concepts:** [Swarms and multi-agent navigation](../../catalog/concepts/multi-agent.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `cooperative-localization`, `covariance-intersection`, `multi-robot`

## Related

- cites: [A non-divergent estimation algorithm in the presence of unknown correlations](../../catalog/resources/julier-uhlmann-1997-covariance-intersection.md)
- same_author: [Recursive decentralized localization for multi-robot systems with asynchronous pairwise communication](../../catalog/resources/luft-2018-recursive-decentralized-localization.md)

## Referenced by

- [Recursive decentralized localization for multi-robot systems with asynchronous pairwise communication](../../catalog/resources/luft-2018-recursive-decentralized-localization.md) (same_author)

_Indexed by lane(s): backlog_
