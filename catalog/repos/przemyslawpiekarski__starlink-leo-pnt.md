# Starlink LEO-PNT

`repo:przemyslawpiekarski/starlink-leo-pnt` - <https://github.com/przemyslawpiekarski/starlink-leo-pnt>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 11 | Python | ? | 2026-03-11 | False | research-prototype | high |

Passive positioning using Starlink downlink signals as signals of opportunity: SDR capture, blind OFDM analysis, Doppler extraction, TDOA/FDOA solver and EKF with TLE-based orbits.

**Why it matters:** One of the very few open end-to-end attempts at Starlink-based PNT, a hot GNSS-alternative topic.

**Hackathon notes:** Needs an SDR that covers Ku-band via LNB, or use the simulation path with TLEs. Treat claims as unverified.

**Concepts:** [Signals of opportunity](../../catalog/concepts/signals-of-opportunity.md), [Software-defined GNSS receivers](../../catalog/concepts/gnss-sdr.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Space and orbital navigation](../../catalog/concepts/space-nav.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md)

**Tags:** `starlink`, `leo`, `doppler`, `sdr`, `leo-pnt`, `tdoa`

**Domains:** ground, multi

## Related

- alternative_to: [LEO SoOP positioning thesis (Voska)](../../catalog/repos/voskavoj__dp.md)
- alternative_to: [LEO-SPINE](../../catalog/repos/xyangll__leospine.md)
- alternative_to: [UT Starlink signal simulator](../../catalog/repos/gitlab.com__radionavlab__public__ut-starlink-signal-simulator.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [5. Absolute alternative PNT](../../docs/primer/05-absolute-alt-pnt.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [UT Starlink signal simulator](../../catalog/repos/gitlab.com__radionavlab__public__ut-starlink-signal-simulator.md) (alternative_to)
- [LEO SoOP positioning thesis (Voska)](../../catalog/repos/voskavoj__dp.md) (alternative_to)
- [Iridium PNT (Satellite Time and Location) and Iridium PNT ASIC](../../catalog/resources/iridium-pnt-stl-asic.md) (alternative_to)
- [Exploiting Starlink Signals for Navigation: First Results](../../catalog/resources/kassas-starlink-first-results-2022.md) (uses)
- [TrustPoint - C-band LEO PNT](../../catalog/resources/trustpoint-leo-pnt.md) (alternative_to)
- [Xona Space Systems Pulsar LEO PNT constellation](../../catalog/resources/xona-pulsar-leo-pnt.md) (alternative_to)

_Indexed by lane(s): alt-nav, gnss_

_GitHub metadata fetched 2026-11-06._
