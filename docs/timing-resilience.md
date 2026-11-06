# Timing resilience: the T in PNT

<!-- about: repo:nwtime/linuxptp, repo:gitlab.com/chrony/chrony, repo:aewallin/allantools, repo:jclark/satpulse, repo:tum-esi/ptpsec, repo:time-appliances-project/time-card, repo:andrewbcn/stm32-gpsdo, repo:cloudflare/roughtime, repo:pendulum-project/ntpd-rs, repo:gitlab.com/ohwr/project/wr-cores, res:nist-sp1065-frequency-stability-handbook, res:cisa-time-guidance-network-operators, res:itu-t-g8272-1-eprtc, res:rfc8915-nts -->

After this page you can explain why a GNSS-denied system loses time before it loses position,
estimate how long a given oscillator holds time from its datasheet, name the attacks on GNSS
and network time, and pick a 24-48 h build that shows timing resilience with numbers.

Working code: [samples/timing-holdover](../samples/timing-holdover/) (stdlib Python, run and
tested). Numbers on this page marked "sample" are that run's observed output; numbers marked
"computed" come from the formulas below and the cited oscillator figures.

## 1. Why timing is its own problem

- **GNSS receivers are clocks first.** Every GNSS fix solves for receiver clock bias, and many
  systems (telecom, power grid phasor units, data centres, broadcast) use GNSS only for time.
  Jamming takes that time away; spoofing can move it without any position effect on a static
  site.
- **Distributed sensing needs common time.** TDOA localization, multistatic radar and coherent
  DF arrays turn time error straight into position error: light covers about 0.3 m per
  nanosecond. A TDOA network whose receivers each hold time from GNSS fails when GNSS is jammed,
  even if nothing else in the system uses GNSS.
- **Faults happen without attackers.** On 26 January 2016 GPS receivers worldwide reported time
  about 13 microseconds off for hours, traced to faulty UTC correction parameters uploaded during
  the retirement of SVN 23
  ([Meinberg note](../catalog/resources/meinberg-gps-utc-anomaly-2016.md),
  [Inside GNSS](../catalog/resources/insidegnss-gps-utc-anomaly-2016.md)). Navigation was fine;
  only time was wrong.
- **Policy says so.** [CISA time guidance](../catalog/resources/cisa-time-guidance-network-operators.md),
  the [DHS S&T 2025 PNT best practices](../catalog/resources/dhs-st-pnt-best-practices-critical-infrastructure-2025.md)
  (stationary timing use case), the [NIST PNT profile](../catalog/resources/nist-ir-8323r1-pnt-profile.md)
  and the [DHS conformance framework](../catalog/resources/dhs-resilient-pnt-conformance-framework.md)
  all ask for the same three things: know your time sources, have more than one, detect when one
  is wrong.

## 2. Vocabulary

| Term | Meaning |
|---|---|
| Phase / time error `x(t)` | local clock minus reference time, seconds |
| Fractional frequency `y` | `dx/dt`; 1e-9 = 1 ppb = 86.4 us per day |
| Aging `D` | slow linear change of `y` with time, quoted per day, month or year |
| ADEV `sigma_y(tau)` | Allan deviation: frequency stability over averaging time `tau` ([NIST SP 1065](../catalog/resources/nist-sp1065-frequency-stability-handbook.md)) |
| TDEV, MTIE | time-domain stability statistics used in telecom specs |
| Holdover | running on the local oscillator after the reference (GNSS) is lost |
| GPSDO | GNSS-disciplined oscillator: a loop steers a local oscillator to the receiver's 1PPS |
| PRTC / ePRTC | telecom names for a GNSS-fed time source and its enhanced, long-holdover version ([G.8272](../catalog/resources/itu-t-g8272-prtc.md), [G.8272.1](../catalog/resources/itu-t-g8272-1-eprtc.md)) |
| Grandmaster, BC, TC | PTP roles: the time source, boundary clock, transparent clock ([IEEE 1588-2019](../catalog/resources/ieee-1588-2019.md)) |
| PHC | PTP hardware clock inside a NIC; linuxptp's `phc2sys` copies it to the system clock |
| NTS | Network Time Security, authenticated NTP ([RFC 8915](../catalog/resources/rfc8915-nts.md)) |

## 3. Holdover math: from a datasheet to time error

After GNSS is lost at `t = 0`, free-running time error grows as

```
x(t) = x0 + y0 * t + D * t^2 / 2 + e(t)
```

- `x0`: time error at the moment of loss (the loop's locked error, a few to tens of ns).
- `y0`: residual frequency error the loop left behind. 1e-11 gives 0.86 us per day; 1e-9 gives
  3.6 us per hour. A good holdover design spends most of its effort here: long averaging before
  the loss, and aging-rate estimation.
- `D t^2 / 2`: aging. Quadratic, so it dominates long outages.
- `e(t)`: oscillator noise. A useful order-of-magnitude rule is `|e(t)| ~ t * sigma_y(t)`. For
  white frequency noise `sigma_y(t) = sigma_1 / sqrt(t)`, so `e(t) ~ sigma_1 * sqrt(t)`, which
  is exactly the random-walk phase the sample simulates. For flicker or random-walk FM the
  growth is faster (`~t` and `~t^1.5`); read the slope of your ADEV plot before extrapolating.
- Temperature: a TCXO or OCXO frequency follows temperature. Over a day the temperature term
  is often bigger than aging for anything below an OCXO.

Computed, aging term alone over 24 h, from Vig's oscillator table
([Vig](../catalog/resources/vig-intro-quartz-frequency-standards.md)) and the
[SA65 datasheet](../catalog/resources/microchip-csac-sa65-datasheet.md):

| Grade | ADEV at 1 s | Aging | `D` (1/s) | Aging error after 1 h | after 24 h | White-FM noise after 24 h |
|---|---|---|---|---|---|---|
| TCXO | 1e-9 | 5e-7 / year | 1.6e-14 | 103 ns | 59 us | 0.29 us |
| CSAC (SA65) | 3e-10 | <9e-10 / month | 3.4e-16 | 2.2 ns | 1.3 us | 88 ns |
| OCXO | 1e-12 | 5e-9 / year | 1.6e-16 | 1.0 ns | 0.59 us | 0.3 ns |
| Rubidium | 3e-12 | 2e-10 / year | 6.3e-18 | 0.04 ns | 24 ns | 0.9 ns |

Read it with care: Vig's 1 s figure for an OCXO is near its flicker floor, so white-FM
extrapolation understates OCXO noise at long `tau`; real units also have retrace after power
cycling, warm-up, vibration and temperature terms. Reference points from sources: Meta's
open Time Card targets within 1 us over 24 h of holdover with a miniature atomic clock
([Meta 2021](../catalog/resources/meta-time-appliance-2021.md)); the telecom ePRTC is
summarized as within 100 ns of UTC over a multi-week holdover with a cesium-class reference
([Calnex summary](../catalog/resources/calnex-eprtc-summary.md), check the ITU text).

**Loop time constant.** GNSS 1PPS noise is white phase noise, ADEV about `sqrt(3) * sigma_pps / tau`;
the oscillator is about `sigma_1 / sqrt(tau)`. Trust GNSS above the crossover, trust the
oscillator below it: `tau_c = (sqrt(3) * sigma_pps / sigma_1)^2`. With 20 ns PPS noise that is
about 1200 s for a TCXO and over 13000 s for the SA65 (computed). Long time constants also
mean a disciplined clock follows a slow spoof slowly, which is what makes the internal monitor
in section 5 possible.

### Sample results (samples/timing-holdover, default run)

Median |time error| after a GNSS outage, 20 runs per grade, no temperature term:

| Grade | 1 h | 4 h | 24 h |
|---|---|---|---|
| TCXO | 146 ns | 1.67 us | 59.6 us |
| CSAC | 19 ns | 89 ns | 1.27 us |
| OCXO | 2.1 ns | 20 ns | 0.61 us |
| Rb | 1.5 ns | 5.2 ns | 44 ns |

With a 24 h temperature cycle at 10 % of each spec (an assumption) the 24 h medians become
TCXO 3.4 ms, OCXO 6.5 us, CSAC 3.1 us, Rb 2.1 us: the CSAC overtakes the OCXO because its
temperature figure is a third of Vig's OCXO figure.

## 4. Threats to time

| Threat | What happens | Reference |
|---|---|---|
| GNSS jamming | receiver loses lock; system enters holdover; error grows per section 3 | [Jammertest](../catalog/resources/jammertest-norway.md) |
| GNSS time-push spoofing | receiver keeps "lock" while time is walked off slowly; a GPSDO follows | [Shepard, Humphreys 2012](../catalog/resources/shepard-humphreys-2012-pmu-spoofing.md), [TEXBAT](../catalog/resources/ut-texbat.md) |
| Serial / NMEA injection | time server trusts the receiver's serial time; no RF needed | [NMEAdesync](../catalog/repos/zxsecurity__nmeadesync.md) |
| NTP time shifting | on-path or off-path attacks on unauthenticated NTP | [Malhotra 2016](../catalog/resources/malhotra-2016-attacking-ntp.md) |
| PTP delay attacks | attacker delays one direction; PTP assumes symmetric paths; crypto does not help | [RFC 7384](../catalog/resources/rfc7384-time-protocol-security.md), [PTPsec](../catalog/repos/tum-esi__ptpsec.md) |
| Constellation fault | bad broadcast parameters move time for everyone at once | [2016 anomaly](../catalog/resources/meinberg-gps-utc-anomaly-2016.md) |

## 5. Defences, layered

1. **A holdover oscillator matched to the outage you must survive.** Section 3 table plus your
   required error budget gives the grade.
2. **Internal plausibility.** The loop's steering should change no faster than the
   oscillator's own aging and temperature behaviour allow. A walk that forces more steering than
   that is suspicious. Works only with a good oscillator: in the sample it caught every walk on
   OCXO, CSAC and Rb within 3-9 min, and missed 0.5 and 2 ns/s walks on the TCXO.
3. **Cross-check against an independent time source.** NTS-authenticated NTP
   ([ntpd-rs](../catalog/repos/pendulum-project__ntpd-rs.md), [chrony](../catalog/repos/gitlab.com__chrony__chrony.md)),
   PTP from a protected network ([linuxptp](../catalog/repos/nwtime__linuxptp.md)), White Rabbit
   inside a facility ([wr-cores](../catalog/repos/gitlab.com__ohwr__project__wr-cores.md)),
   LF time signals ([DCF77](../catalog/resources/ptb-dcf77.md), [WWVB](../catalog/resources/nist-wwvb.md)),
   eLoran ([UK programme](../catalog/resources/uk-eloran-programme-2025.md)) or LEO signals.
   In the sample this caught every walk on every grade in 2-11 min, independent of the oscillator.
   Many-source selection with outlier trimming ([Khronos, RFC 9523](../catalog/resources/rfc9523-khronos.md))
   and coarse signed bounds ([Roughtime](../catalog/repos/cloudflare__roughtime.md)) limit what
   one lying network source can do.
4. **Authenticated GNSS.** [Galileo OSNMA](../catalog/resources/galileo-osnma-service-page.md) authenticates navigation data, which blocks forged
   data but not a delayed (meaconed) signal, so it complements rather than replaces the
   cross-check.
5. **Detection must lead to a safe action.** The sample's guard drops into holdover on alarm.
   With Rb, OCXO or CSAC that kept time within 4-95 ns of truth while the unguarded clock
   followed the spoofer by up to 72 us. With a TCXO the guard ended about 52-55 us off, worse
   than following a 0.5 ns/s walk (3.6 us). A detector without a holdover oscillator only tells
   you that you are wrong.
6. **Monitor and log.** [chrony_exporter](../catalog/repos/superq__chrony_exporter.md) to
   Prometheus; [allantools](../catalog/repos/aewallin__allantools.md) on logged offsets to
   check your oscillator against its datasheet.

## 6. What a hackathon team can build

| Build | Stack | Time | What it shows |
|---|---|---|---|
| GNSS time server with spoof alarm | Pi CM4/CM5 + u-blox timing receiver + [SatPulse](../catalog/repos/jclark__satpulse.md) or [Time Pi](../catalog/repos/geerlingguy__time-pi.md), chrony with NTS sources, the sample's cross-source detector on `chronyc sourcestats` | 1 day | live alarm when GNSS time and NTS time diverge |
| Holdover scorecard | log a GPSDO or Pi PHC offset through an antenna-unplugged hour, [allantools](../catalog/repos/aewallin__allantools.md) for ADEV, compare with section 3 | 0.5 day | measured holdover vs datasheet; honest numbers |
| Spoof without RF | [NMEAdesync](../catalog/repos/zxsecurity__nmeadesync.md) against your own chrony+gpsd box in a closed lab | 0.5 day | the detector firing on a real daemon |
| Time-synced TDOA trio | three RTL-SDR receivers, [DC9ST TDOA scripts](../catalog/repos/dc9st__tdoa-evaluation-rtlsdr.md) with reference-transmitter sync, or PTP between Pis via [linuxptp](../catalog/repos/nwtime__linuxptp.md) | 1-2 days | localization error vs time error, and that it survives GNSS loss |
| GNSS-free time from LF | SDR + [gr_DCF77_Receiver](../catalog/repos/henningm1r__gr_dcf77_receiver.md) or [SDRangel](../catalog/repos/f4exb__sdrangel.md) Radio Clock | 1 day | a second time source that shares no failure mode with GNSS |
| Cheap GPSDO with a guard | [STM32 GPSDO](../catalog/repos/andrewbcn__stm32-gpsdo.md) or [PicoGPSDO](../catalog/repos/gibbi__picogpsdo.md) plus the sample's steering-plausibility check in firmware | 2 days, hardware dependent | detect a slow walk from the oscillator alone |

Gotchas from the sources and the sample:

- PTP accuracy needs hardware timestamping (`ethtool -T`) and symmetric paths; software
  timestamping on a Pi is microseconds, not nanoseconds.
- NMEA time arrives late and jittery; discipline on 1PPS and use NMEA only to label the second.
- A disciplined clock with a long time constant hides a slow walk in its own lag for a while;
  test detectors with walks from 0.1 to 10 ns/s, not only steps.
- Always run a no-spoof control and a "blind detector" control, as the sample's tests do; an
  alarm that never fires proves nothing.

## 7. Catalog

Repos (this lane): stacks [linuxptp](../catalog/repos/nwtime__linuxptp.md),
[chrony](../catalog/repos/gitlab.com__chrony__chrony.md),
[NTPsec](../catalog/repos/gitlab.com__ntpsec__ntpsec.md),
[ntpd-rs](../catalog/repos/pendulum-project__ntpd-rs.md),
[Statime](../catalog/repos/pendulum-project__statime.md),
[Meta Time](../catalog/repos/meta__time.md),
[PPSi](../catalog/repos/gitlab.com__ohwr__project__ppsi.md);
appliances [Time Card](../catalog/repos/time-appliances-project__time-card.md),
[Open Time Server](../catalog/repos/time-appliances-project__open-time-server.md),
[oscillatord](../catalog/repos/orolia2s__oscillatord.md),
[GPSDO PTP Master](../catalog/repos/rjrouquette__gpsdo.md);
GPSDO firmware [STM32 GPSDO](../catalog/repos/andrewbcn__stm32-gpsdo.md),
[Lars DIY GPSDO](../catalog/repos/andrewbcn__lars-diy-gpsdo.md),
[gpsdo-fw](../catalog/repos/dankar__gpsdo-fw.md),
[PicoGPSDO](../catalog/repos/gibbi__picogpsdo.md),
[SI5351 GPSDO](../catalog/repos/erikkaashoek__arduino_si5351_gpsdo.md);
measurement [allantools](../catalog/repos/aewallin__allantools.md),
[TICC](../catalog/repos/tapr__ticc.md), [pps-tools](../catalog/repos/redlab-i__pps-tools.md),
[clknetsim](../catalog/repos/mlichvar__clknetsim.md);
security [PTPsec](../catalog/repos/tum-esi__ptpsec.md),
[Roughtime](../catalog/repos/cloudflare__roughtime.md);
distributed sensing [TDOA RTL-SDR](../catalog/repos/dc9st__tdoa-evaluation-rtlsdr.md),
[kiwiclient](../catalog/repos/jks-prv__kiwiclient.md),
[cuckoo_time_translator](../catalog/repos/ethz-asl__cuckoo_time_translator.md),
[Heimdall DAQ](../catalog/repos/krakenrf__heimdall_daq_fw.md).

Reading order: [Lombardi, fundamentals](../catalog/resources/nist-lombardi-fundamentals-time-frequency.md)
=> [Lombardi, GPSDOs](../catalog/resources/nist-lombardi-gpsdo-calibration.md)
=> [NIST SP 1065](../catalog/resources/nist-sp1065-frequency-stability-handbook.md)
=> [CISA time guidance](../catalog/resources/cisa-time-guidance-network-operators.md)
=> [RFC 7384](../catalog/resources/rfc7384-time-protocol-security.md)
=> [Meta PTP deployment](../catalog/resources/meta-ptp-at-meta-2022.md)
=> [ION webinar: Should it be TPN?](../catalog/resources/ion-webinar-tpn.md).
Concept page: [concept:timing](../catalog/concepts/timing.md).
