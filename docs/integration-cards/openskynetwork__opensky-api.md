# OpenSky Network API client - integration card
<!-- about: repo:openskynetwork/opensky-api -->
One-line: official Python client for OpenSky's REST API - current (and up to 1 h old) ADS-B/MLAT state vectors for a bounding box, plus flights and tracks - for an air picture or a truth/reference feed when you have no receiver.

| | |
|---|---|
| Install | Not on PyPI (`opensky-api` returns 404; open #20 "Add to PyPi" since 2020). README: `pip install "git+https://github.com/openskynetwork/opensky-api.git#subdirectory=python"` or clone and `pip install -e opensky-api/python`. Package name `opensky-api` 1.4.0 (`python/pyproject.toml`), single module `opensky_api`. Only dependency `requests`. |
| Runs on | Any OS, Python >=3.10, Internet access to `opensky-network.org`. README warns OpenSky "may block AWS and other hyperscalers" - run from a laptop, not a cloud VM. |
| Inputs | Optional OAuth2 client credentials (`credentials.json` from the OpenSky account page) - basic auth no longer accepted since 2026-03-18. Query args: `bbox=(min_lat, max_lat, min_lon, max_lon)` in WGS84 degrees, `icao24` hex string(s), Unix time in seconds (or UTC `datetime`). |
| Outputs | `OpenSkyStates` with `.time` and `.states: list[StateVector]`. `StateVector` fields: `icao24`, `callsign`, `origin_country`, `time_position`, `last_contact`, `longitude`, `latitude` (WGS84 deg), `baro_altitude`, `geo_altitude` (m), `on_ground`, `velocity` (m/s), `true_track` (deg from north), `vertical_rate` (m/s), `sensors`, `squawk`, `spi`, `position_source` (0 ADS-B, 1 ASTERIX, 2 MLAT, 3 FLARM), `category`. Also `FlightData`, `FlightTrack` / `Waypoint`. |
| Key API / entry points | `OpenSkyApi(token_manager=None, client_id=None, client_secret=None)` (context manager, `close()`); `TokenManager.from_json_file(path)`; `get_states(time_secs=0, icao24=None, bbox=())`; `get_my_states(time_secs=0, icao24=None, serials=None)` (own receivers, no credit cost); `get_flights_from_interval(begin, end)`; `get_flights_by_aircraft(icao24, begin, end)`; `get_arrivals_by_airport(airport, begin, end)` / `get_departures_by_airport(...)`; `get_track_by_aircraft(icao24, t=0)`. |
| Time to first result | Estimate: 5 min to anonymous aircraft states over a bounding box, assuming pip can reach GitHub and your IP is not a blocked cloud range. |
| License | Client code GPL-3.0 (LICENSE.txt). Data is governed separately by the OpenSky terms of use (README: "By using the OpenSky API, you agree with the terms of use"). |

## Minimal usage

Not run. Adapted from `python/example.py`:

```python
from opensky_api import OpenSkyApi, TokenManager
import os

tm = TokenManager.from_json_file("credentials.json") if os.path.exists("credentials.json") else None
with OpenSkyApi(token_manager=tm) as api:
    s = api.get_states(bbox=(47.2, 55.1, 5.9, 15.1))   # min_lat, max_lat, min_lon, max_lon
    if s is None:
        raise SystemExit("blocked by client-side rate limit or request failed")
    for v in s.states:
        print(v.icao24, v.callsign, v.latitude, v.longitude, v.geo_altitude, v.position_source)
```

## Wiring it into a nav stack

- Air picture without hardware: poll `get_states(bbox=AOI)` every 10 s (anonymous) or 5 s (authenticated), convert to GeoJSON and push to [MapLibre](./maplibre__maplibre-gl-js.md) or to TAK as CoT via [PyTAK](./snstac__pytak.md) (the [adsbcot card](./snstac__adsbcot.md) shows the field mapping for readsb JSON; OpenSky fields map the same way).
- Reference for your own receiver: compare a local [readsb](./wiedehopf__readsb.md) + [pyModeS](./junzis__pymodes.md) picture against OpenSky for the same box and time to sanity-check decoding and position.
- Contributing a receiver: `get_my_states` returns your own feeder's data without credit cost or the 1 h limit (docs `rest.rst`, "own-states").
- Historical work and trajectory analysis: [traffic](../../catalog/repos/xoolive__traffic.md) wraps OpenSky access with resampling and airspace tools.

Catalog page: [catalog/repos/openskynetwork__opensky-api.md](../../catalog/repos/openskynetwork__opensky-api.md). Concepts: [situational-awareness](../../catalog/concepts/situational-awareness.md).

## Gotchas

- Data terms: not reproduced here - the terms page could not be fetched in this pass (automated fetch blocked). Read https://opensky-network.org/about/terms-of-use before any use beyond personal research, and before redistributing data in a deliverable. The docs list a separate "Licensed user" tier (14,400 credits hourly), which points to a licence for heavier or commercial use.
- Credits (docs `rest.rst`): per-endpoint daily buckets - anonymous 400, standard user 4,000, active feeder 8,000; `/states/all` costs 1-4 credits by bbox area (<=25 sq deg = 1, global = 4). A global poll every 10 s exhausts the anonymous bucket in under 20 min. Keep the bbox small.
- Time limits: anonymous ignores `time` and gets only the latest states at 10 s resolution; authenticated can go back 1 h (older => HTTP 400) at 5 s resolution. This is not a history API.
- Methods return `None` instead of raising when the client-side rate limiter blocks the call (10 s anonymous, 5 s authenticated for `get_states`) or the HTTP request fails - always check for `None`. Server-side throttling support is still open (#75).
- OAuth tokens expire after 30 min; `TokenManager` refreshes 30 s before expiry. Old code using `OpenSkyApi(username, password)` no longer works.
- Name confusion on PyPI: `pyopensky` (2.18, open-aviation) and `python_opensky` (1.0.1, MIT) are different projects, not this client.
- `position_source` 2 (MLAT) positions are not broadcast positions; do not treat them as the aircraft's own GNSS when studying spoofing or NIC/NACp.
- Java client is "not actively maintained" (README).

## Alternatives

- [readsb](./wiedehopf__readsb.md) + an RTL-SDR - your own live, local, unthrottled ADS-B; prefer whenever you can put an antenna up.
- [traffic](../../catalog/repos/xoolive__traffic.md) - higher-level trajectory toolbox with OpenSky access built in; prefer for historical analysis.
- [pyModeS](./junzis__pymodes.md) - decode raw Mode S yourself (from your receiver) when you need fields OpenSky's state vectors do not carry.

Sources: `gh api repos/openskynetwork/opensky-api` (GPL-3.0, pushed 2026-11-05), README.md, python/README.md, python/pyproject.toml, python/opensky_api.py (class and method signatures, rate limits, return None), python/example.py, LICENSE.txt, docs/free/rest.rst (auth, limitations, credits), PyPI JSON for `opensky-api` (404), `pyopensky`, `python_opensky`; issues #20, #67, #75. Terms of use page: not read (fetch blocked).
