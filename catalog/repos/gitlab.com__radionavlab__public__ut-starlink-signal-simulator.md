# UT Starlink signal simulator

`repo:gitlab.com/radionavlab/public/ut-starlink-signal-simulator` - <https://gitlab.com/radionavlab/public/ut-starlink-signal-simulator>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| ? | MATLAB | ? | ? | ? | research-prototype | medium |

MATLAB utility functions from UT Austin's Radionavigation Lab for simulating Starlink Ku-band downlink signals (OFDM frames, PSS/SSS, Doppler and path-loss histories), with MATLAB live-script playground examples.

**Why it matters:** Lets teams experiment with Starlink as a signal of opportunity for PNT without capturing real Ku-band data.

**Hackathon notes:** Small MATLAB codebase, MIT licensed, last commit January 2024 and marked work in progress. The companion paper is Komodromos, Qin and Humphreys, 'Signal Simulator for Starlink Ku-Band Downlink' (ION GNSS+ 2023).

## Deep dives

- [humphreys-2023-starlink-signal-structure](../../docs/paper-digests/humphreys-2023-starlink-signal-structure.md) (paper-digests)

**Concepts:** [Signals of opportunity](../../catalog/concepts/signals-of-opportunity.md), [Space and orbital navigation](../../catalog/concepts/space-nav.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md)

**Tags:** `starlink`, `leo-pnt`, `ku-band`, `ofdm`

**Domains:** space, multi

## Related

- alternative_to: [Starlink LEO-PNT](../../catalog/repos/przemyslawpiekarski__starlink-leo-pnt.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [5. Absolute alternative PNT](../../docs/primer/05-absolute-alt-pnt.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [Starlink LEO-PNT](../../catalog/repos/przemyslawpiekarski__starlink-leo-pnt.md) (alternative_to)
- [Signal Structure of the Starlink Ku-Band Downlink](../../catalog/resources/humphreys-2023-starlink-signal-structure.md) (has_code)
- [Iridium PNT (Satellite Time and Location) and Iridium PNT ASIC](../../catalog/resources/iridium-pnt-stl-asic.md) (alternative_to)
- [TrustPoint - C-band LEO PNT](../../catalog/resources/trustpoint-leo-pnt.md) (alternative_to)
- [Xona Space Systems Pulsar LEO PNT constellation](../../catalog/resources/xona-pulsar-leo-pnt.md) (alternative_to)

_Indexed by lane(s): gnss_
