# A non-divergent estimation algorithm in the presence of unknown correlations

`res:julier-uhlmann-1997-covariance-intersection` - paper - <https://doi.org/10.1109/ACC.1997.609105>

**By:** Simon J. Julier, Jeffrey K. Uhlmann - **Year:** 1997 - **Level:** advanced - **Access:** paywalled

The original covariance intersection (CI) paper (American Control Conference 1997). It fuses two estimates whose cross-correlation is unknown by taking a convex combination of their information matrices, which stays consistent whatever the true correlation is. This is the building block behind most decentralized cooperative localization filters that cannot track inter-agent correlations.

## Key takeaways

- CI gives a consistent fused estimate without knowing cross-covariance
- Motivated by decentralized estimation, where a plain Kalman update double-counts shared information
- Trades some conservatism for guaranteed consistency

**Concepts:** [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Swarms and multi-agent navigation](../../catalog/concepts/multi-agent.md)

**Tags:** `covariance-intersection`, `decentralized-estimation`, `data-fusion`, `classic`

## Referenced by

- [Decentralized multi-robot cooperative localization using covariance intersection](../../catalog/resources/carrillo-arce-2013-ci-cooperative-localization.md) (cites)
- [Resilient and consistent multirobot cooperative localization with covariance intersection](../../catalog/resources/chang-2021-resilient-ci-cooperative-localization.md) (cites)
- [Weighted Covariance Intersection for Range-based Distributed Cooperative Localization of Multi-Vehicle Systems](../../catalog/resources/tu-2025-weighted-ci-range-cooperative-localization.md) (cites)

_Indexed by lane(s): backlog_
