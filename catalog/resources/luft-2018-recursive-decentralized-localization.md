# Recursive decentralized localization for multi-robot systems with asynchronous pairwise communication

`res:luft-2018-recursive-decentralized-localization` - paper - <https://doi.org/10.1177/0278364918760698>

**By:** Lukas Luft, Tobias Schubert, Stergios I. Roumeliotis, Wolfram Burgard - **Year:** 2018 - **Level:** advanced - **Access:** paywalled

IJRR 37(10) paper describing a fully decentralized EKF for collaborative localization that approximates inter-robot cross-correlations. Only the two robots involved in a relative measurement need to talk, no measurement history is stored, and generic measurement models are supported. Builds on the authors' RSS 2016 paper and is evaluated on real-world datasets.

## Key takeaways

- Pairwise, asynchronous communication only
- Keeps just the latest pose estimate per robot
- Approximates cross-correlations instead of dropping them

**Concepts:** [Swarms and multi-agent navigation](../../catalog/concepts/multi-agent.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `cooperative-localization`, `decentralized-ekf`, `multi-robot`

## Related

- same_author: [Decentralized multi-robot cooperative localization using covariance intersection](../../catalog/resources/carrillo-arce-2013-ci-cooperative-localization.md)

## Referenced by

- [Decentralized multi-robot cooperative localization using covariance intersection](../../catalog/resources/carrillo-arce-2013-ci-cooperative-localization.md) (same_author)

_Indexed by lane(s): backlog_
