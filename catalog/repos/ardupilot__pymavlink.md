# pymavlink

`repo:ardupilot/pymavlink` - <https://github.com/ArduPilot/pymavlink>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 740 | Python | NOASSERTION | 2026-11-05 | False | production | high |

Python MAVLink implementation plus tools for connections, log parsing (DataFlash/tlog) and code generation.

**Why it matters:** Quickest path to scripting a vehicle or parsing flight logs to evaluate estimator behaviour under GNSS loss.

**Hackathon notes:** pip install pymavlink; mavutil.mavlink_connection('udp:...') against SITL works in minutes.

## Deep dives

- [ardupilot__pymavlink](../../docs/integration-cards/ardupilot__pymavlink.md) (integration-cards)

**Concepts:** [MAVLink, ground control and C2 links](../concepts/mavlink-gcs.md)

**Tags:** `python`, `logs`, `dataflash`, `tlog`

**Domains:** multi

## Related

- depends_on: [MAVLink](../repos/mavlink__mavlink.md)
- integrates_with: [MAVProxy](../repos/ardupilot__mavproxy.md)
- depends_on: [DroneKit-Python](../repos/dronekit__dronekit-python.md)

## Referenced by

- [ArduPilot](../repos/ardupilot__ardupilot.md) (integrates_with)
- [MAVProxy](../repos/ardupilot__mavproxy.md) (depends_on)
- [mavlink-mcp (ArduPilot)](../repos/deepakpopli__mavlink-mcp.md) (depends_on)
- [DroneKit-Python](../repos/dronekit__dronekit-python.md) (depends_on)
- [MAVLink](../repos/mavlink__mavlink.md) (depends_on)
- [Non-GPS Position Estimation (MAVLink messages)](../resources/ardupilot-dev-mavlink-nongps-position.md) (uses)
- [ArduPilot EKF3 source-set switch under GPS denial](../samples/ardupilot-ekf3-source-switch.md) (uses)
- [MAVLink telemetry to TAK Cursor-on-Target](../samples/mavlink-to-tak-cot.md) (uses)
- [VIO to MAVLink bridge with ENU/FLU to NED/FRD conversion](../samples/vio-to-mavlink-bridge.md) (uses)

_Indexed by lane(s): autopilots_

_GitHub metadata fetched 2026-11-06._
