# pymavlink

`repo:ardupilot/pymavlink` - <https://github.com/ArduPilot/pymavlink>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 740 | Python | NOASSERTION | 2026-11-05 | False | production | high |

Python MAVLink implementation plus tools for connections, log parsing (DataFlash/tlog) and code generation.

**Why it matters:** Quickest path to scripting a vehicle or parsing flight logs to evaluate estimator behaviour under GNSS loss.

**Hackathon notes:** pip install pymavlink; mavutil.mavlink_connection('udp:...') against SITL works in minutes.

## Deep dives

- [_index-flight-c2](../../docs/integration-cards/_index-flight-c2.md) (integration-cards)
- [ardupilot__pymavlink](../../docs/integration-cards/ardupilot__pymavlink.md) (integration-cards)

**Concepts:** [MAVLink, ground control and C2 links](../../catalog/concepts/mavlink-gcs.md)

**Tags:** `python`, `logs`, `dataflash`, `tlog`

**Domains:** multi

## Related

- depends_on: [MAVLink](../../catalog/repos/mavlink__mavlink.md)
- integrates_with: [MAVProxy](../../catalog/repos/ardupilot__mavproxy.md)
- depends_on: [DroneKit-Python](../../catalog/repos/dronekit__dronekit-python.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [6. Autopilots and C2](../../docs/primer/06-autopilots-and-c2.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [ArduPilot](../../catalog/repos/ardupilot__ardupilot.md) (integrates_with)
- [MAVProxy](../../catalog/repos/ardupilot__mavproxy.md) (depends_on)
- [mavlink-mcp (ArduPilot)](../../catalog/repos/deepakpopli__mavlink-mcp.md) (depends_on)
- [DroneKit-Python](../../catalog/repos/dronekit__dronekit-python.md) (depends_on)
- [MAVLink](../../catalog/repos/mavlink__mavlink.md) (depends_on)
- [Non-GPS Position Estimation](../../catalog/resources/ardupilot-dev-mavlink-nongps-position.md) (uses)
- [ArduPilot EKF3 source-set switch under GPS denial](../../catalog/samples/ardupilot-ekf3-source-switch.md) (uses)
- [How PX4 EKF2 and ArduPilot EKF3 handle a spoofed GNSS: source walk-through plus a 45-flight SITL sweep (drag rate 0.1-5 m/s, step offsets, default vs tightened gates, PX4 EKF2_GPS_MODE)](../../catalog/samples/autopilot-spoof-response.md) (uses)
- [Golden demo: GPS drag (position-only or coherent) on an ArduCopter SITL AUTO mission, integrity monitoring with solution separation + protection level, real visual geolocalization, EKF3 switch to ExternalNav, Monte Carlo, dashboard replay](../../catalog/samples/golden-demo.md) (uses)
- [Golden demo on PX4 v1.17 SIH: coherent GPS drag via HIL_GPS, integrity monitor (SS + PL, GNSS-vs-VIO velocity), EKF2 switch from GNSS to external vision, comparison with ArduPilot, dashboard replay](../../catalog/samples/golden-demo-px4.md) (uses)
- [LLM mission agent: a safety-gated MAVLink MCP server flying ArduPilot SITL](../../catalog/samples/llm-mission-agent.md) (uses)
- [MAVLink telemetry to TAK Cursor-on-Target](../../catalog/samples/mavlink-to-tak-cot.md) (uses)
- [Headless SITL in Docker: ArduCopter and PX4 SIH with one compose file](../../catalog/samples/sitl-docker.md) (uses)
- [VIO to MAVLink bridge with ENU/FLU to NED/FRD conversion](../../catalog/samples/vio-to-mavlink-bridge.md) (uses)

_Indexed by lane(s): autopilots_

_GitHub metadata fetched 2026-11-06._
