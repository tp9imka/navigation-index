# Sample: MAVLink telemetry to TAK Cursor-on-Target

`sample:mavlink-to-tak-cot` - code and walkthrough in [samples/mavlink-to-tak-cot](../../samples/mavlink-to-tak-cot/)

Bridges autopilot GLOBAL_POSITION_INT messages into Cursor-on-Target events so a UAV shows up as a friendly track on ATAK, WinTAK or iTAK. A stdlib-only CoT builder with unit tests is paired with a pymavlink + PyTAK bridge that targets a TAK server or Mesh SA multicast.

**Verification:** cot.py and 4 unit tests ran with python3.14.7 stdlib on 2026-11-06. bridge.py ran end to end on 2026-11-06 with pymavlink 2.4.50 and pytak 7.6.1 (Python 3.12.14): fake_autopilot.py (pymavlink, UDP) => bridge.py => cot_sink.py received well-formed a-f-A-M-F-Q CoT at ~1 Hz over both tcp:// and udp+wo:// (unicast to localhost). Not verified: a real autopilot or SITL, multicast 239.2.3.1, TLS, a real TAK server or ATAK/WinTAK rendering.

## Practical readiness

| Compute | Hardware | Offline | Setup | Dataset download | Tested platforms | Validation |
|---|---|---|---|---|---|---|
| unknown | unknown | unknown | unknown | unknown | unknown | unverified |

**Main limitation:** Read the sample verification; readiness has not been curated.

**Concepts:** [Situational awareness and C2 interop](../../catalog/concepts/situational-awareness.md), [MAVLink, ground control and C2 links](../../catalog/concepts/mavlink-gcs.md), [Standards and interface specs](../../catalog/concepts/standards.md)

**Tags:** `cot`, `tak`, `atak`, `mavlink`, `pytak`, `uav`, `blue-force-tracking`

## Related

- uses: [pymavlink](../../catalog/repos/ardupilot__pymavlink.md)
- uses: [PyTAK](../../catalog/repos/snstac__pytak.md)
- uses: [FreeTAKServer](../../catalog/repos/freetakteam__freetakserver.md)
- uses: [OpenTAKServer](../../catalog/repos/brian7704__opentakserver.md)
- uses: [ATAK-CIV (TAK Product Center)](../../catalog/repos/tak-product-center__atak-civ.md)

## Referenced by

- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Learning paths](../../docs/learning-paths.md) (mentions)
- [6. Autopilots and C2](../../docs/primer/06-autopilots-and-c2.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [C-UAS classifiers on public data: radar tracks (UAV vs bird) and DroneRF spectra](../../catalog/samples/cuas-classifiers.md) (uses)
- [Low-cost GNSS jammer sensor network: u-blox telemetry => localization => TAK and dashboard](../../catalog/samples/jammer-sensor-network.md) (uses)

_Indexed by lane(s): samples_
