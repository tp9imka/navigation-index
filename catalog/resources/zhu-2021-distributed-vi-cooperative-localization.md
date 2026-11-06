# Distributed Visual-Inertial Cooperative Localization

`res:zhu-2021-distributed-vi-cooperative-localization` - paper - <https://arxiv.org/abs/2103.12770>

**By:** Pengxiang Zhu, Patrick Geneva, Wei Ren, Guoquan Huang - **Year:** 2021 - **Level:** advanced - **Access:** open

IROS 2021 paper on a consistent distributed visual-inertial estimator for multi-robot cooperative localization. Covariance intersection lets each robot keep only its own state and autocovariance while using common SLAM features and loop closures to other robots' past poses. Validated against a centralized counterpart in simulation and real experiments.

## Key takeaways

- CI applied to visual-inertial teams, not just range sensors
- Uses shared map features and inter-robot loop closures
- From the RPNG group behind OpenVINS

**Concepts:** [Swarms and multi-agent navigation](../../catalog/concepts/multi-agent.md), [Visual(-inertial) odometry](../../catalog/concepts/vio.md)

**Tags:** `cooperative-localization`, `covariance-intersection`, `visual-inertial`

## Related

- uses: [OpenVINS](../../catalog/repos/rpng__open_vins.md)

_Indexed by lane(s): backlog_
