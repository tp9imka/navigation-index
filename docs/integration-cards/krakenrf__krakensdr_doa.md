# KrakenSDR DoA - integration card
<!-- about: repo:krakenrf/krakensdr_doa -->
One-line: direction-of-arrival DSP and web UI for the 5-channel coherent KrakenSDR (or KerberosSDR); outputs per-frame bearings with confidence, power and station GPS as CSV, XML or JSON, which several stations can triangulate into emitter positions for spectrum awareness or C-UAS detection.

| | |
|---|---|
| Install | Easiest: prebuilt Raspberry Pi 4/5 or Orange Pi 5B SD images (auto-start on boot), a beta VirtualBox image, or a third-party Docker image (links in README / krakensdr_docs wiki). Manual: install [Heimdall DAQ](../../catalog/repos/krakenrf__heimdall_daq_fw.md) first (creates the `kraken` conda env), then in that env pinned deps (`dash==1.20.0`, `werkzeug==2.0.2`, `plotly==5.23.0`, `quart==0.17.0`, `dash_devices==0.1.3`, `dash_bootstrap_components==1.1.0`, `quart_compress==0.2.1`, `pyargus`, pandas, orjson, matplotlib, requests), `git clone https://github.com/krakenrf/krakensdr_doa` into `~/krakensdr`, copy `util/kraken_doa_start.sh` and `kraken_doa_stop.sh` up one level. Latest release seen V1.8.0 (2024-03). |
| Runs on | Raspberry Pi 4/5 (overclock + cooling recommended), Orange Pi 5B, x86 Linux; DAQ and DSP can run on separate machines over Ethernet. Needs KrakenSDR hardware or recorded IQ. |
| Inputs | Coherent IQ frames from Heimdall DAQ (shared memory or remote); settings in `settings.json` (centre frequency, array type `ULA`/`UCA`, UCA radius, algorithm `MUSIC`/`Bartlett`/`Capon`/`MEM`/`TNA`/`ROOT-MUSIC`, decorrelation `FBA`/`TOEP`/`FBSS`, VFO bandwidth and squelch, station ID, fixed or GPS location/heading); optional `gpsd` USB GPS. |
| Outputs | Web UI on port 8080. `DOA_value.html` rewritten every frame (served on 8081) in "Kraken App" CSV: `timestamp, 360 - theta, confidence, max_power, freq, array_type, latency_ms, station_id, lat, lon, heading, heading, "GPS", R, R, R, R, <DoA spectrum values...>`. Always an XML file with `STATION_ID, TIME, GPS_TIME, FREQUENCY, LOCATION{LATITUDE, LONGITUDE, HEADING, SPEED}, DOA, PWR, CONF, LATENCY, PROCESSING_TIME, ADC_OVERDRIVE, NUM_CORRELATED_SOURCES, SNR_DB`. "Kraken Pro Local/Remote" JSON per VFO: `station_id, tStamp, gps_timestamp, latitude, longitude, gpsBearing, speed, radioBearing, conf, power, freq, antType, ...`. Optional POST to an RDF Mapper server. |
| Key API / entry points | `./kraken_doa_start.sh` (starts Heimdall `daq_start_sm.sh`, then `gui_run.sh`, and a Kraken-to-TAK service if `../Kraken-to-TAK-Python` exists), `gui_run.sh`, `kill.sh`; settings over HTTP: GET/POST `http://KRAKEN_IP:8042/settings` (middleware) or upload to `http://KRAKEN_IP:8081/upload?path=/`; DSP core `_sdr/_signal_processing/kraken_sdr_signal_processor.py` (`SignalProcessor`, `estimate_DOA`, `wr_xml`, `wr_json`). |
| Time to first result | Estimate: 30-60 min with a prebuilt Pi image, a KrakenSDR and a 5-element array to see a bearing on a known transmitter. Days without the hardware; synthetic DAQ mode exists in Heimdall (commented `daq_synthetic_start.sh` line in the start script) but was not tried. |
| License | GPL-3.0. |

## Minimal usage
Remote control and polling from another machine, from README plus the output format in `kraken_sdr_signal_processor.py`. Not run.

```bash
curl http://KRAKEN_IP:8042/settings > settings.json          # read settings
# edit center_freq, ant_arrangement, station lat/lon ...
curl -X POST -H "Content-Type: application/json" -d @settings.json http://KRAKEN_IP:8042/settings
curl http://KRAKEN_IP:8081/DOA_value.html                      # one CSV line per VFO
```
Note the CSV bearing is written as `360 - theta`; check the convention against a known transmitter and the compass offset before fusing.

## Wiring it into a nav stack
- Triangulation and tracking: bearings from 2+ stations => [Stone Soup](./dstl__stone-soup.md) `Cartesian2DToBearing` detections (station position via [pymap3d](./geospace-code__pymap3d.md) to local ENU) => emitter track with covariance.
- Common picture: Kraken-to-TAK service (hooked from the start script) or your own [PyTAK](./snstac__pytak.md) bridge sending bearing lines and fused fixes to [OpenTAKServer](./brian7704__opentakserver.md) / [GoATAK](./kdudkov__goatak.md).
- On a moving platform the station heading matters as much as the bearing; take heading from the vehicle autopilot ([MAVROS](./mavlink__mavros.md) / [pymavlink](./ardupilot__pymavlink.md)) rather than GPS course when slow.
- Pair with [readsb](./wiedehopf__readsb.md) NIC/NACp monitoring for a GNSS-interference awareness demo (detect degradation from aircraft, bearing to an emitter from DF), staying on the defensive detection side.
- Catalog: [KrakenSDR DoA page](../../catalog/repos/krakenrf__krakensdr_doa.md).

## Gotchas
- Dependency pins are fragile (README insists on install order and exact dash/werkzeug versions). Open #145 reports `np.Infinity` errors, which points at NumPy 2 removing that alias; keep NumPy < 2 in the env (inference from the issue title, not tested).
- First run takes 1-2 min on a Pi while numba JIT-compiles; the UI looks frozen meanwhile (README). Open #157: port 8080 not opening.
- `UCA` arrays are internally switched to a virtual ULA when `ROOT-MUSIC` or decorrelation is selected (`estimate_DOA`), which changes behaviour silently.
- Multipath indoors makes bearings meaningless; test outdoors with line of sight.
- Legal: receive-only DF is generally fine, but check local rules on monitoring specific bands; never transmit test signals outside allowed bands.

## Alternatives
- [Heimdall DAQ firmware](../../catalog/repos/krakenrf__heimdall_daq_fw.md) alone if you want to write your own DoA on the coherent IQ.
- A single rotating directional antenna plus RSSI (no repo indexed) is a cheaper but slower bearing source.

Sources: `README.md`, repo tree, `_sdr/_signal_processing/kraken_sdr_signal_processor.py` (output writers, `estimate_DOA`, algorithm names), `util/kraken_doa_start.sh`, releases API, issue search (#145, #157).
