# Factor Graphs for Robot Perception

`res:dellaert-kaess-factor-graphs-robot-perception` - paper - <https://www.cs.cmu.edu/~kaess/pub/Dellaert17fnt.pdf>

**By:** Frank Dellaert, Michael Kaess - **Year:** 2017 - **Level:** intermediate - **Access:** open

Foundations and Trends monograph (free author PDF) explaining SLAM and sensor fusion as inference on factor graphs, with incremental smoothing (iSAM) and the reasoning behind the GTSAM library.

## Key takeaways

- Why sparsity makes smoothing tractable
- From batch to incremental (iSAM) inference
- Why smoothing beats filtering for multi-sensor nav
- Direct conceptual guide to GTSAM

## Deep dives

- [dellaert-kaess-factor-graphs-robot-perception](../../docs/paper-digests/dellaert-kaess-factor-graphs-robot-perception.md) (paper-digests)

**Concepts:** [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [Visual SLAM](../concepts/visual-slam.md), [GNSS/INS integration](../concepts/gnss-ins.md)

**Tags:** `factor-graph`, `gtsam`, `isam`

## Related

- has_code: [GTSAM](../repos/borglab__gtsam.md)
- explains: [Factor Graphs and GTSAM: A Hands-on Introduction](../resources/gtsam-intro-tutorial.md)

## Referenced by

- [Factor Graphs and GTSAM: A Hands-on Introduction](../resources/gtsam-intro-tutorial.md) (same_author)
- [iSAM2: Incremental Smoothing and Mapping Using the Bayes Tree](../resources/kaess-isam2.md) (same_author)

_Indexed by lane(s): ins-fusion, learning_
