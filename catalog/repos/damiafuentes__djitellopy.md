# DJITelloPy

`repo:damiafuentes/djitellopy` - <https://github.com/damiafuentes/DJITelloPy>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| ? | Python | ? | ? | ? | production | high |

Python wrapper around the official Tello UDP text SDK: takeoff, relative moves, rc sticks, state telemetry and the video stream. Works with Tello, Tello EDU and RoboMaster TT.

**Why it matters:** If the hackathon hands out Tellos, this is the fastest path from a planner to a flying drone. All compute stays on the laptop.

**Build notes:** MIT, pure-Python wheel (djitellopy 2.5.0). Last push 2025-01. No simulator: mock the UDP protocol for dry runs. Tello auto-lands after 15 s without a command, so keep a heartbeat. rc commands have no ack.

**Concepts:** [Autopilots and flight control](../../catalog/concepts/autopilot.md), [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md)

**Tags:** `tello`, `robomaster-tt`, `udp`, `python`, `indoor`, `mit`

**Domains:** air

## Related

- integrates_with: [TypeFly](../../catalog/repos/typefly__typefly.md)

## Referenced by

- [First-day intake: close-area A=>B, answers => stack](../../docs/first-day-intake.md) (mentions)
- [Tello SDK 2.0 User Guide](../../catalog/resources/tello-sdk-2-user-guide.md) (explains)

_Indexed by lane(s): close-area-sims_
