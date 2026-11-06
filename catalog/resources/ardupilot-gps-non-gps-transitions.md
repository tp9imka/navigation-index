# GPS / Non-GPS Transitions

`res:ardupilot-gps-non-gps-transitions` - doc - <https://ardupilot.org/copter/docs/common-non-gps-to-gps.html>

**By:** ArduPilot Dev Team - **Year:** None - **Level:** intermediate - **Access:** open

Explains configuring EKF3 with two source sets (e.g. GPS and external nav/optical flow) and switching between them in flight via RC switch, Lua script or MAVLink.

## Key takeaways

- EK3_SRCn_* defines up to three source sets
- Switching can be automated with Lua for GNSS-loss handling

**Concepts:** [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [GNSS/INS integration](../../catalog/concepts/gnss-ins.md)

**Tags:** `ekf3`, `source-switching`, `lua`

## Related

- explains: [ArduPilot](../../catalog/repos/ardupilot__ardupilot.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Learning paths](../../docs/learning-paths.md) (mentions)
- [6. Autopilots and C2](../../docs/primer/06-autopilots-and-c2.md) (mentions)

_Indexed by lane(s): autopilots_
