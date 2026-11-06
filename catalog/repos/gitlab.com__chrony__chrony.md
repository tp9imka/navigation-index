# chrony

`repo:gitlab.com/chrony/chrony` - <https://gitlab.com/chrony/chrony>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| ? | C | ? | ? | ? | production | high |

NTP client and server that also disciplines the system clock from reference clocks (1PPS, gpsd shared memory, PHC). Supports NTS, hardware timestamping on NTP packets, and source selection with outlier rejection. GitHub mirror: mlichvar/chrony.

**Why it matters:** The default Linux time daemon on most distributions; combining a GNSS refclock with several NTS servers is the quickest way to get a clock that notices when one source lies.

**Hackathon notes:** Configure `refclock PPS /dev/pps0 lock NMEA` plus `refclock SHM 0` from gpsd, add `server ... nts` lines, then `chronyc sources -v` and `chronyc tracking` show offset, frequency and which sources are rejected. Good live demo of source selection when one GNSS source is walked off.

**Concepts:** [Timing and time transfer](../concepts/timing.md), [Assured / resilient PNT](../concepts/assured-pnt.md)

**Tags:** `ntp`, `nts`, `refclock`, `pps`, `gpsd`, `linux`, `time-sync`

**Domains:** multi

## Related

- integrates_with: [gpsd](../repos/gitlab.com__gpsd__gpsd.md)
- integrates_with: [linuxptp](../repos/nwtime__linuxptp.md)
- alternative_to: [ntpd-rs](../repos/pendulum-project__ntpd-rs.md)
- alternative_to: [NTPsec](../repos/gitlab.com__ntpsec__ntpsec.md)
- evaluated_on: [clknetsim](../repos/mlichvar__clknetsim.md)
- integrates_with: [chrony_exporter](../repos/superq__chrony_exporter.md)

## Referenced by

- [Time Pi](../repos/geerlingguy__time-pi.md) (depends_on)
- [NTPsec](../repos/gitlab.com__ntpsec__ntpsec.md) (alternative_to)
- [SatPulse](../repos/jclark__satpulse.md) (integrates_with)
- [clknetsim](../repos/mlichvar__clknetsim.md) (integrates_with)
- [linuxptp](../repos/nwtime__linuxptp.md) (integrates_with)
- [ntpd-rs](../repos/pendulum-project__ntpd-rs.md) (alternative_to)
- [pps-tools](../repos/redlab-i__pps-tools.md) (integrates_with)
- [chrony_exporter](../repos/superq__chrony_exporter.md) (integrates_with)
- [Comparison of NTP implementations (chrony)](../resources/chrony-comparison.md) (explains)
- [RFC 5905: Network Time Protocol Version 4: Protocol and Algorithms Specification](../resources/rfc5905-ntpv4.md) (has_code)
- [RFC 8915: Network Time Security for the Network Time Protocol](../resources/rfc8915-nts.md) (has_code)
- [GNSS-disciplined clock holdover per oscillator grade, and a slow time-walk spoof](../samples/timing-holdover.md) (explains)

_Indexed by lane(s): timing_
