# GPS / Non-GPS Transitions

`res:ardupilot-gps-non-gps-transitions` - doc - <https://ardupilot.org/copter/docs/common-non-gps-to-gps.html>

**By:** ArduPilot Dev Team - **Year:** None - **Level:** intermediate - **Access:** open

Explains configuring EKF3 with two source sets (e.g. GPS and external nav/optical flow) and switching between them in flight via RC switch, Lua script or MAVLink.

## Key takeaways

- EK3_SRCn_* defines up to three source sets
- Switching can be automated with Lua for GNSS-loss handling

**Concepts:** [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [Assured / resilient PNT](../concepts/assured-pnt.md), [GNSS/INS integration](../concepts/gnss-ins.md)

**Tags:** `ekf3`, `source-switching`, `lua`

## Related

- explains: [ArduPilot](../repos/ardupilot__ardupilot.md)

_Indexed by lane(s): autopilots_
