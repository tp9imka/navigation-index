# Sample: GNSS jammer geolocation from DF bearings to TAK

`sample:interference-geolocation-to-tak` - code and walkthrough in [samples/interference-geolocation-to-tak](../../samples/interference-geolocation-to-tak/)

Locates a GNSS interference source from KrakenSDR-style direction-of-arrival bearings taken at two fixed sites and one moving vehicle, with noise and multipath outliers. A stdlib robust least-squares triangulation (RANSAC + Gauss-Newton + outlier rejection) runs alongside Stone Soup particle filter and UKF estimators; the fix and its 95% error ellipse go out as Cursor-on-Target events (point + u-d-c-e ellipse) so the emitter can be reported on ATAK/WinTAK. An adapter reads the real krakensdr_doa JSON (websocket) and CSV (DOA_value.html) outputs with the bearing convention taken from its source.

**Verification:** Ran 2026-11-06: 11 unittest cases OK with python3.14.7 stdlib (geo, Kraken JSON/CSV parsing incl. HTTP poll against a local server, triangulation, ellipse, CoT build, UDP send to localhost); locate.py --method all ran with Python 3.12.14 + stonesoup 1.9.1 on synthetic data, outputs in README. Not run: a live KrakenSDR, the websocket listener (needs websockets), and rendering of the CoT ellipse on an ATAK/WinTAK client (ellipse angle convention unverified).

**Concepts:** [Jamming and spoofing](../concepts/gnss-interference.md), [RF localization and direction finding](../concepts/rf-localization.md), [Tracking and data association](../concepts/target-tracking.md), [Situational awareness and C2 interop](../concepts/situational-awareness.md), [Electronic warfare resilience](../concepts/ew-resilience.md)

**Tags:** `jammer`, `direction-finding`, `doa`, `krakensdr`, `triangulation`, `bearing-only`, `stone-soup`, `particle-filter`, `ukf`, `cot`, `tak`, `error-ellipse`

## Related

- uses: [KrakenSDR DoA DSP](../repos/krakenrf__krakensdr_doa.md)
- explains: [Heimdall DAQ firmware](../repos/krakenrf__heimdall_daq_fw.md)
- uses: [Stone Soup](../repos/dstl__stone-soup.md)
- explains: [PyTAK](../repos/snstac__pytak.md)
- explains: [OpenTAKServer](../repos/brian7704__opentakserver.md)
- explains: [ATAK-CIV (TAK Product Center)](../repos/tak-product-center__atak-civ.md)

_Indexed by lane(s): samples_
