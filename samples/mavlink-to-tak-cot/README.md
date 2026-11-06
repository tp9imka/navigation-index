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
- `bridge.py` - pymavlink + PyTAK glue. Run end to end against a fake autopilot and a local sink.
- `fake_autopilot.py` - pymavlink MAVLink source: HEARTBEAT 1 Hz + GLOBAL_POSITION_INT 10 Hz on a 200 m circle.
- `cot_sink.py` - stdlib TCP/UDP listener standing in for a TAK server input; prints each CoT event.
- `offline_demo.sh` - starts sink, fake autopilot and bridge, stops after 5 track events.
- `requirements.txt` - pinned `pymavlink==2.4.50`, `pytak==7.6.1`.

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

## Part 2 - Bridge, offline end to end (verified)

```sh
cd samples/mavlink-to-tak-cot
python3 -m pip install -r requirements.txt
./offline_demo.sh tcp     # bridge => tcp://127.0.0.1:18087 (TAK server style input)
./offline_demo.sh udp     # bridge => udp+wo://127.0.0.1:16969 (Mesh SA style, unicast here)
```

The script runs `fake_autopilot.py --out udpout:127.0.0.1:14550`, `bridge.py --mavlink
udpin:127.0.0.1:14550 --cot-url <url> --callsign UAV-1` and `cot_sink.py`, and exits when
the sink has 5 track events. Set `PYTHON=` to pick the interpreter.

Observed, TCP (pymavlink 2.4.50, pytak 7.6.1, Python 3.12.14, 2026-11-06):

```
other: uid=takPing type=t-x-d-d
cot 1: uid=mavlink-sys1 type=a-f-A-M-F-Q lat=51.5008382 lon=-0.1245914 hae=120.00 course=4.4 speed=15.00 time=2026-11-06T06:38:09.300Z stale=2026-11-06T06:38:39.300Z
<event version="2.0" type="a-f-A-M-F-Q" uid="mavlink-sys1" how="m-g" time="2026-11-06T06:38:09.300Z" start="2026-11-06T06:38:09.300Z" stale="2026-11-06T06:38:39.300Z"><point lat="51.5008382" lon="-0.1245914" hae="120.00" ce="9999999.0" le="9999999.0" /><detail><contact callsign="UAV-1" /><track course="4.4" speed="15.00" /></detail></event>
cot 2: uid=mavlink-sys1 type=a-f-A-M-F-Q lat=51.5009762 lon=-0.1245657 hae=120.00 course=8.8 speed=15.00 time=2026-11-06T06:38:10.331Z stale=2026-11-06T06:38:40.331Z
cot 3: uid=mavlink-sys1 type=a-f-A-M-F-Q lat=51.5011120 lon=-0.1245231 hae=120.00 course=13.3 speed=15.00 time=2026-11-06T06:38:11.358Z stale=2026-11-06T06:38:41.358Z
cot 4: uid=mavlink-sys1 type=a-f-A-M-F-Q lat=51.5012450 lon=-0.1244640 hae=120.00 course=17.7 speed=15.00 time=2026-11-06T06:38:12.382Z stale=2026-11-06T06:38:42.382Z
cot 5: uid=mavlink-sys1 type=a-f-A-M-F-Q lat=51.5013750 lon=-0.1243886 hae=120.00 course=22.1 speed=15.00 time=2026-11-06T06:38:13.408Z stale=2026-11-06T06:38:43.408Z
sink: received 5 track CoT events over tcp
```

The UDP run printed the same shape (`received 5 track CoT events over udp`). What this
shows: `wait_heartbeat` and `recv_match` work in the executor, `uid` comes from the
autopilot's system id, `MIN_SEND_INTERVAL_S` thins 10 Hz telemetry to one event every
~1.03 s, and heading/course and speed round-trip from MAVLink units. PyTAK also sends its
own `takPing` keepalive (`t-x-d-d`) first; a sink or server that expects only tracks must
skip it. When the sink closes, the bridge dies with `BrokenPipeError` (no reconnect logic).

Not verified: a real autopilot or SITL, the multicast group `239.2.3.1:6969`, TLS on
8089, FreeTAKServer / OpenTAKServer, and how ATAK/WinTAK/iTAK render the icon.

Live use:

```sh
python3 bridge.py --mavlink udpin:0.0.0.0:14550 --cot-url udp+wo://239.2.3.1:6969 --callsign UAV-1   # Mesh SA
python3 bridge.py --mavlink udpin:0.0.0.0:14550 --cot-url tcp://127.0.0.1:8087                       # local TAK server
```

with ArduPilot SITL (`sim_vehicle.py -v ArduPlane --out udp:127.0.0.1:14550`) or PX4 SITL
(`make px4_sitl gz_x500`, MAVLink on UDP 14550) as the source.

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
