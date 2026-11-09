# Attention and Anticipation in Fast Visual-Inertial Navigation

`res:carlone-karaman-attention-anticipation-vin` - paper - <https://arxiv.org/abs/1610.03344>

**By:** Luca Carlone, Sertac Karaman - **Year:** 2019 - **Level:** advanced - **Access:** open

ICRA 2017 and IEEE Transactions on Robotics 2019 (doi 10.1109/TRO.2018.2872402), per Crossref; arXiv 1610.03344 abstract read. Selects which visual features a compute-limited drone processes by forward-simulating dynamics and predicting each feature's utility for VIN over a horizon; greedy selection with submodularity guarantees.

## Key takeaways

- Anticipate future estimation value under a compute budget
- Inside the VIO front end, not for absolute fixes
- No deadline or processing delay model

**Concepts:** [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md)

**Tags:** `feature-selection`, `anticipation`, `compute-budget`, `submodularity`

_Indexed by lane(s): innovation-pa-scheduling_
