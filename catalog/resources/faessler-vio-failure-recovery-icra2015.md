# Automatic Re-Initialization and Failure Recovery for Aggressive Flight with a Monocular Vision-Based Quadrotor

`res:faessler-vio-failure-recovery-icra2015` - paper - <https://rpg.ifi.uzh.ch/docs/ICRA15_Faessler.pdf>

**By:** Matthias Faessler, Flavio Fontana, Christian Forster, Davide Scaramuzza - **Year:** 2015 - **Level:** intermediate - **Access:** open

After visual tracking is lost or the vehicle is thrown, it stabilises attitude and height from IMU and a range sensor, then re-initialises the monocular visual pipeline before resuming. ICRA 2015.

## Key takeaways

- The standard answer to VIO loss: stabilise, then re-initialise
- No multi-hypothesis relocalization

**Concepts:** [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Autopilots and flight control](../../catalog/concepts/autopilot.md)

**Tags:** `failure-recovery`, `re-initialization`, `monocular`

_Indexed by lane(s): close-area-innovation_
