# Sample: MAVLink telemetry to TAK Cursor-on-Target

`sample:mavlink-to-tak-cot` - code and walkthrough in [samples/mavlink-to-tak-cot](../../samples/mavlink-to-tak-cot/)

Bridges autopilot GLOBAL_POSITION_INT messages into Cursor-on-Target events so a UAV shows up as a friendly track on ATAK, WinTAK or iTAK. A stdlib-only CoT builder with unit tests is paired with a pymavlink + PyTAK bridge that targets a TAK server or Mesh SA multicast.

**Verification:** cot.py and test_cot.py ran with python3.14.7 stdlib on 2026-11-06 (4 tests OK), output shown in README; bridge.py is an unverified sketch: syntax-checked only, requires pymavlink and pytak plus a MAVLink source and TAK endpoint.

**Concepts:** [Situational awareness and C2 interop](../concepts/situational-awareness.md), [MAVLink, ground control and C2 links](../concepts/mavlink-gcs.md), [Standards and interface specs](../concepts/standards.md)

**Tags:** `cot`, `tak`, `atak`, `mavlink`, `pytak`, `uav`, `blue-force-tracking`

## Related

- uses: [pymavlink](../repos/ardupilot__pymavlink.md)
- uses: [PyTAK](../repos/snstac__pytak.md)
- uses: [FreeTAKServer](../repos/freetakteam__freetakserver.md)
- uses: [OpenTAKServer](../repos/brian7704__opentakserver.md)
- uses: [ATAK-CIV (TAK Product Center)](../repos/tak-product-center__atak-civ.md)

_Indexed by lane(s): samples_
