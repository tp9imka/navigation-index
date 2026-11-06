# Sample: GNSS interference monitor from u-blox telemetry and ADS-B NACp

`sample:gnss-interference-monitor` - code and walkthrough in [samples/gnss-interference-monitor](../../samples/gnss-interference-monitor/)

A stdlib heuristic scorer turns per-epoch receiver telemetry (C/N0 across SVs, AGC, CW jamming indicator, clock and position jumps, receiver spoofing/jamming flags) into jamming and spoofing scores with stated reasons. A pyubx2 adapter feeds it live from UBX NAV-SAT, NAV-STATUS, NAV-CLOCK, MON-RF and SEC-SIG. A second stdlib module applies the GPSJam percentage method to readsb aircraft.json NACp for area-level interference maps.

**Verification:** scorer.py, adsb_area_map.py and their 14 unit tests ran with python3.14.7 stdlib on 2026-11-06, output shown in README; a negative control (cn0_drop weight 0) made test_broadband_jamming fail as expected. ubx_monitor.py is an unverified sketch: syntax-checked only, requires pyubx2 (attribute names checked against pyubx2 v1.4.1 ubxtypes_get.py) and a u-blox receiver; readsb field names were checked against its README-json.md.

**Concepts:** [Jamming and spoofing](../concepts/gnss-interference.md), [Electronic warfare resilience](../concepts/ew-resilience.md), [Assured / resilient PNT](../concepts/assured-pnt.md), [GNSS positioning](../concepts/gnss.md), [Situational awareness and C2 interop](../concepts/situational-awareness.md)

**Tags:** `jamming`, `spoofing`, `u-blox`, `ubx`, `mon-rf`, `agc`, `cn0`, `spoofdetstate`, `sec-sig`, `ads-b`, `nacp`, `gpsjam`, `readsb`, `stdlib`

## Related

- uses: [pyubx2](../repos/semuconsulting__pyubx2.md)
- uses: [readsb](../repos/wiedehopf__readsb.md)
- uses: [pygnssutils](../repos/semuconsulting__pygnssutils.md)
- explains: [Multi-frequency GNSS spoofing raw dataset](../repos/s7am1na__gnss-spoofing-dataset.md)

_Indexed by lane(s): samples_
