# GNSS jammer geolocation from DF bearings to TAK

Goal: find a GNSS interference source so it can be reported and removed. Several
direction-finding (DF) stations, KrakenSDR-style, each report a bearing to the emitter.
Intersect the bearings, put an honest error ellipse on the fix, and push it to TAK as a
Cursor-on-Target (CoT) point plus a 95% ellipse drawing.

```
KrakenSDR DoA (JSON / CSV)  or  scenario.py (same JSON shape)
        => kraken.py  Bearing(t, station, lat, lon, true bearing)
        => triangulate.py (stdlib)  |  locate_stonesoup.py (Stone Soup PF / UKF)
        => tak_out.py  CoT point (a-u-G) + ellipse (u-d-c-e)  => .cot.xml files / UDP
```

Defensive scope: receive-only DF on an interference source. Nothing here transmits.

## Repos used

| Repo | Why |
|---|---|
| `repo:krakenrf/krakensdr_doa` | Real bearing source. Output formats and the bearing convention were read from its source (see "Swapping in a real KrakenSDR"). |
| `repo:krakenrf/heimdall_daq_fw` | Coherent 5-channel DAQ under krakensdr_doa (not used directly). |
| `repo:dstl/stone-soup` | `Cartesian2DToBearing` measurement model, particle filter and UKF. |
| `../mavlink-to-tak-cot/cot.py` | CoT event builder, imported unchanged. |
| `repo:snstac/pytak`, `repo:brian7704/opentakserver`, `repo:tak-product-center/atak-civ` | Where the CoT goes next (TLS transport, server, client). |

## Files

- `geo.py` - WGS84 <=> local ENU, compass bearings, meridian-convergence correction (stdlib).
- `kraken.py` - adapter: `from_kraken_json`, `from_kraken_csv_line`, `read_jsonl`,
  `poll_csv(url)`, `listen_ws(url, cb)` (stdlib except the websocket listener).
- `scenario.py` - synthetic bearings: jammer at 52.0800 N 5.1200 E on GPS L1, fixed sites
  KR-A and KR-B (3 deg 1-sigma), vehicle KR-C-mobile driving east then south-east at
  12 m/s (5 deg 1-sigma, heading error lumped in), 1 Hz for 300 s, 12% multipath outliers
  offset 25-160 deg. Emits records in the krakensdr_doa "Kraken Pro Local" JSON shape.
- `triangulate.py` - stdlib baseline: RANSAC over bearing pairs, range-weighted
  Gauss-Newton on angle residuals, iterative 3-sigma rejection, covariance and ellipse.
- `locate_stonesoup.py` - Stone Soup: particle filter with a heavy-tailed bearing
  likelihood (Gaussian mixed with a uniform floor, so multipath bearings do not collapse
  the cloud) and a UKF with a 3-sigma innovation gate. Static emitter as a random walk.
- `tak_out.py` - CoT point + ellipse, `.cot.xml` writer, UDP sender (Mesh SA default
  239.2.3.1:6969).
- `locate.py` - CLI tying it together. `test_pipeline.py` - unittest, stdlib only.
- `example_output/` - the CoT files and first JSON lines from the run below.

## Run (all of this was run on 2026-11-06)

Stdlib tests (python3.14.7):

```
$ python3 -m unittest -v test_pipeline
test_bearing_and_wrap (test_pipeline.GeoTest.test_bearing_and_wrap) ... ok
test_bearing_in_frame_convergence (test_pipeline.GeoTest.test_bearing_in_frame_convergence) ... ok
test_enu_round_trip (test_pipeline.GeoTest.test_enu_round_trip) ... ok
test_csv_line_matches_json (test_pipeline.KrakenAdapterTest.test_csv_line_matches_json) ... ok
test_json_convention (test_pipeline.KrakenAdapterTest.test_json_convention) ... ok
test_poll_csv_over_http (test_pipeline.KrakenAdapterTest.test_poll_csv_over_http) ... ok
test_events (test_pipeline.TakOutTest.test_events) ... ok
test_write_and_udp (test_pipeline.TakOutTest.test_write_and_udp) ... ok
test_ellipse_axes (test_pipeline.TriangulateTest.test_ellipse_axes) ... ok
test_noiseless_exact (test_pipeline.TriangulateTest.test_noiseless_exact) ... ok
test_rejects_multipath_outliers (test_pipeline.TriangulateTest.test_rejects_multipath_outliers) ... ok
----------------------------------------------------------------------
Ran 11 tests in 0.596s
OK
```

`test_poll_csv_over_http` serves a CSV line from a local `http.server`; `test_write_and_udp`
sends the CoT to a UDP socket on localhost. Neither touches real hardware or a TAK client.

Stdlib baseline only:

```
$ python3 locate.py
synthetic: 900 bearings from 3 stations, 111 injected outliers
ls     lat=52.079990 lon=5.120200  95% ellipse 49 x 33 m @ 90 deg  used 789/900  error 14 m
wrote out/jammer-est-1-0.cot.xml
wrote out/jammer-est-1-1.cot.xml
```

All three estimators (Python 3.12.14, stonesoup 1.9.1, numpy 2.5.4, scipy 1.18.1 in a venv;
about 40 s wall on the first run, mostly imports and the 5000-particle filter):

```
$ pip install -r requirements.txt
$ python locate.py --method all
synthetic: 900 bearings from 3 stations, 111 injected outliers
ls     lat=52.079990 lon=5.120200  95% ellipse 49 x 33 m @ 90 deg  used 789/900  error 14 m
pf     lat=52.079990 lon=5.120176  95% ellipse 57 x 41 m @ 93 deg  used 900/900  error 12 m
ukf    lat=52.079983 lon=5.120116  95% ellipse 54 x 40 m @ 91 deg  used 784/900  error 8 m
```

Only the first 30 s (90 bearings), closer to what you have when the jammer first shows up:

```
$ python locate.py --method all --window 30
window 30 s: 90 bearings
ls     lat=52.079754 lon=5.120900  95% ellipse 167 x 105 m @ 86 deg  used 79/90  error 68 m
pf     lat=52.079746 lon=5.121103  95% ellipse 161 x 88 m @ 85 deg  used 90/90  error 81 m
ukf    lat=52.079702 lon=5.120944  95% ellipse 175 x 109 m @ 89 deg  used 80/90  error 73 m
```

Reading the numbers: these come from one seeded synthetic run with Gaussian bearing noise
and gross outliers; real DF bearings have biased, correlated multipath that this does not
model, so treat the ellipse sizes as best case. In every run the true position is inside
the 95% ellipse. The PF reports 900/900 "used" because it down-weights outliers instead of
dropping them. The UKF starts from a 5 km prior at the station centroid and still gated out
the outliers here; with worse geometry or an early burst of outliers it can lock onto a wrong
line, so the PF or the RANSAC baseline is the safer default.

Recorded JSON lines, no truth available (the default sigma 5 deg is applied to every
station, so the ellipse is wider than the synthetic run that knew per-station sigmas):

```
$ python3 scenario.py synthetic_bearings.jsonl
wrote 900 bearings (111 injected outliers) to synthetic_bearings.jsonl
$ python3 locate.py --jsonl synthetic_bearings.jsonl
ls     lat=52.080044 lon=5.120410  95% ellipse 73 x 49 m @ 106 deg  used 789/900
```

## CoT output

`example_output/jammer-est-1-0.cot.xml` (point; `ce` = 1-sigma semi-major axis):

```xml
<event version="2.0" type="a-u-G" uid="jammer-est-1" how="m-f" time="2026-11-06T07:32:00.646Z" start="2026-11-06T07:32:00.646Z" stale="2026-11-06T07:42:00.646Z"><point lat="52.0799904" lon="5.1202001" hae="0.00" ce="20.0" le="9999999.0" /><detail><contact callsign="GNSS-JAM est" /><remarks>GNSS interference source estimate (ls, 789/900 bearings). 95% ellipse 49 x 33 m.</remarks></detail></event>
```

`example_output/jammer-est-1-1.cot.xml` (ellipse drawing):

```xml
<event version="2.0" type="u-d-c-e" uid="jammer-est-1.ellipse" how="m-f" ...><point lat="52.0799904" lon="5.1202001" hae="0.00" ce="9999999.0" le="9999999.0" /><detail><contact callsign="GNSS-JAM 95%" /><shape><ellipse major="49.0" minor="32.8" angle="89.6" /><link uid="jammer-est-1.ellipse.Style" type="b-x-KmlStyle" relation="p-c"><Style><LineStyle><color>ff0000ff</color><width>3.0</width></LineStyle><PolyStyle><color>400000ff</color></PolyStyle></Style></link></shape></detail></event>
```

Notes on the CoT:
- `a-u-G` (unknown, ground) is a neutral choice; change `EMITTER_COT_TYPE` to whatever your
  unit uses for an interference source. `how` is retagged from cot.py's `m-g` to `m-f` (fused).
- The ellipse layout (`shape/ellipse major minor angle` + `b-x-KmlStyle` link, radii in
  metres) follows dfpc-coe/node-cot's `u-d-c-e` test fixture and meshtastic's atak.proto
  ("major radius"). `angle` is written as the compass bearing of the major axis; that
  convention was not checked on an ATAK client (node-cot fixtures also carry a `swapAxis`
  flag, so verify the orientation once on a device before trusting it).
- `hae="0.00"` because DF gives no height; `le` stays unknown.
- Send it: `python3 locate.py --send-udp 239.2.3.1:6969` (Mesh SA multicast, which ATAK
  listens on by default) or the UDP CoT input of a TAK server. Not run against a client.
  For TCP/TLS to a TAK server use PyTAK (see `../mavlink-to-tak-cot/bridge.py`).

## Swapping in a real KrakenSDR

Read from krakenrf/krakensdr_doa at commit 2e1c4e6 (2025-12-13), not run on hardware.

| Mode (`doa_data_format` in settings) | Where | Shape | Adapter |
|---|---|---|---|
| "Kraken Pro Local" | `SignalProcessor.wr_json()` POSTs each VFO to the node middleware `/doapost` (`_nodejs/index.js`, port 8042), which rebroadcasts it to websocket clients on `ws://KRAKEN_IP:8021` | JSON: `station_id, tStamp` (ms), `latitude, longitude` (strings), `gpsBearing` (station heading), `radioBearing` (raw DoA theta), `conf, power, freq, antType, ...` | `kraken.listen_ws("ws://KRAKEN_IP:8021", cb)` |
| "Kraken App" (default) | `DOA_value.html` rewritten every frame, served on `http://KRAKEN_IP:8081/DOA_value.html` | CSV per VFO: `timestamp, 360 - theta, conf, power, freq, ant_type, latency, station_id, lat, lon, heading, heading, GPS, R, R, R, R, <spectrum>` | `kraken.poll_csv(url)` or `locate.py --kraken-csv URL --polls N` |
| any | `doa.xml` in the shared folder (always written, used by DF-Aggregator) | XML, first VFO only | not implemented |

Bearing convention: `calculate_end_lat_lng()` in the same file draws the bearing line at
`heading + 360 - theta`, so `kraken.py` computes the true bearing as
`(gpsBearing + 360 - radioBearing) % 360` for JSON and `(heading + field2) % 360` for CSV
(field 2 is already `360 - theta`). `heading` is the array orientation from settings for a
fixed station, or GPS/compass heading for a mobile one; a wrong heading rotates every
bearing from that station, which no estimator here can detect. Check against a known
transmitter first.

To use several stations: give each a unique `station_id`, collect their bearings into one
list (one `poll_csv` per station, or one websocket per station), then call
`triangulate.locate(bearings, sigma_deg)` or `locate_stonesoup.locate_pf(...)`. Recording to
JSONL (one `to_kraken_json`-shaped dict per line) and replaying with `--jsonl` is the easiest
way to iterate offline.

## Gotchas and limits

- Bearings are measured against local true north at each station. Over a few km the north
  of a shared tangent plane differs by the meridian convergence (about 0.14 deg for 12 km
  east-west at 52 N); ignoring it cost 1.7 m of error in the noiseless test before
  `bearing_in_frame()` was added. Small, but it is a bias, not noise.
- Same-station bearings are treated as independent. A fixed site's multipath is
  persistent, so its 300 bearings do not carry 300x the information; the ellipse is
  optimistic for long dwell times. Inflate sigma or decimate per station for real data.
- Geometry matters more than count: two stations nearly in line with the emitter give a
  long thin ellipse. The moving station is what gives cross-range here.
- Frequency coverage is not stated in the krakensdr_doa or heimdall READMEs. KrakenSDR
  uses RTL-SDR-class R820T2 tuners, which reach roughly 1.7 GHz (general RTL-SDR knowledge,
  not checked here), so L1 at 1575.42 MHz should be in range but near the top; the array
  spacing must suit the wavelength (about 19 cm at L1). Confirm on the KrakenSDR docs wiki.
- The synthetic outliers are random gross errors; real multipath often gives a consistent
  wrong bearing, which RANSAC can pick if it outnumbers the direct path.

Related: [Stone Soup tracking sample](../stone-soup-tracking/), [MAVLink to TAK CoT](../mavlink-to-tak-cot/),
[GNSS interference monitor](../gnss-interference-monitor/), [KrakenSDR DoA card](../../docs/integration-cards/krakenrf__krakensdr_doa.md),
[Stone Soup card](../../docs/integration-cards/dstl__stone-soup.md).
