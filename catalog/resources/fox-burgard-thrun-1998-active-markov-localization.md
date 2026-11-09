# Active Markov Localization for Mobile Robots

`res:fox-burgard-thrun-1998-active-markov-localization` - paper - <https://publications.ri.cmu.edu/storage/publications/pub_files/pub1/fox_dieter_1998_1/fox_dieter_1998_1.pdf>

**By:** Dieter Fox, Wolfram Burgard, Sebastian Thrun - **Year:** 1998 - **Level:** intermediate - **Access:** open

Grid Markov localization that chooses where to move and where to point sensors by expected entropy reduction minus expected path cost. Actions are target points relative to the robot. Shown in a symmetric office corridor where only some rooms disambiguate the pose. Full text read.

## Key takeaways

- Utility = expected entropy reduction after the action, traded against path cost
- Random wandering failed in all 10 extra runs in the symmetric corridor; the active method localized in 20+ runs
- Notes that greedy one-step entropy minimisation fails when the disambiguating place is far away
- Starts with random motion until the belief has a few modes, then plans: a practical trigger

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `active-localization`, `markov-localization`, `entropy`, `multimodal`, `kidnapped-robot`, `robotics-and-autonomous-systems`

_Indexed by lane(s): innovation-pa-maneuvers_
