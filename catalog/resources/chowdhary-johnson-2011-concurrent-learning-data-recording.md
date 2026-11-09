# A Singular Value Maximizing Data Recording Algorithm for Concurrent Learning

`res:chowdhary-johnson-2011-concurrent-learning-data-recording` - paper - <https://skoge.folk.ntnu.no/prost/proceedings/acc11/data/papers/1207.pdf>

**By:** Girish Chowdhary, Eric Johnson - **Year:** 2011 - **Level:** advanced - **Access:** open

ACC 2011 (abstract read from proceedings PDF). Concurrent-learning adaptive controllers reuse recorded data alongside current data; the paper picks which data to record by maximising the minimum singular value of the stored regressor history, which gives exponential parameter convergence without persistent excitation when the recorded data are rich enough.

## Key takeaways

- Excitation is measured as the minimum singular value of a recorded regressor stack, a verifiable online test
- Flight-control adaptation, not navigation; the transferable idea is a stored informative-data buffer

**Concepts:** [Autopilots and flight control](../../catalog/concepts/autopilot.md), [Sensor calibration](../../catalog/concepts/calibration.md)

**Tags:** `concurrent-learning`, `persistent-excitation`, `adaptive-control`, `singular-value`

## Related

- same_author: [Concurrent learning for convergence in adaptive control without persistency of excitation](../../catalog/resources/chowdhary-johnson-2010-concurrent-learning.md)

_Indexed by lane(s): innovation-pa-aero-adaptation_
