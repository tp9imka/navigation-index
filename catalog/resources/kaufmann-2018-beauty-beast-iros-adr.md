# Beauty and the Beast: Optimal Methods Meet Learning for Drone Racing

`res:kaufmann-2018-beauty-beast-iros-adr` - paper - <https://arxiv.org/abs/1810.06224>

**By:** Elia Kaufmann, Mathias Gehrig, Philipp Foehn, Rene Ranftl, Alexey Dosovitskiy, Vladlen Koltun, Davide Scaramuzza - **Year:** 2018 - **Level:** advanced - **Access:** open

Preprint (later ICRA 2019) of the IROS 2018 Autonomous Drone Race winner: a CNN predicts the next gate pose with uncertainty, an EKF fuses it with coarse gate positions from one demonstration flight, and MPC flies the track onboard. Reports the 2018 race result over 8 gates.

## Key takeaways

- IROS 2018: 31.8 s vs 61 s and 90.1 s for second and third
- Coarse map plus local gate detection handled gates moved by up to 2 m in sim

**Concepts:** [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Path and motion planning](../../catalog/concepts/path-planning.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md)

**Tags:** `iros`, `adr`, `drone-racing`, `preprint`

## Related

- cites: [Challenges and implemented technologies used in autonomous drone racing](../../catalog/resources/moon-2019-adr-iros-challenges.md)

_Indexed by lane(s): loop-12_
