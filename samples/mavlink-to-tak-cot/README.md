# MAVLink to TAK (Cursor-on-Target) bridge

Goal: show your drone on ATAK / WinTAK / iTAK maps. Read `GLOBAL_POSITION_INT` from an
autopilot over MAVLink, turn each fix into a Cursor-on-Target (CoT) XML event, and send it
to a TAK server or straight onto the Mesh SA multicast group. This is the "friendly blue
force track" piece of situational awareness for a hackathon UAV build.

## Repos used

| Repo | Why |
|---|---|
| `repo:ardupilot/pymavlink` | Python MAVLink parser; `mavutil.mavlink_connection` + `recv_match` read the telemetry stream. |
| `repo:snstac/pytak` | asyncio TAK client; handles TCP/TLS/UDP/multicast transport so you only produce CoT bytes. |
| `repo:freetakteam/freetakserver` | Open-source TAK server you can run locally to fan events out to clients. |
| `repo:brian7704/opentakserver` | Alternative open-source TAK server with a web UI. |
| `repo:tak-product-center/atak-civ` | The ATAK-CIV client that renders the track. |

## Files

- `cot.py` - stdlib-only CoT builder. `build_event(...)` and
  `from_global_position_int(msg, uid, ...)`. No dependencies.
- `test_cot.py` - unit tests that build events and parse the XML back with `xml.etree`.
- `bridge.py` - pymavlink + PyTAK glue. Sketch: syntax-checked, not run.

## Part 1 - CoT builder (verified, stdlib only)

```sh
cd samples/mavlink-to-tak-cot
python3 -m unittest -v test_cot
python3 cot.py
```

Observed output (python3.14.7, 2026-11-06):

```
test_no_track_without_velocity (test_cot.BuildEventTest.test_no_track_without_velocity) ... ok
test_round_trip (test_cot.BuildEventTest.test_round_trip) ... ok
test_course_from_velocity_when_heading_unknown (test_cot.GlobalPositionIntTest.test_course_from_velocity_when_heading_unknown) ... ok
test_scaling (test_cot.GlobalPositionIntTest.test_scaling) ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.001s

OK
<event version="2.0" type="a-f-A-M-F-Q" uid="uav-demo-1" how="m-g" time="2026-11-06T05:19:46.561Z" start="2026-11-06T05:19:46.561Z" stale="2026-11-06T05:20:16.561Z"><point lat="51.5007000" lon="-0.1246000" hae="120.00" ce="9999999.0" le="9999999.0" /><detail><contact callsign="DEMO-1" /><track course="90.0" speed="15.00" /></detail></event>
```

(Timestamps differ on every run.)

Event fields:

- `type="a-f-A-M-F-Q"` - atom / friendly / air / military / fixed wing / UAV.
- `how="m-g"` - machine-generated from GPS.
- `time`, `start`, `stale` - UTC, millisecond ISO 8601 with `Z`. Stale is 30 s after time
  (`DEFAULT_STALE_S`); clients grey out the icon after that.
- `point` - `lat`/`lon` in degrees, `hae` metres above the WGS84 ellipsoid, `ce`/`le`
  circular/linear error in metres (`9999999.0` = unknown).
- `detail/track` - `course` degrees true, `speed` m/s.
- `detail/contact` - `callsign` shown on the map.

## Part 2 - Live bridge (unverified sketch)

Prerequisites (not installed in this repo's verification environment):

```sh
python3 -m pip install pymavlink pytak
```

A MAVLink source, for example ArduPilot SITL (`sim_vehicle.py -v ArduPlane --out udp:127.0.0.1:14550`)
or PX4 SITL (`make px4_sitl gz_x500`, MAVLink on UDP 14550).

Run against the ATAK Mesh SA multicast group (clients on the same LAN see it, no server):

```sh
python3 bridge.py --mavlink udpin:0.0.0.0:14550 --cot-url udp+wo://239.2.3.1:6969 --callsign UAV-1
```

Run against a local FreeTAKServer / OpenTAKServer TCP input:

```sh
python3 bridge.py --mavlink udpin:0.0.0.0:14550 --cot-url tcp://127.0.0.1:8087
```

Expected: a friendly UAV icon named `UAV-1` moving on ATAK/WinTAK/iTAK, refreshed once per
second (`MIN_SEND_INTERVAL_S`).

## Extending it in a hackathon

- Fill `ce`/`le` from the EKF: `GPS_RAW_INT.eph`/`epv` or `ESTIMATOR_STATUS` accuracies.
  In GNSS-denied tests this makes degraded navigation visible to the whole team.
- Publish one event per vehicle (`uid` per `target_system`) for a swarm.
- Add `detail/remarks` with nav-source state (GNSS / VIO / dead reckoning).
- Use `stale_s` shorter than your link timeout so a lost link shows as a stale icon.

## Pitfalls

- MAVLink `GLOBAL_POSITION_INT.alt` is AMSL, CoT `hae` is ellipsoidal. Pass
  `--geoid-sep <N metres>` for your area (EGM96/EGM2008 N can be tens of metres).
- `hdg == 65535` means heading unknown; `cot.py` then derives course from `vx`/`vy`.
- `recv_match(blocking=True)` blocks; `bridge.py` runs it in an executor so the PyTAK
  asyncio loop keeps sending.
- `udp+wo://` is write-only; drop `+wo` if you also want to receive CoT.
- TAK servers often require TLS client certificates on 8089; see PyTAK docs
  (`PYTAK_TLS_CLIENT_CERT`) - plain TCP 8087 is for local testing only.
