# chrony

`repo:gitlab.com/chrony/chrony` - <https://gitlab.com/chrony/chrony>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| ? | C | ? | ? | ? | production | high |

NTP client and server that also disciplines the system clock from reference clocks (1PPS, gpsd shared memory, PHC). Supports NTS, hardware timestamping on NTP packets, and source selection with outlier rejection. GitHub mirror: mlichvar/chrony.

**Why it matters:** The default Linux time daemon on most distributions; combining a GNSS refclock with several NTS servers is the quickest way to get a clock that notices when one source lies.

**Hackathon notes:** Configure `refclock PPS /dev/pps0 lock NMEA` plus `refclock SHM 0` from gpsd, add `server ... nts` lines, then `chronyc sources -v` and `chronyc tracking` show offset, frequency and which sources are rejected. Good live demo of source selection when one GNSS source is walked off.

## Deep dives

- [_index-round5-nav](../../docs/integration-cards/_index-round5-nav.md) (integration-cards)
- [gitlab.com__chrony__chrony](../../docs/integration-cards/gitlab.com__chrony__chrony.md) (integration-cards)

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md)

**Tags:** `ntp`, `nts`, `refclock`, `pps`, `gpsd`, `linux`, `time-sync`

**Domains:** multi

## Related

- integrates_with: [gpsd](../../catalog/repos/gitlab.com__gpsd__gpsd.md)
- integrates_with: [linuxptp](../../catalog/repos/nwtime__linuxptp.md)
- alternative_to: [ntpd-rs](../../catalog/repos/pendulum-project__ntpd-rs.md)
- alternative_to: [NTPsec](../../catalog/repos/gitlab.com__ntpsec__ntpsec.md)
- evaluated_on: [clknetsim](../../catalog/repos/mlichvar__clknetsim.md)
- integrates_with: [chrony_exporter](../../catalog/repos/superq__chrony_exporter.md)

## Referenced by

- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [Timing resilience: the T in PNT](../../docs/timing-resilience.md) (mentions)
- [Time Pi](../../catalog/repos/geerlingguy__time-pi.md) (depends_on)
- [NTPsec](../../catalog/repos/gitlab.com__ntpsec__ntpsec.md) (alternative_to)
- [SatPulse](../../catalog/repos/jclark__satpulse.md) (integrates_with)
- [clknetsim](../../catalog/repos/mlichvar__clknetsim.md) (integrates_with)
- [ntpperf](../../catalog/repos/mlichvar__ntpperf.md) (same_org)
- [linuxptp](../../catalog/repos/nwtime__linuxptp.md) (integrates_with)
- [ntpd-rs](../../catalog/repos/pendulum-project__ntpd-rs.md) (alternative_to)
- [pps-tools](../../catalog/repos/redlab-i__pps-tools.md) (integrates_with)
- [chrony_exporter](../../catalog/repos/superq__chrony_exporter.md) (integrates_with)
- [Comparison of NTP implementations (chrony)](../../catalog/resources/chrony-comparison.md) (explains)
- [RFC 5905: Network Time Protocol Version 4: Protocol and Algorithms Specification](../../catalog/resources/rfc5905-ntpv4.md) (has_code)
- [RFC 8915: Network Time Security for the Network Time Protocol](../../catalog/resources/rfc8915-nts.md) (has_code)
- [Data for "PTP over wide area networks with offset measurement outlier filtering"](../../catalog/resources/uniri-wan-ptp-outlier-filtering-dataset.md) (evaluates)
- [GNSS-disciplined clock holdover per oscillator grade, and a slow time-walk spoof](../../catalog/samples/timing-holdover.md) (explains)

_Indexed by lane(s): timing_
