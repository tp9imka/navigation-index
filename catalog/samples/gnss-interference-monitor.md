# Sample: GNSS interference monitor from u-blox telemetry and ADS-B NACp

`sample:gnss-interference-monitor` - code and walkthrough in [samples/gnss-interference-monitor](../../samples/gnss-interference-monitor/)

A stdlib heuristic scorer turns per-epoch receiver telemetry (C/N0 across SVs, AGC, CW jamming indicator, clock and position jumps, receiver spoofing/jamming flags) into jamming and spoofing scores with stated reasons. A pyubx2 adapter feeds it live from UBX NAV-SAT, NAV-STATUS, NAV-CLOCK, MON-RF and SEC-SIG. A second stdlib module applies the GPSJam percentage method to readsb aircraft.json NACp for area-level interference maps.

**Verification:** scorer.py, adsb_area_map.py and 15 unit tests ran on 2026-11-06 (14 stdlib with python3.14.7; the full set incl. test_ubx_replay with pyubx2 1.4.1 on Python 3.12.14); negative controls: cn0_drop weight 0 fails test_broadband_jamming, disabling NAV-SAT parsing fails test_ubx_replay. ubx_monitor.py replay mode ran on a synthetic UBX capture generated with pyubx2 (gen_synthetic_ubx.py, invented values): jamming 60-89 s and spoofing 120-159 s were flagged on every epoch, clean epochs stayed clean. Not verified: live u-blox receiver (--port/--enable, CFG-VALSET), real recordings, real readsb feed.

**Concepts:** [Jamming and spoofing](../concepts/gnss-interference.md), [Electronic warfare resilience](../concepts/ew-resilience.md), [Assured / resilient PNT](../concepts/assured-pnt.md), [GNSS positioning](../concepts/gnss.md), [Situational awareness and C2 interop](../concepts/situational-awareness.md)

**Tags:** `jamming`, `spoofing`, `u-blox`, `ubx`, `mon-rf`, `agc`, `cn0`, `spoofdetstate`, `sec-sig`, `ads-b`, `nacp`, `gpsjam`, `readsb`, `stdlib`

## Related

- uses: [pyubx2](../repos/semuconsulting__pyubx2.md)
- uses: [readsb](../repos/wiedehopf__readsb.md)
- uses: [pygnssutils](../repos/semuconsulting__pygnssutils.md)
- explains: [Multi-frequency GNSS spoofing raw dataset](../repos/s7am1na__gnss-spoofing-dataset.md)

_Indexed by lane(s): samples_
