# Resilient and consistent multirobot cooperative localization with covariance intersection

`res:chang-2021-resilient-ci-cooperative-localization` - paper - <https://arxiv.org/abs/2108.08789>

**By:** Tsang-Kai Chang, Kenny Chen, Ankur Mehta - **Year:** 2021 - **Level:** advanced - **Access:** open

IEEE T-RO 38(1) paper that uses covariance intersection to separate an explicit communication update from the observation update in multirobot cooperative localization, keeping estimates consistent. It analyses when the covariance stays bounded as a function of the communication and observation graphs, and tests resilience on simulated and benchmark physical data.

## Key takeaways

- Decouples communication from observation so either can fail
- Covariance boundedness conditions in terms of graph topology
- Directly relevant to lossy tactical links

**Concepts:** [Swarms and multi-agent navigation](../../catalog/concepts/multi-agent.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `cooperative-localization`, `covariance-intersection`, `resilience`

## Related

- cites: [A non-divergent estimation algorithm in the presence of unknown correlations](../../catalog/resources/julier-uhlmann-1997-covariance-intersection.md)

_Indexed by lane(s): backlog_
