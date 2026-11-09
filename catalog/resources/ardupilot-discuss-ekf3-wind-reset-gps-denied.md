# Custom EKF3 Position/Wind Reset for GPS-Denied Flight (ArduPlane 4.4.3)

`res:ardupilot-discuss-ekf3-wind-reset-gps-denied` - blog - <https://discuss.ardupilot.org/t/custom-ekf3-position-wind-reset-for-gps-denied-flight-arduplane-4-4-3/143360>

**By:** ArduPilot Discourse thread - **Year:** 2026 - **Level:** intermediate - **Access:** open

Forum discussion, April 2026. A user adds a command to seed EKF3 wind and position without GPS; reports that with GPS absent and wind set, EKF3 keeps wind fixed (frozen) and uses it for airspeed and sideslip fusion, and resumes learning when GPS returns. Contributors suggest reusing MAV_CMD_EXTERNAL_POSITION_ESTIMATE and MAV_CMD_EXTERNAL_WIND_ESTIMATE.

## Key takeaways

- Practitioners already treat wind as frozen during GPS-denied fixed-wing flight and inject it externally
- No discussion of identifiability theory

**Concepts:** [Autopilots and flight control](../../catalog/concepts/autopilot.md), [GNSS/INS integration](../../catalog/concepts/gnss-ins.md)

**Tags:** `forum`, `ekf3`, `wind`, `gps-denied`, `arduplane`

## Related

- part_of: [ArduPilot](../../catalog/repos/ardupilot__ardupilot.md)

_Indexed by lane(s): innovation-pa-aero-adaptation_
